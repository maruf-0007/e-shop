from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ---- Auth ----
class UserRegister(BaseModel):
    email: str
    first_name: str
    last_name: str
    mobile: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    mobile: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ---- Category ----
class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Product ----
class ProductCreate(BaseModel):
    name: str
    category_id: Optional[int] = None
    price: float
    stock: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    price: float
    stock: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Customer ----
class CustomerCreate(BaseModel):
    name: str
    email: str
    mobile: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    email: str
    mobile: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Invoice ----
class InvoiceItemCreate(BaseModel):
    product_id: int
    qty: int


class InvoiceCreate(BaseModel):
    customer_id: int
    items: List[InvoiceItemCreate]
    discount_pct: float = 0.0


class InvoiceItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    qty: int
    price: float
    total: float

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    total: float
    discount: float
    vat: float
    payable: float
    created_at: datetime
    items: List[InvoiceItemOut] = []

    class Config:
        from_attributes = True


# ---- Dashboard ----
class DashboardStats(BaseModel):
    products: int
    categories: int
    customers: int
    invoices: int
    total_sale: float
    vat_collection: float
    total_collection: float
