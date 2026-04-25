import requests
from bs4 import BeautifulSoup
from src.safwanbuddy.core import logger

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })

    def scrape_url(self, url: str, retries: int = 3):
        for i in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return BeautifulSoup(response.text, 'html.parser')
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden for {url}. Attempt {i+1}/{retries}")
                else:
                    logger.error(f"Failed to scrape {url}: Status {response.status_code}")
            except Exception as e:
                logger.error(f"Error scraping {url} on attempt {i+1}: {e}")
            import time
            time.sleep(1)
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
