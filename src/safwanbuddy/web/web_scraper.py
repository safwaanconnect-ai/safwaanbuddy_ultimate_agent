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

    def scrape_to_csv(self, url: str, selector: str, filename: str):
        """Scrapes data from a selector and saves to CSV."""
        soup = self.scrape_url(url)
        if not soup:
            return False
            
        elements = soup.select(selector)
        data = [el.get_text(strip=True) for el in elements]
        
        import pandas as pd
        df = pd.DataFrame(data, columns=["Extracted Data"])
        df.to_csv(filename, index=False)
        logger.info(f"Scraped data saved to {filename}")
        return True

    def scrape_table(self, url: str, table_index: int = 0):
        """Scrapes a table from URL using pandas."""
        import pandas as pd
        try:
            dfs = pd.read_html(url)
            if dfs:
                return dfs[table_index]
        except Exception as e:
            logger.error(f"Error scraping table from {url}: {e}")
        return None

web_scraper = WebScraper()
