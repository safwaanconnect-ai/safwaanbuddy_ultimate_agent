"""Selenium wrapper for browser automation."""

import logging
from typing import Optional, List
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available, browser automation disabled")

from ..core.events import EventBus, EventType
from ..core.config import ConfigManager


class BrowserController:
    """Browser automation controller."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
    
    def start_browser(self, browser: str = "chrome", headless: bool = False) -> bool:
        """Start browser.
        
        Args:
            browser: Browser type (chrome, firefox, edge)
            headless: Run in headless mode
            
        Returns:
            True if successful
        """
        if not SELENIUM_AVAILABLE:
            self.logger.error("Selenium not available")
            return False
        
        if self.driver:
            self.logger.warning("Browser already running")
            return True
        
        try:
            if browser == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                self.driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                
                self.driver = webdriver.Firefox(options=options)
            elif browser == "edge":
                options = webdriver.EdgeOptions()
                if headless:
                    options.add_argument("--headless")
                
                self.driver = webdriver.Edge(options=options)
            else:
                self.logger.error(f"Unknown browser: {browser}")
                return False
            
            timeout = self.config.get("browser.timeout", 30)
            self.wait = WebDriverWait(self.driver, timeout)
            
            window_size = self.config.get("browser.window_size", [1920, 1080])
            self.driver.set_window_size(*window_size)
            
            self.event_bus.emit(EventType.BROWSER_OPENED, {"browser": browser})
            self.logger.info(f"Browser started: {browser}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            return False
    
    def close_browser(self) -> None:
        """Close browser."""
        if self.driver:
            try:
                self.driver.quit()
                self.event_bus.emit(EventType.BROWSER_CLOSED, {})
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate(self, url: str) -> bool:
        """Navigate to URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        if not self.driver:
            self.logger.error("Browser not started")
            return False
        
        try:
            self.driver.get(url)
            self.event_bus.emit(EventType.PAGE_LOADED, {"url": url})
            self.logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
    
    def find_element(self, selector: str, by: str = "css") -> Optional[any]:
        """Find element on page.
        
        Args:
            selector: Element selector
            by: Selection method (css, xpath, id, name, class)
            
        Returns:
            Element or None
        """
        if not self.driver:
            return None
        
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        
        try:
            element = self.wait.until(
                EC.presence_of_element_located((by_map.get(by, By.CSS_SELECTOR), selector))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found: {selector}")
            return None
    
    def click_element(self, selector: str, by: str = "css") -> bool:
        """Click element.
        
        Args:
            selector: Element selector
            by: Selection method
            
        Returns:
            True if successful
        """
        element = self.find_element(selector, by)
        
        if element:
            try:
                element.click()
                self.logger.info(f"Clicked element: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Click failed: {e}")
                return False
        
        return False
    
    def type_text(self, selector: str, text: str, by: str = "css", clear_first: bool = True) -> bool:
        """Type text into element.
        
        Args:
            selector: Element selector
            text: Text to type
            by: Selection method
            clear_first: Clear field first
            
        Returns:
            True if successful
        """
        element = self.find_element(selector, by)
        
        if element:
            try:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.info(f"Typed text into: {selector}")
                return True
            except Exception as e:
                self.logger.error(f"Type failed: {e}")
                return False
        
        return False
    
    def get_text(self, selector: str, by: str = "css") -> str:
        """Get element text.
        
        Args:
            selector: Element selector
            by: Selection method
            
        Returns:
            Element text
        """
        element = self.find_element(selector, by)
        
        if element:
            return element.text
        
        return ""
    
    def execute_script(self, script: str) -> any:
        """Execute JavaScript.
        
        Args:
            script: JavaScript code
            
        Returns:
            Script result
        """
        if not self.driver:
            return None
        
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            return None
    
    def take_screenshot(self, filepath: Path) -> bool:
        """Take screenshot.
        
        Args:
            filepath: Output file path
            
        Returns:
            True if successful
        """
        if not self.driver:
            return False
        
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            self.driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False
    
    @property
    def current_url(self) -> str:
        """Get current URL."""
        if self.driver:
            return self.driver.current_url
        return ""
    
    @property
    def page_title(self) -> str:
        """Get page title."""
        if self.driver:
            return self.driver.title
        return ""
