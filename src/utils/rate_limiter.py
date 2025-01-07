import time
from threading import Lock
import logging
from typing import Optional
from collections import deque

class RateLimiter:
    """Rate limiting implementation using token bucket algorithm"""
    
    def __init__(self, requests_per_second: float = 10.0, burst_size: int = 10):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        # Request tracking for adaptive rate limiting
        self.request_history = deque(maxlen=100)
        self.blocked_count = 0
        
    def _add_tokens(self):
        """Add tokens based on elapsed time"""
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * self.requests_per_second
        
        self.tokens = min(self.burst_size, self.tokens + new_tokens)
        self.last_update = now
        
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire a token for making a request"""
        start_time = time.time()
        
        while True:
            with self.lock:
                self._add_tokens()
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    self.request_history.append(time.time())
                    return True
                    
                if timeout is not None:
                    if time.time() - start_time >= timeout:
                        self.blocked_count += 1
                        self.logger.warning("Rate limit exceeded, request blocked")
                        return False
                        
            # Wait before trying again
            time.sleep(1.0 / self.requests_per_second)
            
    def adaptive_rate_adjust(self):
        """Adaptively adjust rate based on response patterns"""
        if len(self.request_history) < 10:
            return
            
        # Calculate request intervals
        intervals = []
        for i in range(1, len(self.request_history)):
            interval = self.request_history[i] - self.request_history[i-1]
            intervals.append(interval)
            
        avg_interval = sum(intervals) / len(intervals)
        
        # Adjust rate if needed
        if self.blocked_count > 5 or avg_interval < 0.1:
            self.requests_per_second *= 0.8  # Reduce rate by 20%
            self.blocked_count = 0
            self.logger.info(f"Adjusting rate limit to {self.requests_per_second} req/s") 