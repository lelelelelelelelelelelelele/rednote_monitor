from .base import Scraper
from .manual import ManualScraper
from .xhs_mcp import XhsMcpScraper
from .fallback import FallbackScraper

__all__ = ["Scraper", "ManualScraper", "XhsMcpScraper", "FallbackScraper"]
