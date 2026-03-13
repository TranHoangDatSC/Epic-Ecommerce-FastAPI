#!/usr/bin/env python3
"""
OldShop E-commerce Platform - Project Setup Script
Automates the complete development environment setup for new developers.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def run_command(command, cwd=None, shell=False):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def check_docker():
    """Check if Docker is running"""
    success, output = run_command("docker info")
    return success

def setup_backend():
    """Setup the backend environment"""
    print_header("Setting up Backend Environment")

    backend_dir = Path("backend")

    if not backend_dir.exists():
        print_error("Backend directory not found!")
        return False

    os.chdir(backend_dir)

    # Create virtual environment
    print_info("Creating Python virtual environment...")
    success, error = run_command("python -m venv venv")
    if not success:
        print_error(f"Failed to create virtual environment: {error}")
        return False
    print_success("Virtual environment created")

    # Activate venv and install dependencies
    print_info("Installing Python dependencies...")
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_cmd = "venv/bin/pip install -r requirements.txt"

    success, error = run_command(pip_cmd, shell=True)
    if not success:
        print_error(f"Failed to install dependencies: {error}")
        return False
    print_success("Dependencies installed")

    os.chdir("..")
    return True

def setup_frontend():
    """Setup the frontend environment"""
    print_header("Setting up Frontend Environment")

    frontend_dir = Path("frontend")

    if not frontend_dir.exists():
        print_error("Frontend directory not found!")
        return False

    os.chdir(frontend_dir)

    # Install npm dependencies
    print_info("Installing Node.js dependencies...")
    success, error = run_command("npm install")
    if not success:
        print_error(f"Failed to install npm packages: {error}")
        return False
    print_success("Node.js dependencies installed")

    os.chdir("..")
    return True

def setup_database():
    """Setup the database using Docker"""
    print_header("Setting up Database")

    if not check_docker():
        print_warning("Docker is not running. Please start Docker and run:")
        print("  docker-compose up -d")
        return False

    print_info("Starting PostgreSQL database with Docker...")
    success, error = run_command("docker-compose up -d")
    if not success:
        print_error(f"Failed to start database: {error}")
        return False
    print_success("Database started successfully")
    print_info("Adminer available at: http://localhost:8080")

    return True

def copy_env_file():
    """Copy .env.example to .env"""
    print_header("Setting up Environment Variables")

    if Path(".env").exists():
        print_warning(".env file already exists, skipping copy")
        return True

    if not Path(".env.example").exists():
        print_error(".env.example file not found!")
        return False

    try:
        shutil.copy(".env.example", ".env")
        print_success("Environment file created from template")
        print_info("Please edit .env file with your actual credentials")
        return True
    except Exception as e:
        print_error(f"Failed to copy .env file: {e}")
        return False

def main():
    """Main setup function"""
    print_header("OldShop E-commerce Platform - Setup")
    print("This script will set up the complete development environment.\n")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 12):
        print_warning(f"Python {python_version.major}.{python_version.minor} detected. "
                     "This project is optimized for Python 3.12+")

    # Copy environment file
    if not copy_env_file():
        return 1

    # Setup backend
    if not setup_backend():
        return 1

    # Setup frontend
    if not setup_frontend():
        return 1

    # Setup database
    if not setup_database():
        print_warning("Database setup skipped. Run 'docker-compose up -d' manually.")

    # Final instructions
    print_header("Setup Complete!")
    print_success("Development environment is ready!")
    print("\nNext steps:")
    print("1. Edit .env file with your database credentials")
    print("2. Run database migrations: cd backend && alembic upgrade head")
    print("3. Start the backend: cd backend && python -m uvicorn app.main:app --reload")
    print("4. Start the frontend: cd frontend && npm start")
    print("\nAPI Documentation: http://localhost:8000/api/docs")
    print("Adminer (Database UI): http://localhost:8080")

    return 0

if __name__ == "__main__":
    sys.exit(main())