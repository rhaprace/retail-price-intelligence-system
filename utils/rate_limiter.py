"""
Rate limiting utilities.
"""
import time
from typing import Dict
from collections import defaultdict


class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request: Dict[str, float] = defaultdict(float)
    
    def wait_if_needed(self, key: str = 'default'):
        """Wait if needed to respect rate limit."""
        now = time.time()
        last = self.last_request[key]
        elapsed = now - last
        
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
        
        self.last_request[key] = time.time()
    
    def reset(self, key: str = 'default'):
        """Reset rate limiter for a key."""
        self.last_request[key] = 0.0

