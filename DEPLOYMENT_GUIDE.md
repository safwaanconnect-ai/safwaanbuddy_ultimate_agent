# SafwaanBuddy Ultimate++ v7.0 - Deployment Guide

## 🚀 Quick Deployment

### For End Users (Windows)

1. **Download the repository**
   ```cmd
   git clone <repository-url>
   cd safwaanbuddy_ultimate_agent
   ```

2. **Run the installer**
   ```cmd
   install.bat
   ```
   
3. **Launch the application**
   ```cmd
   run.bat
   ```

### For Developers

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd safwaanbuddy_ultimate_agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run in development mode**
   ```bash
   python run_safwaanbuddy.py
   ```

---

## 📋 Prerequisites

### Required
- **Python 3.9 or higher**
  - Download: https://www.python.org/downloads/
  - ⚠️ During installation, check "Add Python to PATH"

### Recommended
- **Vosk Speech Recognition Models**
  - Download from: https://alphacephei.com/vosk/models
  - Recommended: `vosk-model-en-us-0.22` (40MB)
  - Extract to: `data/models/vosk/vosk-model-en-us-0.22/`

- **Tesseract OCR**
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

- **Web Browser**
  - Chrome, Firefox, or Edge (for web automation)

---

## 🔧 Installation Methods

### Method 1: Windows Batch Installer (Easiest)

**Steps:**
1. Open Command Prompt
2. Navigate to project directory
3. Run: `install.bat`
4. Wait for installation to complete
5. Follow on-screen instructions

**What it does:**
- Creates virtual environment
- Installs all dependencies
- Displays next steps

### Method 2: Python Auto-Installer (Cross-Platform)

**Steps:**
```bash
python auto_installer.py
```

**What it does:**
- Checks Python version
- Upgrades pip
- Installs all requirements
- Shows configuration steps

### Method 3: Manual Installation (Advanced)

**Steps:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/ui.txt
pip install -r requirements/voice.txt
pip install -r requirements/web.txt
pip install -r requirements/documents.txt
pip install -r requirements/automation.txt

# Or install all at once
pip install -r requirements.txt
```

---

## 🎯 Post-Installation Setup

### 1. Download Vosk Models (For Voice Features)

**Why:** Enable offline voice recognition

**Steps:**
1. Visit: https://alphacephei.com/vosk/models
2. Download:
   - English (US): `vosk-model-en-us-0.22.zip` (40MB)
   - OR Hindi: `vosk-model-hi-0.22.zip`
   - OR English (India): `vosk-model-en-in-0.5.zip`
3. Extract to: `data/models/vosk/[model-name]/`
4. Verify structure:
   ```
   data/models/vosk/
   └── vosk-model-en-us-0.22/
       ├── am/
       ├── conf/
       ├── graph/
       └── ...
   ```

### 2. Install Tesseract OCR (For Screen Text Recognition)

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Add to PATH:
   - Default: `C:\Program Files\Tesseract-OCR`
   - Add to System Environment Variables
4. Verify: `tesseract --version`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
tesseract --version
```

**macOS:**
```bash
brew install tesseract
tesseract --version
```

### 3. Configure (Optional)

**Edit `config/config.yaml`:**
```yaml
voice:
  enabled: true
  wake_word: "hey safwan"
  default_language: "en-US"

gui:
  theme: "dark"
  width: 1200
  height: 800

browser:
  default: "chrome"  # or "firefox", "edge"
```

**Or use environment variables:**
```bash
# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env
VOICE_ENABLED=true
GUI_THEME=dark
BROWSER_DEFAULT=chrome
```

---

## 🏃 Running the Application

### Method 1: Windows Batch (Easiest)
```cmd
run.bat
```

### Method 2: Python Script
```bash
python run_safwaanbuddy.py
```

### Method 3: Direct Import
```python
from safwaanbuddy.main import main
main()
```

---

## ✅ Verification

### Test Installation
```bash
python test_installation.py
```

**Expected Output:**
```
============================================================
SafwaanBuddy Ultimate++ v7.0 - Installation Test
============================================================

Testing module imports...
✓ Core modules
✓ Voice modules
✓ Automation modules
✓ Vision modules
✓ Web modules
✓ Document modules
✓ Profile modules
✓ Plugin modules
✓ Utility modules

Testing core functionality...
✓ EventBus initialized
✓ ConfigManager initialized: SafwaanBuddy Ultimate++

Testing directory structure...
✓ src/safwaanbuddy
✓ config
✓ data
✓ requirements
✓ logs

Testing configuration files...
✓ config/config.yaml
✓ requirements/base.txt
✓ .env.example

============================================================
Test Results
============================================================
✓ Module Imports: PASSED
✓ Core Functionality: PASSED
✓ Directory Structure: PASSED
✓ Configuration Files: PASSED

✓ All tests passed! SafwaanBuddy is ready to use.
```

### Run Examples
```bash
python examples_usage.py
```

**What it demonstrates:**
- Basic automation
- Form filling
- Document generation
- Web automation
- Profile management
- Plugin usage
- System monitoring
- Event system

---

## 🎮 First Use

### 1. Launch the Application
```cmd
run.bat
```

### 2. GUI Opens
- Modern dark-themed interface appears
- 5 tabs: Chat, Automation, Browser, Dashboard, Settings

### 3. Try Voice Commands (If Vosk installed)
Say: **"Hey Safwan"** then:
- "search for Python tutorials"
- "open browser"
- "help"

### 4. Or Type Commands in Chat Tab
```
search for weather today
open browser
help
```

---

## 📁 Directory Layout After Installation

```
safwaanbuddy_ultimate_agent/
├── venv/                       # Virtual environment (created by installer)
├── src/safwaanbuddy/           # Application code
├── config/                     # Configuration files
├── data/
│   ├── models/vosk/            # Place Vosk models here
│   ├── profiles/               # User profiles
│   ├── templates/              # Document templates
│   ├── workflows/              # Saved workflows
│   └── cache/                  # Temporary files
├── logs/                       # Application logs
├── output/                     # Generated documents (auto-created)
├── requirements/               # Dependency files
├── assets/                     # Asset files
└── ...                         # Documentation and scripts
```

---

## 🐛 Troubleshooting

### Issue: "Python not found"
**Solution:**
1. Install Python 3.9+ from python.org
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

### Issue: "Virtual environment creation failed"
**Solution:**
```bash
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m venv venv
```

### Issue: "Module not found" errors
**Solution:**
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Then install dependencies
pip install -r requirements.txt
```

### Issue: Voice recognition not working
**Solutions:**
1. Verify Vosk model is downloaded and extracted
2. Check path: `data/models/vosk/[model-name]/`
3. Ensure microphone permissions are granted
4. Test microphone: `python -c "import sounddevice; print(sounddevice.query_devices())"`

### Issue: OCR not finding text
**Solutions:**
1. Install Tesseract OCR
2. Add Tesseract to system PATH
3. Verify: `tesseract --version`
4. Increase `ocr_confidence` in config.yaml

### Issue: Browser won't open
**Solutions:**
1. Install Chrome, Firefox, or Edge
2. Check firewall settings
3. Try different browser in config.yaml
4. Ensure webdriver-manager can download drivers

### Issue: GUI doesn't appear
**Solutions:**
1. Verify PyQt6 is installed: `pip list | grep PyQt6`
2. Reinstall UI requirements: `pip install -r requirements/ui.txt`
3. Check for error messages in logs/

---

## 🔄 Updating

### Update Application
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Update Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

---

## 📦 Building Distribution

### Create Distributable Package
```bash
python build.py
```

**Output:**
- `dist/safwaanbuddy-ultimate-7.0.0.tar.gz`
- `dist/safwaanbuddy_ultimate-7.0.0-py3-none-any.whl`

### Install from Package
```bash
pip install dist/safwaanbuddy_ultimate-7.0.0-py3-none-any.whl
```

---

## 🌐 Network Configuration

### Firewall Rules (Windows)

If browser automation fails, add firewall rules:

1. Windows Defender Firewall
2. Advanced Settings
3. Outbound Rules → New Rule
4. Allow Python.exe and browser executables

### Proxy Configuration

If behind a proxy:

```yaml
# config/config.yaml
browser:
  proxy: "http://proxy.example.com:8080"
```

Or set environment variables:
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
```

---

## 📊 Performance Tuning

### For Low-End Systems

Edit `config/config.yaml`:
```yaml
gui:
  animation_speed: 0.5  # Reduce animations

voice:
  enabled: false  # Disable voice if not needed

automation:
  screenshot_quality: 60  # Lower quality screenshots
```

### For High-Performance Systems

```yaml
gui:
  animation_speed: 2.0  # Faster animations
  width: 1920
  height: 1080

automation:
  screenshot_quality: 95  # Higher quality
```

---

## 🔐 Security Considerations

### Encryption

Enable profile encryption:
```yaml
security:
  encryption_enabled: true
  key_file: "data/.key"
```

### Permissions

Set proper file permissions:
```bash
# Linux/macOS
chmod 600 data/profiles/*.yaml
chmod 600 data/.key
```

---

## 📞 Support

### Getting Help

1. **Documentation**: Check README.md and QUICKSTART.md
2. **Examples**: Run `python examples_usage.py`
3. **Test**: Run `python test_installation.py`
4. **Logs**: Check `logs/` directory for error messages
5. **Issues**: Open a GitHub issue with:
   - OS and Python version
   - Error message
   - Steps to reproduce
   - Log files

### Community

- GitHub Issues
- Discussions
- Pull Requests welcome (see CONTRIBUTING.md)

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Python 3.9+ installed
- [ ] All dependencies installed (`pip list`)
- [ ] Vosk models downloaded (if using voice)
- [ ] Tesseract OCR installed (if using OCR)
- [ ] Web browser installed (if using web automation)
- [ ] Configuration customized (`config/config.yaml`)
- [ ] Installation test passed (`python test_installation.py`)
- [ ] Example scripts work (`python examples_usage.py`)
- [ ] Firewall rules configured (if needed)
- [ ] Logs directory writable
- [ ] Data directory writable
- [ ] Virtual environment activated

---

## 🎉 Success!

Once everything is set up:

✅ Launch: `run.bat` or `python run_safwaanbuddy.py`  
✅ GUI opens with dark theme  
✅ Chat tab ready for commands  
✅ Voice recognition active (if configured)  
✅ All automation features available  

**Enjoy using SafwaanBuddy Ultimate++!** 🚀

---

*For more information, see README.md, QUICKSTART.md, and CONTRIBUTING.md*
