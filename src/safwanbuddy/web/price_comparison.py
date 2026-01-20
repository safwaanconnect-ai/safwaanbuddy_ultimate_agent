from .browser_controller import browser_controller
from .web_scraper import web_scraper
from src.safwanbuddy.core import logger, event_bus

class PriceComparison:
    def __init__(self):
        self.sites = {
            "amazon": "https://www.amazon.com/s?k=",
            "ebay": "https://www.ebay.com/sch/i.html?_nkw="
        }

    def compare_prices(self, product_name: str):
        logger.info(f"Comparing prices for: {product_name}")
        event_bus.emit("system_log", f"Price Comparison: {product_name}")
        
        results = []
        for site, url in self.sites.items():
            full_url = f"{url}{product_name.replace(' ', '+')}"
            logger.info(f"Scraping {site}...")
            # In a real scenario, we would use Selenium or requests
            # For now, we'll mock the result
            results.append({"site": site, "price": "$199.99", "url": full_url})
        
        event_bus.emit("system_log", f"Results: {results}")
        return results

price_comparison = PriceComparison()
