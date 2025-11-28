"""
HTTP client utilities for web scraping.
"""
import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import settings


class HTTPClient:
    """Simple HTTP client with retry logic and rate limiting."""
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: int = None,
        max_retries: int = None
    ):
        self.user_agent = user_agent or settings.DEFAULT_USER_AGENT
        self.timeout = timeout or settings.DEFAULT_TIMEOUT
        self.max_retries = max_retries or settings.DEFAULT_RETRIES
        
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configure session with retry strategy."""
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({'User-Agent': self.user_agent})
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request."""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make POST request."""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close session."""
        self.session.close()

