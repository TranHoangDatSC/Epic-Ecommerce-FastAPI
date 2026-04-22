@echo off
REM OldShop Backend Setup Script for Windows

echo =========================================
echo OldShop Backend Setup
echo =========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo [4/5] Creating .env file from .env.example...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please update the database credentials.
) else (
    echo .env file already exists
)

echo [5/5] Setup complete!
echo.
echo =========================================
echo Next steps:
echo 1. Update .env with your PostgreSQL credentials
echo 2. Make sure PostgreSQL is running
echo 3. Run: python -m uvicorn app.main:app --reload
echo 4. Open http://localhost:8000/api/docs for API documentation
echo =========================================

pause
