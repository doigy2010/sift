@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  SIFT Report Builder
echo ============================================
echo.

echo [1/4] Installing Flask...
pip install flask --quiet
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)
echo Done.
echo.

echo [2/4] Building clusters...
python build_clusters.py
if errorlevel 1 (
    echo ERROR: build_clusters.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

echo [3/4] Building entry points...
python build_entry_points.py
if errorlevel 1 (
    echo ERROR: build_entry_points.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

echo [4/4] Generating report...
python sift_report.py
if errorlevel 1 (
    echo ERROR: sift_report.py failed.
    pause
    exit /b 1
)
echo Done.
echo.

echo ============================================
echo  Report complete.
echo ============================================
pause
