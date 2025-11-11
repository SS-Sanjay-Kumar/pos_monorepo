# app/api/invoices.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
import traceback
from decimal import Decimal, InvalidOperation
from typing import Any
from fastapi import Path

from app.db.session import get_db
from app.crud import create_invoice_with_items
from app.schemas.invoice import InvoiceCreate, InvoiceOut
from app.db.models import Invoice  # import model to re-query with selectinload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["invoices"])


def _decimal_to_float(value: Any) -> float:
    """
    Helper: convert Decimal or numeric-like to float safely; fallback to 0.0.
    """
    if value is None:
        return 0.0
    if isinstance(value, float):
        return value
    try:
        # cover Decimal, int, str
        return float(Decimal(value))
    except (InvalidOperation, TypeError, ValueError):
        try:
            return float(value)
        except Exception:
            return 0.0


@router.post("/", response_model=InvoiceOut)
async def create_invoice(payload: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """
    Create an invoice with its items.

    We create using existing CRUD helper, then re-fetch the invoice with
    selectinload(Invoice.items) so Pydantic won't attempt lazy loads (which
    fail in async contexts). We then build a response dict that includes
    'line_total' for each item (schema expects it).
    """
    try:
        # create invoice in DB (this returns ORM object or dict depending on your CRUD)
        invoice = await create_invoice_with_items(db, payload)

        # Ensure we have a numeric invoice.id to re-query; invoice may be ORM object
        invoice_id = None
        try:
            invoice_id = getattr(invoice, "id", None) or invoice.get("id")
        except Exception:
            invoice_id = None

        if not invoice_id:
            # If create_invoice_with_items returned a dict containing id, try that path:
            invoice_id = invoice.get("id") if isinstance(invoice, dict) else None

        if not invoice_id:
            # Give a helpful error if we can't determine id
            logger.error("Unable to determine created invoice id: %r", invoice)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                    "error": "invoice created but id not returned"
                },
            )

        # Re-fetch invoice with items eagerly loaded to avoid async lazy loads
        stmt = select(Invoice).options(selectinload(Invoice.items)).filter(Invoice.id == invoice_id)
        result = await db.execute(stmt)
        invoice_fresh = result.scalars().first()

        if not invoice_fresh:
            logger.error("Invoice not found after creation: id=%s", invoice_id)
            return JSONResponse(status_code=500, content={"detail": "Invoice not found after creation"})

        # Build response dict matching InvoiceOut schema
        resp = {
            "id": invoice_fresh.id,
            "invoice_number": invoice_fresh.invoice_number,
            "created_by": getattr(invoice_fresh, "created_by", None),
            "table_number": getattr(invoice_fresh, "table_number", None),
            "order_type": getattr(invoice_fresh, "order_type", None),
            "employee_id": getattr(invoice_fresh, "employee_id", None),
            "status": getattr(invoice_fresh, "status", None),
            "created_at": getattr(invoice_fresh, "created_at").isoformat() if getattr(invoice_fresh, "created_at", None) else None,
            "total_amount": _decimal_to_float(getattr(invoice_fresh, "total_amount", 0)),
            # items: ensure each item contains expected fields (and 'line_total')
            "items": []
        }

        for it in getattr(invoice_fresh, "items", []) or []:
            # try to get existing computed totals; fall back to compute from fields.
            qty = _decimal_to_float(getattr(it, "quantity", 0))
            unit_price = _decimal_to_float(getattr(it, "unit_price", 0))
            tax_rate = _decimal_to_float(getattr(it, "tax_rate", 0))
            discount_amount = _decimal_to_float(getattr(it, "discount_amount", 0))

            # prefer DB stored columns if present
            line_excl = getattr(it, "line_total_excl_tax", None)
            line_tax = getattr(it, "line_tax_amount", None)
            line_incl = getattr(it, "line_total_incl_tax", None)

            # convert if present
            line_excl_f = _decimal_to_float(line_excl) if line_excl is not None else None
            line_tax_f = _decimal_to_float(line_tax) if line_tax is not None else None
            line_incl_f = _decimal_to_float(line_incl) if line_incl is not None else None

            # If DB didn't store totals, compute them
            if line_excl_f is None:
                line_excl_f = round(qty * unit_price, 2)
            if line_tax_f is None:
                line_tax_f = round(line_excl_f * (tax_rate / 100.0), 2)
            if line_incl_f is None:
                line_incl_f = round(line_excl_f + line_tax_f - discount_amount, 2)

            item_obj = {
                "id": getattr(it, "id", None),
                "invoice_id": getattr(it, "invoice_id", None),
                "product_id": getattr(it, "product_id", None),
                "description": getattr(it, "description", None),
                "quantity": qty,
                "unit_price": unit_price,
                "tax_rate": tax_rate,
                "discount_amount": discount_amount,
                "line_total_excl_tax": line_excl_f,
                "line_tax_amount": line_tax_f,
                "line_total_incl_tax": line_incl_f,
                # some frontends expect a compact 'line_total' field — set to incl tax by convention
                "line_total": line_incl_f,
            }
            resp["items"].append(item_obj)

        # Return the response dict (FastAPI will apply response_model validation)
        return resp

    except IntegrityError as e:
        logger.exception("Database integrity error while creating invoice")
        detail = str(getattr(e, "orig", e))
        return JSONResponse(
            status_code=409,
            content={"detail": "Database integrity error", "error": detail},
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Unhandled exception in create_invoice:\n%s", tb)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e), "trace": tb},
        )


@router.post("/{invoice_id}/pay")
async def pay_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """
    Marks an invoice as paid if it exists.
    """
    from app.db.models import Invoice  # avoid circular import

    try:
        result = await db.execute(select(Invoice).filter(Invoice.id == invoice_id))
        invoice = result.scalars().first()
        if not invoice:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Invoice {invoice_id} not found"}
            )

        invoice.status = "paid"
        await db.commit()
        await db.refresh(invoice)

        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "total_amount": _decimal_to_float(invoice.total_amount),
            "paid_at": invoice.created_at.isoformat() if invoice.created_at else None
        }

    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )

@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(invoice_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    """
    Return invoice by id (with items). Builds a response dict identical
    to the create path to avoid async lazy-load / pydantic issues.
    """
    try:
        # re-query invoice with items eagerly loaded
        stmt = select(Invoice).options(selectinload(Invoice.items)).filter(Invoice.id == invoice_id)
        result = await db.execute(stmt)
        invoice = result.scalars().first()
        if not invoice:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        resp = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "created_by": getattr(invoice, "created_by", None),
            "table_number": getattr(invoice, "table_number", None),
            "order_type": getattr(invoice, "order_type", None),
            "employee_id": getattr(invoice, "employee_id", None),
            "status": getattr(invoice, "status", None),
            "created_at": getattr(invoice, "created_at").isoformat() if getattr(invoice, "created_at", None) else None,
            "total_amount": _decimal_to_float(getattr(invoice, "total_amount", 0)),
            "items": []
        }

        for it in getattr(invoice, "items", []) or []:
            qty = _decimal_to_float(getattr(it, "quantity", 0))
            unit_price = _decimal_to_float(getattr(it, "unit_price", 0))
            tax_rate = _decimal_to_float(getattr(it, "tax_rate", 0))
            discount_amount = _decimal_to_float(getattr(it, "discount_amount", 0))

            line_excl = getattr(it, "line_total_excl_tax", None)
            line_tax = getattr(it, "line_tax_amount", None)
            line_incl = getattr(it, "line_total_incl_tax", None)

            line_excl_f = _decimal_to_float(line_excl) if line_excl is not None else round(qty * unit_price, 2)
            line_tax_f = _decimal_to_float(line_tax) if line_tax is not None else round(line_excl_f * (tax_rate / 100.0), 2)
            line_incl_f = _decimal_to_float(line_incl) if line_incl is not None else round(line_excl_f + line_tax_f - discount_amount, 2)

            item_obj = {
                "id": getattr(it, "id", None),
                "invoice_id": getattr(it, "invoice_id", None),
                "product_id": getattr(it, "product_id", None),
                "description": getattr(it, "description", None),
                "quantity": qty,
                "unit_price": unit_price,
                "tax_rate": tax_rate,
                "discount_amount": discount_amount,
                "line_total_excl_tax": line_excl_f,
                "line_tax_amount": line_tax_f,
                "line_total_incl_tax": line_incl_f,
                "line_total": line_incl_f,
            }
            resp["items"].append(item_obj)

        return resp

    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Unhandled exception in get_invoice:\n%s", tb)
        return JSONResponse(status_code=500, content={"detail":"Internal Server Error","error":str(e),"trace":tb})