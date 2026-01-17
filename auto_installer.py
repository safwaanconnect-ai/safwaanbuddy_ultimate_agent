#!/usr/bin/env python3
"""Automated installation script for SafwaanBuddy."""

import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"Error: Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_package(package):
    """Install a single package."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def install_requirements(req_file):
    """Install requirements from file."""
    if not Path(req_file).exists():
        print(f"Warning: {req_file} not found")
        return False
    
    print(f"\nInstalling from {req_file}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", req_file
        ])
        return True
    except subprocess.CalledProcessError:
        print(f"Warning: Some packages from {req_file} failed to install")
        return False


def main():
    """Main installation routine."""
    print("=" * 60)
    print("SafwaanBuddy Ultimate++ v7.0 - Automated Installer")
    print("=" * 60)
    print()
    
    if not check_python_version():
        return 1
    
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    print("Installing pip...")
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    requirements_files = [
        "requirements/base.txt",
        "requirements/ui.txt",
        "requirements/voice.txt",
        "requirements/web.txt",
        "requirements/documents.txt",
        "requirements/automation.txt"
    ]
    
    for req_file in requirements_files:
        install_requirements(req_file)
    
    print()
    print("=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Download Vosk models from https://alphacephei.com/vosk/models")
    print("2. Install Tesseract OCR for your platform")
    print("3. Ensure a web browser (Chrome/Firefox/Edge) is installed")
    print()
    print("To start: python run_safwaanbuddy.py")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
