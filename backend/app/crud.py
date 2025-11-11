from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from app.db import models
from decimal import Decimal
from app.db.models import Invoice, InvoiceItem   # ✅ you were missing this!
import traceback                                 # ✅ and this too


async def get_product(db: AsyncSession, product_id: int):
    q = await db.execute(select(models.Product).where(models.Product.id == product_id))
    return q.scalar_one_or_none()

async def create_product(db: AsyncSession, product_in):
    obj = models.Product(
        name=product_in.name,
        sku=product_in.sku,
        category_id=product_in.category_id,
        current_unit_price=product_in.current_unit_price,
        tax_slab_id=product_in.tax_slab_id,
    )
    db.add(obj)
    await db.flush()
    return obj

async def get_employee_by_code(db: AsyncSession, code: str):
    q = await db.execute(select(models.Employee).where(models.Employee.employee_code == code))
    return q.scalar_one_or_none()

# invoice creation in a transaction
from sqlalchemy import func

async def create_invoice_with_items(db: AsyncSession, payload):
    """
    Create invoice and its associated items atomically.
    """
    try:
        # Create the Invoice object
        invoice = Invoice(
            invoice_number=payload.invoice_number,
            created_by=payload.created_by,
            table_number=payload.table_number,
            order_type=payload.order_type,
            employee_id=payload.employee_id,
            status="finalized",
            total_amount=Decimal("0.00")
        )
        db.add(invoice)
        await db.flush()  # ensures invoice.id is generated before adding items

        total = Decimal("0.00")

        for item in payload.items:
            line_total_excl = Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
            line_tax = (line_total_excl * Decimal(str(item.tax_rate))) / Decimal("100")
            line_total_incl = line_total_excl + line_tax
            total += line_total_incl

            db_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                description=item.description,
                quantity=Decimal(str(item.quantity)),
                unit_price=Decimal(str(item.unit_price)),
                tax_rate=Decimal(str(item.tax_rate)),
                discount_amount=Decimal(str(item.discount_amount or 0)),
                line_total_excl_tax=line_total_excl,
                line_tax_amount=line_tax,
                line_total_incl_tax=line_total_incl,
            )
            db.add(db_item)

        invoice.total_amount = total

        await db.commit()
        await db.refresh(invoice)
        return invoice

    except Exception as e:
        await db.rollback()
        tb = traceback.format_exc()
        print(f"❌ Error in create_invoice_with_items:\n{tb}")
        raise e


async def get_or_create_tax_slab(db, rate: float, name: str):
    from app.db.models import TaxSlab
    result = await db.execute(
        select(TaxSlab).where(TaxSlab.rate == rate)
    )
    slab = result.scalars().first()
    if slab:
        return slab
    new_slab = TaxSlab(rate=rate, name=name)
    db.add(new_slab)
    await db.commit()
    await db.refresh(new_slab)
    return new_slab
