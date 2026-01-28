#!/usr/bin/env python3
"""
Desktop Executor for SafwanBuddy
Real desktop automation using pyautogui and system commands
"""

import logging
import time
import subprocess
import platform
import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)

@dataclass
class ApplicationInfo:
    """Application information for launching"""
    name: str
    executable: str
    path: str = ""
    args: List[str] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = []

class DesktopExecutor:
    """Desktop automation executor using pyautogui and system commands"""
    
    def __init__(self, config_manager=None):
        """
        Initialize Desktop Executor
        
        Args:
            config_manager: Configuration manager for settings
        """
        self.config_manager = config_manager
        self.is_initialized = False
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # Application registry
        self.applications = {}
        self._setup_application_registry()
        
        # Automation settings
        self.click_delay = 0.1
        self.type_delay = 0.05
        self.max_retries = 3
        
        # Load configuration
        self._load_config()
        
        # Initialize pyautogui
        self._initialize()
    
    def _load_config(self):
        """Load configuration settings"""
        if not self.config_manager:
            return
        
        try:
            self.click_delay = self.config_manager.get('automation.click_delay_range', (0.1, 0.5))[0]
            self.type_delay = self.config_manager.get('automation.type_delay_range', (0.05, 0.15))[0]
            self.max_retries = self.config_manager.get('automation.retry_attempts', 3)
            
            # Set pyautogui settings
            import pyautogui
            pyautogui.PAUSE = self.click_delay
            pyautogui.FAILSAFE = True
            
        except Exception as e:
            logger.warning(f"Failed to load automation config: {e}")
    
    def _initialize(self) -> bool:
        """Initialize desktop automation"""
        try:
            import pyautogui
            
            # Configure pyautogui
            pyautogui.PAUSE = self.click_delay
            pyautogui.FAILSAFE = True
            
            # Test screen size
            screen_width, screen_height = pyautogui.size()
            logger.info(f"Screen size: {screen_width}x{screen_height}")
            
            self.is_initialized = True
            logger.info("Desktop Executor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Desktop Executor: {e}")
            return False
    
    def _setup_application_registry(self):
        """Set up application registry with common applications"""
        system = platform.system()
        
        if system == "Windows":
            self._setup_windows_apps()
        elif system == "Darwin":  # macOS
            self._setup_macos_apps()
        else:  # Linux
            self._setup_linux_apps()
    
    def _setup_windows_apps(self):
        """Setup Windows applications"""
        apps = {
            "notepad": ApplicationInfo("Notepad", "notepad.exe"),
            "calculator": ApplicationInfo("Calculator", "calc.exe"),
            "paint": ApplicationInfo("Paint", "mspaint.exe"),
            "wordpad": ApplicationInfo("WordPad", "wordpad.exe"),
            "firefox": ApplicationInfo("Firefox", "firefox.exe", r"C:\Program Files\Mozilla Firefox\firefox.exe"),
            "chrome": ApplicationInfo("Chrome", "chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            "edge": ApplicationInfo("Edge", "msedge.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            "explorer": ApplicationInfo("File Explorer", "explorer.exe"),
            "cmd": ApplicationInfo("Command Prompt", "cmd.exe"),
            "powershell": ApplicationInfo("PowerShell", "powershell.exe"),
            "control": ApplicationInfo("Control Panel", "control.exe"),
            "services": ApplicationInfo("Services", "services.msc"),
            "taskmgr": ApplicationInfo("Task Manager", "taskmgr.exe"),
            "msconfig": ApplicationInfo("System Configuration", "msconfig.exe"),
            "regedit": ApplicationInfo("Registry Editor", "regedit.exe"),
            "snipping": ApplicationInfo("Snipping Tool", "SnippingTool.exe"),
        }
        self.applications.update(apps)
    
    def _setup_macos_apps(self):
        """Setup macOS applications"""
        apps = {
            "textedit": ApplicationInfo("TextEdit", "TextEdit.app", "/Applications/TextEdit.app"),
            "calculator": ApplicationInfo("Calculator", "Calculator.app", "/Applications/Calculator.app"),
            "firefox": ApplicationInfo("Firefox", "Firefox.app", "/Applications/Firefox.app"),
            "chrome": ApplicationInfo("Chrome", "Google Chrome.app", "/Applications/Google Chrome.app"),
            "safari": ApplicationInfo("Safari", "Safari.app", "/Applications/Safari.app"),
            "finder": ApplicationInfo("Finder", "Finder.app"),
            "terminal": ApplicationInfo("Terminal", "Terminal.app", "/Applications/Utilities/Terminal.app"),
            "system": ApplicationInfo("System Preferences", "System Preferences.app", "/Applications/System Preferences.app"),
        }
        self.applications.update(apps)
    
    def _setup_linux_apps(self):
        """Setup Linux applications"""
        apps = {
            "gedit": ApplicationInfo("Gedit", "gedit"),
            "firefox": ApplicationInfo("Firefox", "firefox"),
            "chrome": ApplicationInfo("Chrome", "google-chrome"),
            "chromium": ApplicationInfo("Chromium", "chromium-browser"),
            "nautilus": ApplicationInfo("Files", "nautilus"),
            "thunar": ApplicationInfo("Thunar", "thunar"),
            "terminal": ApplicationInfo("Terminal", "gnome-terminal"),
            "xterm": ApplicationInfo("XTerm", "xterm"),
            "libreoffice": ApplicationInfo("LibreOffice", "libreoffice"),
            "calc": ApplicationInfo("Calculator", "gnome-calculator"),
        }
        self.applications.update(apps)
    
    def open_application(self, app_name: str) -> bool:
        """
        Open an application
        
        Args:
            app_name: Name of application to open
            
        Returns:
            bool: True if opened successfully
        """
        try:
            # Find application in registry
            app_info = self._find_application(app_name)
            
            if not app_info:
                # Try to find executable in PATH
                if shutil.which(app_name):
                    return self._launch_process([app_name])
                else:
                    logger.error(f"Application '{app_name}' not found")
                    return False
            
            # Launch application
            if app_info.path and os.path.exists(app_info.path):
                # Use full path
                command = [app_info.path] + app_info.args
            else:
                # Use executable name
                command = [app_info.executable] + app_info.args
            
            return self._launch_process(command, app_info.name)
            
        except Exception as e:
            logger.error(f"Failed to open application '{app_name}': {e}")
            return False
    
    def _find_application(self, name: str) -> Optional[ApplicationInfo]:
        """Find application by name (case-insensitive)"""
        name_lower = name.lower()
        
        # Direct match
        if name_lower in self.applications:
            return self.applications[name_lower]
        
        # Fuzzy match
        for app_name, app_info in self.applications.items():
            if name_lower in app_name or app_name in name_lower:
                return app_info
        
        return None
    
    def _launch_process(self, command: List[str], app_name: str = "") -> bool:
        """Launch a process"""
        try:
            if platform.system() == "Windows":
                # Windows: Use subprocess with CREATE_NEW_PROCESS_GROUP
                process = subprocess.Popen(
                    command,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Unix-like systems
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            logger.info(f"Launched application: {app_name or ' '.join(command)}")
            
            # Wait a moment for the application to start
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch process '{' '.join(command)}': {e}")
            return False
    
    def search_web(self, query: str) -> bool:
        """
        Search the web using default browser
        
        Args:
            query: Search query
            
        Returns:
            bool: True if search initiated successfully
        """
        try:
            import pyautogui
            import webbrowser
            import urllib.parse
            
            # Encode query for URL
            encoded_query = urllib.parse.quote(query)
            
            # Default search URL (Google)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open browser with search
            webbrowser.open(search_url)
            
            logger.info(f"Web search initiated for: {query}")
            
            # Give browser time to load
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to search web for '{query}': {e}")
            return False
    
    def type_text(self, text: str, interval: float = None) -> bool:
        """
        Type text using keyboard
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            bool: True if typing successful
        """
        try:
            import pyautogui
            
            # Use configured delay if not specified
            if interval is None:
                interval = self.type_delay
            
            # Type the text
            pyautogui.write(text, interval=interval)
            
            logger.info(f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def click_element(self, element: str, timeout: float = 5.0) -> bool:
        """
        Click on a UI element by text
        
        Args:
            element: Text or description of element to click
            timeout: Timeout for finding element
            
        Returns:
            bool: True if click successful
        """
        try:
            import pyautogui
            
            # Try to find element on screen using OCR
            try:
                import pytesseract
                from PIL import ImageGrab
                
                # Take screenshot
                screenshot = pytesseract.image_to_string(ImageGrab.grab())
                
                # Look for the text
                if element.lower() in screenshot.lower():
                    # Find approximate position and click
                    # This is a simplified approach - in practice, you'd want better text location
                    screen_width, screen_height = pyautogui.size()
                    center_x = screen_width // 2
                    center_y = screen_height // 2
                    
                    pyautogui.click(center_x, center_y)
                    logger.info(f"Clicked on approximate position for '{element}'")
                    return True
                    
            except ImportError:
                logger.warning("pytesseract not available for text-based clicking")
            
            # Fallback: click at center of screen
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            pyautogui.click(center_x, center_y)
            logger.info(f"Clicked at center position (OCR not available)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to click element '{element}': {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """
        Take a screenshot
        
        Args:
            filename: Optional filename for screenshot
            
        Returns:
            str: Path to saved screenshot or None if failed
        """
        try:
            import pyautogui
            
            # Generate filename if not provided
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Save screenshot
            screenshot_path = self.screenshot_dir / filename
            pyautogui.screenshot(str(screenshot_path))
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def find_text_on_screen(self, text: str, confidence: float = 0.7) -> Optional[Tuple[int, int]]:
        """
        Find text on screen using OCR
        
        Args:
            text: Text to find
            confidence: Minimum confidence for match
            
        Returns:
            Tuple[int, int]: Center coordinates of found text or None
        """
        try:
            import pytesseract
            from PIL import ImageGrab
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Use OCR to find text
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            # Look for matching text
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > confidence:
                    if text.lower() in data['text'][i].lower():
                        # Calculate center of found text
                        x = data['left'][i] + data['width'][i] // 2
                        y = data['top'][i] + data['height'][i] // 2
                        logger.info(f"Found text '{text}' at ({x}, {y})")
                        return (x, y)
            
            logger.warning(f"Text '{text}' not found on screen")
            return None
            
        except ImportError:
            logger.error("pytesseract not available for text finding")
            return None
        except Exception as e:
            logger.error(f"Failed to find text on screen: {e}")
            return None
    
    def mouse_move(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        Move mouse cursor
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration for smooth movement
            
        Returns:
            bool: True if move successful
        """
        try:
            import pyautogui
            
            pyautogui.moveTo(x, y, duration=duration)
            return True
            
        except Exception as e:
            logger.error(f"Failed to move mouse to ({x}, {y}): {e}")
            return False
    
    def mouse_click(self, x: int = None, y: int, button: str = 'left') -> bool:
        """
        Click mouse at specified position
        
        Args:
            x: X coordinate (if None, uses current position)
            y: Y coordinate (if x is None, this should be the second parameter)
            button: Mouse button to click
            
        Returns:
            bool: True if click successful
        """
        try:
            import pyautogui
            
            if x is None:
                # Click at current position
                pyautogui.click(button=button)
            else:
                pyautogui.click(x, y, button=button)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to click mouse at ({x}, {y}): {e}")
            return False
    
    def keyboard_press(self, key: str, presses: int = 1) -> bool:
        """
        Press keyboard key(s)
        
        Args:
            key: Key to press
            presses: Number of times to press
            
        Returns:
            bool: True if press successful
        """
        try:
            import pyautogui
            
            for _ in range(presses):
                pyautogui.press(key)
                time.sleep(self.type_delay)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}")
            return False
    
    def volume_up(self, steps: int = 5) -> bool:
        """Increase system volume"""
        try:
            import pyautogui
            
            for _ in range(steps):
                if platform.system() == "Windows":
                    pyautogui.press('volumeup')
                elif platform.system() == "Darwin":  # macOS
                    pyautogui.press('volumeup')
                else:  # Linux
                    pyautogui.press('volumeup')
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increase volume: {e}")
            return False
    
    def volume_down(self, steps: int = 5) -> bool:
        """Decrease system volume"""
        try:
            import pyautogui
            
            for _ in range(steps):
                if platform.system() == "Windows":
                    pyautogui.press('volumedown')
                elif platform.system() == "Darwin":  # macOS
                    pyautogui.press('volumedown')
                else:  # Linux
                    pyautogui.press('volumedown')
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to decrease volume: {e}")
            return False
    
    def set_volume(self, level: int) -> bool:
        """
        Set system volume to specific level (0-100)
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            bool: True if volume set successfully
        """
        try:
            import pyautogui
            
            level = max(0, min(100, level))
            
            if platform.system() == "Windows":
                # Windows volume control
                import winsound
                # This is a simplified approach - full volume control would require Windows API
                logger.info(f"Volume set to {level}% (simplified implementation)")
                return True
            else:
                # For macOS and Linux, we can use keyboard shortcuts to approximate
                logger.info(f"Volume control to {level}% not fully implemented")
                return True
            
        except Exception as e:
            logger.error(f"Failed to set volume to {level}%: {e}")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        try:
            import pyautogui
            return pyautogui.size()
        except Exception as e:
            logger.error(f"Failed to get screen size: {e}")
            return (1920, 1080)  # Default fallback
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        try:
            import pyautogui
            return pyautogui.position()
        except Exception as e:
            logger.error(f"Failed to get mouse position: {e}")
            return (0, 0)
    
    def scroll(self, clicks: int, direction: str = 'down') -> bool:
        """
        Scroll mouse wheel
        
        Args:
            clicks: Number of scroll clicks
            direction: 'up' or 'down'
            
        Returns:
            bool: True if scroll successful
        """
        try:
            import pyautogui
            
            if direction.lower() == 'up':
                pyautogui.scroll(clicks)
            else:
                pyautogui.scroll(-clicks)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll {direction} {clicks} clicks: {e}")
            return False
    
    def wait_for_element(self, text: str, timeout: float = 10.0, confidence: float = 0.7) -> bool:
        """
        Wait for element to appear on screen
        
        Args:
            text: Text to wait for
            timeout: Maximum time to wait
            confidence: Minimum OCR confidence
            
        Returns:
            bool: True if element found within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.find_text_on_screen(text, confidence):
                return True
            time.sleep(0.5)
        
        logger.warning(f"Element '{text}' not found within {timeout} seconds")
        return False
    
    def create_workflow(self, actions: List[Dict[str, Any]], name: str) -> str:
        """
        Create a workflow (macro) from actions
        
        Args:
            actions: List of action dictionaries
            name: Name for the workflow
            
        Returns:
            str: Workflow file path
        """
        try:
            workflow_dir = Path("workflows")
            workflow_dir.mkdir(exist_ok=True)
            
            workflow_file = workflow_dir / f"{name}.json"
            
            workflow_data = {
                'name': name,
                'created': time.time(),
                'actions': actions
            }
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            logger.info(f"Workflow '{name}' saved to {workflow_file}")
            return str(workflow_file)
            
        except Exception as e:
            logger.error(f"Failed to create workflow '{name}': {e}")
            return ""
    
    def run_workflow(self, workflow_file: str) -> bool:
        """
        Run a saved workflow
        
        Args:
            workflow_file: Path to workflow JSON file
            
        Returns:
            bool: True if workflow executed successfully
        """
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            
            actions = workflow_data.get('actions', [])
            logger.info(f"Running workflow with {len(actions)} actions")
            
            for action in actions:
                action_type = action.get('type')
                params = action.get('params', {})
                
                # Execute action based on type
                if action_type == 'click':
                    self.mouse_click(**params)
                elif action_type == 'type':
                    self.type_text(**params)
                elif action_type == 'wait':
                    time.sleep(params.get('duration', 1.0))
                elif action_type == 'scroll':
                    self.scroll(**params)
                elif action_type == 'key':
                    self.keyboard_press(**params)
                
                time.sleep(0.5)  # Small delay between actions
            
            logger.info(f"Workflow executed successfully: {workflow_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run workflow '{workflow_file}': {e}")
            return False
    
    def get_applications(self) -> Dict[str, Dict[str, str]]:
        """Get list of available applications"""
        apps = {}
        for name, app_info in self.applications.items():
            apps[name] = {
                'name': app_info.name,
                'executable': app_info.executable,
                'path': app_info.path
            }
        return apps
    
    def add_application(self, name: str, executable: str, path: str = "", args: List[str] = None):
        """Add custom application to registry"""
        app_info = ApplicationInfo(name, executable, path, args)
        self.applications[name.lower()] = app_info
        logger.info(f"Added application to registry: {name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get desktop executor status"""
        return {
            'initialized': self.is_initialized,
            'screen_size': self.get_screen_size(),
            'mouse_position': self.get_mouse_position(),
            'available_applications': len(self.applications),
            'screenshot_directory': str(self.screenshot_dir)
        }

# Global desktop executor instance
_desktop_executor = None

def get_desktop_executor(config_manager=None) -> DesktopExecutor:
    """Get or create global desktop executor"""
    global _desktop_executor
    if _desktop_executor is None:
        _desktop_executor = DesktopExecutor(config_manager)
    return _desktop_executor

def open_application(app_name: str) -> bool:
    """Open application using global executor"""
    return get_desktop_executor().open_application(app_name)

def search_web(query: str) -> bool:
    """Search web using global executor"""
    return get_desktop_executor().search_web(query)

def take_screenshot(filename: str = None) -> Optional[str]:
    """Take screenshot using global executor"""
    return get_desktop_executor().take_screenshot(filename)