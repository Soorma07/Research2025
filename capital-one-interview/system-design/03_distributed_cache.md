# System Design: Distributed Caching System

This is a foundational system design topic that often comes up in Capital One interviews, especially for backend roles where performance is critical.

## Problem Statement

Design a distributed caching system that can be used across multiple services in a financial services environment.

**Functional Requirements:**
1. Key-value storage with TTL support
2. Support for various data types (strings, hashes, lists, sets)
3. Cache invalidation mechanisms
4. Support for cache-aside, write-through, and write-behind patterns
5. Pub/sub for cache invalidation events

**Non-Functional Requirements:**
1. Sub-millisecond read latency (P99 < 1ms)
2. High availability (99.99%)
3. Horizontal scalability to petabytes
4. Strong consistency within a partition
5. Graceful degradation under load

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │ Service A    │    │ Service B    │    │ Service C    │                  │
│   │ (Cache Client)│   │ (Cache Client)│   │ (Cache Client)│                 │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│          │                   │                   │                          │
│          └───────────────────┼───────────────────┘                          │
│                              │                                              │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────────────────┐
│                              │     Cache Proxy Layer                        │
├──────────────────────────────┼──────────────────────────────────────────────┤
│                              │                                              │
│          ┌───────────────────┼───────────────────┐                          │
│          │                   │                   │                          │
│   ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐                   │
│   │ Proxy Node  │     │ Proxy Node  │     │ Proxy Node  │                   │
│   │ (Routing)   │     │ (Routing)   │     │ (Routing)   │                   │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                   │
│          │                   │                   │                          │
└──────────┼───────────────────┼───────────────────┼──────────────────────────┘
           │                   │                   │
┌──────────┼───────────────────┼───────────────────┼──────────────────────────┐
│          │                   │     Cache Cluster │                          │
├──────────┼───────────────────┼───────────────────┼──────────────────────────┤
│          │                   │                   │                          │
│   ┌──────▼──────┐     ┌──────▼──────┐     ┌──────▼──────┐                   │
│   │ Shard 1     │     │ Shard 2     │     │ Shard 3     │                   │
│   │ Primary     │     │ Primary     │     │ Primary     │                   │
│   │      │      │     │      │      │     │      │      │                   │
│   │      ▼      │     │      ▼      │     │      ▼      │                   │
│   │ Replica 1   │     │ Replica 1   │     │ Replica 1   │                   │
│   │ Replica 2   │     │ Replica 2   │     │ Replica 2   │                   │
│   └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Consistent Hashing for Data Distribution

```python
import hashlib
from bisect import bisect_left
from typing import List, Dict, Optional


class ConsistentHash:
    """
    Consistent hashing implementation for cache key distribution.
    
    Uses virtual nodes to ensure even distribution across physical nodes.
    """
    
    def __init__(self, nodes: List[str] = None, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: List[int] = []
        self.ring_to_node: Dict[int, str] = {}
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """Generate hash for a key."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str) -> None:
        """Add a node to the hash ring."""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            
            # Insert in sorted order
            idx = bisect_left(self.ring, hash_value)
            self.ring.insert(idx, hash_value)
            self.ring_to_node[hash_value] = node
    
    def remove_node(self, node: str) -> None:
        """Remove a node from the hash ring."""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            
            if hash_value in self.ring_to_node:
                self.ring.remove(hash_value)
                del self.ring_to_node[hash_value]
    
    def get_node(self, key: str) -> Optional[str]:
        """Get the node responsible for a key."""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        idx = bisect_left(self.ring, hash_value)
        
        # Wrap around if past the end
        if idx >= len(self.ring):
            idx = 0
        
        return self.ring_to_node[self.ring[idx]]
    
    def get_nodes(self, key: str, count: int = 3) -> List[str]:
        """Get multiple nodes for replication."""
        if not self.ring:
            return []
        
        hash_value = self._hash(key)
        idx = bisect_left(self.ring, hash_value)
        
        nodes = []
        seen = set()
        
        for i in range(len(self.ring)):
            node_idx = (idx + i) % len(self.ring)
            node = self.ring_to_node[self.ring[node_idx]]
            
            if node not in seen:
                nodes.append(node)
                seen.add(node)
                
                if len(nodes) >= count:
                    break
        
        return nodes
```

### 2. Cache Client with Connection Pooling

```python
import asyncio
from typing import Any, Optional
from dataclasses import dataclass
import aioredis


@dataclass
class CacheConfig:
    hosts: List[str]
    pool_size: int = 10
    timeout_ms: int = 100
    retry_count: int = 3
    circuit_breaker_threshold: int = 5


class DistributedCacheClient:
    """
    High-performance cache client with connection pooling,
    circuit breaker, and automatic failover.
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.hasher = ConsistentHash(config.hosts)
        self.pools: Dict[str, aioredis.ConnectionPool] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        self._init_pools()
    
    def _init_pools(self):
        """Initialize connection pools for each node."""
        for host in self.config.hosts:
            self.pools[host] = aioredis.ConnectionPool.from_url(
                f"redis://{host}",
                max_connections=self.config.pool_size
            )
            self.circuit_breakers[host] = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold
            )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        node = self.hasher.get_node(key)
        
        if not node or self.circuit_breakers[node].is_open:
            # Try replica
            nodes = self.hasher.get_nodes(key, count=3)
            for replica in nodes[1:]:
                if not self.circuit_breakers[replica].is_open:
                    node = replica
                    break
            else:
                return None
        
        try:
            async with aioredis.Redis(connection_pool=self.pools[node]) as redis:
                value = await asyncio.wait_for(
                    redis.get(key),
                    timeout=self.config.timeout_ms / 1000
                )
                self.circuit_breakers[node].record_success()
                return value
                
        except Exception as e:
            self.circuit_breakers[node].record_failure()
            # Try replica on failure
            return await self._get_from_replica(key, node)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: int = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        nodes = self.hasher.get_nodes(key, count=3)
        
        # Write to primary
        primary = nodes[0]
        success = await self._write_to_node(primary, key, value, ttl_seconds)
        
        if success:
            # Async replication to replicas
            asyncio.create_task(
                self._replicate_to_nodes(nodes[1:], key, value, ttl_seconds)
            )
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        nodes = self.hasher.get_nodes(key, count=3)
        
        # Delete from all nodes
        tasks = [
            self._delete_from_node(node, key)
            for node in nodes
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return any(r for r in results if r is True)
    
    async def _write_to_node(
        self, 
        node: str, 
        key: str, 
        value: Any, 
        ttl: int
    ) -> bool:
        """Write to a specific node."""
        try:
            async with aioredis.Redis(connection_pool=self.pools[node]) as redis:
                if ttl:
                    await redis.setex(key, ttl, value)
                else:
                    await redis.set(key, value)
                return True
        except Exception:
            return False
```

### 3. Cache Patterns Implementation

```python
class CachePatterns:
    """
    Common caching patterns for different use cases.
    """
    
    def __init__(self, cache: DistributedCacheClient, db: Database):
        self.cache = cache
        self.db = db
    
    # Pattern 1: Cache-Aside (Lazy Loading)
    async def cache_aside_get(self, key: str) -> Any:
        """
        Cache-aside pattern: Check cache first, load from DB on miss.
        
        Pros: Only requested data is cached
        Cons: Cache miss penalty, potential stale data
        """
        # Try cache first
        value = await self.cache.get(key)
        
        if value is not None:
            return value
        
        # Cache miss - load from database
        value = await self.db.get(key)
        
        if value is not None:
            # Populate cache
            await self.cache.set(key, value, ttl_seconds=3600)
        
        return value
    
    # Pattern 2: Write-Through
    async def write_through(self, key: str, value: Any) -> bool:
        """
        Write-through pattern: Write to cache and DB synchronously.
        
        Pros: Cache always consistent with DB
        Cons: Higher write latency
        """
        # Write to cache first
        cache_success = await self.cache.set(key, value)
        
        if not cache_success:
            return False
        
        # Write to database
        try:
            await self.db.set(key, value)
            return True
        except Exception:
            # Rollback cache on DB failure
            await self.cache.delete(key)
            return False
    
    # Pattern 3: Write-Behind (Write-Back)
    async def write_behind(self, key: str, value: Any) -> bool:
        """
        Write-behind pattern: Write to cache, async write to DB.
        
        Pros: Low write latency
        Cons: Risk of data loss if cache fails before DB write
        """
        # Write to cache immediately
        cache_success = await self.cache.set(key, value)
        
        if cache_success:
            # Queue async write to database
            await self.write_queue.enqueue({
                'key': key,
                'value': value,
                'timestamp': time.time()
            })
        
        return cache_success
    
    # Pattern 4: Read-Through
    async def read_through_get(self, key: str) -> Any:
        """
        Read-through pattern: Cache handles DB loading transparently.
        
        Similar to cache-aside but cache is responsible for loading.
        """
        return await self.cache.get_or_load(
            key,
            loader=lambda k: self.db.get(k),
            ttl_seconds=3600
        )
    
    # Pattern 5: Refresh-Ahead
    async def refresh_ahead_get(self, key: str) -> Any:
        """
        Refresh-ahead pattern: Proactively refresh before expiry.
        
        Pros: Reduces cache miss latency
        Cons: May refresh unused data
        """
        value, ttl_remaining = await self.cache.get_with_ttl(key)
        
        if value is not None:
            # If TTL is low, trigger async refresh
            if ttl_remaining < 300:  # Less than 5 minutes
                asyncio.create_task(self._refresh_key(key))
            return value
        
        # Cache miss
        return await self.cache_aside_get(key)
    
    async def _refresh_key(self, key: str):
        """Refresh a key from database."""
        value = await self.db.get(key)
        if value is not None:
            await self.cache.set(key, value, ttl_seconds=3600)
```

### 4. Cache Invalidation Strategies

```python
class CacheInvalidation:
    """
    Cache invalidation strategies for maintaining consistency.
    """
    
    def __init__(self, cache: DistributedCacheClient, pubsub: PubSubClient):
        self.cache = cache
        self.pubsub = pubsub
    
    # Strategy 1: TTL-based expiration
    async def set_with_ttl(self, key: str, value: Any, ttl: int):
        """Simple TTL-based invalidation."""
        await self.cache.set(key, value, ttl_seconds=ttl)
    
    # Strategy 2: Event-based invalidation
    async def invalidate_on_update(self, entity_type: str, entity_id: str):
        """
        Publish invalidation event when data changes.
        All cache nodes subscribe and invalidate locally.
        """
        # Build cache key pattern
        pattern = f"{entity_type}:{entity_id}:*"
        
        # Publish invalidation event
        await self.pubsub.publish(
            'cache-invalidation',
            {
                'pattern': pattern,
                'timestamp': time.time(),
                'source': self.node_id
            }
        )
    
    async def handle_invalidation_event(self, event: Dict):
        """Handle incoming invalidation events."""
        pattern = event['pattern']
        
        # Find and delete matching keys
        keys = await self.cache.scan(pattern)
        for key in keys:
            await self.cache.delete(key)
    
    # Strategy 3: Version-based invalidation
    async def get_versioned(self, key: str, version: int) -> Any:
        """
        Version-based cache key to handle updates.
        """
        versioned_key = f"{key}:v{version}"
        return await self.cache.get(versioned_key)
    
    async def set_versioned(self, key: str, value: Any, version: int):
        """Set with version, invalidate old versions."""
        versioned_key = f"{key}:v{version}"
        
        # Set new version
        await self.cache.set(versioned_key, value)
        
        # Delete old versions (async)
        asyncio.create_task(
            self._cleanup_old_versions(key, version)
        )
    
    # Strategy 4: Tag-based invalidation
    async def set_with_tags(self, key: str, value: Any, tags: List[str]):
        """
        Associate cache entries with tags for bulk invalidation.
        """
        # Store the value
        await self.cache.set(key, value)
        
        # Associate key with each tag
        for tag in tags:
            await self.cache.sadd(f"tag:{tag}", key)
    
    async def invalidate_by_tag(self, tag: str):
        """Invalidate all entries with a specific tag."""
        # Get all keys with this tag
        keys = await self.cache.smembers(f"tag:{tag}")
        
        # Delete all keys
        for key in keys:
            await self.cache.delete(key)
        
        # Clear the tag set
        await self.cache.delete(f"tag:{tag}")
```

### 5. Cache Warming and Preloading

```python
class CacheWarmer:
    """
    Strategies for warming cache to prevent cold start issues.
    """
    
    def __init__(self, cache: DistributedCacheClient, db: Database):
        self.cache = cache
        self.db = db
    
    async def warm_on_startup(self, config: WarmingConfig):
        """Warm cache on application startup."""
        
        # Load frequently accessed data
        hot_keys = await self.db.get_hot_keys(limit=config.hot_key_limit)
        
        for key in hot_keys:
            value = await self.db.get(key)
            await self.cache.set(key, value, ttl_seconds=config.default_ttl)
        
        logger.info(f"Warmed {len(hot_keys)} keys on startup")
    
    async def warm_from_access_log(self, hours: int = 24):
        """Warm cache based on recent access patterns."""
        
        # Get keys accessed in last N hours
        recent_keys = await self.access_log.get_recent_keys(hours=hours)
        
        # Sort by access frequency
        sorted_keys = sorted(
            recent_keys.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Warm top N keys
        for key, count in sorted_keys[:10000]:
            value = await self.db.get(key)
            if value:
                await self.cache.set(key, value)
    
    async def warm_predictively(self):
        """
        Predictive warming based on time patterns.
        E.g., warm user data before business hours.
        """
        current_hour = datetime.now().hour
        
        if current_hour == 7:  # Before business hours
            # Warm frequently accessed user accounts
            active_users = await self.db.get_active_users()
            for user_id in active_users:
                user_data = await self.db.get_user(user_id)
                await self.cache.set(f"user:{user_id}", user_data)
```

## Interview Discussion Points

1. **How do you handle cache stampede?**
   - Locking/mutex on cache miss
   - Probabilistic early expiration
   - Request coalescing

2. **How do you ensure consistency between cache and database?**
   - Write-through for strong consistency
   - Event-driven invalidation
   - Version-based keys

3. **How do you handle hot keys?**
   - Local caching layer
   - Key replication across shards
   - Request rate limiting

4. **What happens when a cache node fails?**
   - Consistent hashing minimizes redistribution
   - Replicas serve reads
   - Automatic failover and recovery

5. **How do you monitor cache performance?**
   - Hit/miss ratio
   - Latency percentiles
   - Memory utilization
   - Eviction rate
