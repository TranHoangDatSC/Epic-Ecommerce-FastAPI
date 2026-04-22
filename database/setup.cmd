@echo off
REM ===============================================
REM OLDSHOP DATABASE - Database Setup (Windows)
REM ===============================================

setlocal enabledelayedexpansion

REM Default values
set DB_USER=postgres
set DB_PASSWORD=123
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=oldshop

:show_header
cls
echo.
echo ==================================================
echo OLDSHOP DATABASE - Database Setup
echo ==================================================
echo.
goto select_database

:select_database
echo Select database system to use:
echo.
echo 1. PostgreSQL (sql_pg)
echo 2. Exit
echo.
set /p choice="Enter your choice (1-2): "

if "%choice%"=="1" goto get_postgres_credentials
if "%choice%"=="2" (
    echo [INFO] Exiting setup...
    exit /b 0
)

echo [ERROR] Invalid choice. Please select 1 or 2.
goto select_database

:get_postgres_credentials
cls
echo.
echo ==================================================
echo Enter PostgreSQL Connection Details
echo (Press Enter to use default values)
echo ==================================================
echo.

set /p input_user="Username (default: %DB_USER%): "
if not "!input_user!"=="" set DB_USER=!input_user!

set /p input_password="Password (default: %DB_PASSWORD%): "
if not "!input_password!"=="" set DB_PASSWORD=!input_password!

set PGPASSWORD=%DB_PASSWORD%

set /p input_host="Host (default: %DB_HOST%): "
if not "!input_host!"=="" set DB_HOST=!input_host!

set /p input_port="Port (default: %DB_PORT%): "
if not "!input_port!"=="" set DB_PORT=!input_port!

set /p input_db="Database name (default: %DB_NAME%): "
if not "!input_db!"=="" set DB_NAME=!input_db!

goto show_credentials

:show_credentials
echo.
echo ==================================================
echo PostgreSQL Credentials Summary:
echo ==================================================
echo Username: %DB_USER%
echo Host: %DB_HOST%
echo Port: %DB_PORT%
echo Database: %DB_NAME%
echo.

goto test_connection

:test_connection
echo [INFO] Testing connection...

REM Test connection using psql
psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -c "SELECT 1" >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo [OK] Connection successful
    echo.
    goto main_menu
) else (
    echo [ERROR] Connection failed
    set /p retry="Try again? (yes/no): "
    if "!retry!"=="yes" goto get_postgres_credentials
    exit /b 1
)

:main_menu
echo.
echo ==================================================
echo What would you like to do?
echo.
echo 1. Create database (New)
echo 2. Reset database (Drop and create again)
echo 3. Run init script (Database already exists)
echo 4. Exit
echo.
set /p menu_choice="Enter your choice (1-4): "

if "!menu_choice!"=="1" goto create_database
if "!menu_choice!"=="2" goto reset_database
if "!menu_choice!"=="3" goto run_init_script
if "!menu_choice!"=="4" (
    echo [INFO] Exiting setup...
    goto exit_setup
)

echo [ERROR] Invalid choice. Please select 1-4.
goto main_menu

:create_database
echo [INFO] Creating database...

REM Check if database exists
for /f "delims=" %%i in ('psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" 2^>nul') do set db_exists=%%i

if "!db_exists!"=="1" (
    echo [WARNING] Database '%DB_NAME%' already exists
) else (
    psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -c "CREATE DATABASE %DB_NAME%" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Database '%DB_NAME%' created successfully
    ) else (
        echo [ERROR] Failed to create database
    )
)
goto main_menu

:reset_database
echo.
echo ==================================================
echo [WARNING] WARNING: This will DELETE all data in the database!
set /p confirm="Are you sure? (yes/no): "

if not "!confirm!"=="yes" (
    echo [INFO] Operation cancelled
    goto main_menu
)

echo [INFO] Resetting database...
echo [INFO] - Terminating existing connections...
echo [INFO] - Dropping old database...
echo [INFO] - Creating new database...
echo.

REM Kill existing connections and drop database
psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '%DB_NAME%' AND pid <> pg_backend_pid();" >nul 2>&1
psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -c "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1
psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d postgres -c "CREATE DATABASE %DB_NAME%;" >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo [OK] Database '%DB_NAME%' reset successfully
    echo.
    set /p run_init="Run initialization script? (yes/no): "
    if "!run_init!"=="yes" (
        goto run_init_script
    )
) else (
    echo [ERROR] Failed to reset database
)
goto main_menu

:run_init_script
set script_path=%~dp0init.sql

echo [INFO] Running initialization script...
echo [INFO] Script path: !script_path!
echo.

if not exist "!script_path!" (
    echo [ERROR] Script file not found: !script_path!
    goto main_menu
)

echo [INFO] Executing SQL file - this may take a moment...
echo.

cd /d "%~dp0"
psql -h %DB_HOST% -U %DB_USER% -p %DB_PORT% -d %DB_NAME% -f "!script_path!"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==================================================
    echo [OK] Initialization script executed successfully
    echo ==================================================
    echo.
    echo Database setup complete with all tables and seed data!
    echo.
) else (
    echo.
    echo ==================================================
    echo [ERROR] Failed to execute script
    echo ==================================================
    echo.
)
goto main_menu

:exit_setup
echo [INFO] Setup completed!
echo.
endlocal
exit /b 0
