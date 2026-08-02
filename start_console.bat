@echo off

rem ==========================================================
rem Trading System V2
rem CONSOLE UI 起動バッチ
rem ==========================================================

title CONSOLE UI

rem ==========================================================
rem 起動コマンド設定
rem ==========================================================

rem ブラウザ自動起動を無効化
rem TradingSystem_Start.bat側でブラウザ配置を制御
rem
rem   --server.headless true

set CONSOLE_CMD=streamlit run ui\console.py --server.port 8501 --server.headless true

rem ==========================================================
rem プロジェクト移動
rem ==========================================================

cd /d C:\StockProjects\trading_system_v2

rem ==========================================================
rem venv有効化
rem ==========================================================

call venv\Scripts\activate


echo.
echo ==========================
echo CONSOLE UI START
echo ==========================
echo.

echo ブラウザでCONSOLE画面を表示する場合:
echo.
echo   http://localhost:8501
echo.

echo [Ctrl-C]で終了した場合:
echo.
echo   s
echo.
echo を入力すると再起動します。
echo.

%CONSOLE_CMD%

echo.
echo ==========================
echo CONSOLE UI STOPPED
echo ==========================
echo.
echo 再起動する場合:
echo   s
echo.
echo 終了する場合:
echo   exit
echo.


doskey s=%CONSOLE_CMD%

cmd