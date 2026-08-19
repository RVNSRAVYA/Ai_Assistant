@echo off
title SmartCode AI - Server Launcher
echo ===================================================
echo           Starting SmartCode AI Server
echo ===================================================
echo.
cd /d "%~dp0backend"

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo Installing required Python packages...
pip install -r requirements.txt

echo.
echo Starting FastAPI Web Server at http://localhost:8000
echo Press Ctrl+C to stop the server.
echo.
start http://localhost:8000
python main.py

pause
