"""
Capital One Coding Sample: LRU Cache Implementation

This is a fundamental data structure question that tests:
- Understanding of cache eviction policies
- Combining hash maps with doubly linked lists
- O(1) time complexity requirements
- Clean API design

LeetCode 146: LRU Cache
"""

from collections import OrderedDict
from typing import Optional, Dict


class ListNode:
    """Doubly linked list node for LRU Cache."""
    
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev: Optional['ListNode'] = None
        self.next: Optional['ListNode'] = None


class LRUCache:
    """
    LRU Cache implementation using HashMap + Doubly Linked List.
    
    Time Complexity: O(1) for both get and put
    Space Complexity: O(capacity)
    
    The doubly linked list maintains access order (most recent at head).
    The hash map provides O(1) lookup by key.
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[int, ListNode] = {}
        
        # Dummy head and tail for easier list manipulation
        self.head = ListNode()
        self.tail = ListNode()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node: ListNode) -> None:
        """Add node right after head (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node: ListNode) -> None:
        """Remove node from its current position."""
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _move_to_head(self, node: ListNode) -> None:
        """Move existing node to head (mark as most recently used)."""
        self._remove_node(node)
        self._add_to_head(node)
    
    def _pop_tail(self) -> ListNode:
        """Remove and return the least recently used node."""
        lru = self.tail.prev
        self._remove_node(lru)
        return lru
    
    def get(self, key: int) -> int:
        """
        Get value by key. Returns -1 if not found.
        Marks the key as recently used.
        """
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair.
        Evicts LRU item if at capacity.
        """
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                lru = self._pop_tail()
                del self.cache[lru.key]
            
            new_node = ListNode(key, value)
            self.cache[key] = new_node
            self._add_to_head(new_node)


class LRUCacheSimple:
    """
    Simplified LRU Cache using Python's OrderedDict.
    
    Good for interviews where you need to implement quickly,
    but be prepared to explain the underlying data structure.
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # Remove oldest (first) item
            self.cache.popitem(last=False)


class LFUCache:
    """
    LFU (Least Frequently Used) Cache - a harder variant.
    
    Evicts the least frequently used item. If tie, evicts LRU among them.
    
    Time Complexity: O(1) for both get and put
    Space Complexity: O(capacity)
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_val: Dict[int, int] = {}
        self.key_to_freq: Dict[int, int] = {}
        self.freq_to_keys: Dict[int, OrderedDict] = {}
    
    def _update_freq(self, key: int) -> None:
        """Increment frequency of key and update data structures."""
        freq = self.key_to_freq[key]
        self.key_to_freq[key] = freq + 1
        
        # Remove from current frequency list
        del self.freq_to_keys[freq][key]
        
        # Update min_freq if needed
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq = freq + 1
        
        # Add to new frequency list
        if freq + 1 not in self.freq_to_keys:
            self.freq_to_keys[freq + 1] = OrderedDict()
        self.freq_to_keys[freq + 1][key] = None
    
    def get(self, key: int) -> int:
        if key not in self.key_to_val:
            return -1
        
        self._update_freq(key)
        return self.key_to_val[key]
    
    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        
        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._update_freq(key)
            return
        
        # Evict if at capacity
        if len(self.key_to_val) >= self.capacity:
            # Get LRU key among min frequency
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
        
        # Add new key
        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.min_freq = 1
        
        if 1 not in self.freq_to_keys:
            self.freq_to_keys[1] = OrderedDict()
        self.freq_to_keys[1][key] = None


# Test cases
def test_lru_cache():
    print("Testing LRU Cache (HashMap + DLL)...")
    cache = LRUCache(2)
    
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1, "Should return 1"
    
    cache.put(3, 3)  # Evicts key 2
    assert cache.get(2) == -1, "Key 2 should be evicted"
    
    cache.put(4, 4)  # Evicts key 1
    assert cache.get(1) == -1, "Key 1 should be evicted"
    assert cache.get(3) == 3, "Should return 3"
    assert cache.get(4) == 4, "Should return 4"
    
    print("LRU Cache tests passed!")
    
    print("\nTesting LRU Cache (OrderedDict)...")
    cache_simple = LRUCacheSimple(2)
    
    cache_simple.put(1, 1)
    cache_simple.put(2, 2)
    assert cache_simple.get(1) == 1
    cache_simple.put(3, 3)
    assert cache_simple.get(2) == -1
    
    print("LRU Cache (OrderedDict) tests passed!")
    
    print("\nTesting LFU Cache...")
    lfu = LFUCache(2)
    
    lfu.put(1, 1)
    lfu.put(2, 2)
    assert lfu.get(1) == 1  # freq(1) = 2
    
    lfu.put(3, 3)  # Evicts key 2 (freq 1, LRU)
    assert lfu.get(2) == -1
    assert lfu.get(3) == 3  # freq(3) = 2
    
    lfu.put(4, 4)  # Evicts key 1 or 3? Key 1 has freq 2, key 3 has freq 2
                   # Key 1 was accessed earlier, so evict key 1
    assert lfu.get(1) == -1
    assert lfu.get(3) == 3
    assert lfu.get(4) == 4
    
    print("LFU Cache tests passed!")
    
    print("\nAll cache tests passed!")


if __name__ == "__main__":
    test_lru_cache()
