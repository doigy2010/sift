@echo off
echo.
echo ============================================================
echo   SIFT - Find the truth in any codebase
echo ============================================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not on your PATH.
    echo.
    echo Download Python from: https://www.python.org/downloads/
    echo During install, check the box: "Add Python to PATH"
    echo Then run this file again.
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo.
REM Run SIFT
python sift.py

echo.
pause
