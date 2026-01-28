#!/usr/bin/env python3
"""
Setup script for SafwanBuddy Ultimate++ v7.0
JARVIS-Style AI Agent

This script sets up the complete development environment and dependencies.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  ████████╗ █████╗ ████████╗██╗  ██╗    ██╗██╗███╗   ██╗ ║
    ║  ╚══██╔══╝██╔══██╗╚══██╔══╝██║  ██║    ██║██║████╗  ██║ ║
    ║     ██║   ███████║   ██║   ███████║    ██║██║██╔██╗ ██║ ║
    ║     ██║   ██╔══██║   ██║   ██╔══██║    ██║██║██║╚██╗██║ ║
    ║     ██║   ██║  ██║   ██║   ██║  ██║    ██║██║██║ ╚████║ ║
    ║     ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝╚═╝╚═╝  ╚═══╝ ║
    ║                                                              ║
    ║  Ultimate++ v7.0 - JARVIS-Style AI Agent                    ║
    ║  Complete Voice-Controlled Desktop Automation System          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade your Python installation.")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def check_system_requirements():
    """Check system requirements"""
    print("\n💻 Checking system requirements...")
    
    system = platform.system()
    print(f"✅ Operating System: {system} ({platform.release()})")
    
    # Check for required system tools
    required_tools = []
    
    if system == "Windows":
        required_tools = ["git"]
    elif system == "Darwin":  # macOS
        required_tools = ["git"]
    else:  # Linux
        required_tools = ["git", "ffmpeg"]
    
    missing_tools = []
    for tool in required_tools:
        if not check_command_exists(tool):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"⚠️  Missing tools: {', '.join(missing_tools)}")
        print("   Please install these tools before continuing.")
        return False
    
    print("✅ System requirements satisfied")
    return True

def check_command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, "--version"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL, 
                     check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                     check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip is not available!")
        print("   Please install pip first.")
        return False
    
    # Upgrade pip first
    print("📈 Upgrading pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                     check=True)
    except subprocess.CalledProcessError:
        print("⚠️  Failed to upgrade pip, continuing...")
    
    # Install dependencies from requirements.txt
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    print("📋 Installing from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                     check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create required directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "logs",
        "data",
        "screenshots",
        "workflows",
        "profiles",
        "config/backups"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Directories created")
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("\n📚 Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        print("✅ NLTK data downloaded")
        return True
    except ImportError:
        print("⚠️  NLTK not installed, skipping data download")
        return True
    except Exception as e:
        print(f"⚠️  NLTK data download failed: {e}")
        return True  # Non-critical error

def setup_tesseract():
    """Setup Tesseract OCR (optional but recommended)"""
    print("\n🔍 Setting up Tesseract OCR...")
    
    system = platform.system()
    
    if system == "Windows":
        # Check if Tesseract is installed
        if check_command_exists("tesseract"):
            print("✅ Tesseract found")
            return True
        else:
            print("⚠️  Tesseract not found")
            print("   Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   Or install via Chocolatey: choco install tesseract")
            return True  # Not critical
    else:
        # For macOS and Linux, try to install via package manager
        try:
            if system == "Darwin":
                # macOS
                result = subprocess.run(["brew", "list", "tesseract"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Tesseract found")
                    return True
                else:
                    print("⚠️  Tesseract not found")
                    print("   Install via: brew install tesseract")
                    return True
            else:
                # Linux
                result = subprocess.run(["dpkg", "-l", "|", "grep", "tesseract"], 
                                      shell=True, capture_output=True, text=True)
                if result.returncode == 0 and "tesseract" in result.stdout:
                    print("✅ Tesseract found")
                    return True
                else:
                    print("⚠️  Tesseract not found")
                    print("   Install via: sudo apt-get install tesseract-ocr")
                    return True
        except Exception:
            print("⚠️  Could not verify Tesseract installation")
            return True  # Not critical

def create_desktop_shortcuts():
    """Create desktop shortcuts (Windows only)"""
    if platform.system() != "Windows":
        return True
    
    print("\n🖥️  Creating desktop shortcuts...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(os.path.join(desktop, "SafwanBuddy.lnk"))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(Path(__file__).parent / "main.py")
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = sys.executable
        shortcut.Description = "SafwanBuddy Ultimate++ - JARVIS AI Agent"
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except ImportError:
        print("⚠️  winshell not available, skipping shortcuts")
        return True
    except Exception as e:
        print(f"⚠️  Failed to create shortcuts: {e}")
        return True  # Not critical

def setup_microphone_permissions():
    """Setup microphone permissions"""
    print("\n🎤 Checking microphone access...")
    
    try:
        import speech_recognition as sr
        
        # Try to list microphones
        microphones = sr.Microphone.list_microphone_names()
        
        if microphones:
            print(f"✅ Found {len(microphones)} microphone(s)")
            for i, mic_name in enumerate(microphones):
                print(f"   {i}: {mic_name}")
        else:
            print("⚠️  No microphones found")
        
        print("\n📝 Microphone Setup Notes:")
        print("   • Ensure microphone is connected and working")
        print("   • Grant microphone permissions to Python")
        print("   • On Windows: Check Privacy > Microphone settings")
        print("   • On macOS: Check System Preferences > Security & Privacy")
        print("   • On Linux: Check PulseAudio/ALSA configuration")
        
        return True
    except ImportError:
        print("⚠️  SpeechRecognition not installed")
        return True
    except Exception as e:
        print(f"⚠️  Microphone check failed: {e}")
        return True

def run_diagnostics():
    """Run system diagnostics"""
    print("\n🔧 Running diagnostics...")
    
    try:
        result = subprocess.run([sys.executable, "main.py", "--test"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Diagnostics passed")
            print(result.stdout)
        else:
            print("⚠️  Some diagnostics failed:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
        
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Diagnostics timed out")
        return True
    except Exception as e:
        print(f"⚠️  Diagnostics failed: {e}")
        return True

def print_usage_instructions():
    """Print usage instructions"""
    instructions = """
    
    ╔══════════════════════════════════════════════════════════════╗
    ║                    SETUP COMPLETE! 🎉                        ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  🚀 SAFWANBUDDY IS READY TO USE!                           ║
    ║                                                              ║
    ║  📖 QUICK START GUIDE:                                      ║
    ║                                                              ║
    ║  1. Run the application:                                    ║
    ║     python main.py                                          ║
    ║                                                              ║
    ║  2. Command Line Mode:                                      ║
    ║     python main.py --headless                               ║
    ║                                                              ║
    ║  3. Run Diagnostics:                                         ║
    ║     python main.py --test                                   ║
    ║                                                              ║
    ║  4. Demo Mode:                                              ║
    ║     python main.py --demo                                   ║
    ║                                                              ║
    ║  🎤 VOICE COMMANDS YOU CAN TRY:                            ║
    ║     • 'Open Firefox'                                        ║
    ║     • 'Search for Python tutorials'                         ║
    ║     • 'Take a screenshot'                                   ║
    ║     • 'What time is it?'                                   ║
    ║     • 'System status'                                       ║
    ║     • 'Volume up'                                           ║
    ║     • 'Help'                                                ║
    ║                                                              ║
    ║  ⚙️  CONFIGURATION:                                         ║
    ║     • Edit: config/config.yaml                              ║
    ║     • Profiles: config/profiles/                            ║
    ║     • Logs: logs/                                          ║
    ║                                                              ║
    ║  🔧 TROUBLESHOOTING:                                        ║
    ║     • Check logs/ directory for errors                      ║
    ║     • Run: python main.py --test                           ║
    ║     • Ensure microphone permissions are granted             ║
    ║     • Install missing dependencies with pip                ║
    ║                                                              ║
    ║  📚 DOCUMENTATION:                                          ║
    ║     • README.md for detailed information                    ║
    ║     • config/config.yaml for settings                      ║
    ║                                                              ║
    ║  🌟 FEATURES:                                               ║
    ║     ✓ Real-time voice recognition                           ║
    ║     ✓ Text-to-speech synthesis                             ║
    ║     ✓ Desktop automation                                   ║
    ║     ✓ Natural language understanding                       ║
    ║     ✓ Beautiful JARVIS-style GUI                           ║
    ║     ✓ Profile management                                   ║
    ║     ✓ System monitoring                                    ║
    ║     ✓ Workflow recording/playback                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(instructions)

def main():
    """Main setup function"""
    print_banner()
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking system requirements", check_system_requirements),
        ("Installing Python dependencies", install_python_dependencies),
        ("Setting up directories", setup_directories),
        ("Downloading NLTK data", download_nltk_data),
        ("Setting up Tesseract OCR", setup_tesseract),
        ("Creating desktop shortcuts", create_desktop_shortcuts),
        ("Setting up microphone permissions", setup_microphone_permissions),
        ("Running diagnostics", run_diagnostics)
    ]
    
    print("🚀 Starting SafwanBuddy Setup...\n")
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        print(f"STEP: {step_name}")
        print('='*60)
        
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    # Final report
    print(f"\n{'='*60}")
    print("SETUP SUMMARY")
    print('='*60)
    
    if not failed_steps:
        print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
        print_usage_instructions()
    else:
        print(f"⚠️  {len(failed_steps)} step(s) failed:")
        for step in failed_steps:
            print(f"   • {step}")
        print("\nThe application may still work, but some features might be limited.")
        print("Check the error messages above and install missing dependencies.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with unexpected error: {e}")
        sys.exit(1)