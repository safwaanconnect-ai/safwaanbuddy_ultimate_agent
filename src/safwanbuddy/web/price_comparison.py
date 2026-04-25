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
        
        # Real-ish selectors for demonstration
        selectors = {
            "Amazon": {"price": "span.a-price-whole", "title": "span.a-size-medium"},
            "Flipkart": {"price": "div._30jeq3", "title": "div._4rR01T"}
        }

        for site, base_url in self.sources.items():
            search_url = f"{base_url}{product_name.replace(' ', '+')}"
            logger.info(f"Checking {site}...")
            
            soup = web_scraper.scrape_url(search_url)
            price = "N/A"
            title = product_name
            
            if soup:
                sel = selectors.get(site)
                price_el = soup.select_one(sel["price"])
                title_el = soup.select_one(sel["title"])
                
                if price_el: price = price_el.get_text(strip=True)
                if title_el: title = title_el.get_text(strip=True)

            results.append({
                "Site": site,
                "Product": title,
                "Price": price,
                "Link": search_url
            })
            
        df = pd.DataFrame(results)
        event_bus.emit("system_log", f"Price comparison complete for {product_name}")
        
        try:
            from src.safwanbuddy.documents.excel_generator import excel_generator
            excel_generator.create_spreadsheet([df.columns.tolist()] + df.values.tolist(), f"price_compare_{product_name.replace(' ', '_')}.xlsx")
        except Exception as e:
            logger.error(f"Failed to generate excel report: {e}")
        
        return results

price_comparison = PriceComparison()
