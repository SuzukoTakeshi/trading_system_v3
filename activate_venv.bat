@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat

echo.
echo ========================================
echo  V3 Python Virtual Environment
echo ========================================
echo.
echo python -m market.rakuten.emulator.main scenario_7203_master.json 1
echo.

cmd /k