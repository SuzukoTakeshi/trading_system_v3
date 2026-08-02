@echo off

echo ==========================
echo Trading System 停止
echo ==========================

echo.
echo APP停止...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Streamlit停止...

taskkill /F /IM streamlit.exe >nul 2>&1

echo.
echo ==========================
echo APP停止確認
echo ==========================

netstat -ano | findstr LISTENING | findstr :8000

echo.
echo ※ 何も表示されなければ正常に停止しています。
echo ※ LISTENING が表示された場合は APP がまだ動作しています。
echo.

echo ==========================
echo 停止完了
echo ==========================

pause