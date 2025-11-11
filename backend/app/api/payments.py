# app/api/payments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.db.models import Invoice
from app.db.models import Payment
from datetime import datetime
import traceback

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/{invoice_id}/pay")
async def pay_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Invoice).filter(Invoice.id == invoice_id))
        invoice = result.scalars().first()

        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

        payment = Payment(
            invoice_id=invoice.id,
            paid_at=datetime.utcnow(),
            amount=invoice.total_amount,
            method="cash",
            reference=f"PAY-{invoice.invoice_number}"
        )
        invoice.status = "paid"

        db.add(payment)
        await db.commit()
        await db.refresh(invoice)

        return {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status,
            "amount": float(invoice.total_amount),
            "paid_at": payment.paid_at.isoformat(),
        }

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
