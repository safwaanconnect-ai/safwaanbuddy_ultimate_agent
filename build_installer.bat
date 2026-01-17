@echo off
echo ============================================================
echo SafwaanBuddy Ultimate++ v7.0
echo Complete Build and Installer Creation
echo ============================================================
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

echo ============================================================
echo Step 1: Installing Build Dependencies
echo ============================================================
echo.

echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo Warning: PyInstaller installation had issues
)

echo Installing setuptools and wheel...
python -m pip install setuptools wheel
if errorlevel 1 (
    echo Warning: setuptools/wheel installation had issues
)

echo.
echo ============================================================
echo Step 2: Installing Application Dependencies
echo ============================================================
echo.

echo Installing all requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Warning: Some requirements failed to install
    echo The build may still work if core dependencies are installed
)

echo.
echo ============================================================
echo Step 3: Building Executable
echo ============================================================
echo.

python build_exe.py
if errorlevel 1 (
    echo.
    echo ============================================================
    echo BUILD FAILED
    echo ============================================================
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Step 4: Creating Windows Installer (Optional)
echo ============================================================
echo.

REM Check if Inno Setup is installed
where iscc >nul 2>&1
if errorlevel 1 (
    echo Inno Setup not found
    echo To create a Windows installer:
    echo 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Install Inno Setup
    echo 3. Run: iscc installer.iss
    echo.
    echo Skipping installer creation...
    goto :skip_installer
)

echo Creating Windows installer with Inno Setup...
iscc installer.iss
if errorlevel 1 (
    echo Warning: Installer creation had issues
    goto :skip_installer
)

echo.
echo ✓ Windows installer created successfully!
echo Location: installer_output\SafwaanBuddy-Ultimate-v7.0.0-Setup.exe

:skip_installer

echo.
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Your executable is ready at: dist\SafwaanBuddy\SafwaanBuddy.exe
echo.
echo To test: cd dist\SafwaanBuddy ^&^& SafwaanBuddy.exe
echo.
echo To distribute:
echo   Option 1: Share the entire dist\SafwaanBuddy\ folder (zipped)
echo   Option 2: Share the installer (if created)
echo.

:show_info
echo ============================================================
echo DISTRIBUTION OPTIONS
echo ============================================================
echo.
echo PORTABLE VERSION (No installation required):
echo   1. Zip the dist\SafwaanBuddy\ folder
echo   2. Users extract and run SafwaanBuddy.exe
echo   Size: ~100-300 MB (depending on dependencies)
echo.
echo INSTALLER VERSION (Recommended for end users):
echo   1. Use the .exe in installer_output\
echo   2. Users run the installer
echo   3. Creates Start Menu shortcuts
echo   4. Handles uninstallation
echo.
echo OPTIONAL COMPONENTS (Users install separately):
echo   - Vosk models for voice recognition
echo   - Tesseract OCR for text recognition
echo   - See README.md for details
echo.

pause
