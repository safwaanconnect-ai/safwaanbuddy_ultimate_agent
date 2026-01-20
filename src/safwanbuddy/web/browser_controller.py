from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from src.safwanbuddy.core import logger

class BrowserController:
    def __init__(self, browser_type: str = "chrome"):
        self.browser_type = browser_type.lower()
        self.driver = None

    def launch(self, headless: bool = False):
        try:
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if headless: options.add_argument("--headless")
                self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            elif self.browser_type == "edge":
                options = webdriver.EdgeOptions()
                if headless: options.add_argument("--headless")
                self.driver = webdriver.Edge(service=webdriver.edge.service.Service(EdgeChromiumDriverManager().install()), options=options)
            elif self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if headless: options.add_argument("--headless")
                self.driver = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()), options=options)
            
            logger.info(f"{self.browser_type.capitalize()} browser launched successfully.")
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
