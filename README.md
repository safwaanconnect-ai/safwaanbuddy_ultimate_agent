# SafwanBuddy Ultimate++ v7.0

SafwanBuddy is a comprehensive AI-powered automation assistant for Windows. It features voice control, web automation, document generation, and a modular plugin architecture.

## Features
- **Voice Recognition**: Offline speech-to-text using Vosk.
- **Holographic UI**: Modern PyQt6 interface with ModernGL animations.
- **Smart Automation**: OCR-based clicking and human-like typing.
- **Web Control**: Browser automation via Selenium.
- **Document Suite**: Generate Word, Excel, and PDF files.
- **Plugin System**: Easily extend functionality with custom Python scripts.
- **Security**: Encrypted storage for sensitive user data.

## Installation

1. Install Python 3.9+
2. Install Tesseract OCR on your system.
3. Run `install.bat` to install dependencies.
4. Download Vosk models to `assets/models/`.

## Usage

Run `run.bat` or `python run_safwaan_buddy.py`.
Say "Hey Safwan" to wake up the assistant.

## Project Structure
- `src/safwanbuddy/`: Source code
- `config/`: Configuration files
- `plugins/`: User-defined plugins
- `data/`: Profiles and encrypted storage
- `assets/`: UI resources, models, and shaders

## Development
To add a plugin, create a new `.py` file in the `plugins/` directory inheriting from `PluginBase`.
