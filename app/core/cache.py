"""
PPK Document Factory - Data Cache System
========================================
In-memory caching system for frequently accessed data.

Features:
- Time-to-live (TTL) based expiration
- Pattern-based invalidation
- Statistics tracking
- Thread-safe operations
- Decorator for easy caching

Example Usage:
-------------
```python
from app.core.cache import DataCache, cached

# Get singleton cache instance
cache = DataCache()

# Basic get/set
cache.set("satker:active", satker_list, ttl=3600)
data = cache.get("satker:active")

# Get or compute
data = cache.get_or_set(
    "transaksi:list:UP",
    lambda: db.list_transaksi(mekanisme="UP"),
    ttl=60
)

# Invalidate on update
cache.invalidate_pattern("transaksi:*")

# Using decorator
@cached(ttl=300, key_prefix="transaksi")
def get_transaksi(transaksi_id):
    return db.get_transaksi(transaksi_id)
```

Recommended Cache Keys:
----------------------
- "satker:active" - Active satker (ttl: 1 hour)
- "pegawai:all" - All pegawai list (ttl: 30 min)
- "penyedia:all" - All penyedia list (ttl: 30 min)
- "transaksi:{id}" - Single transaksi (ttl: 5 min)
- "transaksi:list:{mekanisme}" - Transaksi list (ttl: 1 min)
- "stats:{mekanisme}" - Statistics (ttl: 1 min)
- "saldo:up" - UP balance (ttl: 30 sec)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, Generic
from functools import wraps
import fnmatch
import logging
import threading
import hashlib
import json

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# CACHE ENTRY
# =============================================================================


@dataclass
class CacheEntry:
    """
    Single cache entry with metadata.

    Attributes:
        data: The cached data
        created_at: When the entry was created
        expires_at: When the entry expires
        hits: Number of times this entry was accessed
        key: The cache key
    """
    data: Any
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    hits: int = 0
    key: str = ""

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """Increment hit counter."""
        self.hits += 1

    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    @property
    def ttl_remaining(self) -> Optional[float]:
        """Get remaining TTL in seconds."""
        if self.expires_at is None:
            return None
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)


# =============================================================================
# CACHE STATS
# =============================================================================


@dataclass
class CacheStats:
    """
    Cache statistics.

    Attributes:
        hits: Total cache hits
        misses: Total cache misses
        size: Current number of entries
        total_memory: Estimated memory usage (bytes)
        evictions: Number of entries evicted
    """
    hits: int = 0
    misses: int = 0
    size: int = 0
    total_memory: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate as percentage."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100

    @property
    def total_requests(self) -> int:
        """Total number of requests."""
        return self.hits + self.misses

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "size": self.size,
            "total_memory": self.total_memory,
            "evictions": self.evictions,
            "hit_rate": f"{self.hit_rate:.1f}%",
            "total_requests": self.total_requests,
        }


# =============================================================================
# DATA CACHE (SINGLETON)
# =============================================================================


class DataCache:
    """
    Thread-safe in-memory data cache with TTL support.

    Implements singleton pattern - all instances share the same cache.

    Example:
    --------
    ```python
    cache = DataCache()

    # Store with TTL
    cache.set("key", value, ttl=300)  # 5 minutes

    # Retrieve
    value = cache.get("key")  # None if expired or missing

    # Get or compute
    value = cache.get_or_set("key", lambda: compute_value(), ttl=60)

    # Invalidate by pattern
    cache.invalidate_pattern("transaksi:*")

    # Get statistics
    stats = cache.stats
    print(f"Hit rate: {stats.hit_rate}%")
    ```
    """

    _instance: Optional['DataCache'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'DataCache':
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize cache."""
        if self._initialized:
            return

        self._cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._data_lock = threading.RLock()
        self._max_size = 1000  # Maximum entries
        self._cleanup_threshold = 100  # Cleanup every N operations
        self._operation_count = 0
        self._initialized = True

        logger.debug("DataCache initialized")

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._data_lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats.misses += 1
                logger.debug(f"Cache miss: {key}")
                return None

            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                self._stats.misses += 1
                self._stats.size = len(self._cache)
                logger.debug(f"Cache expired: {key}")
                return None

            # Update stats
            entry.touch()
            self._stats.hits += 1
            logger.debug(f"Cache hit: {key} (hits: {entry.hits})")

            return entry.data

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 300
    ) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds (None = no expiration)
        """
        with self._data_lock:
            # Calculate expiration
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)

            # Create entry
            entry = CacheEntry(
                data=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                key=key
            )

            # Check if replacing existing
            if key in self._cache:
                logger.debug(f"Cache replace: {key}")
            else:
                logger.debug(f"Cache set: {key} (ttl: {ttl}s)")

            self._cache[key] = entry
            self._stats.size = len(self._cache)

            # Periodic cleanup
            self._operation_count += 1
            if self._operation_count >= self._cleanup_threshold:
                self._cleanup()
                self._operation_count = 0

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key existed and was deleted
        """
        with self._data_lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.size = len(self._cache)
                logger.debug(f"Cache delete: {key}")
                return True
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Cache key

        Returns:
            True if key exists and is valid
        """
        with self._data_lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                self._stats.size = len(self._cache)
                return False
            return True

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._data_lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats.size = 0
            logger.info(f"Cache cleared ({count} entries)")

    # =========================================================================
    # ADVANCED OPERATIONS
    # =========================================================================

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[int] = 300
    ) -> T:
        """
        Get from cache or compute and store.

        If the key doesn't exist or is expired, calls factory()
        to compute the value and stores it.

        Args:
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time-to-live in seconds

        Returns:
            Cached or computed value
        """
        # Try cache first
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = factory()

        # Store in cache
        self.set(key, value, ttl=ttl)

        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Supports wildcards: * matches any characters.

        Args:
            pattern: Glob pattern (e.g., "transaksi:*", "*:list:*")

        Returns:
            Number of keys invalidated
        """
        with self._data_lock:
            keys_to_delete = [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, pattern)
            ]

            for key in keys_to_delete:
                del self._cache[key]

            self._stats.size = len(self._cache)
            self._stats.evictions += len(keys_to_delete)

            if keys_to_delete:
                logger.debug(
                    f"Cache invalidated: {pattern} ({len(keys_to_delete)} keys)"
                )

            return len(keys_to_delete)

    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values at once.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key -> value (only for found keys)
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = 300
    ) -> None:
        """
        Set multiple values at once.

        Args:
            items: Dictionary of key -> value
            ttl: TTL for all items
        """
        for key, value in items.items():
            self.set(key, value, ttl=ttl)

    # =========================================================================
    # MAINTENANCE
    # =========================================================================

    def _cleanup(self) -> None:
        """Remove expired entries and enforce max size."""
        with self._data_lock:
            # Remove expired entries
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats.evictions += 1

            # Enforce max size (LRU-like: remove entries with fewest hits)
            if len(self._cache) > self._max_size:
                # Sort by hits and age, remove oldest/least used
                entries = sorted(
                    self._cache.items(),
                    key=lambda x: (x[1].hits, -x[1].age_seconds)
                )
                to_remove = len(self._cache) - self._max_size
                for key, _ in entries[:to_remove]:
                    del self._cache[key]
                    self._stats.evictions += 1

            self._stats.size = len(self._cache)

            if expired_keys:
                logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired")

    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a cache entry.

        Args:
            key: Cache key

        Returns:
            Dictionary with entry info or None
        """
        with self._data_lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            return {
                "key": key,
                "created_at": entry.created_at.isoformat(),
                "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                "hits": entry.hits,
                "age_seconds": entry.age_seconds,
                "ttl_remaining": entry.ttl_remaining,
                "is_expired": entry.is_expired(),
            }

    def list_keys(self, pattern: str = "*") -> list:
        """
        List all keys matching pattern.

        Args:
            pattern: Glob pattern

        Returns:
            List of matching keys
        """
        with self._data_lock:
            return [
                key for key in self._cache.keys()
                if fnmatch.fnmatch(key, pattern)
            ]

    # =========================================================================
    # STATISTICS
    # =========================================================================

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._data_lock:
            # Estimate memory (rough)
            self._stats.total_memory = sum(
                len(str(entry.data)) for entry in self._cache.values()
            )
            return self._stats

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._data_lock:
            self._stats.hits = 0
            self._stats.misses = 0
            self._stats.evictions = 0
            logger.debug("Cache stats reset")


# =============================================================================
# DECORATOR
# =============================================================================


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key

    Example:
    --------
    ```python
    @cached(ttl=300, key_prefix="transaksi")
    def get_transaksi(transaksi_id):
        return db.get_transaksi(transaksi_id)

    # Cache key will be "transaksi:get_transaksi:abc123"
    result = get_transaksi("abc123")
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = DataCache()

            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                # Default key: prefix:func_name:args_hash
                key_parts = [key_prefix] if key_prefix else []
                key_parts.append(func.__name__)

                # Hash arguments
                args_str = json.dumps(
                    {"args": args, "kwargs": kwargs},
                    sort_keys=True,
                    default=str
                )
                args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
                key_parts.append(args_hash)

                key = ":".join(filter(None, key_parts))

            # Try cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)

            return result

        # Add cache control methods to wrapper
        wrapper.cache_clear = lambda: DataCache().invalidate_pattern(
            f"{key_prefix}:{func.__name__}:*" if key_prefix
            else f"{func.__name__}:*"
        )
        wrapper.cache_key_prefix = key_prefix or func.__name__

        return wrapper
    return decorator


def cache_invalidate(*patterns: str):
    """
    Decorator to invalidate cache after function execution.

    Args:
        *patterns: Cache patterns to invalidate

    Example:
    --------
    ```python
    @cache_invalidate("transaksi:*", "stats:*")
    def create_transaksi(data):
        return db.create_transaksi(data)
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate patterns
            cache = DataCache()
            for pattern in patterns:
                cache.invalidate_pattern(pattern)

            return result
        return wrapper
    return decorator


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_cache() -> DataCache:
    """Get the singleton cache instance."""
    return DataCache()


def clear_cache() -> None:
    """Clear all cache entries."""
    DataCache().clear()


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics as dictionary."""
    return DataCache().stats.to_dict()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Classes
    'CacheEntry',
    'CacheStats',
    'DataCache',

    # Decorators
    'cached',
    'cache_invalidate',

    # Helper functions
    'get_cache',
    'clear_cache',
    'cache_stats',
]
