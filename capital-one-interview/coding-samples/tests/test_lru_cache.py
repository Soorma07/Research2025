"""
Unit tests for LRU cache module.
Run with: pytest tests/test_lru_cache.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from importlib.machinery import SourceFileLoader

# Load the module with numeric prefix
lru_cache = SourceFileLoader(
    "lru_cache",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "04_lru_cache.py")
).load_module()

LRUCache = lru_cache.LRUCache
LRUCacheSimple = lru_cache.LRUCacheSimple
LFUCache = lru_cache.LFUCache


class TestLRUCache:
    """Test cases for LRU Cache (HashMap + DLL implementation)."""
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = LRUCache(2)
        assert cache.get(1) == -1, "Nonexistent key should return -1"
    
    def test_put_and_get(self):
        """Test basic put and get operations."""
        cache = LRUCache(2)
        cache.put(1, 100)
        assert cache.get(1) == 100, "Should return stored value"
    
    def test_update_existing_key(self):
        """Test updating an existing key."""
        cache = LRUCache(2)
        cache.put(1, 100)
        cache.put(1, 200)
        assert cache.get(1) == 200, "Should return updated value"
    
    def test_eviction_lru(self):
        """Test that LRU item is evicted when capacity is exceeded."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # Access key 1, making key 2 the LRU
        cache.put(3, 3)  # Should evict key 2
        assert cache.get(2) == -1, "Key 2 should be evicted"
        assert cache.get(1) == 1, "Key 1 should still exist"
        assert cache.get(3) == 3, "Key 3 should exist"
    
    def test_capacity_one(self):
        """Test cache with capacity of 1."""
        cache = LRUCache(1)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == -1, "Key 1 should be evicted"
        assert cache.get(2) == 2, "Key 2 should exist"
    
    def test_access_updates_recency(self):
        """Test that get updates the recency of a key."""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # Access key 1
        cache.put(3, 3)  # Should evict key 2, not key 1
        assert cache.get(1) == 1, "Key 1 should still exist"
        assert cache.get(2) == -1, "Key 2 should be evicted"


class TestLRUCacheSimple:
    """Test cases for LRU Cache (OrderedDict implementation)."""
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = LRUCacheSimple(2)
        assert cache.get(1) == -1, "Nonexistent key should return -1"
    
    def test_put_and_get(self):
        """Test basic put and get operations."""
        cache = LRUCacheSimple(2)
        cache.put(1, 100)
        assert cache.get(1) == 100, "Should return stored value"
    
    def test_eviction_lru(self):
        """Test that LRU item is evicted when capacity is exceeded."""
        cache = LRUCacheSimple(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # Access key 1
        cache.put(3, 3)  # Should evict key 2
        assert cache.get(2) == -1, "Key 2 should be evicted"
        assert cache.get(1) == 1, "Key 1 should still exist"


class TestLFUCache:
    """Test cases for LFU Cache."""
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = LFUCache(2)
        assert cache.get(1) == -1, "Nonexistent key should return -1"
    
    def test_put_and_get(self):
        """Test basic put and get operations."""
        cache = LFUCache(2)
        cache.put(1, 100)
        assert cache.get(1) == 100, "Should return stored value"
    
    def test_eviction_lfu(self):
        """Test that least frequently used item is evicted."""
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)  # freq(1) = 2, freq(2) = 1
        cache.put(3, 3)  # Should evict key 2 (lowest frequency)
        assert cache.get(2) == -1, "Key 2 should be evicted (lowest freq)"
        assert cache.get(1) == 1, "Key 1 should still exist"
        assert cache.get(3) == 3, "Key 3 should exist"
    
    def test_eviction_lru_on_tie(self):
        """Test that LRU is evicted when frequencies are tied."""
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        # Both have freq 1, key 1 is older
        cache.put(3, 3)  # Should evict key 1
        assert cache.get(1) == -1, "Key 1 should be evicted (LRU among same freq)"
        assert cache.get(2) == 2, "Key 2 should still exist"
    
    def test_zero_capacity(self):
        """Test cache with zero capacity."""
        cache = LFUCache(0)
        cache.put(1, 1)
        assert cache.get(1) == -1, "Zero capacity cache should not store anything"
    
    def test_update_existing_key(self):
        """Test updating an existing key increases frequency."""
        cache = LFUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(1, 10)  # Update key 1, freq(1) = 2
        cache.put(3, 3)  # Should evict key 2 (freq 1)
        assert cache.get(2) == -1, "Key 2 should be evicted"
        assert cache.get(1) == 10, "Key 1 should have updated value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
