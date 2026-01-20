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
        if os.path.exists("safwanbuddy.spec"):
            subprocess.check_call(["pyinstaller", "--noconfirm", "safwanbuddy.spec"])
        else:
            subprocess.check_call(["pyinstaller", "--noconfirm", "--onefile", "--name", "SafwanBuddy", "main.py"])
        print("Build successful! Check the 'dist' directory.")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")

if __name__ == "__main__":
    build()
