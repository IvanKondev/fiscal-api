@echo off
chcp 65001 >nul 2>&1
title Print Gateway - Datecs

echo ========================================
echo     Print Gateway - Datecs
echo     http://127.0.0.1:8787
echo ========================================
echo.

:: Find Python
where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=py
    goto :found
)
where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=python
    goto :found
)
where python3 >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=python3
    goto :found
)

echo [ERROR] Python not found!
echo Please install Python 3.11+ from https://www.python.org/downloads/
echo.
pause
exit /b 1

:found
echo [OK] Python: %PYTHON%

:: Change to script directory
cd /d "%~dp0"

:: Check if dependencies are installed
%PYTHON% -c "import uvicorn, fastapi, serial" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    %PYTHON% -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
)

:: Open browser after a short delay
start /b "" cmd /c "ping -n 3 127.0.0.1 >nul & start "" http://127.0.0.1:8787"

echo [OK] Starting server...
echo.
echo    Open browser: http://127.0.0.1:8787
echo    Press Ctrl+C to stop
echo.

%PYTHON% -m app

echo.
echo Server stopped.
pause
