from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from src.safwanbuddy.core.logging import logger

class BrowserController:
    def __init__(self, browser_type: str = "chrome"):
        self.browser_type = browser_type.lower()
        self.driver = None

    def launch(self, headless: bool = False):
        try:
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                logger.info("Chrome browser launched successfully.")
            # Add Firefox, Edge support here
        except Exception as e:
            logger.error(f"Failed to launch browser: {e}")

    def open_url(self, url: str):
        if self.driver:
            self.driver.get(url)
        else:
            logger.error("Browser not launched.")

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

browser_controller = BrowserController()
