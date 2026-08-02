@echo off

rem ==========================================================
rem Trading System V1.4
rem MONITOR UI 起動バッチ
rem ==========================================================

title MONITOR UI

rem ==========================================================
rem 起動コマンド設定
rem ==========================================================
rem

rem ブラウザ自動起動を無効にする
rem （ブラウザで手動表示する場合）
rem
rem   --server.headless true

set MONITOR_CMD=streamlit run ui/monitor_app.py --server.port 8502 --server.headless true

rem ==========================================================
rem プロジェクト移動
rem ==========================================================

cd /d C:\StockProjects\trading_system

rem ==========================================================
rem venv有効化
rem ==========================================================

call venv\Scripts\activate

echo.
echo ==========================
echo MONITOR UI START
echo ==========================
echo.

echo.
echo ブラウザでMONITOR画面を表示する場合:
echo.
echo   http://localhost:8502/?symbols=8306
echo   http://localhost:8502/?symbols=8306,7203
echo.

echo [Ctrl-C]で終了した場合:
echo.
echo   s
echo.
echo を入力すると再起動します。
echo.

%MONITOR_CMD%

echo.
echo ==========================
echo MONITOR UI STOPPED
echo ==========================
echo.
echo 再起動する場合:
echo   s
echo.
echo 終了する場合:
echo   exit
echo.


doskey s=%MONITOR_CMD%

cmd