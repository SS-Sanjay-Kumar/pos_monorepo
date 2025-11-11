from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    category_id: Optional[int] = None
    current_unit_price: Decimal
    tax_slab_id: int
    is_active: Optional[bool] = True

class ProductOut(BaseModel):
    id: int
    name: str
    sku: Optional[str]
    current_unit_price: Decimal
    tax_slab_id: int

    class Config:
        orm_mode = True
