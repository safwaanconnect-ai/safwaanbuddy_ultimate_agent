# Contributing to SafwaanBuddy Ultimate++

Thank you for your interest in contributing to SafwaanBuddy Ultimate++!

## Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/safwaanbuddy_ultimate_agent.git
   cd safwaanbuddy_ultimate_agent
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and modular

### Module Structure

Each module should:
- Have a clear, single responsibility
- Include proper logging
- Handle exceptions gracefully
- Emit appropriate events via EventBus
- Use ConfigManager for settings

### Adding New Features

1. **Create a new branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement your feature** following the existing architecture patterns

3. **Test your changes** thoroughly

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Creating Plugins

To create a new plugin:

1. Create `src/safwaanbuddy/plugins/plugin_yourname.py`
2. Extend `PluginBase` class
3. Implement required methods: `name`, `version`, `initialize`, `execute`
4. Add plugin to README

Example:
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
        # Setup code here
        return True
    
    def execute(self, *args, **kwargs):
        # Plugin logic here
        return "Result"
```

### Adding Voice Commands

To add new voice commands:

1. Open `src/safwaanbuddy/voice/command_processor.py`
2. Add command pattern to `_register_default_commands()`
3. Implement handler function
4. Register handler in main application

### Testing

Before submitting:
- Test on Windows (primary target)
- Verify all dependencies are in requirements files
- Check that logging works properly
- Ensure no hardcoded paths
- Test with different configurations

### Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Modifying configuration options
- Creating new plugins

## Areas for Contribution

### High Priority
- Additional language support for Vosk
- More UI themes
- Performance optimizations
- Error handling improvements
- Unit tests

### Medium Priority
- Additional plugins (weather, calendar, etc.)
- Browser automation enhancements
- Document template library
- Profile import/export formats
- Voice command expansions

### Nice to Have
- Mobile app integration
- Cloud sync for profiles
- Advanced OCR features
- Machine learning integrations
- Cross-platform GUI improvements

## Bug Reports

When reporting bugs, include:
- Operating system and version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs
- Screenshots if applicable

## Questions?

Open an issue with the "question" label or start a discussion.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🚀
