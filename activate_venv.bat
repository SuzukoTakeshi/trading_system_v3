@echo off

rem ==========================================================
rem Trading System
rem Python Virtual Environment
rem ==========================================================

set ROOT=C:\StockProjects\trading_system_v3_dev

rem ==========================================================
rem venv有効化
rem ==========================================================

call "%ROOT%\venv\Scripts\activate.bat"

rem ==========================================================
rem Python Path設定
rem ==========================================================

set PYTHONPATH=%ROOT%\program;%ROOT%

echo.
echo ========================================
echo  V3 Python Virtual Environment
echo ========================================
echo.
echo python -m program.market.rakuten.emulator.main scenario_7203_master.json 1
echo.

cmd