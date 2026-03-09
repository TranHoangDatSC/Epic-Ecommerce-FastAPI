#!/bin/bash

# Setup script for OldShop PostgreSQL Database

echo "Setting up OldShop Database..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Please start PostgreSQL service first."
    echo "You can start it with: sudo systemctl start postgresql"
    echo "Or using Docker: docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15"
    exit 1
fi

# Check if database exists, create if not
DB_EXISTS=$(psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw oldshop; echo $?)

if [ $DB_EXISTS -ne 0 ]; then
    echo "Creating database 'oldshop'..."
    createdb -h localhost -U postgres oldshop
    if [ $? -ne 0 ]; then
        echo "Failed to create database. Please check your PostgreSQL permissions."
        exit 1
    fi
else
    echo "Database 'oldshop' already exists."
fi

# Run initialization script
echo "Running database initialization..."
psql -h localhost -U postgres -d oldshop -f ../init.sql

if [ $? -eq 0 ]; then
    echo "Database setup completed successfully!"
    echo ""
    echo "Default login credentials:"
    echo "Admin: admin@oldshop.com / admin123"
    echo "Mod: reviewer@gmail.com / reviewer123"
    echo "User: user1@gmail.com / user123"
    echo "Seller: seller1@gmail.com / seller123"
    echo ""
    echo "You can now start your application!"
else
    echo "Database setup failed. Please check the error messages above."
    exit 1
fi