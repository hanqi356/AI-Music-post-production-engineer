@echo off
REM Use English to avoid encoding issues
title AI Music Engineer - Smart Launcher

echo ========================================
echo   AI Music Engineer - Smart Launcher
echo ========================================
echo.

REM Check Python environment
echo [Check] Python environment...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python detected, installing dependencies...
    pip install -r requirements.txt --upgrade
    echo Starting program...
    python run_app.py
    goto :end
)

echo Python not found, installing automatically...
echo.

REM Download Python installer
echo [Step 1] Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python_installer.exe'"

if not exist "python_installer.exe" (
    echo Download failed, please install Python manually
    echo Download URL: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [Step 2] Installing Python...
echo Please check "Add Python to PATH" during installation
echo Installation window will pop up, please follow the prompts...

REM Silent install Python
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo [Step 3] Verifying installation...
timeout /t 10 /nobreak >nul

REM Recheck Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python installation may require system restart
    echo Please restart your computer and run this program again
    pause
    exit /b 1
)

echo [Step 4] Installing dependencies...
pip install -r requirements.txt --upgrade

echo [Step 5] Starting program...
python run_app.py

:end
echo.
echo Program exited
pause