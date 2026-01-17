# SafwaanBuddy Ultimate++ v7.0

**A comprehensive Windows AI assistant with voice control, web automation, document generation, and intelligent form filling.**

## 🚀 Features

### Voice AI Subsystem
- **Offline Speech Recognition** using Vosk (English, Hindi, Hyderabadi)
- **Wake Word Detection** - "Hey Safwan"
- **Text-to-Speech** synthesis with customizable voices
- **Intent Recognition** and command routing
- **Multi-language Support** with configurable models

### Automation Engine
- **OCR-Based Smart Clicking** - Find and click elements by text
- **Human-Like Typing** with randomized delays
- **Automated Form Filling** using user profiles
- **Workflow Recording & Playback** for repetitive tasks
- **Multi-Target Element Selection**

### Computer Vision & OCR
- **Fast Screen Capture** with multi-monitor support (mss)
- **Tesseract OCR** for text recognition
- **UI Element Detection** - buttons, links, fields, checkboxes
- **Text Overlay** with visual feedback

### Web Automation
- **Browser Control** - Chrome, Firefox, Edge support via Selenium
- **Multi-Search Engine** integration (Google, Bing, DuckDuckGo)
- **Web Scraping** and data extraction
- **Automated Navigation** and form submission

### Document Generation
- **Word Documents** - formatted text, lists, tables, images (python-docx)
- **Excel Spreadsheets** - data writing, formulas, styling (openpyxl)
- **PDF Generation** - professional documents (ReportLab)
- **Template System** - YAML-based document templates

### GUI Framework
- **Modern PyQt6 Interface** with dark theme
- **Chat Interface** for voice/text commands
- **Automation Controls** - workflow management
- **Browser Tab** - web automation controls
- **System Dashboard** - monitoring and status
- **Settings Panel** - configuration management

### Profile & Data Management
- **User Profiles** - YAML storage with JSON import/export
- **Form Profiles** - structured field definitions
- **Preferences System** - persistent settings
- **Multiple Profile Support** (personal, professional)

### Plugin System
- **Dynamic Plugin Loading** from plugins/ directory
- **Plugin Base Classes** for standardization
- **Event-Driven Architecture** for plugin communication
- **Example Plugins** - notes, calculator, file operations

### System Features
- **Event Bus** - inter-module communication
- **Comprehensive Logging** - file and console output
- **Configuration Management** - YAML with environment overrides
- **System Monitoring** - CPU, memory, disk usage
- **Alert System** - notifications and warnings
- **Encrypted Storage** - for sensitive data

## 📋 Requirements

- **Python 3.9+**
- **Windows 10/11** (primary target, cross-platform architecture)
- **4GB RAM minimum** (8GB+ recommended)
- **1GB free disk space**
- **Internet connection** (for initial setup)

## 🔧 Installation

### Option 1: Windows Batch Script (Recommended)

1. **Clone or download** this repository
2. **Run the installer**:
   ```cmd
   install.bat
   ```
3. **Follow the on-screen instructions**

### Option 2: Python Script

```bash
python auto_installer.py
```

### Option 3: Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install from setup.py
pip install -e .
```

## 📦 Additional Setup

### 1. Vosk Speech Recognition Models

Download language models from [Vosk Models](https://alphacephei.com/vosk/models):

- **English (US)**: `vosk-model-en-us-0.22` (recommended)
- **Hindi**: `vosk-model-hi-0.22`
- **English (India)**: `vosk-model-en-in-0.5`

Extract to: `data/models/vosk/[model-name]`

### 2. Tesseract OCR

**Windows:**
- Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Install and add to system PATH
- Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 3. Web Browser

Ensure at least one of these browsers is installed:
- Google Chrome
- Mozilla Firefox
- Microsoft Edge

WebDriver will be managed automatically via `webdriver-manager`.

## 🎯 Quick Start

### Windows

```cmd
run.bat
```

### Python

```bash
python run_safwaanbuddy.py
```

### From Code

```python
from safwaanbuddy.main import main
main()
```

## 💡 Usage Examples

### Voice Commands

After starting, say **"Hey Safwan"** followed by:

- **"search for Python tutorials"** - Search the web
- **"open browser"** - Launch web browser
- **"type Hello World"** - Type text
- **"click Submit"** - Click button by text
- **"fill form"** - Auto-fill form with profile data
- **"create document"** - Generate Word document
- **"take screenshot"** - Capture screen
- **"help"** - List available commands

### Automation Example

```python
from safwaanbuddy.automation import ClickSystem, TypeSystem

click = ClickSystem()
typer = TypeSystem()

# Click on text
click.click_text("Login")

# Type with human-like delays
typer.type_text("username@example.com", human_like=True)

# Press Tab
typer.press_key('tab')

# Type password
typer.type_text("password123", human_like=True)

# Press Enter
typer.press_key('enter')
```

### Form Filling Example

```python
from safwaanbuddy.automation import FormFiller
from safwaanbuddy.automation.form_filler import FormField

filler = FormFiller()
filler.load_profile("personal")

fields = [
    FormField("name", "text", label="Full Name", required=True),
    FormField("email", "email", label="Email Address", required=True),
    FormField("phone", "tel", label="Phone Number")
]

filler.fill_form(fields)
```

### Document Generation Example

```python
from safwaanbuddy.documents import WordGenerator

doc = WordGenerator()
doc.create_document()

doc.add_heading("My Report", level=1)
doc.add_paragraph("This is a sample document.")

table_data = [
    ["Name", "Age", "City"],
    ["John", "30", "New York"],
    ["Jane", "25", "London"]
]
doc.add_table(table_data, has_header=True)

doc.save_document("output/my_report.docx")
```

### Web Automation Example

```python
from safwaanbuddy.web import BrowserController, SearchEngine

browser = BrowserController()
browser.start_browser("chrome")

search = SearchEngine()
search.search("Python automation")

browser.navigate("https://example.com")
browser.type_text("#username", "myuser")
browser.click_element("#login-button")
```

### Workflow Recording Example

```python
from safwaanbuddy.automation import WorkflowEngine

workflow = WorkflowEngine()

# Start recording
workflow.start_recording("Login Workflow", "Automated login process")

# Perform actions (clicks, typing, etc.)
workflow.record_step("click", {"target": "Login", "method": "text"})
workflow.record_step("type", {"text": "username", "field": "#user"})

# Stop and save
recorded = workflow.stop_recording()
workflow.save_workflow(recorded)

# Playback later
loaded = workflow.load_workflow("Login_Workflow.json")
workflow.playback_workflow(loaded)
```

## 🔌 Creating Plugins

Create a file `src/safwaanbuddy/plugins/plugin_myplugin.py`:

```python
from safwaanbuddy.plugins import PluginBase

class MyPlugin(PluginBase):
    @property
    def name(self):
        return "My Plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self):
        self.logger.info("Plugin initialized")
        return True
    
    def execute(self, *args, **kwargs):
        self.logger.info("Plugin executed")
        return "Success"
```

## 📁 Project Structure

```
safwaanbuddy_ultimate_agent/
├── src/safwaanbuddy/
│   ├── core/              # Core engine (events, config, logging)
│   ├── voice/             # Speech recognition & TTS
│   ├── automation/        # Clicking, typing, forms, workflows
│   ├── gui/               # PyQt6 interface
│   ├── vision/            # Screen capture & OCR
│   ├── web/               # Browser automation
│   ├── documents/         # Document generation
│   ├── profiles/          # Profile management
│   ├── plugins/           # Plugin system
│   ├── social/            # Social media integration
│   ├── utils/             # Utilities & monitoring
│   └── main.py            # Main application
├── config/                # Configuration files
├── data/                  # Data storage
│   ├── profiles/          # User profiles
│   ├── templates/         # Document templates
│   ├── workflows/         # Saved workflows
│   ├── models/            # Vosk models
│   └── cache/             # Temporary files
├── assets/                # Assets (shaders, fonts, icons)
├── logs/                  # Application logs
├── requirements/          # Dependency specifications
├── setup.py               # Package setup
├── run_safwaanbuddy.py    # Main launcher
├── install.bat            # Windows installer
├── run.bat                # Windows runner
└── README.md              # This file
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

- Voice settings (wake word, languages, confidence)
- TTS settings (rate, volume, voice)
- GUI theme and appearance
- Automation delays and behavior
- Browser preferences
- Plugin configuration
- Security settings

Environment variables override config:
```bash
export VOICE_ENABLED=true
export GUI_THEME=dark
export DEBUG=true
```

## 🐛 Troubleshooting

### Voice Recognition Not Working
- Ensure Vosk model is downloaded and extracted to `data/models/vosk/`
- Check microphone permissions
- Verify audio device settings

### OCR Not Finding Text
- Install Tesseract OCR
- Add Tesseract to system PATH
- Increase `ocr_confidence` in config
- Ensure screen text is readable

### Browser Automation Fails
- Install Chrome/Firefox/Edge
- Check firewall settings
- Update browser to latest version
- Try different browser in config

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`
- Activate virtual environment

## 📊 System Requirements

### Minimum
- Python 3.9
- 4GB RAM
- 2-core CPU
- 1GB free space

### Recommended
- Python 3.10+
- 8GB+ RAM
- 4-core CPU
- 2GB+ free space
- Dedicated GPU (for advanced vision tasks)

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional language support
- More plugin examples
- UI/UX improvements
- Performance optimizations
- Bug fixes

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Vosk** - Offline speech recognition
- **PyQt6** - GUI framework
- **Tesseract** - OCR engine
- **Selenium** - Web automation
- **python-docx, openpyxl, ReportLab** - Document generation

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## 🔄 Version History

### v7.0.0 (Current)
- Complete modular architecture
- Voice AI with wake word detection
- Advanced automation engine
- Modern PyQt6 GUI
- Comprehensive document generation
- Plugin system
- Multi-profile support
- System monitoring

---

**SafwaanBuddy Ultimate++ v7.0** - Your AI-powered productivity command center! 🚀
