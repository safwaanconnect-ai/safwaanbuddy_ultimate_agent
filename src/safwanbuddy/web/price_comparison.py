from src.safwanbuddy.web.web_scraper import web_scraper
from src.safwanbuddy.core import logger, event_bus
import pandas as pd

class PriceComparison:
    def __init__(self):
        self.sources = {
            "Amazon": "https://www.amazon.in/s?k=",
            "Flipkart": "https://www.flipkart.com/search?q="
        }

    def compare_prices(self, product_name: str):
        logger.info(f"Comparing prices for: {product_name}")
        results = []
        
        for site, base_url in self.sources.items():
            url = f"{base_url}{product_name.replace(' ', '+')}"
            logger.info(f"Checking {site}...")
            # In a real scenario, we'd need more sophisticated scraping or APIs
            # Mocking results for demonstration if scraping fails
            results.append({
                "Site": site,
                "Product": product_name,
                "Price": "Check Website",
                "Link": url
            })
            
        df = pd.DataFrame(results)
        event_bus.emit("system_log", f"Price comparison complete for {product_name}")
        # Could save to Excel
        from src.safwanbuddy.documents.excel_generator import excel_generator
        excel_generator.create_spreadsheet([df.columns.tolist()] + df.values.tolist(), f"price_compare_{product_name.replace(' ', '_')}.xlsx")
        
        return results

price_comparison = PriceComparison()
