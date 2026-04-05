@echo off
REM Kill python processes
taskkill /F /IM python.exe /T 2>nul

REM Wait a moment
timeout /t 2 /nobreak

REM Start backend server
cd /d "C:\Users\hoang\Downloads\Web Technology\Oldshop-Ecommecre\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
