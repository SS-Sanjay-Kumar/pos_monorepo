# app/schemas/invoice.py

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    product_id: int
    description: Optional[str] = None
    quantity: Decimal = Field(..., max_digits=12, decimal_places=2)
    unit_price: Decimal = Field(..., max_digits=12, decimal_places=2)
    tax_rate: Decimal = Field(..., max_digits=5, decimal_places=2)
    discount_amount: Optional[Decimal] = Field(
        Decimal("0.00"), max_digits=12, decimal_places=2
    )


class InvoiceCreate(BaseModel):
    invoice_number: str
    created_by: Optional[str] = None
    table_number: Optional[str] = None
    order_type: Optional[str] = "dine-in"
    employee_id: Optional[int] = None
    items: List[InvoiceItemCreate]


class InvoiceItemOut(BaseModel):
    id: int
    invoice_id: int
    product_id: int
    description: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    discount_amount: Decimal
    line_total: Decimal

    class Config:
        orm_mode = True


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    created_by: Optional[str] = None
    table_number: Optional[str] = None
    order_type: Optional[str] = None
    employee_id: Optional[int] = None
    status: str
    created_at: datetime
    total_amount: Decimal
    items: Optional[List[InvoiceItemOut]] = []

    class Config:
        orm_mode = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
        }
