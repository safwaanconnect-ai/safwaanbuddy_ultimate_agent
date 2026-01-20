import os
import subprocess
import sys

def build():
    print("========================================")
    print("SafwanBuddy Build System - Windows 11")
    print("========================================")
    
    # Check if running on Windows (optional, but good for user feedback)
    if sys.platform != "win32":
        print("Warning: You are not running on Windows. The resulting .exe will not be a Windows executable.")
        print("To build for Windows, please run this script on a Windows machine.")

    # Ensure all requirements are installed
    print("Checking dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Warning: Failed to install requirements: {e}")

    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Run pyinstaller
    print("Building executable (this may take a few minutes)...")
    try:
        if os.path.exists("safwanbuddy.spec"):
            subprocess.check_call(["pyinstaller", "--noconfirm", "safwanbuddy.spec"])
        else:
            # Fallback if spec file is missing
            subprocess.check_call([
                "pyinstaller", 
                "--noconfirm", 
                "--onefile", 
                "--windowed", 
                "--name", "SafwanBuddy", 
                "--icon", "assets/icons/app.ico" if os.path.exists("assets/icons/app.ico") else "NONE",
                "main.py"
            ])
        
        print("\n" + "="*40)
        print("BUILD SUCCESSFUL!")
        print(f"Executable location: {os.path.abspath('dist/SafwanBuddy.exe')}")
        print("========================================")
        print("Note: Ensure 'config/', 'data/', and 'plugins/' folders are in the same directory as the .exe for full functionality.")
    except subprocess.CalledProcessError as e:
        print(f"\nBUILD FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
