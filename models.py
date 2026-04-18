import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Use DATABASE_URL env var for production (e.g. Railway/Render MySQL/Postgres)
# Falls back to local SQLite for easy local dev
# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{os.getenv('MYSQLUSER','root')}:{os.getenv('MYSQLPASSWORD','')}@{os.getenv('MYSQLHOST','localhost')}:{os.getenv('MYSQLPORT','3306')}/{os.getenv('MYSQLDATABASE','eshop')}"
)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"
# SQLite needs check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    mobile = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", back_populates="owner")
    products = relationship("Product", back_populates="owner")
    customers = relationship("Customer", back_populates="owner")
    invoices = relationship("Invoice", back_populates="owner")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    vat = Column(Float, nullable=False, default=0.0)
    payable = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    product_name = Column(String(150), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")
