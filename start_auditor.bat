@echo off
chcp 65001 >nul

rem ==========================================================
rem Trading System
rem Auditor 起動バッチ
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

title AUDITOR %ENV%

rem ==========================================================
rem 起動コマンド設定
rem ==========================================================

set AUDITOR_CMD=python -m program.auditor.main

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
rem 再起動用コマンド登録
rem ==========================================================

doskey s=%AUDITOR_CMD%

rem ==========================================================
rem Auditor起動
rem ==========================================================

echo.
echo ==========================
echo AUDITOR %ENV% START
echo ==========================
echo.

%AUDITOR_CMD%


rem ==========================================================
rem 終了後
rem ==========================================================

echo.
echo ==========================
echo AUDITOR %ENV% STOPPED
echo ==========================
echo.

echo 再起動する場合: s + [ENTER]

echo.

doskey s=%AUDITOR_CMD%

cmd
