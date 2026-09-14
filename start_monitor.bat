@echo off
chcp 65001 >nul

rem ==========================================================
rem Trading System
rem MONITOR UI 起動バッチ
rem ==========================================================

title MONITOR UI

rem ==========================================================
rem プロジェクトルート設定
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

set PYTHONPATH=%ROOT%\program;%ROOT%

rem ==========================================================
rem ポート設定
rem ==========================================================

for /f %%P in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('server', {}).get('monitor_port', 8502))"') do set MONITOR_PORT=%%P

rem ==========================================================
rem 起動コマンド設定
rem ==========================================================

rem ブラウザ自動起動を無効化
rem TradingSystem_Start.bat側でブラウザ配置を制御
rem
rem   --server.headless true

set MONITOR_CMD=python -m streamlit run %ROOT%\program\ui\monitor\monitor.py --server.port %MONITOR_PORT% --server.headless true

echo.
echo ==========================
echo MONITOR UI START
echo ==========================
echo.

echo Port:
echo   %MONITOR_PORT%
echo.

echo MONITOR UIを起動しました。
echo.
echo   [http://localhost:%MONITOR_PORT%/?symbols=8306](http://localhost:%MONITOR_PORT%/?symbols=8306)
echo   [http://localhost:%MONITOR_PORT%/?symbols=8306,7203](http://localhost:%MONITOR_PORT%/?symbols=8306,7203)
echo.

echo [Ctrl-C]で終了します。
echo.
echo 終了後に再起動する場合:
echo.
echo   s
echo.
echo sコマンドは同じコンソールで再起動できます。
echo.

%MONITOR_CMD%

echo.
echo ==========================
echo MONITOR UI STOPPED
echo ==========================
echo.
echo 再起動:
echo   s
echo.
echo コンソール終了:
echo   exit
echo.

doskey s=%MONITOR_CMD%

cmd
