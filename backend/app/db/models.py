from sqlalchemy import (
    Column, Integer, BigInteger, String, DateTime, Boolean, Numeric, Text, Enum, ForeignKey, Date
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
# app/db/models.py (add or replace Employee model)
from sqlalchemy.orm import declarative_base
# keep your current import if different
Base = declarative_base()

class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

class UserAccount(Base):
    __tablename__ = "user_account"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role")

class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

class TaxSlab(Base):
    __tablename__ = "tax_slab"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rate = Column(Numeric(5,2), nullable=False)
    name = Column(String(50), nullable=False)

class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text)

class Product(Base):
    __tablename__ = "product"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sku = Column(String(100), unique=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    current_unit_price = Column(Numeric(12,2), nullable=False, default=0.00)
    tax_slab_id = Column(Integer, ForeignKey("tax_slab.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category")
    tax_slab = relationship("TaxSlab")

class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey("product.id"), nullable=False)
    unit_price = Column(Numeric(12,2), nullable=False)
    tax_slab_id = Column(Integer, ForeignKey("tax_slab.id"), nullable=False)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)



class Employee(Base):
    __tablename__ = "employee"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(30))
    employee_code = Column(String(100), unique=True, nullable=False)
    hire_date = Column(Date)
    designation = Column(String(100))
    user_account_id = Column(BigInteger, ForeignKey("user_account.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvoiceStatusEnum(str, enum.Enum):
    draft = "draft"
    preparing = "preparing"
    served = "served"
    finalized = "finalized"
    paid = "paid"
    cancelled = "cancelled"


class Invoice(Base):
    __tablename__ = "invoice"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("user_account.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(
        Enum("draft", "preparing", "served", "finalized", "paid", "cancelled", name="invoice_status"),
        default="draft"
    )
    total_amount = Column(Numeric(14, 2), default=0.00)
    notes = Column(Text, nullable=True)
    table_number = Column(String(50))
    order_type = Column(
        Enum("dine-in", "takeaway", "delivery", name="order_type"),
        default="dine-in"
    )
    employee_id = Column(Integer, ForeignKey("employee.id"), nullable=True)

    # ✅ Relationship to items
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        lazy="selectin",   # ✅ this is the key fix
        cascade="all, delete-orphan"
    )

class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    description = Column(String(512))
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0.00)
    line_total_excl_tax = Column(Numeric(14, 2), nullable=False)
    line_tax_amount = Column(Numeric(14, 2), nullable=False)
    line_total_incl_tax = Column(Numeric(14, 2), nullable=False)

    # ✅ Relationship to parent invoice
    invoice = relationship(
        "Invoice",
        back_populates="items",
        lazy="selectin"   # ✅ also important
    )


class Payment(Base):
    __tablename__ = "payment"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id = Column(BigInteger, ForeignKey("invoice.id"), nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow)
    amount = Column(Numeric(14,2), nullable=False)
    method = Column(String(50))
    reference = Column(String(255))

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor_id = Column(BigInteger, ForeignKey("user_account.id"))
    action = Column(String(100))
    entity = Column(String(100))
    entity_id = Column(String(100))
    payload = Column(Text)  # storing JSON text
    created_at = Column(DateTime, default=datetime.utcnow)
