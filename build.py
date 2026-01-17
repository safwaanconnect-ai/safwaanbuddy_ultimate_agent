#!/usr/bin/env python3
"""Build script for SafwaanBuddy."""

import sys
import subprocess
import shutil
from pathlib import Path


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    dirs_to_remove = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        "**/__pycache__",
        "**/*.pyc"
    ]
    
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            else:
                path.unlink()
                print(f"Removed: {path}")


def build_package():
    """Build Python package."""
    print("\nBuilding package...")
    
    try:
        subprocess.check_call([sys.executable, "setup.py", "sdist", "bdist_wheel"])
        print("✓ Package built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False


def install_local():
    """Install package locally."""
    print("\nInstalling locally...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✓ Installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        return False


def main():
    """Main build routine."""
    print("=" * 60)
    print("SafwaanBuddy Ultimate++ v7.0 - Build Script")
    print("=" * 60)
    print()
    
    clean_build()
    
    if not build_package():
        return 1
    
    print("\nBuild complete! Package files in dist/")
    
    response = input("\nInstall locally? (y/n): ")
    if response.lower() == 'y':
        if not install_local():
            return 1
    
    print("\n" + "=" * 60)
    print("Build process complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
