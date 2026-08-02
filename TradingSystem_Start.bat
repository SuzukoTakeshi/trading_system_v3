@echo off

rem ==========================================================
rem Trading System V2 Start
rem
rem 目的:
rem   Trading System の各サービスを起動し、
rem   指定モニターへ配置する。
rem
rem ==========================================================
rem
rem 引数:
rem
rem   第1引数
rem       サービス画面配置モニター
rem
rem       APP API (FastAPI)
rem       CONSOLE UI (Streamlit)
rem       MONITOR UI (Streamlit)
rem
rem   第2引数
rem       CONSOLEブラウザ配置モニター
rem
rem       0 : ブラウザ起動なし
rem       1～4 : 指定モニターへ最大表示
rem
rem 使用例:
rem
rem   TradingSystem_Start.bat
rem       サービス : モニター1
rem       ブラウザ : モニター2
rem
rem   TradingSystem_Start.bat 1 0
rem       サービス : モニター1
rem       ブラウザ : 起動なし
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



set ROOT=C:\StockProjects\trading_system_v2



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
echo ==========================



rem ==========================================================
rem APP API
rem ==========================================================

echo.
echo ==========================
echo APP API
echo ==========================


powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\tools\CheckWindow.ps1" "APP API"


if errorlevel 1 (

    echo APP API 起動

    start "" "%ROOT%\start_app.bat"

    timeout /t 1 >nul

) else (

    echo APP API 起動済み

)



powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\tools\ArrangeWindow.ps1" ^
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
-File "%ROOT%\tools\CheckWindow.ps1" "CONSOLE UI"


if errorlevel 1 (

    echo CONSOLE UI 起動

    start "" "%ROOT%\start_console.bat"

    timeout /t 1 >nul

) else (

    echo CONSOLE UI 起動済み

)



powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\tools\ArrangeWindow.ps1" ^
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
-File "%ROOT%\tools\CheckWindow.ps1" "MONITOR UI"


if errorlevel 1 (

    echo MONITOR UI 起動

    start "" "%ROOT%\start_monitor.bat"

    timeout /t 1 >nul

) else (

    echo MONITOR UI 起動済み

)



powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\tools\ArrangeWindow.ps1" ^
-Title "MONITOR UI" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 3




rem ==========================================================
rem CONSOLE Browser
rem ==========================================================

if "%BROWSER_MONITOR%"=="0" (

    echo.
    echo CONSOLE Browser 起動なし


) else (


    echo.
    echo ==========================
    echo CONSOLE Browser
    echo ==========================



    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\tools\CheckWindow.ps1" "Trading System V2 Console"



    if errorlevel 1 (

        echo CONSOLE Browser 起動

        start "" http://localhost:8501

        timeout /t 2 >nul


    ) else (

        echo CONSOLE Browser 起動済み

    )



    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\tools\ArrangeWindow.ps1" ^
    -Title "Trading System V2 Console" ^
    -Monitor %BROWSER_MONITOR% ^
    -Layout MAX


)



echo.
echo ==========================
echo 起動完了
echo ==========================


exit /b




:HELP


echo.
echo ==========================================================
echo Trading System V2 Start
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
echo       CONSOLEブラウザ起動なし

echo.

echo   TradingSystem_Start.bat 1 3
echo       CONSOLEブラウザ:
echo           モニター3

echo.

echo ==========================================================
echo.

exit /b