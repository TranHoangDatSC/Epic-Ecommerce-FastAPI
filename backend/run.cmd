@echo off
REM OldShop Backend Run Script

echo Starting OldShop Backend Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
