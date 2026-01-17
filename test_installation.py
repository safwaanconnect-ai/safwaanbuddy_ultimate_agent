#!/usr/bin/env python3
"""Test script to verify SafwaanBuddy installation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing module imports...")
    
    try:
        from safwaanbuddy.core import EventBus, ConfigManager, setup_logger
        print("✓ Core modules")
    except ImportError as e:
        print(f"✗ Core modules: {e}")
        return False
    
    try:
        from safwaanbuddy.voice import CommandProcessor, LanguageManager
        print("✓ Voice modules")
    except ImportError as e:
        print(f"✗ Voice modules: {e}")
        return False
    
    try:
        from safwaanbuddy.automation import ClickSystem, TypeSystem, FormFiller, WorkflowEngine
        print("✓ Automation modules")
    except ImportError as e:
        print(f"✗ Automation modules: {e}")
        return False
    
    try:
        from safwaanbuddy.vision import ScreenCapture, OCREngine, ElementDetector
        print("✓ Vision modules")
    except ImportError as e:
        print(f"✗ Vision modules: {e}")
        return False
    
    try:
        from safwaanbuddy.web import BrowserController, SearchEngine, WebScraper
        print("✓ Web modules")
    except ImportError as e:
        print(f"✗ Web modules: {e}")
        return False
    
    try:
        from safwaanbuddy.documents import WordGenerator, ExcelGenerator, PDFGenerator
        print("✓ Document modules")
    except ImportError as e:
        print(f"✗ Document modules: {e}")
        return False
    
    try:
        from safwaanbuddy.profiles import ProfileManager, FormProfile, Preferences
        print("✓ Profile modules")
    except ImportError as e:
        print(f"✗ Profile modules: {e}")
        return False
    
    try:
        from safwaanbuddy.plugins import PluginLoader, PluginBase
        print("✓ Plugin modules")
    except ImportError as e:
        print(f"✗ Plugin modules: {e}")
        return False
    
    try:
        from safwaanbuddy.utils import SystemMonitor, AlertSystem
        print("✓ Utility modules")
    except ImportError as e:
        print(f"✗ Utility modules: {e}")
        return False
    
    return True


def test_core_functionality():
    """Test core functionality."""
    print("\nTesting core functionality...")
    
    try:
        from safwaanbuddy.core import EventBus, ConfigManager
        
        # Test EventBus
        event_bus = EventBus()
        print("✓ EventBus initialized")
        
        # Test ConfigManager
        config = ConfigManager()
        app_name = config.get("app.name")
        print(f"✓ ConfigManager initialized: {app_name}")
        
        return True
    except Exception as e:
        print(f"✗ Core functionality: {e}")
        return False


def test_directory_structure():
    """Test that required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "src/safwaanbuddy",
        "config",
        "data",
        "requirements",
        "logs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"✗ {dir_path} - missing")
            all_exist = False
    
    return all_exist


def test_config_files():
    """Test that config files exist."""
    print("\nTesting configuration files...")
    
    required_files = [
        "config/config.yaml",
        "requirements/base.txt",
        ".env.example"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("SafwaanBuddy Ultimate++ v7.0 - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("Core Functionality", test_core_functionality()))
    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Configuration Files", test_config_files()))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")
    
    print()
    
    if all(result[1] for result in results):
        print("✓ All tests passed! SafwaanBuddy is ready to use.")
        print()
        print("Next steps:")
        print("1. Download Vosk models (see README.md)")
        print("2. Install Tesseract OCR")
        print("3. Run: python run_safwaanbuddy.py")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
