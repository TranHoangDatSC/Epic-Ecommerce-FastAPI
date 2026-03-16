# OldShop API Endpoints Reference

## Base URL
```
http://localhost:8000/api/v1
```

> **Note:** For backwards compatibility, all endpoints are also available under `/api/*` (e.g., `/api/auth/login`).

## Authentication

### Register
```
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone_number": "0912345678",
  "address": "123 Main St"
}

Response: 201 Created
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-03-12T10:30:00"
}
```

### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Users

### Get Current User
```
GET /users/me
Authorization: Bearer {access_token}

Response: 200 OK
{
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone_number": "0912345678",
  "address": "123 Main St",
  "is_active": true,
  "roles": [
    {
      "role_id": 3,
      "role_name": "User",
      "description": "Regular user"
    }
  ]
}
```

### Update Current User Profile
```
PUT /users/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "John Updated",
  "phone_number": "0987654321",
  "address": "456 New St"
}

Response: 200 OK
```

### Get User by ID
```
GET /users/{user_id}

Response: 200 OK
```

### List All Users (Admin Only)
```
GET /users?skip=0&limit=100
Authorization: Bearer {admin_token}

Response: 200 OK
[
  {
    "user_id": 1,
    "username": "john_doe",
    ...
  },
  ...
]
```

### Delete User (Admin Only)
```
DELETE /users/{user_id}
Authorization: Bearer {admin_token}

Response: 204 No Content
```

## Categories

### List Categories
```
GET /categories?skip=0&limit=100&active_only=true

Response: 200 OK
[
  {
    "category_id": 1,
    "name": "Electronics",
    "description": "Electronic devices",
    "parent_id": null,
    "is_active": true,
    "created_at": "2024-03-12T10:00:00"
  }
]
```

### Get Parent Categories
```
GET /categories/parent

Response: 200 OK
```

### Get Category Details
```
GET /categories/{category_id}

Response: 200 OK
{
  "category_id": 1,
  "name": "Electronics",
  "description": "Electronic devices",
  "parent_id": null,
  "is_active": true
}
```

### Get Child Categories
```
GET /categories/{category_id}/children

Response: 200 OK
```

### Create Category (Admin Only)
```
POST /categories
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "New Category",
  "description": "Description",
  "parent_id": null
}

Response: 201 Created
```

### Update Category (Admin Only)
```
PUT /categories/{category_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Updated Name",
  "is_active": false
}

Response: 200 OK
```

### Delete Category (Admin Only)
```
DELETE /categories/{category_id}
Authorization: Bearer {admin_token}

Response: 204 No Content
```

## Products

### List Approved Products
```
GET /products?skip=0&limit=100&sort_by=created_at
GET /products?sort_by=price&search=laptop
GET /products?category_id=1

Query Parameters:
- skip: int (default 0)
- limit: int (default 100, max 1000)
- category_id: int (optional)
- search: string (optional - searches title and description)
- sort_by: string (created_at|price|rating)

Response: 200 OK
[
  {
    "product_id": 1,
    "seller_id": 5,
    "category_id": 1,
    "title": "HP Laptop",
    "description": "High performance laptop",
    "price": "15000000.00",
    "quantity": 10,
    "status": 1,
    "view_count": 250,
    "created_at": "2024-03-12T10:00:00"
  }
]
```

### Get Product Details
```
GET /products/{product_id}

Response: 200 OK
{
  "product_id": 1,
  "title": "HP Laptop",
  "price": "15000000.00",
  "product_images": [
    {
      "image_id": 1,
      "image_url": "https://...",
      "alt_text": "Front view",
      "is_primary": true
    }
  ],
  "seller": {
    "user_id": 5,
    "username": "seller_john",
    "full_name": "John Seller"
  }
}
```

### Create Product (Authenticated)
```
POST /products
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "category_id": 1,
  "title": "New Product",
  "description": "Product description",
  "price": "1000000.00",
  "quantity": 10,
  "video_url": "https://youtube.com/...",
  "weight_grams": 1500,
  "dimensions": "10x20x5 cm",
  "condition_rating": 8,
  "warranty_months": 12
}

Response: 201 Created
{
  "product_id": 2,
  "status": 0,
  "seller_id": 1,
  ...
}
```

### Get My Products (Authenticated)
```
GET /products/seller/my-products
Authorization: Bearer {access_token}

Response: 200 OK
```

### Update Product (Seller or Admin)
```
PUT /products/{product_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title",
  "price": "950000.00",
  "quantity": 5
}

Response: 200 OK
```

### Delete Product (Seller or Admin)
```
DELETE /products/{product_id}
Authorization: Bearer {access_token}

Response: 204 No Content
```

### List Pending Products (Moderator+)
```
GET /products/pending/all
Authorization: Bearer {moderator_token}

Response: 200 OK
```

### Approve Product (Moderator+)
```
POST /products/{product_id}/approve
Authorization: Bearer {moderator_token}

Response: 200 OK
{
  "product_id": 2,
  "status": 1,
  "approved_by": 2
}
```

### Reject Product (Moderator+)
```
POST /products/{product_id}/reject?reject_reason=Quality%20not%20good
Authorization: Bearer {moderator_token}

Response: 200 OK
{
  "product_id": 2,
  "status": 2,
  "reject_reason": "Quality not good"
}
```

## Orders

### List My Orders
```
GET /orders?skip=0&limit=100
GET /orders?status_filter=0
Authorization: Bearer {access_token}

Query Parameters:
- skip: int
- limit: int
- status_filter: int (0=Pending, 1=Confirmed, 2=Shipping, 3=Delivered, 4=Cancelled)

Response: 200 OK
[
  {
    "order_id": 1,
    "buyer_id": 1,
    "order_date": "2024-03-12T10:00:00",
    "total_amount": "15000000.00",
    "final_amount": "15050000.00",
    "order_status": 0
  }
]
```

### Get Order Details
```
GET /orders/{order_id}
Authorization: Bearer {access_token}

Response: 200 OK
{
  "order_id": 1,
  "buyer_id": 1,
  "contact_id": 1,
  "payment_method_id": 1,
  "order_date": "2024-03-12T10:00:00",
  "order_status": 0,
  "order_details": [
    {
      "order_detail_id": 1,
      "product_id": 1,
      "quantity": 2,
      "price_at_purchase": "15000000.00",
      "subtotal": "30000000.00",
      "product": { ... }
    }
  ]
}
```

### Create Order ⚠️ (KEY: User Cannot Be Seller)
```
POST /orders
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "contact_id": 1,
  "payment_method_id": 1,
  "order_items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ],
  "shipping_fee": "50000.00",
  "voucher_id": null,
  "notes": "Please deliver after 5pm"
}

Response: 201 Created
{
  "order_id": 1,
  "buyer_id": 1,
  "order_status": 0,
  "final_amount": "30050000.00"
}

IMPORTANT ERROR MESSAGES:
- "You cannot order product 'XXX' because you are the seller"
- "Product 'XXX' has insufficient quantity"
- "Invalid contact information"
```

### Update Order (User Can Cancel Pending, Moderator+ Can Update Status)
```
PUT /orders/{order_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "order_status": 4,
  "tracking_number": "TRACK123",
  "notes": "Updated notes"
}

Response: 200 OK

Note: Regular users can only cancel (status=4) pending orders
Moderators can update to any status
```

### Delete Order (Admin Only)
```
DELETE /orders/{order_id}
Authorization: Bearer {admin_token}

Response: 204 No Content
```

### Admin: List All Orders
```
GET /orders/admin/all?skip=0&limit=100
GET /orders/admin/all?status_filter=0
Authorization: Bearer {admin_token}

Response: 200 OK
```

### Admin: Get Pending Orders
```
GET /orders/admin/pending
Authorization: Bearer {admin_token}

Response: 200 OK
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Successful request |
| 201 | Created - Resource created successfully |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

## Order Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Pending | Order created, awaiting confirmation |
| 1 | Confirmed | Order confirmed by admin |
| 2 | Shipping | Order shipped |
| 3 | Delivered | Order delivered |
| 4 | Cancelled | Order cancelled |

## Product Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Pending | Awaiting moderation review |
| 1 | Approved | Approved and visible to buyers |
| 2 | Rejected | Rejected by moderator |
| 3 | Sold Out | Out of stock |

## Role IDs

| ID | Role | Permissions |
|----|------|------------|
| 1 | Admin | Full access to all resources |
| 2 | Moderator | Can approve/reject products, manage orders |
| 3 | User | Can create products (pending), place orders, write reviews |

---

**Last Updated:** March 12, 2026
**API Version:** 1.0.0
