"""Data extraction and summary generation."""

import logging
from typing import List, Dict, Optional

try:
    from bs4 import BeautifulSoup
    import requests
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup not available")

from ..core.config import ConfigManager


class WebScraper:
    """Web scraping and data extraction."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
    
    def scrape_url(self, url: str) -> Optional[str]:
        """Scrape URL content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Page content or None
        """
        if not BS4_AVAILABLE:
            self.logger.error("BeautifulSoup not available")
            return None
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Failed to scrape URL: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract text from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        if not BS4_AVAILABLE:
            return ""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
    
    def extract_links(self, html: str, base_url: str = "") -> List[str]:
        """Extract links from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL for relative links
            
        Returns:
            List of URLs
        """
        if not BS4_AVAILABLE:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append(href)
                elif base_url:
                    links.append(base_url.rstrip('/') + '/' + href.lstrip('/'))
            
            return links
        except Exception as e:
            self.logger.error(f"Link extraction failed: {e}")
            return []
