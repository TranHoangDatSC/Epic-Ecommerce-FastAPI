#!/usr/bin/env python3
"""
===============================================
OLDSHOP DATABASE - Database Setup
===============================================
Interactive setup script for OldShop database
"""

import psycopg2 # type: ignore
import os
import sys
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print application header"""
    print("\n" + "=" * 50)
    print("OLDSHOP DATABASE - Database Setup")
    print("=" * 50 + "\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}[OK] {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}[ERROR] {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}[INFO] {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}[WARNING] {message}{Colors.ENDC}")


def select_database_type():
    """Select which database system to use"""
    print("Select database system to use:\n")
    print("1. PostgreSQL (sql_pg)")
    print("2. Exit")
    print()
    
    choice = input("Enter your choice (1-2): ").strip()
    
    if choice == "1":
        return "postgresql"
    elif choice == "2":
        print_info("Exiting setup...")
        sys.exit(0)
    else:
        print_error("Invalid choice. Please select 1 or 2.")
        return select_database_type()


def get_postgres_credentials():
    """Get PostgreSQL connection credentials"""
    print("\n" + "=" * 50)
    print("Enter PostgreSQL Connection Details")
    print("(Press Enter to use default values)")
    print("=" * 50 + "\n")
    
    # Default values
    defaults = {
        'username': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': '5432',
        'database': 'oldshop'
    }
    
    credentials = {}
    
    print(f"Username (default: {defaults['username']}): ", end="")
    username = input().strip()
    credentials['username'] = username if username else defaults['username']
    
    print(f"Password (default: {defaults['password']}): ", end="")
    password = input().strip()
    credentials['password'] = password if password else defaults['password']
    
    print(f"Host (default: {defaults['host']}): ", end="")
    host = input().strip()
    credentials['host'] = host if host else defaults['host']
    
    print(f"Port (default: {defaults['port']}): ", end="")
    port = input().strip()
    credentials['port'] = port if port else defaults['port']
    
    print(f"Database name (default: {defaults['database']}): ", end="")
    database = input().strip()
    credentials['database'] = database if database else defaults['database']
    
    return credentials


def test_connection(credentials):
    """Test PostgreSQL connection"""
    print_info("Testing connection...")
    
    try:
        conn = psycopg2.connect(
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            port=credentials['port'],
            database='postgres'  # Connect to default postgres database first
        )
        conn.close()
        print_success("Connection successful")
        return True
    except psycopg2.Error as e:
        print_error(f"Connection failed: {str(e)}")
        return False


def create_database(credentials):
    """Create OldShop database"""
    print_info("Creating database...")
    
    try:
        # Connect to postgres to create new database
        conn = psycopg2.connect(
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            port=int(credentials['port']),
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{credentials['database']}'"
        )
        db_exists = cursor.fetchone()
        
        if db_exists:
            print_warning(f"Database '{credentials['database']}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {credentials['database']}")
            print_success(f"Database '{credentials['database']}' created successfully")
        
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print_error(f"Failed to create database: {str(e)}")
        return False


def reset_database(credentials):
    """Reset OldShop database (drop and recreate)"""
    print("\n" + "=" * 50)
    print_warning("WARNING: This will DELETE all data in the database!")
    response = input("Are you sure? (yes/no): ").strip().lower()
    
    if response != "yes":
        print_info("Operation cancelled")
        return False
    
    print_info("Resetting database...")
    
    try:
        conn = psycopg2.connect(
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            port=int(credentials['port']),
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Terminate existing connections
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{credentials['database']}'
            AND pid <> pg_backend_pid();
        """)
        
        # Drop database
        cursor.execute(f"DROP DATABASE IF EXISTS {credentials['database']}")
        print_success(f"Database '{credentials['database']}' dropped")
        
        # Create new database
        cursor.execute(f"CREATE DATABASE {credentials['database']}")
        print_success(f"Database '{credentials['database']}' created")
        
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print_error(f"Failed to reset database: {str(e)}")
        return False


def run_init_script(credentials, script_path):
    """Run initialization SQL script"""
    print_info("Running initialization script...")
    
    if not os.path.exists(script_path):
        print_error(f"Script file not found: {script_path}")
        return False
    
    try:
        # Read SQL script
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Connect and execute
        conn = psycopg2.connect(
            user=credentials['username'],
            password=credentials['password'],
            host=credentials['host'],
            port=int(credentials['port']),
            database=credentials['database']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute script
        cursor.execute(sql_script)
        
        print_success("Initialization script executed successfully")
        
        cursor.close()
        conn.close()
        return True
    except (psycopg2.Error, Exception) as e:
        print_error(f"Failed to execute script: {str(e)}")
        return False


def main_menu(credentials):
    """Show main menu with database operations"""
    while True:
        print("\n" + "=" * 50)
        print("What would you like to do?\n")
        print("1. Create database (New)")
        print("2. Reset database (Drop and create again)")
        print("3. Run init script (Database already exists)")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            create_database(credentials)
        elif choice == "2":
            reset_database(credentials)
            # Optionally run init script after reset
            if input("\nRun initialization script? (yes/no): ").strip().lower() == "yes":
                script_path = os.path.join(
                    os.path.dirname(__file__),
                    "init.sql"
                )
                run_init_script(credentials, script_path)
        elif choice == "3":
            script_path = os.path.join(
                os.path.dirname(__file__),
                "init.sql"
            )
            run_init_script(credentials, script_path)
        elif choice == "4":
            print_info("Exiting setup...")
            break
        else:
            print_error("Invalid choice. Please select 1-4.")


def main():
    """Main entry point"""
    print_header()
    
    # Select database type
    db_type = select_database_type()
    
    if db_type == "postgresql":
        # Get credentials
        credentials = get_postgres_credentials()
        
        print("\n" + "=" * 50)
        print("PostgreSQL Credentials Summary:")
        print("=" * 50)
        print(f"Username: {credentials['username']}")
        print(f"Host: {credentials['host']}")
        print(f"Port: {credentials['port']}")
        print(f"Database: {credentials['database']}")
        print()
        
        # Test connection
        if not test_connection(credentials):
            print_warning("Please check your PostgreSQL connection settings")
            retry = input("Try again? (yes/no): ").strip().lower()
            if retry == "yes":
                main()
            else:
                sys.exit(1)
        
        print()
        
        # Show main menu
        main_menu(credentials)
    
    print_info("Setup completed!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[INTERRUPT] Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
