# OldShop Database Setup Guide

## Overview

The OldShop database has been professionally converted from SQL Server to PostgreSQL with a modern, scalable architecture.

## Directory Structure

```
database/
├── setup.py                    # Python interactive setup (cross-platform)
├── setup.cmd                   # Windows batch setup script
├── setup.sh                    # Linux/macOS bash setup script
├── SETUP_GUIDE.md              # Detailed setup documentation
├── init.sql                    # Database initialization script
├── 01_schema/                  # Table definitions
│   ├── roles.sql
│   ├── users.sql
│   ├── categories.sql
│   ├── products.sql
│   ├── orders.sql
│   └── ... (15 tables total)
├── 02_functions/               # Stored procedures and triggers
│   ├── user/
│   ├── order_detail/
│   └── system/
├── 03_seeds/                   # Sample data (by table)
│   ├── role/
│   ├── user/
│   ├── product/
│   └── ...
├── 04_modules/                 # CRUD operations
│   ├── category/
│   ├── product/
│   ├── user/
│   └── order/
├── config/                     # Configuration files
│   ├── database_config.sql     # Database settings
│   ├── docker-compose.yml      # Docker setup
│   └── setup.sh                # Legacy setup script
└── migrations/                 # Migration scripts
    ├── 001_initial_schema.sql
    ├── 002_add_indexes.sql
    └── 003_add_functions.sql
```

## Quick Start

### Option 1: Python Setup (Recommended - Cross-platform)

**Windows:**
```cmd
python setup.py
```

**macOS/Linux:**
```bash
python3 setup.py
```

**Requirements:**
- Python 3.6+
- psycopg2: `pip install psycopg2-binary`

### Option 2: Windows Batch Setup

```cmd
setup.cmd
```

Requires: PostgreSQL client tools (psql) in PATH

### Option 3: Linux/macOS Bash Setup

```bash
chmod +x setup.sh
./setup.sh
```

Requires: PostgreSQL client tools (psql)

## Setup Process

All setup scripts follow an identical interactive workflow:

### Step 1: Select Database
```
Select database system to use:
1. PostgreSQL (sql_pg)
2. Exit
```

### Step 2: Enter Connection Details
```
Username (default: postgres): postgres
Password (default: password): your_password
Host (default: localhost): localhost
Port (default: 5432): 5432
Database name (default: oldshop): oldshop
```

### Step 3: Connection Test
The script verifies your PostgreSQL connection before proceeding.

### Step 4: Choose Operation
```
What would you like to do?

1. Create database (New)
2. Reset database (Drop and create again)
3. Run init script (Database already exists)
4. Exit
```

**1. Create Database**: Creates fresh `oldshop` database
**2. Reset Database**: Wipes all data and recreates database
**3. Run Init Script**: Loads schema and seed data into existing database

## Using Docker Compose

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Access psql
docker exec -it oldshop_postgres psql -U postgres -d oldshop

# Stop PostgreSQL
docker-compose down
```

## Manual Setup (Advanced)

```bash
# 1. Create database
createdb -U postgres oldshop

# 2. Run initialization script
psql -U postgres -d oldshop -f init.sql

# 3. Verify installation
psql -U postgres -d oldshop -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
```

## Database Schema

### 15 Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `role` | User roles | role_id, role_name |
| `user` | User accounts | user_id, username, email, password_hash |
| `user_role` | User-Role mapping | user_id, role_id |
| `category` | Product categories | category_id, name, parent_id |
| `product` | Products | product_id, seller_id, price, status |
| `product_image` | Product images | image_id, product_id, image_url |
| `order` | Customer orders | order_id, buyer_id, order_status |
| `order_detail` | Order items | order_detail_id, order_id, product_id |
| `payment_method` | Payment types | payment_method_id, method_name |
| `contact_info` | Shipping addresses | contact_id, user_id, address |
| `shopping_cart` | User carts | cart_id, user_id |
| `shopping_cart_item` | Cart items | cart_item_id, cart_id, product_id |
| `review` | Product reviews | review_id, product_id, buyer_id, rating |
| `voucher` | Discount codes | voucher_id, code, discount_value |
| `transaction` | Payment records | transaction_id, order_id, amount |

### Key Features

✅ **15 related tables** with proper foreign keys
✅ **Soft delete support** (is_deleted flag)
✅ **Status tracking** for products and orders
✅ **Audit logging** with system_log table
✅ **Performance indexes** on frequently queried columns
✅ **Check constraints** for data validation
✅ **Cascading operations** for data integrity

## Backend Connection

Connect your FastAPI backend using:

```python
# backend/.env
DATABASE_URL=postgresql://postgres:password@localhost:5432/oldshop
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=oldshop
```

Or use the values entered during setup.

## Troubleshooting

### "Connection failed"
- Verify PostgreSQL is running
- Check username/password
- Ensure host is correct (usually `localhost`)
- Verify port (usually `5432`)

### "psql: command not found"
- Install PostgreSQL completely (includes psql)
- Add PostgreSQL bin to system PATH

### Permission denied
```bash
chmod +x setup.sh
```

### Database already exists
- The setup script handles this gracefully
- Use "Reset database" option to overwrite

## Default Admin Account

After setup, you can create an admin user:

```sql
-- Insert admin role if not present
INSERT INTO role (role_name, description) VALUES ('Admin', 'Administrator');

-- Create admin user (you need to hash the password)
INSERT INTO "user" (username, email, password_hash, random_key, full_name, is_active) 
VALUES ('admin', 'admin@oldshop.com', 'hashed_password', 'random_key', 'Administrator', true);

-- Assign admin role
INSERT INTO user_role (user_id, role_id) SELECT user_id, role_id 
FROM "user", role WHERE username='admin' AND role_name='Admin';
```

## Notes

- **Soft Deletes**: Records are marked `is_deleted=true` instead of permanent deletion
- **Triggers**: Database includes triggers for business logic enforcement
- **Seed Data**: Sample data is included for testing
- **Indexes**: Optimized indexes on commonly queried columns

## Documentation

See **SETUP_GUIDE.md** for detailed setup instructions and troubleshooting.

## Support

For issues:
1. Review SETUP_GUIDE.md
2. Check PostgreSQL is running
3. Verify psql is in your PATH
4. Ensure init.sql is in the correct directory

---

**Version**: 1.0.0
**Last Updated**: March 12, 2026
**Status**: Production Ready ✅
- Sử dụng soft delete cho các bảng chính
- Dữ liệu mẫu được tách theo từng bảng để dễ quản lý