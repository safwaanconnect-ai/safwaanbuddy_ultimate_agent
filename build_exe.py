import os
import subprocess
import sys

def build():
    print("Starting build process for SafwanBuddy...")
    
    # Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Run pyinstaller
    try:
        subprocess.check_call(["pyinstaller", "--noconfirm", "safwanbuddy.spec"])
        print("Build successful! Check the 'dist' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")

if __name__ == "__main__":
    build()
