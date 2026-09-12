@echo off

rem ==========================================================
rem Trading System Start
rem
rem �ړI:
rem   Trading System �̊e�T�[�r�X���N�����A
rem   �w�胂�j�^�[�֔z�u����B
rem
rem ==========================================================
rem
rem ����:
rem
rem   ��1����
rem       �T�[�r�X��ʔz�u���j�^�[
rem
rem       APP API (FastAPI)
rem       CONSOLE UI (Streamlit)
rem       MONITOR UI (Streamlit)
rem
rem   ��2����
rem       CONSOLE�u���E�U�z�u���j�^�[
rem
rem       0 : �u���E�U�N���Ȃ�
rem       1�`4 : �w�胂�j�^�[�֍ő�\��
rem
rem �g�p��:
rem
rem   TradingSystem_Start.bat
rem       �T�[�r�X : ���j�^�[1
rem       �u���E�U : ���j�^�[2
rem
rem   TradingSystem_Start.bat 1 0
rem       �T�[�r�X : ���j�^�[1
rem       �u���E�U : �N���Ȃ�
rem
rem   TradingSystem_Start.bat 1 3
rem       �T�[�r�X : ���j�^�[1
rem       �u���E�U : ���j�^�[3
rem
rem ==========================================================
rem
rem �g�p�c�[��:
rem
rem   tools\CheckWindow.ps1
rem       �N���ς݃E�B���h�E�m�F
rem
rem   tools\ArrangeWindow.ps1
rem       �E�B���h�E�z�u
rem
rem ==========================================================



rem ==========================================================
rem �w���v
rem ==========================================================

if /i "%1"=="help" goto HELP
if /i "%1"=="?" goto HELP
if /i "%1"=="/?" goto HELP



set ROOT=C:\StockProjects\trading_system_v3_dev



rem ==========================================================
rem ���j�^�[�ݒ�
rem ==========================================================

set SERVICE_MONITOR=1
set BROWSER_MONITOR=2


if not "%1"=="" set SERVICE_MONITOR=%1

if not "%2"=="" set BROWSER_MONITOR=%2



echo ==========================
echo Trading System �N��
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
-File "%ROOT%\program\tools\CheckWindow.ps1" "APP API"


if errorlevel 1 (

    echo APP API �N��

    start "" "%ROOT%\start_app.bat"

    timeout /t 1 >nul

) else (

    echo APP API �N���ς�

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

    echo CONSOLE UI �N��

    start "" "%ROOT%\start_console.bat"

    timeout /t 1 >nul

) else (

    echo CONSOLE UI �N���ς�

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

    echo MONITOR UI �N��

    start "" "%ROOT%\start_monitor.bat"

    timeout /t 1 >nul

) else (

    echo MONITOR UI �N���ς�

)



powershell -ExecutionPolicy Bypass ^
-File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
-Title "MONITOR UI" ^
-Monitor %SERVICE_MONITOR% ^
-Layout V3 ^
-Position 3




rem ==========================================================
rem CONSOLE Browser
rem ==========================================================

if "%BROWSER_MONITOR%"=="0" (

    echo.
    echo CONSOLE Browser �N���Ȃ�


) else (


    echo.
    echo ==========================
    echo CONSOLE Browser
    echo ==========================



    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\program\tools\CheckWindow.ps1" "Trading System Console"



    if errorlevel 1 (

        echo CONSOLE Browser �N��

        start "" http://localhost:8501

        timeout /t 2 >nul


    ) else (

        echo CONSOLE Browser �N���ς�

    )



    powershell -ExecutionPolicy Bypass ^
    -File "%ROOT%\program\tools\ArrangeWindow.ps1" ^
    -Title "Trading System Console" ^
    -Monitor %BROWSER_MONITOR% ^
    -Layout MAX


)



echo.
echo ==========================
echo �N������
echo ==========================


exit /b




:HELP


echo.
echo ==========================================================
echo Trading System Start
echo ==========================================================
echo.

echo �g�p���@:
echo.

echo   TradingSystem_Start.bat
echo       �T�[�r�X:
echo           ���j�^�[1
echo       CONSOLE�u���E�U:
echo           ���j�^�[2

echo.

echo   TradingSystem_Start.bat 1 0
echo       CONSOLE�u���E�U�N���Ȃ�

echo.

echo   TradingSystem_Start.bat 1 3
echo       CONSOLE�u���E�U:
echo           ���j�^�[3

echo.

echo ==========================================================
echo.

exit /b