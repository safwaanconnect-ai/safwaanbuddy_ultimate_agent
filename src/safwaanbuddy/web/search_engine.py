"""Multi-search-engine integration."""

import logging
from typing import List, Dict
from urllib.parse import quote_plus

from ..core.config import ConfigManager
from ..core.events import EventBus, EventType
from .browser_controller import BrowserController


class SearchEngine:
    """Multi-search engine integration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        self.browser = BrowserController()
        
        self.engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}"
        }
    
    def search(self, query: str, engine: str = None) -> bool:
        """Perform web search.
        
        Args:
            query: Search query
            engine: Search engine (uses default if None)
            
        Returns:
            True if successful
        """
        if engine is None:
            engine = self.config.get("search.default_engine", "google")
        
        if engine not in self.engines:
            self.logger.error(f"Unknown search engine: {engine}")
            return False
        
        url = self.engines[engine].format(quote_plus(query))
        
        if not self.browser.driver:
            self.browser.start_browser()
        
        result = self.browser.navigate(url)
        
        if result:
            self.event_bus.emit(EventType.SEARCH_PERFORMED, {
                "query": query,
                "engine": engine
            })
        
        return result
