from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import backend.models as models
import backend.schemas as schemas
import backend.auth as auth
from backend.models import get_db, User, Category, Product, Customer, Invoice, InvoiceItem

# Create tables
models.Base.metadata.create_all(bind=models.engine)

app = FastAPI(title="e-shop POS API", version="1.0.0", description="Point of Sale backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTH ROUTES
# ============================================================

@app.post("/api/auth/register", response_model=schemas.Token, tags=["Auth"])
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        mobile=user_data.mobile,
        hashed_password=auth.hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.post("/api/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/api/auth/me", response_model=schemas.UserOut, tags=["Auth"])
def me(current_user: User = Depends(auth.get_current_user)):
    return current_user


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/api/dashboard", response_model=schemas.DashboardStats, tags=["Dashboard"])
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    uid = current_user.id
    products = db.query(Product).filter(Product.user_id == uid).count()
    categories = db.query(Category).filter(Category.user_id == uid).count()
    customers = db.query(Customer).filter(Customer.user_id == uid).count()
    invoices_list = db.query(Invoice).filter(Invoice.user_id == uid).all()
    total_sale = sum(i.total for i in invoices_list)
    vat_collection = sum(i.vat for i in invoices_list)
    total_collection = sum(i.payable for i in invoices_list)
    return {
        "products": products,
        "categories": categories,
        "customers": customers,
        "invoices": len(invoices_list),
        "total_sale": total_sale,
        "vat_collection": vat_collection,
        "total_collection": total_collection,
    }


# ============================================================
# CATEGORIES
# ============================================================

@app.get("/api/categories", response_model=List[schemas.CategoryOut], tags=["Categories"])
def list_categories(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    q = db.query(Category).filter(Category.user_id == current_user.id)
    if search:
        q = q.filter(Category.name.ilike(f"%{search}%"))
    return q.order_by(Category.id.desc()).all()


@app.post("/api/categories", response_model=schemas.CategoryOut, status_code=201, tags=["Categories"])
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    existing = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.name == data.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = Category(name=data.name, user_id=current_user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@app.put("/api/categories/{cat_id}", response_model=schemas.CategoryOut, tags=["Categories"])
def update_category(
    cat_id: int,
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    cat = db.query(Category).filter(Category.id == cat_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = data.name
    db.commit()
    db.refresh(cat)
    return cat


@app.delete("/api/categories/{cat_id}", tags=["Categories"])
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    cat = db.query(Category).filter(Category.id == cat_id, Category.user_id == current_user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted"}


# ============================================================
# PRODUCTS
# ============================================================

def _product_out(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category_id": p.category_id,
        "category_name": p.category.name if p.category else None,
        "price": p.price,
        "stock": p.stock,
        "created_at": p.created_at,
    }


@app.get("/api/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    q = db.query(Product).filter(Product.user_id == current_user.id)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    products = q.order_by(Product.id.desc()).all()
    return [_product_out(p) for p in products]


@app.post("/api/products", response_model=schemas.ProductOut, status_code=201, tags=["Products"])
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    if data.category_id:
        cat = db.query(Category).filter(Category.id == data.category_id, Category.user_id == current_user.id).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
    prod = Product(
        name=data.name,
        category_id=data.category_id,
        price=data.price,
        stock=data.stock,
        user_id=current_user.id
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return _product_out(prod)


@app.put("/api/products/{prod_id}", response_model=schemas.ProductOut, tags=["Products"])
def update_product(
    prod_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    prod = db.query(Product).filter(Product.id == prod_id, Product.user_id == current_user.id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.name is not None: prod.name = data.name
    if data.category_id is not None: prod.category_id = data.category_id
    if data.price is not None: prod.price = data.price
    if data.stock is not None: prod.stock = data.stock
    db.commit()
    db.refresh(prod)
    return _product_out(prod)


@app.delete("/api/products/{prod_id}", tags=["Products"])
def delete_product(
    prod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    prod = db.query(Product).filter(Product.id == prod_id, Product.user_id == current_user.id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(prod)
    db.commit()
    return {"message": "Product deleted"}


# ============================================================
# CUSTOMERS
# ============================================================

@app.get("/api/customers", response_model=List[schemas.CustomerOut], tags=["Customers"])
def list_customers(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    q = db.query(Customer).filter(Customer.user_id == current_user.id)
    if search:
        q = q.filter(
            Customer.name.ilike(f"%{search}%") |
            Customer.email.ilike(f"%{search}%")
        )
    return q.order_by(Customer.id.desc()).all()


@app.post("/api/customers", response_model=schemas.CustomerOut, status_code=201, tags=["Customers"])
def create_customer(
    data: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    existing = db.query(Customer).filter(
        Customer.user_id == current_user.id,
        Customer.email == data.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    cust = Customer(name=data.name, email=data.email, mobile=data.mobile, user_id=current_user.id)
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust


@app.put("/api/customers/{cust_id}", response_model=schemas.CustomerOut, tags=["Customers"])
def update_customer(
    cust_id: int,
    data: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    cust = db.query(Customer).filter(Customer.id == cust_id, Customer.user_id == current_user.id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    if data.name is not None: cust.name = data.name
    if data.email is not None: cust.email = data.email
    if data.mobile is not None: cust.mobile = data.mobile
    db.commit()
    db.refresh(cust)
    return cust


@app.delete("/api/customers/{cust_id}", tags=["Customers"])
def delete_customer(
    cust_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    cust = db.query(Customer).filter(Customer.id == cust_id, Customer.user_id == current_user.id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(cust)
    db.commit()
    return {"message": "Customer deleted"}


# ============================================================
# INVOICES / SALES
# ============================================================

def _invoice_out(inv: Invoice) -> dict:
    return {
        "id": inv.id,
        "customer_id": inv.customer_id,
        "customer_name": inv.customer.name if inv.customer else None,
        "customer_email": inv.customer.email if inv.customer else None,
        "total": inv.total,
        "discount": inv.discount,
        "vat": inv.vat,
        "payable": inv.payable,
        "created_at": inv.created_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "qty": item.qty,
                "price": item.price,
                "total": item.total,
            }
            for item in inv.items
        ],
    }


@app.get("/api/invoices", response_model=List[schemas.InvoiceOut], tags=["Invoices"])
def list_invoices(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    q = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    invoices = q.order_by(Invoice.id.desc()).all()
    result = [_invoice_out(inv) for inv in invoices]
    if search:
        search = search.lower()
        result = [r for r in result if
                  search in str(r["id"]) or
                  search in (r["customer_name"] or "").lower()]
    return result


@app.get("/api/invoices/{inv_id}", response_model=schemas.InvoiceOut, tags=["Invoices"])
def get_invoice(
    inv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == inv_id, Invoice.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _invoice_out(inv)


@app.post("/api/invoices", response_model=schemas.InvoiceOut, status_code=201, tags=["Invoices"])
def create_invoice(
    data: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    customer = db.query(Customer).filter(Customer.id == data.customer_id, Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if not data.items:
        raise HTTPException(status_code=400, detail="Invoice must have at least one item")

    # Calculate totals
    subtotal = 0.0
    item_records = []
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id, Product.user_id == current_user.id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        if product.stock < item_data.qty:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")
        line_total = product.price * item_data.qty
        subtotal += line_total
        item_records.append((product, item_data.qty, line_total))

    discount_amt = subtotal * (data.discount_pct / 100)
    after_disc = subtotal - discount_amt
    vat = after_disc * 0.05
    payable = after_disc + vat

    inv = Invoice(
        customer_id=data.customer_id,
        user_id=current_user.id,
        total=subtotal,
        discount=discount_amt,
        vat=vat,
        payable=payable,
    )
    db.add(inv)
    db.flush()

    for product, qty, line_total in item_records:
        inv_item = InvoiceItem(
            invoice_id=inv.id,
            product_id=product.id,
            product_name=product.name,
            qty=qty,
            price=product.price,
            total=line_total,
        )
        db.add(inv_item)
        # Deduct stock
        product.stock -= qty

    db.commit()
    db.refresh(inv)
    return _invoice_out(inv)


@app.delete("/api/invoices/{inv_id}", tags=["Invoices"])
def delete_invoice(
    inv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.id == inv_id, Invoice.user_id == current_user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(inv)
    db.commit()
    return {"message": "Invoice deleted"}


# ============================================================
# HEALTH
# ============================================================

@app.get("/", tags=["Health"])
def root():
    return {"message": "e-shop POS API is running", "docs": "/docs"}


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}