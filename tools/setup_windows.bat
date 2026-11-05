@echo off
chcp 65001 >nul
rem 在教室/新电脑上一键装依赖。双击运行，或在命令行执行 tools\setup_windows.bat
cd /d "%~dp0.."

where python >nul 2>nul
if errorlevel 1 (
    echo 没找到 python。
    echo 请先安装 Python 3.12，或从开始菜单打开 Miniforge Prompt 后再运行本脚本。
    pause
    exit /b 1
)

echo === 当前解释器 ===
python -c "import sys; print(sys.executable)"
echo.
echo === 安装 requirements.txt ===
python -m pip install -r requirements.txt
echo.
echo === 检查环境 ===
python tools\check_env.py

echo.
echo 装好后运行：python analysis\01_clean.py
pause
