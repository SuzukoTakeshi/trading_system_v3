@echo off
chcp 65001 >nul

rem ==========================================================
rem
rem Trading System V3
rem Python Virtual Environment
rem
rem ==========================================================

set ROOT=C:\StockProjects\trading_system_v3_dev

rem ==========================================================
rem
rem venv有効化
rem
rem ==========================================================

call "%ROOT%\venv\Scripts\activate.bat"

rem ==========================================================
rem
rem Python Path設定
rem
rem ==========================================================

set PYTHONPATH=%ROOT%\program;%ROOT%

echo.
echo ========================================
echo  V3 Python Virtual Environment
echo ========================================
echo.

echo [Emulator]
echo.
echo python -m program.market.rakuten.emulator.main scenario_7203.json 1
echo.
echo   第1引数 : Scenarioファイル
echo   第2引数 : Trade作成
echo              1 = 作成する
echo              0 = 作成しない
echo.

cmd