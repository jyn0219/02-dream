@echo off
setlocal
cd /d "%~dp0.."

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] python not found.
    echo Install Python 3.12 first, or open Miniforge Prompt and run this script again.
    pause
    exit /b 1
)

echo === interpreter ===
python -c "import sys; print(sys.executable)"
echo.
echo === pip install -r requirements.txt ===
python -m pip install -r requirements.txt
echo.
echo === environment check ===
python tools\check_env.py
echo.
echo Done. Next step: python analysis\01_clean.py
pause
