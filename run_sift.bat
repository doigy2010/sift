@echo off
chcp 65001 >nul

REM Always run from the folder this bat file lives in
cd /d "%~dp0"

echo ============================================
echo   SIFT - Find the truth in any codebase
echo ============================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed on this machine.
    echo Please install Python from https://www.python.org
    echo Make sure to tick "Add Python to PATH" during install.
    echo Then double-click this file again.
    pause
    exit /b 1
)

REM Install all dependencies
echo Installing required tools...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 1: Run scan
echo [1/4] Scanning your machine...
python "%~dp0sift.py"
if errorlevel 1 (
    echo ERROR: sift.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 2: Build clusters
echo [2/4] Grouping files into projects...
python "%~dp0build_clusters.py"
if errorlevel 1 (
    echo ERROR: build_clusters.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 3: Build entry points
echo [3/4] Checking which projects can run...
python "%~dp0build_entry_points.py"
if errorlevel 1 (
    echo ERROR: build_entry_points.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

REM Step 3b: Build project descriptions
echo [3b/4] Building project descriptions...
python "%~dp0build_descriptions.py"
if errorlevel 1 (
    echo WARNING: build_descriptions.py failed. Descriptions will be skipped.
)
echo Done.
echo.

REM Step 4: Start report
echo [4/4] Opening report in your browser...
python "%~dp0sift_report.py"
if errorlevel 1 (
    echo ERROR: sift_report.py failed.
    pause
    exit /b 1
)

pause
