@echo off
echo ====================================
echo SafwaanBuddy Ultimate++ v7.0
echo Installation Script for Windows
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
echo.
echo Installing base requirements...
pip install -r requirements\base.txt
if errorlevel 1 (
    echo Warning: Some base packages failed to install
)

echo Installing UI requirements...
pip install -r requirements\ui.txt
if errorlevel 1 (
    echo Warning: Some UI packages failed to install
)

echo Installing voice requirements...
pip install -r requirements\voice.txt
if errorlevel 1 (
    echo Warning: Some voice packages failed to install
)

echo Installing web requirements...
pip install -r requirements\web.txt
if errorlevel 1 (
    echo Warning: Some web packages failed to install
)

echo Installing document requirements...
pip install -r requirements\documents.txt
if errorlevel 1 (
    echo Warning: Some document packages failed to install
)

echo Installing automation requirements...
pip install -r requirements\automation.txt
if errorlevel 1 (
    echo Warning: Some automation packages failed to install
)

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo IMPORTANT NOTES:
echo 1. Download Vosk model from: https://alphacephei.com/vosk/models
echo    - Recommended: vosk-model-en-us-0.22
echo    - Extract to: data/models/vosk/
echo.
echo 2. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
echo    - Add Tesseract to your system PATH
echo.
echo 3. For browser automation, ensure Chrome/Firefox/Edge is installed
echo.
echo To start SafwaanBuddy, run: run.bat
echo.
pause
