# app/api/tax_slabs.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import TaxSlab  # adjust if separate model
from sqlalchemy.future import select

router = APIRouter(prefix="/tax_slabs", tags=["tax_slabs"])

class TaxSlabCreate(BaseModel):
    rate: float
    name: str

@router.post("/")
async def create_tax_slab(payload: TaxSlabCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(TaxSlab).where(TaxSlab.rate == payload.rate))
    slab = existing.scalars().first()
    if not slab:
        slab = TaxSlab(rate=payload.rate, name=payload.name)
        db.add(slab)
        await db.commit()
        await db.refresh(slab)
    return {"id": slab.id, "rate": slab.rate, "name": slab.name}
