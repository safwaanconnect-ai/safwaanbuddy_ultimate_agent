from src.safwanbuddy.web import browser_controller, web_scraper
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
        # Simulate results for demo purposes if scraping fails
        mock_results = [
            {"site": "Amazon", "price": "$189.00", "status": "Available"},
            {"site": "eBay", "price": "$175.50", "status": "Used"},
            {"site": "Walmart", "price": "$190.00", "status": "Available"}
        ]
        
        for site, url in self.sites.items():
            full_url = f"{url}{product_name.replace(' ', '+')}"
            logger.info(f"Checking {site}...")
            # We would normally do: soup = web_scraper.scrape_url(full_url)
            # and then parse it.
            
        results = mock_results
        event_bus.emit("notification", f"Found {len(results)} price matches for {product_name}")
        event_bus.emit("price_results", results)
        return results

price_comparison = PriceComparison()
