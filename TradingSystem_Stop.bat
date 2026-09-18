@echo off
chcp 65001 >nul

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
rem APIポート取得
rem ==========================================================

for /f %%P in ('python -c "from core.config_loader import Config; print(Config.instance().data.get('server', {}).get('api_port', 8000))"') do set API_PORT=%%P

echo ==========================
echo Trading System 停止
echo ==========================
echo.

echo APP停止...
echo Port=%API_PORT%

for /f "tokens=5" %%a in ('netstat -ano ^| findstr LISTENING ^| findstr /C:":%API_PORT% "') do (

```
taskkill /F /PID %%a >nul 2>&1
```

)

echo.

echo Streamlit停止...

taskkill /F /IM streamlit.exe >nul 2>&1

echo.

echo ==========================
echo APP停止確認
echo ==========================

netstat -ano | findstr LISTENING | findstr /C:":%API_PORT% "

echo.

echo ※ 何も表示されなければ正常に停止しています。
echo ※ LISTENING が表示された場合は APP がまだ動作しています。

echo.

echo ==========================
echo 停止完了
echo ==========================

pause
