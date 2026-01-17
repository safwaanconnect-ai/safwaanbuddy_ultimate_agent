@echo off
echo ====================================
echo SafwaanBuddy Ultimate++ v7.0
echo Starting Application...
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python run_safwaanbuddy.py

REM Deactivate on exit
call venv\Scripts\deactivate.bat

pause
