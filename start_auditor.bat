@echo off
chcp 65001 >nul

rem ==========================================================
rem
rem Trading System V3
rem AUDITOR 起動バッチ
rem
rem 起動:
rem   start_auditor.bat
rem       DEV環境
rem
rem   start_auditor.bat DEV
rem       DEV環境
rem
rem   start_auditor.bat PROD
rem       PROD環境
rem
rem 停止:
rem   Ctrl + C
rem
rem 再起動:
rem   s
rem
rem 終了:
rem   exit
rem
rem ==========================================================

rem ==========================================================
rem 環境設定
rem ==========================================================

set ENV=%~1

if "%ENV%"=="" set ENV=DEV

if /i not "%ENV%"=="PROD" if /i not "%ENV%"=="DEV" (
    echo.
    echo ERROR: PROD または DEV を指定してください。
    echo.
    echo   start_auditor.bat
    echo   start_auditor.bat DEV
    echo   start_auditor.bat PROD
    echo.
    exit /b 1
)

rem ==========================================================
rem ウィンドウタイトル
rem ==========================================================

title Trading System AUDITOR %ENV%

rem ==========================================================
rem プロジェクト設定
rem ==========================================================

set ROOT=%~dp0
set ROOT=%ROOT:~0,-1%

rem ==========================================================
rem venv起動
rem ==========================================================

call "%ROOT%\venv\Scripts\activate.bat"

rem ==========================================================
rem Python Path設定
rem ==========================================================

set PYTHONPATH=%ROOT%

rem ==========================================================
rem ポート設定
rem ==========================================================

for /f %%P in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('server', {}).get('auditor_port', 8508))"') do set AUDITOR_PORT=%%P

rem ==========================================================
rem 起動コマンド設定
rem ==========================================================

rem ブラウザ自動起動を無効化
rem TradingSystem_Start.bat側でブラウザ配置を制御

set AUDITOR_CMD=python -m streamlit run %ROOT%\auditor\main.py --server.port %AUDITOR_PORT% --server.headless true

echo.
echo ==========================
echo TRADING SYSTEM AUDITOR %ENV% START
echo ==========================
echo.

echo Port:
echo %AUDITOR_PORT%
echo.

echo ブラウザからAUDITOR画面を表示する場合:
echo.
echo http://localhost:%AUDITOR_PORT%
echo.

echo [Ctrl-C]で終了した場合:
echo.
echo   s
echo.
echo sを入力すると再起動します。
echo.

%AUDITOR_CMD%

echo.
echo ==========================
echo TRADING SYSTEM AUDITOR %ENV% STOPPED
echo ==========================
echo.
echo 再起動する場合:
echo   s
echo.
echo 終了する場合:
echo   exit
echo.

doskey s=%AUDITOR_CMD%

cmd