@echo off
chcp 65001 >nul

rem ==========================================================
rem Trading System Start
rem
rem 目的:
rem   Trading System の各サービスを起動し、
rem   指定モニターへ配置する。
rem
rem ==========================================================
rem
rem 使用方法:
rem
rem   TradingSystem_Start.bat PROD
rem   TradingSystem_Start.bat DEV
rem
rem   TradingSystem_Start.bat PROD 1 2
rem   TradingSystem_Start.bat DEV 1 2
rem
rem   第1引数
rem       PROD / DEV
rem
rem   第2引数
rem       サービス用モニター
rem
rem   第3引数
rem       CONSOLEブラウザ配置用モニター
rem
rem       0   : ブラウザを起動しない
rem       1～4 : 指定モニターへ最大化表示
rem
rem ==========================================================

rem ==========================================================
rem ヘルプ
rem ==========================================================

if /i "%1"=="help" goto HELP
if /i "%1"=="?" goto HELP
if /i "%1"=="/?" goto HELP

rem ==========================================================
rem 環境設定
rem ==========================================================

set ENV=%~1

if /i "%ENV%"=="PROD" goto ENV_OK
if /i "%ENV%"=="DEV" goto ENV_OK

echo.
echo ==========================================================
echo ERROR: 環境を指定してください。
echo.
echo   TradingSystem_Start.bat PROD
echo   TradingSystem_Start.bat DEV
echo ==========================================================
echo.

exit /b 1

:ENV_OK

rem ==========================================================
rem プロジェクト設定
rem ==========================================================

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

rem ==========================================================
rem venv / Python Path
rem ==========================================================

call "%ROOT%\venv\Scripts\activate.bat"

set PYTHONPATH=%ROOT%\program;%ROOT%

rem ==========================================================
rem ポート設定
rem ==========================================================

for /f %%P in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('server', {}).get('console_port', 8501))"') do set CONSOLE_PORT=%%P

rem ==========================================================
rem モニター設定
rem ==========================================================

set SERVICE_MONITOR=1
set BROWSER_MONITOR=2

if not "%2"=="" set SERVICE_MONITOR=%2
if not "%3"=="" set BROWSER_MONITOR=%3

echo.
echo ==========================
echo Trading System %ENV% 起動
echo ==========================
echo Service Monitor=%SERVICE_MONITOR%
echo Browser Monitor=%BROWSER_MONITOR%
echo Console Port=%CONSOLE_PORT%
echo ==========================


rem ==========================================================
rem 楽天RSS Excel
rem ==========================================================

echo.
echo ==========================
echo Rakuten RSS Excel
echo ==========================

echo Rakuten RSS Excel 起動

call "%ROOT%\rakuten\start_excel.bat"

timeout /t 2 >nul


rem ==========================================================
rem APP API
rem ==========================================================

echo.
echo ==========================
echo APP API %ENV%
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "APP API %ENV%"

if errorlevel 1 (

    echo APP API %ENV% 起動

    start "" "%ROOT%\start_app.bat" %ENV%

    timeout /t 1 >nul

) else (

    echo APP API %ENV% 起動済み

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "APP API %ENV%" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 1


rem ==========================================================
rem CONSOLE UI
rem ==========================================================

echo.
echo ==========================
echo CONSOLE UI %ENV%
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "CONSOLE UI %ENV%"

if errorlevel 1 (

    echo CONSOLE UI %ENV% 起動

    start "" "%ROOT%\start_console.bat" %ENV%

    timeout /t 1 >nul

) else (

    echo CONSOLE UI %ENV% 起動済み

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "CONSOLE UI %ENV%" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 2


rem ==========================================================
rem MONITOR UI
rem ==========================================================

echo.
echo ==========================
echo MONITOR UI %ENV%
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "MONITOR UI %ENV%"

if errorlevel 1 (

    echo MONITOR UI %ENV% 起動

    start "" "%ROOT%\start_monitor.bat" %ENV%

    timeout /t 1 >nul

) else (

    echo MONITOR UI %ENV% 起動済み

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "MONITOR UI %ENV%" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 3


rem ==========================================================
rem AUDITOR
rem ==========================================================

echo.
echo ==========================
echo AUDITOR %ENV%
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "AUDITOR %ENV%"

if errorlevel 1 (

    echo AUDITOR %ENV% 起動

    start "" "%ROOT%\start_auditor.bat" %ENV%

    timeout /t 1 >nul

) else (

    echo AUDITOR %ENV% 起動済み

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "AUDITOR %ENV%" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 4


rem ==========================================================
rem CONSOLE Browser
rem ==========================================================

if "%BROWSER_MONITOR%"=="0" (

    echo.
    echo CONSOLE Browser 起動しない

) else (

    echo.
    echo ==========================
    echo CONSOLE Browser %ENV%
    echo ==========================

    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\program\tools\CheckWindow.ps1" "Trading System Console"

    if errorlevel 1 (

        echo CONSOLE Browser %ENV% 起動

        start "" http://localhost:%CONSOLE_PORT%

        timeout /t 2 >nul

    ) else (

        echo CONSOLE Browser %ENV% 起動済み

    )

    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
    -Title "Trading System Console" ^
    -Monitor %BROWSER_MONITOR% ^
    -Layout MAX

)


echo.
echo ==========================
echo Trading System %ENV%
echo 起動処理完了
echo ==========================

exit /b


:HELP

echo.
echo ==========================================================
echo Trading System Start
echo ==========================================================
echo.

echo 使用方法:
echo.

echo   TradingSystem_Start.bat PROD
echo       PROD環境
echo       サービス : モニター1
echo       CONSOLEブラウザ : モニター2

echo.

echo   TradingSystem_Start.bat DEV
echo       DEV環境
echo       サービス : モニター1
echo       CONSOLEブラウザ : モニター2

echo.

echo   TradingSystem_Start.bat PROD 1 0
echo       PROD環境
echo       CONSOLEブラウザを起動しない

echo.

echo   TradingSystem_Start.bat DEV 1 3
echo       DEV環境
echo       CONSOLEブラウザ : モニター3

echo.

echo ==========================================================
echo.

exit /b
