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
rem 構成:
rem
rem   第1引数
rem       サービス用モニター
rem
rem       APP API (FastAPI)
rem       CONSOLE UI (Streamlit)
rem       MONITOR UI (Streamlit)
rem
rem   第2引数
rem       CONSOLEブラウザ配置用モニター
rem
rem       0   : ブラウザを起動しない
rem       1～4 : 指定モニターへ最大化表示
rem
rem 使用例:
rem
rem   TradingSystem_Start.bat
rem       サービス : モニター1
rem       ブラウザ : モニター2
rem
rem   TradingSystem_Start.bat 1 0
rem       サービス : モニター1
rem       ブラウザ : 起動しない
rem
rem   TradingSystem_Start.bat 1 3
rem       サービス : モニター1
rem       ブラウザ : モニター3
rem
rem ==========================================================
rem
rem 使用ツール:
rem
rem   tools\CheckWindow.ps1
rem       起動済みウィンドウ確認
rem
rem   tools\ArrangeWindow.ps1
rem       ウィンドウ配置
rem
rem ==========================================================

rem ==========================================================
rem ヘルプ
rem ==========================================================

if /i "%1"=="help" goto HELP
if /i "%1"=="?" goto HELP
if /i "%1"=="/?" goto HELP

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

rem ==========================================================
rem ポート設定
rem ==========================================================

call "%ROOT%\venv\Scripts\activate.bat"

set PYTHONPATH=%ROOT%\program;%ROOT%

for /f %%P in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('server', {}).get('console_port', 8501))"') do set CONSOLE_PORT=%%P

rem ==========================================================
rem モニター設定
rem ==========================================================

set SERVICE_MONITOR=1
set BROWSER_MONITOR=2

if not "%1"=="" set SERVICE_MONITOR=%1

if not "%2"=="" set BROWSER_MONITOR=%2

echo ==========================
echo Trading System 起動
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
echo APP API
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "APP API"

if errorlevel 1 (

```
echo APP API 起動

start "" "%ROOT%\start_app.bat"

timeout /t 1 >nul
```

) else (

```
echo APP API 起動済み
```

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "APP API" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 1

rem ==========================================================
rem CONSOLE UI
rem ==========================================================

echo.
echo ==========================
echo CONSOLE UI
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "CONSOLE UI"

if errorlevel 1 (

```
echo CONSOLE UI 起動

start "" "%ROOT%\start_console.bat"

timeout /t 1 >nul
```

) else (

```
echo CONSOLE UI 起動済み
```

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "CONSOLE UI" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 2

rem ==========================================================
rem MONITOR UI
rem ==========================================================

echo.
echo ==========================
echo MONITOR UI
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "MONITOR UI"

if errorlevel 1 (

```
echo MONITOR UI 起動

start "" "%ROOT%\start_monitor.bat"

timeout /t 1 >nul
```

) else (

```
echo MONITOR UI 起動済み
```

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "MONITOR UI" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 3


rem ==========================================================
rem AUDITOR
rem ==========================================================

echo.
echo ==========================
echo AUDITOR
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "AUDITOR"

if errorlevel 1 (

    echo AUDITOR 起動

    start "" "%ROOT%\start_auditor.bat"

    timeout /t 1 >nul

) else (

    echo AUDITOR 起動済み

)

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "AUDITOR" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 4


rem ==========================================================
rem CONSOLE Browser
rem ==========================================================

if "%BROWSER_MONITOR%"=="0" (

```
echo.
echo CONSOLE Browser 起動しない
```

) else (

```
echo.
echo ==========================
echo CONSOLE Browser
echo ==========================

powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\CheckWindow.ps1" "Trading System Console"

if errorlevel 1 (

    echo CONSOLE Browser 起動

    start "" http://localhost:%CONSOLE_PORT%

    timeout /t 2 >nul

) else (

    echo CONSOLE Browser 起動済み

)


powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "Trading System Console" ^
-Monitor %BROWSER_MONITOR% ^
-Layout MAX
```

)

echo.
echo ==========================
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

echo   TradingSystem_Start.bat
echo       サービス:
echo           モニター1
echo       CONSOLEブラウザ:
echo           モニター2

echo.

echo   TradingSystem_Start.bat 1 0
echo       CONSOLEブラウザを起動しない

echo.

echo   TradingSystem_Start.bat 1 3
echo       CONSOLEブラウザ:
echo           モニター3

echo.

echo ==========================================================
echo.

exit
