from src.safwanbuddy.web import browser_controller

class SearchEngine:
    def __init__(self):
        self.engines = {
            "google": "https://www.google.com/search?q=",
            "bing": "https://www.bing.com/search?q=",
            "duckduckgo": "https://duckduckgo.com/?q="
        }

    def search(self, query: str, engine: str = "google"):
        base_url = self.engines.get(engine.lower(), self.engines["google"])
        url = f"{base_url}{query.replace(' ', '+')}"
        browser_controller.open_url(url)

search_engine = SearchEngine()
