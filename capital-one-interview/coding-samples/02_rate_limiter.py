"""
Capital One Coding Sample: API Rate Limiter

This problem tests your understanding of:
- System design concepts at a code level
- Time-based data structures
- Thread safety considerations
- Clean API design

Problem: Implement a rate limiter that allows at most N requests per user
within a sliding window of T seconds.

Requirements:
1. is_allowed(user_id) -> bool: Returns True if request is allowed
2. Should handle high throughput
3. Memory efficient (don't store all requests forever)
"""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Deque
import heapq


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter using a deque to track request timestamps.
    
    Time Complexity: O(1) amortized for is_allowed
    Space Complexity: O(max_requests * num_users)
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: Dict[str, Deque[float]] = defaultdict(deque)
        self.locks: Dict[str, Lock] = defaultdict(Lock)
    
    def is_allowed(self, user_id: str) -> bool:
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        with self.locks[user_id]:
            requests = self.user_requests[user_id]
            
            # Remove expired requests
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Check if under limit
            if len(requests) < self.max_requests:
                requests.append(current_time)
                return True
            
            return False
    
    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests allowed in current window."""
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        with self.locks[user_id]:
            requests = self.user_requests[user_id]
            
            # Count valid requests
            valid_count = sum(1 for t in requests if t >= window_start)
            return max(0, self.max_requests - valid_count)


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter - allows bursts up to bucket capacity.
    
    This is commonly used in production systems like AWS API Gateway.
    
    Time Complexity: O(1) for is_allowed
    Space Complexity: O(num_users)
    """
    
    def __init__(self, bucket_capacity: int, refill_rate: float):
        """
        Args:
            bucket_capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.bucket_capacity = bucket_capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, float] = {}
        self.last_refill: Dict[str, float] = {}
        self.locks: Dict[str, Lock] = defaultdict(Lock)
    
    def is_allowed(self, user_id: str) -> bool:
        current_time = time.time()
        
        with self.locks[user_id]:
            # Initialize bucket if new user
            if user_id not in self.buckets:
                self.buckets[user_id] = self.bucket_capacity
                self.last_refill[user_id] = current_time
            
            # Refill tokens based on elapsed time
            elapsed = current_time - self.last_refill[user_id]
            self.buckets[user_id] = min(
                self.bucket_capacity,
                self.buckets[user_id] + elapsed * self.refill_rate
            )
            self.last_refill[user_id] = current_time
            
            # Check if token available
            if self.buckets[user_id] >= 1:
                self.buckets[user_id] -= 1
                return True
            
            return False


class LeakyBucketRateLimiter:
    """
    Leaky bucket rate limiter - processes requests at a constant rate.
    
    Good for smoothing out bursty traffic.
    """
    
    def __init__(self, bucket_capacity: int, leak_rate: float):
        """
        Args:
            bucket_capacity: Maximum requests that can be queued
            leak_rate: Requests processed per second
        """
        self.bucket_capacity = bucket_capacity
        self.leak_rate = leak_rate
        self.buckets: Dict[str, float] = defaultdict(float)
        self.last_leak: Dict[str, float] = {}
        self.locks: Dict[str, Lock] = defaultdict(Lock)
    
    def is_allowed(self, user_id: str) -> bool:
        current_time = time.time()
        
        with self.locks[user_id]:
            # Initialize if new user
            if user_id not in self.last_leak:
                self.last_leak[user_id] = current_time
            
            # Leak water based on elapsed time
            elapsed = current_time - self.last_leak[user_id]
            leaked = elapsed * self.leak_rate
            self.buckets[user_id] = max(0, self.buckets[user_id] - leaked)
            self.last_leak[user_id] = current_time
            
            # Try to add request to bucket
            if self.buckets[user_id] < self.bucket_capacity:
                self.buckets[user_id] += 1
                return True
            
            return False


class FixedWindowRateLimiter:
    """
    Fixed window rate limiter - simpler but can allow 2x requests at window boundaries.
    
    Time Complexity: O(1)
    Space Complexity: O(num_users)
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows: Dict[str, Dict[int, int]] = defaultdict(dict)
        self.locks: Dict[str, Lock] = defaultdict(Lock)
    
    def _get_window_key(self, timestamp: float) -> int:
        return int(timestamp // self.window_seconds)
    
    def is_allowed(self, user_id: str) -> bool:
        current_time = time.time()
        window_key = self._get_window_key(current_time)
        
        with self.locks[user_id]:
            user_windows = self.windows[user_id]
            
            # Clean up old windows
            old_keys = [k for k in user_windows if k < window_key - 1]
            for k in old_keys:
                del user_windows[k]
            
            # Get current count
            current_count = user_windows.get(window_key, 0)
            
            if current_count < self.max_requests:
                user_windows[window_key] = current_count + 1
                return True
            
            return False


# Test cases
def test_rate_limiters():
    print("Testing Sliding Window Rate Limiter...")
    limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
    
    # Should allow first 5 requests
    for i in range(5):
        assert limiter.is_allowed("user1"), f"Request {i+1} should be allowed"
    
    # 6th request should be denied
    assert not limiter.is_allowed("user1"), "6th request should be denied"
    
    # Different user should be allowed
    assert limiter.is_allowed("user2"), "Different user should be allowed"
    
    print("Sliding Window tests passed!")
    
    print("\nTesting Token Bucket Rate Limiter...")
    token_limiter = TokenBucketRateLimiter(bucket_capacity=10, refill_rate=1.0)
    
    # Should allow burst of 10
    for i in range(10):
        assert token_limiter.is_allowed("user1"), f"Burst request {i+1} should be allowed"
    
    # 11th should be denied
    assert not token_limiter.is_allowed("user1"), "11th request should be denied"
    
    # Wait for refill
    time.sleep(1.1)
    assert token_limiter.is_allowed("user1"), "Should be allowed after refill"
    
    print("Token Bucket tests passed!")
    
    print("\nAll rate limiter tests passed!")


if __name__ == "__main__":
    test_rate_limiters()
