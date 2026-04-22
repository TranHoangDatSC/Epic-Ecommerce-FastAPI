# OldShop Backend API

FastAPI backend for OldShop E-commerce Platform với kiến trúc Clean Code, ORM SQLAlchemy, Authentication JWT + OAuth2, và Role-Based Access Control.

## 🚀 Tính Năng

### Authentication & Authorization
- ✅ User Registration & Login với JWT tokens
- ✅ OAuth2 + JWT token-based authentication
- ✅ Role-Based Access Control (RBAC) - 3 roles: Admin, Moderator, User
- ✅ Password hashing với bcrypt
- ✅ Token expiration management

### Business Logic
- ✅ Product management với status workflow (Pending, Approved, Rejected, Sold Out)
- ✅ **Bảo vệ logic**: User không thể mua hàng của chính mình
- ✅ Order management với order status tracking
- ✅ Shopping cart management
- ✅ Category management (phân cấp)
- ✅ User roles & permissions
- ✅ Product reviews & ratings
- ✅ Voucher/Discount support

### Technical Features
- ✅ SQLAlchemy ORM với PostgreSQL
- ✅ Pydantic schemas cho validation
- ✅ CRUD operations cho tất cả models
- ✅ RESTful API design
- ✅ Comprehensive error handling
- ✅ CORS support
- ✅ API documentation (Swagger/OpenAPI)

## 📋 Yêu Cầu

- Python 3.8+
- PostgreSQL 12+
- pip/poetry

## 🔧 Cài Đặt

### 1. Clone & Setup

```bash
cd backend
```

### 2. Tạo Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Environment

```bash
# Copy .env.example thành .env
cp .env.example .env

# Sửa .env với thông tin PostgreSQL của bạn:
# DATABASE_URL=postgresql://user:password@localhost:5432/oldshop
# SECRET_KEY=your-secret-key-min-32-characters
```

### 5. Khởi Tạo Database

```bash
# Từ thư mục database, chạy:
# psql -U postgres -d postgres -f config/database_config.sql
# psql -U postgres -d oldshop -f init.sql

# Hoặc nếu database đã tồn tại:
psql -U postgres -d oldshop -f database/init.sql
```

### 6. Chạy Server

```bash
# Development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc
python app/main.py
```

Server sẽ chạy tại: `http://localhost:8000`

API Docs: `http://localhost:8000/api/docs`

## 📁 Cấu Trúc Project

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI app
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py      # JWT & password hashing
│   │   ├── dependencies.py  # Auth dependencies & role checking
│   │   └── exceptions.py    # Custom exceptions
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py          # Base CRUD class
│   │   ├── user.py          # User CRUD operations
│   │   ├── product.py       # Product CRUD operations
│   │   ├── order.py         # Order CRUD operations
│   │   └── category.py      # Category CRUD operations
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py      # Auth endpoints (register, login)
│   │       ├── users.py     # User endpoints
│   │       ├── categories.py # Category endpoints
│   │       ├── products.py  # Product endpoints
│   │       └── orders.py    # Order endpoints
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables example
├── .env                    # Environment variables (local)
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🔐 Authentication

### Register
```bash
POST /api/v1/auth/register

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "0912345678",
  "address": "123 Main St"
}
```

### Login
```bash
POST /api/v1/auth/login

{
  "username": "john_doe",
  "password": "securepassword123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Sử Dụng Token
```bash
# Thêm header Authorization
Authorization: Bearer <access_token>
```

## 👥 Roles & Permissions

| Role | ID | Permissions |
|------|----|----|
| Admin | 1 | Quản lý users, products, categories, orders |
| Moderator | 2 | Duyệt products, quản lý orders |
| User | 3 | Tạo products, đặt hàng, viết reviews |

### Protected Endpoints

**Admin Only:**
- `GET /api/v1/users` - List all users
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/categories` - Create category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category
- `GET /api/v1/orders/admin/all` - List all orders
- `GET /api/v1/orders/admin/pending` - List pending orders

**Moderator+ Only:**
- `GET /api/v1/products/pending/all` - List pending products
- `POST /api/v1/products/{id}/approve` - Approve product
- `POST /api/v1/products/{id}/reject` - Reject product

**Authenticated Users:**
- `GET /api/v1/users/me` - Get own profile
- `PUT /api/v1/users/me` - Update own profile
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/seller/my-products` - Get own products
- `PUT /api/v1/products/{id}` - Update own product
- `DELETE /api/v1/products/{id}` - Delete own product
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - Get own orders
- `GET /api/v1/orders/{id}` - Get order details

## 🛒 API Endpoints

### Products
```bash
# List approved products
GET /api/v1/products?skip=0&limit=100&sort_by=created_at

# Search products
GET /api/v1/products?search=laptop

# Filter by category
GET /api/v1/products?category_id=1

# Get product detail
GET /api/v1/products/{product_id}

# Create product (requires auth)
POST /api/v1/products

# Update product
PUT /api/v1/products/{product_id}

# Delete product
DELETE /api/v1/products/{product_id}
```

### Orders
```bash
# Get my orders
GET /api/v1/orders

# Get order detail
GET /api/v1/orders/{order_id}

# Create order (IMPORTANT: checks user is not seller)
POST /api/v1/orders
{
  "contact_id": 1,
  "payment_method_id": 1,
  "order_items": [
    {"product_id": 1, "quantity": 2}
  ],
  "shipping_fee": 50000,
  "voucher_id": null,
  "notes": "Please deliver after 5pm"
}

# Update order status
PUT /api/v1/orders/{order_id}

# Cancel order
PUT /api/v1/orders/{order_id}
{
  "order_status": 4
}
```

### Categories
```bash
# List categories
GET /api/v1/categories

# Get parent categories
GET /api/v1/categories/parent

# Get category detail
GET /api/v1/categories/{category_id}

# Create category (admin only)
POST /api/v1/categories

# Update category (admin only)
PUT /api/v1/categories/{category_id}

# Delete category (admin only)
DELETE /api/v1/categories/{category_id}
```

## 🔒 Bảo Vệ Business Logic

### User không thể mua hàng của chính mình

Khi create order, API sẽ check:

```python
if product.seller_id == current_user.user_id:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"You cannot order product '{product.title}' because you are the seller"
    )
```

### Other Protections:
- ✅ Hashed passwords (bcrypt)
- ✅ JWT token expiration
- ✅ Role-based access control
- ✅ Soft delete for data integrity
- ✅ Product approval workflow
- ✅ Quantity validation on orders
- ✅ User ownership verification

## 📖 Models

### User
- user_id, username, email, password_hash, full_name, phone_number, address
- Relationships: user_roles, products, orders, shopping_cart, reviews

### Product
- product_id, seller_id, category_id, title, description, price, quantity
- status (0: Pending, 1: Approved, 2: Rejected, 3: Sold Out)
- Relationships: images, reviews, order_details, cart_items

### Order
- order_id, buyer_id, contact_id, payment_method_id
- order_status (0: Pending, 1: Confirmed, 2: Shipping, 3: Delivered, 4: Cancelled)
- Relationships: order_details, buyer, transactions

### Category
- category_id, name, description, parent_id
- Relationships: products, children categories

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🚀 Deployment

### Production Checklist:
- [ ] Change SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Configure CORS for specific domains
- [ ] Set up proper logging
- [ ] Use environment variables for all secrets
- [ ] Enable database backups

### Run with Gunicorn:
```bash
pip install gunicorn

gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please create a new branch for your feature or bug fix.

## 📞 Support

For issues and questions, please create an issue or contact the team.
