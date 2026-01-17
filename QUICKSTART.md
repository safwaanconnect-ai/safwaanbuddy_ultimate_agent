# SafwaanBuddy Ultimate++ Quick Start Guide

Get up and running with SafwaanBuddy in 5 minutes!

## Prerequisites

- **Python 3.9 or higher** - [Download](https://www.python.org/downloads/)
- **Git** (optional) - For cloning the repository
- **Windows 10/11** (recommended) or Linux/macOS

## Installation Steps

### Step 1: Get the Code

**Option A: Clone with Git**
```bash
git clone <repository-url>
cd safwaanbuddy_ultimate_agent
```

**Option B: Download ZIP**
- Download and extract the ZIP file
- Open terminal/command prompt in the extracted folder

### Step 2: Run the Installer

**On Windows:**
```cmd
install.bat
```

**On Linux/macOS:**
```bash
python3 auto_installer.py
```

This will:
- Create a virtual environment
- Install all required Python packages
- Set up the directory structure

### Step 3: Download Voice Models (Optional but Recommended)

1. Visit [Vosk Models](https://alphacephei.com/vosk/models)
2. Download **vosk-model-en-us-0.22** (English) or your preferred language
3. Extract to: `data/models/vosk/vosk-model-en-us-0.22/`

### Step 4: Install Tesseract OCR (Optional but Recommended)

**Windows:**
1. Download from [Tesseract @ UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### Step 5: Verify Installation

```bash
python test_installation.py
```

All tests should pass! ✓

### Step 6: Launch SafwaanBuddy

**Windows:**
```cmd
run.bat
```

**Linux/macOS:**
```bash
python run_safwaanbuddy.py
```

## First Run

When you first launch SafwaanBuddy:

1. **GUI Opens** - Modern dark-themed interface appears
2. **Voice System** (if Vosk model installed) - "SafwaanBuddy is ready"
3. **Chat Tab** - Ready for commands

## Try These Commands

In the Chat tab, type or say:

```
open browser
```
Opens your default web browser

```
search for Python automation
```
Searches Google for the query

```
help
```
Lists all available commands

## Quick Examples

### Example 1: Web Search
```python
# In the chat: "search for weather today"
```

### Example 2: Form Filling
```python
# 1. Navigate to a form in your browser
# 2. In chat: "fill form"
# Uses data from data/profiles/personal.yaml
```

### Example 3: Create Document
```python
# In chat: "create document named MyReport"
# Generates: output/MyReport.docx
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
voice:
  enabled: true
  wake_word: "hey safwan"

gui:
  theme: "dark"
  width: 1200
  height: 800

browser:
  default: "chrome"
```

## Troubleshooting

### "No module named 'yaml'"
```bash
pip install -r requirements.txt
```

### Voice recognition not working
- Verify Vosk model is in `data/models/vosk/`
- Check microphone permissions
- Test with: `python -c "import sounddevice; print(sounddevice.query_devices())"`

### OCR not finding text
- Install Tesseract OCR
- Verify PATH: `tesseract --version`
- Adjust `ocr_confidence` in config.yaml

### Browser won't open
- Install Chrome, Firefox, or Edge
- Check firewall settings
- Try different browser in config

## Next Steps

1. **Customize Your Profile**
   - Edit `data/profiles/personal.yaml`
   - Add your information for form filling

2. **Explore Plugins**
   - Check `src/safwaanbuddy/plugins/`
   - Create your own (see CONTRIBUTING.md)

3. **Record Workflows**
   - Use Automation tab to record repetitive tasks
   - Playback anytime

4. **Create Templates**
   - Add document templates to `data/templates/`
   - Generate documents quickly

## Keyboard Shortcuts

- **Ctrl+Q** - Quit application
- **Ctrl+S** - Open settings
- **Enter** - Send chat message

## Command Reference

| Command | Action |
|---------|--------|
| `search for [query]` | Web search |
| `open browser` | Launch browser |
| `type [text]` | Type text |
| `click [element]` | Click by text |
| `fill form` | Auto-fill form |
| `create document` | Generate Word doc |
| `take screenshot` | Capture screen |
| `help` | List commands |
| `stop` | Cancel action |

## Support

- **Documentation**: See README.md
- **Issues**: Open a GitHub issue
- **Examples**: Check examples/ folder
- **Community**: Join discussions

## Tips for Best Results

1. **Speak clearly** for voice commands (if using voice)
2. **Use simple commands** - "search Python" works better than complex sentences
3. **Check logs** in `logs/` folder for troubleshooting
4. **Update regularly** - `git pull` for latest features
5. **Customize config** for your workflow

## What's Next?

Now that you're set up:

- ✅ Explore the GUI tabs (Chat, Automation, Browser, Dashboard)
- ✅ Try voice commands (say "Hey Safwan")
- ✅ Record a workflow
- ✅ Generate your first document
- ✅ Fill a form automatically
- ✅ Create a custom plugin

**Enjoy using SafwaanBuddy Ultimate++!** 🚀

---

Need help? Check README.md or open an issue!
