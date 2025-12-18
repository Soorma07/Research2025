"""
Unit tests for rate limiter module.
Run with: pytest tests/test_rate_limiter.py -v
"""

import pytest
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
rate_limiter = SourceFileLoader(
    "rate_limiter",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "02_rate_limiter.py")
).load_module()

SlidingWindowRateLimiter = rate_limiter.SlidingWindowRateLimiter
TokenBucketRateLimiter = rate_limiter.TokenBucketRateLimiter
LeakyBucketRateLimiter = rate_limiter.LeakyBucketRateLimiter
FixedWindowRateLimiter = rate_limiter.FixedWindowRateLimiter


class TestSlidingWindowRateLimiter:
    """Test cases for sliding window rate limiter."""
    
    def test_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
        for i in range(5):
            assert limiter.is_allowed("user1"), f"Request {i+1} should be allowed"
    
    def test_denies_requests_over_limit(self):
        """Test that requests over the limit are denied."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
        for _ in range(5):
            limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1"), "6th request should be denied"
    
    def test_different_users_independent(self):
        """Test that different users have independent limits."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10)
        assert limiter.is_allowed("user1")
        assert limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1"), "user1 should be rate limited"
        assert limiter.is_allowed("user2"), "user2 should be allowed"
    
    def test_get_remaining(self):
        """Test getting remaining requests."""
        limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)
        assert limiter.get_remaining("user1") == 5
        limiter.is_allowed("user1")
        assert limiter.get_remaining("user1") == 4
    
    def test_window_expiry(self):
        """Test that requests are allowed after window expires."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed("user1")
        assert limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1")
        time.sleep(1.1)  # Wait for window to expire
        assert limiter.is_allowed("user1"), "Should be allowed after window expires"


class TestTokenBucketRateLimiter:
    """Test cases for token bucket rate limiter."""
    
    def test_allows_burst(self):
        """Test that burst up to capacity is allowed."""
        limiter = TokenBucketRateLimiter(bucket_capacity=10, refill_rate=1.0)
        for i in range(10):
            assert limiter.is_allowed("user1"), f"Burst request {i+1} should be allowed"
    
    def test_denies_after_burst(self):
        """Test that requests after burst are denied."""
        limiter = TokenBucketRateLimiter(bucket_capacity=10, refill_rate=1.0)
        for _ in range(10):
            limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1"), "11th request should be denied"
    
    def test_refill(self):
        """Test that tokens refill over time."""
        limiter = TokenBucketRateLimiter(bucket_capacity=2, refill_rate=2.0)
        assert limiter.is_allowed("user1")
        assert limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1")
        time.sleep(0.6)  # Wait for ~1 token to refill
        assert limiter.is_allowed("user1"), "Should be allowed after refill"
    
    def test_different_users_independent(self):
        """Test that different users have independent buckets."""
        limiter = TokenBucketRateLimiter(bucket_capacity=1, refill_rate=0.1)
        assert limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1")
        assert limiter.is_allowed("user2"), "user2 should have full bucket"


class TestLeakyBucketRateLimiter:
    """Test cases for leaky bucket rate limiter."""
    
    def test_allows_under_capacity(self):
        """Test that requests under capacity are allowed."""
        limiter = LeakyBucketRateLimiter(bucket_capacity=5, leak_rate=0.0)
        for i in range(5):
            assert limiter.is_allowed("user1"), f"Request {i+1} should be allowed"
    
    def test_denies_over_capacity(self):
        """Test that requests over capacity are denied."""
        limiter = LeakyBucketRateLimiter(bucket_capacity=3, leak_rate=0.0)
        for _ in range(3):
            limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1"), "Request over capacity should be denied"
    
    def test_leak_allows_new_requests(self):
        """Test that leaking allows new requests over time."""
        limiter = LeakyBucketRateLimiter(bucket_capacity=2, leak_rate=10.0)
        assert limiter.is_allowed("user1")
        assert limiter.is_allowed("user1")
        time.sleep(0.3)  # Wait for bucket to leak (10.0 * 0.3 = 3.0 leaked)
        assert limiter.is_allowed("user1"), "Should be allowed after leak"
        assert limiter.is_allowed("user1"), "Should be allowed after leak"


class TestFixedWindowRateLimiter:
    """Test cases for fixed window rate limiter."""
    
    def test_allows_under_limit(self):
        """Test that requests under limit are allowed."""
        limiter = FixedWindowRateLimiter(max_requests=5, window_seconds=10)
        for i in range(5):
            assert limiter.is_allowed("user1"), f"Request {i+1} should be allowed"
    
    def test_denies_over_limit(self):
        """Test that requests over limit are denied."""
        limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=10)
        for _ in range(3):
            limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1"), "4th request should be denied"
    
    def test_new_window_resets_count(self):
        """Test that new window resets the count."""
        limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=1)
        assert limiter.is_allowed("user1")
        assert limiter.is_allowed("user1")
        assert not limiter.is_allowed("user1")
        time.sleep(1.1)  # Wait for new window
        assert limiter.is_allowed("user1"), "Should be allowed in new window"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
