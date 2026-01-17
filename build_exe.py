#!/usr/bin/env python3
"""
Build script to create standalone executable for SafwaanBuddy Ultimate++ v7.0
Uses PyInstaller to bundle all dependencies into a single executable.
"""

import sys
import subprocess
import shutil
from pathlib import Path
import platform


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("\nInstalling PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install PyInstaller")
        return False


def clean_build_dirs():
    """Clean previous build artifacts."""
    print("\nCleaning previous build artifacts...")
    
    dirs_to_remove = ["build", "dist"]
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_name}/")
    
    # Remove spec file build artifacts
    spec_dirs = [Path(p) for p in Path(".").glob("*.spec")]
    for spec_dir in spec_dirs:
        build_dir = spec_dir.stem
        if Path(build_dir).exists():
            shutil.rmtree(build_dir)
            print(f"  Removed: {build_dir}/")


def create_icon():
    """Create a default icon if none exists."""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / "icon.ico"
    if not icon_path.exists():
        print("\nNote: No icon file found. The executable will use default icon.")
        print(f"  To add a custom icon, place it at: {icon_path}")
    else:
        print(f"✓ Found icon: {icon_path}")


def build_executable():
    """Build the executable using PyInstaller."""
    print("\n" + "=" * 60)
    print("Building SafwaanBuddy Ultimate++ v7.0 Executable")
    print("=" * 60)
    
    spec_file = Path("safwaanbuddy.spec")
    
    if not spec_file.exists():
        print(f"✗ Spec file not found: {spec_file}")
        print("  Creating basic spec file...")
        
        # Create basic spec using PyInstaller
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--name=SafwaanBuddy",
            "--windowed",  # No console window
            "--onedir",  # One directory with all files
            "run_safwaanbuddy.py"
        ]
        
        try:
            subprocess.check_call(cmd)
            print("✓ Basic spec file created")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create spec file: {e}")
            return False
    
    # Build using the spec file
    print(f"\nBuilding from spec file: {spec_file}")
    print("This may take several minutes...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False


def verify_build():
    """Verify the built executable."""
    print("\n" + "=" * 60)
    print("Verifying Build")
    print("=" * 60)
    
    dist_dir = Path("dist/SafwaanBuddy")
    exe_name = "SafwaanBuddy.exe" if platform.system() == "Windows" else "SafwaanBuddy"
    exe_path = dist_dir / exe_name
    
    if not dist_dir.exists():
        print(f"✗ Distribution directory not found: {dist_dir}")
        return False
    
    if not exe_path.exists():
        print(f"✗ Executable not found: {exe_path}")
        return False
    
    print(f"✓ Executable found: {exe_path}")
    print(f"✓ Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
    
    # List contents
    print("\nDistribution contents:")
    for item in sorted(dist_dir.iterdir()):
        if item.is_file():
            size = item.stat().st_size / 1024
            print(f"  {item.name} ({size:.1f} KB)")
        else:
            print(f"  {item.name}/ (directory)")
    
    return True


def create_readme():
    """Create README for the distribution."""
    dist_dir = Path("dist/SafwaanBuddy")
    if not dist_dir.exists():
        return
    
    readme_path = dist_dir / "README_DISTRIBUTION.txt"
    
    readme_content = """
SafwaanBuddy Ultimate++ v7.0 - Standalone Distribution
======================================================

Thank you for using SafwaanBuddy Ultimate++!

QUICK START
-----------
1. Run SafwaanBuddy.exe to start the application
2. The first run may take longer as it initializes

OPTIONAL COMPONENTS
-------------------
For full functionality, you may want to install:

1. Vosk Speech Recognition Models (for voice features)
   - Download from: https://alphacephei.com/vosk/models
   - Place in: data/models/vosk/
   - Recommended: vosk-model-en-us-0.22

2. Tesseract OCR (for text recognition features)
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to system PATH after installation

3. Web Browser (for web automation)
   - Chrome, Firefox, or Edge
   - Already installed on most systems

CONFIGURATION
-------------
- Configuration file: config/config.yaml
- Environment variables: Copy .env.example to .env

DIRECTORIES
-----------
- config/          - Configuration files
- data/profiles/   - User profiles
- data/templates/  - Document templates
- logs/            - Application logs (created on first run)

TROUBLESHOOTING
---------------
If you encounter issues:
1. Check logs/ directory for error messages
2. Ensure antivirus is not blocking the application
3. Run as Administrator if permission errors occur

DOCUMENTATION
-------------
Full documentation available at:
https://github.com/safwaanbuddy/ultimate-agent

LICENSE
-------
MIT License - See LICENSE file for details

SUPPORT
-------
For issues and questions:
https://github.com/safwaanbuddy/ultimate-agent/issues

Version: 7.0.0
Build Date: {BUILD_DATE}
Platform: Windows

Enjoy using SafwaanBuddy Ultimate++!
"""
    
    from datetime import datetime
    readme_content = readme_content.format(
        BUILD_DATE=datetime.now().strftime("%Y-%m-%d")
    )
    
    readme_path.write_text(readme_content.strip())
    print(f"\n✓ Created distribution README: {readme_path}")


def main():
    """Main build routine."""
    print("=" * 60)
    print("SafwaanBuddy Ultimate++ v7.0")
    print("Executable Build Script")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9+ required")
        return 1
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"✓ Platform: {platform.system()} {platform.release()}")
    
    # Check/install PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return 1
    
    # Clean previous builds
    clean_build_dirs()
    
    # Check icon
    create_icon()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Verify build
    if not verify_build():
        return 1
    
    # Create distribution README
    create_readme()
    
    print("\n" + "=" * 60)
    print("BUILD SUCCESS!")
    print("=" * 60)
    print("\nYour executable is ready in: dist/SafwaanBuddy/")
    print("\nTo distribute:")
    print("1. Zip the entire dist/SafwaanBuddy/ folder")
    print("2. Share the zip file with users")
    print("\nUsers simply extract and run SafwaanBuddy.exe")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
