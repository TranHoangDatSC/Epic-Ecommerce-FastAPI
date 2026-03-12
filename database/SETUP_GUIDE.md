# OldShop Database Setup Guide

## Overview

This directory contains interactive setup scripts for initializing and managing the OldShop database. Three versions are provided for different operating systems:

1. **setup.py** - Python version (cross-platform: Windows, macOS, Linux)
2. **setup.cmd** - Windows batch script
3. **setup.sh** - Linux/macOS bash script

## Prerequisites

### Python Version
- Python 3.6 or higher
- psycopg2: `pip install psycopg2-binary`

### Windows Batch Version
- PostgreSQL client tools (psql)
- PostgreSQL must be installed and accessible in PATH

### Linux/macOS Bash Version
- PostgreSQL client tools (psql)
- PostgreSQL must be installed and accessible in PATH

## Installation

### 1. Install PostgreSQL

#### Windows
- Download from: https://www.postgresql.org/download/windows/
- Install and remember your password

#### macOS
```bash
brew install postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install postgresql postgresql-contrib
```

### 2. Ensure PostgreSQL is Running

#### Windows
```cmd
# PostgreSQL typically starts automatically
# Check Services if needed
```

#### macOS
```bash
brew services start postgresql
```

#### Linux
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Verify psql is in PATH

```bash
# Test if psql is accessible
psql --version
```

If not in PATH, add PostgreSQL bin directory to your system PATH.

## Usage

### Python Version (Recommended)

```bash
# Windows
python setup.py

# macOS/Linux
python3 setup.py
```

### Windows Batch Version

```cmd
setup.cmd
```

Or double-click the file in Windows Explorer.

### Linux/macOS Bash Version

```bash
chmod +x setup.sh
./setup.sh
```

## Interactive Menu

All three scripts follow the same interactive workflow:

### 1. Select Database System
```
Select database system to use:

1. PostgreSQL (sql_pg)
2. Exit

Enter your choice (1-2): 1
```

### 2. Enter PostgreSQL Connection Details

```
Enter PostgreSQL Connection Details
(Press Enter to use default values)

Username (default: postgres): postgres
Password (default: password): your_password
Host (default: localhost): localhost
Port (default: 5432): 5432
Database name (default: oldshop): oldshop
```

**Default values:**
- Username: `postgres`
- Password: `password`
- Host: `localhost`
- Port: `5432`
- Database: `oldshop`

### 3. Connection Test

The script will test the connection to PostgreSQL:
```
[INFO] Testing connection...
[OK] Connection successful
```

### 4. Main Menu

Choose from available operations:

```
What would you like to do?

1. Create database (New)
2. Reset database (Drop and create again)
3. Run init script (Database already exists)
4. Exit

Enter your choice (1-4): _
```

#### Option 1: Create Database
- Creates a new `oldshop` database
- Skips if database already exists

#### Option 2: Reset Database
- **WARNING**: Deletes all existing data
- Requires confirmation
- Optionally runs init script after reset

#### Option 3: Run Init Script
- Executes `init.sql` to create all tables and seed data
- Database must already exist
- Loads full schema with:
  - 15 database tables
  - Relationships and constraints
  - Indexes for performance
  - Sample seed data

#### Option 4: Exit
- Closes the setup utility

## Auto-Configuration

Create a `setup.env` file in the same directory to auto-configure credentials:

```bash
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=oldshop
```

The setup script will read these values (Python version only).

## Typical Setup Workflow

### First Time Setup

```bash
1. Run setup script
2. Select PostgreSQL
3. Enter credentials (or use defaults)
4. Choose "1. Create database (New)"
5. Choose "3. Run init script"
```

### Reset Database (Full Data Wipe)

```bash
1. Run setup script
2. Select PostgreSQL
3. Enter credentials
4. Choose "2. Reset database"
5. Confirm deletion
6. Select "yes" to run init script
```

### Just Initialize Schema (Database Exists)

```bash
1. Run setup script
2. Select PostgreSQL
3. Enter credentials
4. Choose "3. Run init script"
```

## Troubleshooting

### "Connection failed"

**Problem**: Cannot connect to PostgreSQL

**Solutions**:
- Verify PostgreSQL is running
- Check username and password
- Verify host address (usually `localhost`)
- Verify port number (usually `5432`)
- Check PostgreSQL is accessible from your network

### "Script file not found"

**Problem**: `init.sql` not in the same directory

**Solution**: Place `init.sql` in the same directory as the setup script

### "psql: command not found"

**Problem**: PostgreSQL client tools not installed or not in PATH

**Solutions**:
- Install PostgreSQL completely (includes psql)
- Add PostgreSQL bin directory to system PATH
  - Windows: `C:\Program Files\PostgreSQL\15\bin`
  - macOS: `/usr/local/opt/postgresql/bin`
  - Linux: Usually already in PATH

### Permission Denied (Linux/macOS)

```bash
chmod +x setup.sh
```

### Database already exists

The script handles this gracefully:
- If you choose "Create", it will skip if DB exists
- To overwrite, choose "Reset"

## Database Contents

After running `init.sql`, your database will contain:

### Tables (15 total)
- `role` - User roles (Admin, Moderator, User)
- `user` - User accounts
- `user_role` - User-Role mappings
- `category` - Product categories
- `product` - Products for sale
- `product_image` - Product images
- `order` - Customer orders
- `order_detail` - Order items
- `payment_method` - Payment types
- `contact_info` - Shipping addresses
- `shopping_cart` - User carts
- `shopping_cart_item` - Cart items
- `review` - Product reviews
- `voucher` - Discount codes
- `transaction` - Payment records
- `system_log` - Audit logs

### Features
- Foreign key relationships
- Check constraints for data validation
- Indexes for query performance
- Soft delete support
- Audit logging capability
- Sample seed data for testing

## API Connection

After setup, connect your FastAPI backend with:

```python
# .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/oldshop
```

Or use connection details from the setup script.

## Uninstall / Reset Everything

```bash
# Using the setup script
1. Choose "2. Reset database"
2. Confirm deletion

# This will drop all tables and data
# A fresh database and schema will be created
```

## Support

For issues:
1. Check PostgreSQL is running
2. Verify credentials are correct
3. Ensure `init.sql` is in the correct location
4. Check PostgreSQL logs for errors

## Version Information

- **Created**: March 12, 2026
- **Version**: 1.0.0
- **Database**: PostgreSQL 12+
- **Python**: 3.6+

---

**Happy database setup!** 🚀
