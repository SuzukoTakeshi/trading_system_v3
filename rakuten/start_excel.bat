@echo off
chcp 65001 >nul

rem ==========================================================
rem
rem rakuten\start_excel.bat
rem
rem Trading System V3
rem Rakuten RSS Excel 起動
rem
rem ==========================================================

for %%I in ("%~dp0..") do set ROOT=%%~fI

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

set PYTHONPATH=%ROOT%

rem ==========================================================
rem
rem Mode取得
rem
rem ==========================================================

for /f %%M in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('mode', 'debug'))"') do set MODE=%%M

rem ==========================================================
rem
rem Excelパス取得
rem
rem ==========================================================

for /f "delims=" %%P in ('python -c "from rakuten.config_loader import MarketConfig; from core.config_loader import Config; mode=Config.instance().data.get('mode', 'debug'); print(MarketConfig.instance().data['excel']['path'].get(mode, ''))"') do set EXCEL_PATH=%%P

rem ==========================================================
rem
rem 設定表示
rem
rem ==========================================================

echo.
echo ========================================
echo  Trading System V3 - Rakuten RSS Excel
echo ========================================
echo.
echo  Mode       : %MODE%
echo  Excel Path : %EXCEL_PATH%
echo.

rem ==========================================================
rem
rem Excel存在確認
rem
rem ==========================================================

if "%EXCEL_PATH%"=="" (
    echo [ERROR] Excel path is not configured.
    pause
    exit /b 1
)

if not exist "%EXCEL_PATH%" (
    echo [ERROR] Excel file not found.
    echo.
    echo %EXCEL_PATH%
    pause
    exit /b 1
)


rem ==========================================================
rem
rem Excel起動済み確認
rem
rem ==========================================================

python -m rakuten.is_excel_ready

if not errorlevel 1 (
    echo.
    echo Rakuten RSS Excel 起動済み
    echo.
    exit /b 0
)

rem ==========================================================
rem
rem Excel起動
rem
rem ==========================================================

echo.
echo Starting Excel...
echo.

start "" "%EXCEL_PATH%"

exit /b 0
