# .shop POS Application

A full-stack Point of Sale system with a **FastAPI backend** and vanilla HTML/CSS/JS frontend.

---

## Project Structure

```
pos-app/
├── backend/
│   ├── main.py          # FastAPI app — all routes
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # JWT authentication utilities
│   └── requirements.txt
└── frontend/
    └── index.html       # Single-page frontend (all pages)
```

---

## Backend Setup

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the API server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`  
Alternative docs (ReDoc): `http://localhost:8000/redoc`

---

## Frontend Setup

Simply open `frontend/index.html` in your browser.  
The frontend connects to the API at `http://localhost:8000`.

> If you deploy the backend to a different host, update the `API` constant at the top of the `<script>` in `index.html`.

---

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET  | `/api/auth/me` | Get current user info |

### Dashboard
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard` | Summary stats |

### Categories
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/categories` | List (supports `?search=`) |
| POST | `/api/categories` | Create |
| PUT | `/api/categories/{id}` | Update |
| DELETE | `/api/categories/{id}` | Delete |

### Products
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/products` | List (supports `?search=`) |
| POST | `/api/products` | Create |
| PUT | `/api/products/{id}` | Update |
| DELETE | `/api/products/{id}` | Delete |

### Customers
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/customers` | List (supports `?search=`) |
| POST | `/api/customers` | Create |
| PUT | `/api/customers/{id}` | Update |
| DELETE | `/api/customers/{id}` | Delete |

### Invoices / Sales
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/invoices` | List all invoices |
| GET | `/api/invoices/{id}` | Get single invoice |
| POST | `/api/invoices` | Create sale/invoice (deducts stock) |
| DELETE | `/api/invoices/{id}` | Delete invoice |

---

## Features

- ✅ JWT authentication (register, login, persistent sessions)
- ✅ SQLite database (zero config, file-based: `pos.db`)
- ✅ Full CRUD for Categories, Products, Customers
- ✅ Sale creation with automatic stock deduction
- ✅ VAT (5%) and discount % calculation
- ✅ Invoice management with printable view
- ✅ Dashboard with live stats
- ✅ Sales reports with bar chart
- ✅ CORS enabled for frontend access

---

## Changing the Database

The app uses SQLite by default (`pos.db` file). To switch to PostgreSQL or MySQL, update the `SQLALCHEMY_DATABASE_URL` in `models.py`:

```python
# PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/posdb"

# MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/posdb"
```

---

## Security Note

Change the `SECRET_KEY` in `auth.py` before deploying to production:
```python
SECRET_KEY = "your-very-secret-key-here"
```
