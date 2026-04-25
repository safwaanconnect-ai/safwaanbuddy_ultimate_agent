import os
import subprocess
import sys
import shutil

def clean_build():
    """Removes old build and dist folders."""
    dirs_to_remove = ['build', 'dist']
    for d in dirs_to_remove:
        if os.path.exists(d):
            print(f"Cleaning up {d} directory...")
            shutil.rmtree(d)

def verify_build():
    """Verifies that the build was successful and assets were copied."""
    output_path = os.path.join('dist', 'SafwanBuddy')
    if not os.path.exists(output_path):
        print("Verification Failed: Output directory not found.")
        return False
    
    asset_path = os.path.join(output_path, 'assets')
    if not os.path.exists(asset_path):
        print("Verification Failed: Assets not bundled.")
        return False
        
    print(f"Verification Successful: Build located at {output_path}")
    return True

def check_dependencies():
    """Checks for required build-time dependencies."""
    print("Checking dependencies...")
    required = ['pyinstaller', 'psutil']
    if os.name == 'nt':
        required.extend(['pywin32', 'pycaw', 'comtypes', 'wmi'])
    
    for lib in required:
        try:
            if lib == 'pywin32':
                import win32api
            else:
                __import__(lib)
        except ImportError:
            print(f"Missing dependency: {lib}. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

def build():
    print("Starting production build process for SafwanBuddy Ultimate++ v7.0...")
    
    # Pre-build cleanup
    clean_build()
    
    # Dependency check
    check_dependencies()
    
    # Run pyinstaller
    try:
        # Use the spec file for the build
        subprocess.check_call(["pyinstaller", "--noconfirm", "safwanbuddy.spec"])
        print("\nPyInstaller process completed.")
        
        # Post-build verification
        if verify_build():
            print("Production-ready executable is ready for deployment.")
        else:
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
