#!/bin/bash

# ===============================================
# OLDSHOP DATABASE - Database Setup (Linux/Mac)
# ===============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DB_USER="postgres"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="oldshop"

# Functions
print_header() {
    echo ""
    echo "=================================================="
    echo "OLDSHOP DATABASE - Database Setup"
    echo "=================================================="
    echo ""
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

select_database() {
    echo "Select database system to use:"
    echo ""
    echo "1. PostgreSQL (sql_pg)"
    echo "2. Exit"
    echo ""
    read -p "Enter your choice (1-2): " choice
    
    case $choice in
        1)
            echo "postgresql"
            ;;
        2)
            print_info "Exiting setup..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please select 1 or 2."
            select_database
            ;;
    esac
}

get_postgres_credentials() {
    echo ""
    echo "=================================================="
    echo "Enter PostgreSQL Connection Details"
    echo "(Press Enter to use default values)"
    echo "=================================================="
    echo ""
    
    read -p "Username (default: $DB_USER): " input_user
    DB_USER="${input_user:-$DB_USER}"
    
    read -sp "Password (default: $DB_PASSWORD): " input_password
    DB_PASSWORD="${input_password:-$DB_PASSWORD}"
    echo ""
    
    read -p "Host (default: $DB_HOST): " input_host
    DB_HOST="${input_host:-$DB_HOST}"
    
    read -p "Port (default: $DB_PORT): " input_port
    DB_PORT="${input_port:-$DB_PORT}"
    
    read -p "Database name (default: $DB_NAME): " input_db
    DB_NAME="${input_db:-$DB_NAME}"
}

test_connection() {
    print_info "Testing connection..."
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "postgres" -c "SELECT 1" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        print_success "Connection successful"
        return 0
    else
        print_error "Connection failed"
        return 1
    fi
}

create_database() {
    print_info "Creating database..."
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "postgres" <<EOF
SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';
EOF
    
    if [ $? -eq 0 ]; then
        # Check if it returned anything (database exists)
        result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'")
        if [ -z "$result" ]; then
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "postgres" <<EOF
CREATE DATABASE $DB_NAME;
EOF
            print_success "Database '$DB_NAME' created successfully"
        else
            print_warning "Database '$DB_NAME' already exists"
        fi
        return 0
    else
        print_error "Failed to create database"
        return 1
    fi
}

reset_database() {
    echo ""
    echo "=================================================="
    print_warning "WARNING: This will DELETE all data in the database!"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Operation cancelled"
        return 1
    fi
    
    print_info "Resetting database..."
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "postgres" <<EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Database '$DB_NAME' reset successfully"
        return 0
    else
        print_error "Failed to reset database"
        return 1
    fi
}

run_init_script() {
    script_path="$(dirname "$0")/init.sql"
    
    print_info "Running initialization script..."
    
    if [ ! -f "$script_path" ]; then
        print_error "Script file not found: $script_path"
        return 1
    fi
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" -f "$script_path"
    
    if [ $? -eq 0 ]; then
        print_success "Initialization script executed successfully"
        return 0
    else
        print_error "Failed to execute script"
        return 1
    fi
}

main_menu() {
    while true; do
        echo ""
        echo "=================================================="
        echo "What would you like to do?"
        echo ""
        echo "1. Create database (New)"
        echo "2. Reset database (Drop and create again)"
        echo "3. Run init script (Database already exists)"
        echo "4. Exit"
        echo ""
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                create_database
                ;;
            2)
                reset_database
                if [ $? -eq 0 ]; then
                    read -p "Run initialization script? (yes/no): " run_init
                    if [ "$run_init" = "yes" ]; then
                        run_init_script
                    fi
                fi
                ;;
            3)
                run_init_script
                ;;
            4)
                print_info "Exiting setup..."
                break
                ;;
            *)
                print_error "Invalid choice. Please select 1-4."
                ;;
        esac
    done
}

# Main execution
main() {
    print_header
    
    db_type=$(select_database)
    
    if [ "$db_type" = "postgresql" ]; then
        get_postgres_credentials
        
        echo ""
        echo "=================================================="
        echo "PostgreSQL Credentials Summary:"
        echo "=================================================="
        echo "Username: $DB_USER"
        echo "Host: $DB_HOST"
        echo "Port: $DB_PORT"
        echo "Database: $DB_NAME"
        echo ""
        
        if test_connection; then
            echo ""
            main_menu
        else
            print_warning "Please check your PostgreSQL connection settings"
            read -p "Try again? (yes/no): " retry
            if [ "$retry" = "yes" ]; then
                main
            fi
        fi
    fi
    
    print_info "Setup completed!"
    echo ""
}

# Execute main function
main
