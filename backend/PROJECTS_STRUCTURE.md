# OldShop Backend - Project Structure & Extension Guide

## 📁 Complete Directory Structure

```
backend/
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection & setup
│   ├── models.py                  # SQLAlchemy ORM models (ALL 15 tables)
│   ├── schemas.py                 # Pydantic validation schemas
│   ├── responses.py               # Standard API response models
│   │
│   ├── core/                      # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py            # JWT token generation, password hashing
│   │   ├── dependencies.py        # Auth middleware, role checking
│   │   └── exceptions.py          # Custom exception classes
│   │
│   ├── crud/                      # Database operations (CRUD)
│   │   ├── __init__.py
│   │   ├── base.py                # Base CRUD class with common operations
│   │   ├── user.py                # User CRUD + custom operations
│   │   ├── product.py             # Product CRUD + search/filter/approve
│   │   ├── category.py            # Category CRUD + hierarchy
│   │   └── order.py               # Order CRUD + status management
│   │
│   └── api/                       # API endpoints
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           ├── auth.py            # Register, Login endpoints
│           ├── users.py           # User management endpoints
│           ├── categories.py       # Category management endpoints
│           ├── products.py         # Product listing, creation, approval workflow
│           └── orders.py           # Order management + business logic
│
├── tests/                         # Unit tests (optional, to be added)
│   └── test_*.py
│
├── .env.example                   # Environment variables template
├── .env                           # Environment variables (git-ignored)
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # PostgreSQL Docker setup
├── requirements.txt               # Python dependencies
├── setup.cmd                      # Windows setup script
├── run.cmd                        # Windows run script
├── README.md                      # Main documentation
└── PROJECTS_STRUCTURE.md          # This file

```

## 🗄️ Database Models (15 Tables)

Tất cả models SQL đã được convert thành SQLAlchemy ORM models:

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| **User** | User accounts | user_id, username, email, password_hash, roles |
| **Role** | User roles | role_id, role_name (Admin, Mod, User) |
| **UserRole** | User-Role mapping | user_id, role_id |
| **Category** | Product categories | category_id, name, parent_id |
| **Product** | Products for sale | product_id, seller_id, price, status |
| **ProductImage** | Product images | image_id, product_id, image_url |
| **Order** | Customer orders | order_id, buyer_id, order_status |
| **OrderDetail** | Order items | order_detail_id, order_id, product_id, quantity |
| **PaymentMethod** | Payment options | payment_method_id, method_name |
| **ContactInfo** | Shipping addresses | contact_id, user_id, address |
| **ShoppingCart** | User cart | cart_id, user_id |
| **ShoppingCartItem** | Cart items | cart_item_id, cart_id, product_id |
| **Review** | Product reviews | review_id, product_id, buyer_id, rating |
| **Voucher** | Discount codes | voucher_id, code, discount_value |
| **Transaction** | Payment records | transaction_id, order_id, amount |
| **SystemLog** | Audit logs | log_id, user_id, action, timestamp |

## 🔌 How to Add New Features

### 1. Add New Database Table

**Step 1:** Add model in `app/models.py`
```python
class NewEntity(Base):
    __tablename__ = "new_entity"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # ... add fields
```

**Step 2:** Create schema in `app/schemas.py`
```python
class NewEntityCreate(BaseModel):
    name: str

class NewEntityResponse(NewEntityCreate):
    id: int
```

**Step 3:** Create CRUD in `app/crud/new_entity.py`
```python
from app.crud.base import CRUDBase
from app.models import NewEntity
from app.schemas import NewEntityCreate, NewEntityUpdate

class CRUDNewEntity(CRUDBase[NewEntity, NewEntityCreate, NewEntityUpdate]):
    def custom_operation(self, db: Session):
        return db.query(NewEntity).filter(...).all()

crud_new_entity = CRUDNewEntity(NewEntity)
```

**Step 4:** Create route in `app/api/routes/new_entity.py`
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import NewEntityResponse, NewEntityCreate
from app.crud.new_entity import crud_new_entity

router = APIRouter(prefix="/api/v1/new-entities", tags=["new-entity"])

@router.get("", response_model=list[NewEntityResponse])
async def list_new_entities(db: Session = Depends(get_db)):
    return crud_new_entity.get_all(db)

@router.post("", response_model=NewEntityResponse)
async def create_new_entity(data: NewEntityCreate, db: Session = Depends(get_db)):
    return crud_new_entity.create(db=db, obj_in=data)
```

**Step 5:** Register route in `app/main.py`
```python
from app.api.routes import new_entity
app.include_router(new_entity.router, prefix=settings.API_V1_STR)
```

### 2. Add Authentication to new endpoint

```python
from app.core.dependencies import get_current_user, check_admin

@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}

@router.post("/admin-only", dependencies=[Depends(check_admin)])
async def admin_endpoint(admin: User = Depends(check_admin)):
    return {"message": "Admin access confirmed"}
```

### 3. Add Role-Based Access Control

```python
from app.core.dependencies import check_user_role

# Allow specific roles (1=Admin, 2=Mod, 3=User)
@router.post("/seller-only", dependencies=[Depends(check_user_role([2, 3]))])
async def seller_endpoint():
    return {"message": "Seller can access"}
```

## 🧪 Testing Tips

### Test Authentication
```python
def test_login(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Test Authorization
```python
def test_admin_endpoint_forbidden(client):
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
```

## 🔐 Security Best Practices

1. **Environment Variables** - Never commit `.env` file
2. **Secret Key** - Change SECRET_KEY in production
3. **CORS** - Restrict origins in production
4. **HTTPS** - Use SSL/TLS in production
5. **Database** - Strong password, regular backups
6. **Password Hashing** - Always use bcrypt (already configured)
7. **Token Expiration** - Default 30 minutes (configurable)

## 📊 Performance Optimization

### Database Indexes
All frequently queried fields have indexes:
```python
Index('idx_product_status', 'status', postgresql_where=(is_deleted == False))
```

### Query Optimization Tips
```python
# ❌ Bad: N+1 query problem
for product in products:
    print(product.category.name)  # Extra query per product

# ✅ Good: Eager loading
products = db.query(Product).options(joinedload(Product.category))
```

### Pagination
Always use skip/limit:
```python
@router.get("/items")
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    items = db.query(Item).offset(skip).limit(limit).all()
```

## 📚 API Documentation

Auto-generated Swagger UI: `http://localhost:8000/api/docs`

### Key Endpoints

**Authentication:**
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get token

**Products:**
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `POST /api/v1/products/{id}/approve` - Approve (moderator)

**Orders:**
- `POST /api/v1/orders` - Create order (checks user is not seller!)
- `GET /api/v1/orders` - Get my orders

**Admin:**
- `GET /api/v1/users` - List users
- `GET /api/v1/orders/admin/all` - All orders

## 🤔 Troubleshooting

### Database Connection Issues
```python
# Check DATABASE_URL in .env
# Format: postgresql://user:password@host:port/database
# Test connection: python -c "from app.database import engine; engine.connect()"
```

### Import Errors
```python
# Make sure all __init__.py files exist
# Clear __pycache__: find . -type d -name __pycache__ -exec rm -r {} +
```

### Port Already in Use
```bash
# Change port in run.cmd or
# Kill process: netstat -ano | findstr :8000
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [JWT Authentication](https://python-jose.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/docs/)

---

**Last Updated:** March 12, 2026
**Version:** 1.0.0
