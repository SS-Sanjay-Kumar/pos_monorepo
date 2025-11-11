from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductOut
from app.crud import create_product, get_product
from typing import List

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductOut)
async def create_product_endpoint(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    obj = await create_product(db, payload)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.get("/{product_id}", response_model=ProductOut)
async def get_product_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    obj = await get_product(db, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    return obj
