import requests
from bs4 import BeautifulSoup
from src.safwanbuddy.core import logger

class WebScraper:
    def __init__(self):
        pass

    def scrape_url(self, url: str):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                logger.error(f"Failed to scrape {url}: Status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def extract_text(self, soup: BeautifulSoup):
        if soup:
            return soup.get_text()
        return ""

web_scraper = WebScraper()
