from src.safwanbuddy.web.browser_controller import browser_controller
from src.safwanbuddy.web.web_scraper import web_scraper
from src.safwanbuddy.core import logger, event_bus

class SearchEngine:
    def __init__(self):
        self.engines = {
            "google": "https://www.google.com/search?q=",
            "bing": "https://www.bing.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q="
        }

    def search(self, query: str, engine: str = "google", open_browser: bool = True):
        base_url = self.engines.get(engine.lower(), self.engines["google"])
        url = f"{base_url}{query.replace(' ', '+')}"
        
        if open_browser:
            browser_controller.open_url(url)
            event_bus.emit("system_log", f"Search performed for: {query}")
        
        return url

    def get_top_links(self, query: str, num_results: int = 5):
        """Fetches top links for a query using scraping."""
        url = self.search(query, open_browser=False)
        soup = web_scraper.scrape_url(url)
        if not soup:
            return []
        
        links = []
        # Basic Google search result scraping
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text if g.find('h3') else link
                links.append({"title": title, "link": link})
                if len(links) >= num_results:
                    break
        return links

search_engine = SearchEngine()
