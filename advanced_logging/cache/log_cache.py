"""
Caching system for logging operations.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from threading import Lock
import json
from dataclasses import dataclass
from collections import OrderedDict
import sqlite3
import os

@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    items: int = 0

class MemoryCache:
    """
    Thread-safe in-memory LRU cache for log entries.
    """
    
    def __init__(
        self,
        max_size_mb: int = 100,
        max_items: int = 10000,
        ttl_seconds: int = 300
    ):
        """
        Initialize memory cache.
        
        Args:
            max_size_mb: Maximum cache size in MB
            max_items: Maximum number of items
            ttl_seconds: Time-to-live in seconds
        """
        self._max_size = max_size_mb * 1024 * 1024
        self._max_items = max_items
        self._ttl = ttl_seconds
        
        self._lock = Lock()
        self._cache: OrderedDict[str, Tuple[Any, float, int]] = OrderedDict()
        self._size = 0
        
        # Stats
        self._stats = CacheStats()
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
                
            value, expiry, size = self._cache[key]
            
            # Check if expired
            if time.time() > expiry:
                self._remove(key)
                self._stats.misses += 1
                return None
                
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._stats.hits += 1
            
            return value
            
    def put(self, key: str, value: Any) -> None:
        """Put item in cache."""
        with self._lock:
            # Calculate size
            size = len(json.dumps(value).encode())
            
            # Remove if already exists
            if key in self._cache:
                self._remove(key)
                
            # Check if we need to make space
            while (
                (self._size + size > self._max_size or
                len(self._cache) >= self._max_items) and
                self._cache
            ):
                # Remove least recently used
                self._remove(next(iter(self._cache)))
                self._stats.evictions += 1
                
            # Add new item
            self._cache[key] = (
                value,
                time.time() + self._ttl,
                size
            )
            self._size += size
            self._stats.items = len(self._cache)
            self._stats.size_bytes = self._size
            
    def _remove(self, key: str) -> None:
        """Remove item from cache."""
        _, _, size = self._cache[key]
        del self._cache[key]
        self._size -= size
        self._stats.items = len(self._cache)
        self._stats.size_bytes = self._size
        
    def clear(self) -> None:
        """Clear cache."""
        with self._lock:
            self._cache.clear()
            self._size = 0
            self._stats = CacheStats()
            
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return self._stats

class DiskCache:
    """
    SQLite-based disk cache for log entries.
    """
    
    def __init__(
        self,
        cache_dir: str,
        max_size_mb: int = 1024,
        ttl_seconds: int = 86400
    ):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Cache directory
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live in seconds
        """
        self._cache_dir = cache_dir
        self._max_size = max_size_mb * 1024 * 1024
        self._ttl = ttl_seconds
        
        os.makedirs(cache_dir, exist_ok=True)
        self._db_path = os.path.join(cache_dir, 'log_cache.db')
        
        self._init_db()
        
    def _init_db(self) -> None:
        """Initialize SQLite database."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    size INTEGER,
                    expiry INTEGER,
                    accessed INTEGER
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_expiry ON cache(expiry)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_accessed ON cache(accessed)"
            )
            
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with sqlite3.connect(self._db_path) as conn:
            # Get item
            row = conn.execute(
                """
                SELECT value, expiry
                FROM cache
                WHERE key = ?
                """,
                (key,)
            ).fetchone()
            
            if not row:
                return None
                
            value, expiry = row
            
            # Check if expired
            if time.time() > expiry:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None
                
            # Update access time
            conn.execute(
                """
                UPDATE cache
                SET accessed = ?
                WHERE key = ?
                """,
                (int(time.time()), key)
            )
            
            return json.loads(value)
            
    def put(self, key: str, value: Any) -> None:
        """Put item in cache."""
        with sqlite3.connect(self._db_path) as conn:
            # Calculate size
            value_json = json.dumps(value)
            size = len(value_json.encode())
            
            # Check total size
            current_size = conn.execute(
                "SELECT COALESCE(SUM(size), 0) FROM cache"
            ).fetchone()[0]
            
            # Make space if needed
            while current_size + size > self._max_size:
                # Remove oldest accessed item
                oldest = conn.execute(
                    """
                    SELECT key, size
                    FROM cache
                    ORDER BY accessed ASC
                    LIMIT 1
                    """
                ).fetchone()
                
                if not oldest:
                    break
                    
                conn.execute(
                    "DELETE FROM cache WHERE key = ?",
                    (oldest[0],)
                )
                current_size -= oldest[1]
                
            # Remove expired items
            conn.execute(
                "DELETE FROM cache WHERE expiry < ?",
                (int(time.time()),)
            )
            
            # Insert or update item
            conn.execute(
                """
                INSERT OR REPLACE INTO cache
                (key, value, size, expiry, accessed)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    key,
                    value_json,
                    size,
                    int(time.time() + self._ttl),
                    int(time.time())
                )
            )
            
    def clear(self) -> None:
        """Clear cache."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache")
            
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with sqlite3.connect(self._db_path) as conn:
            # Get total size and items
            row = conn.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(size), 0)
                FROM cache
                """
            ).fetchone()
            
            return CacheStats(
                items=row[0],
                size_bytes=row[1]
            )

class TieredCache:
    """
    Two-tiered caching system combining memory and disk caches.
    """
    
    def __init__(
        self,
        memory_cache: Optional[MemoryCache] = None,
        disk_cache: Optional[DiskCache] = None
    ):
        """
        Initialize tiered cache.
        
        Args:
            memory_cache: Optional memory cache instance
            disk_cache: Optional disk cache instance
        """
        self.memory = memory_cache or MemoryCache()
        self.disk = disk_cache or DiskCache(
            cache_dir=os.path.join(os.getcwd(), '.log_cache')
        )
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        # Try memory first
        value = self.memory.get(key)
        if value is not None:
            return value
            
        # Try disk
        value = self.disk.get(key)
        if value is not None:
            # Promote to memory
            self.memory.put(key, value)
            return value
            
        return None
        
    def put(self, key: str, value: Any) -> None:
        """Put item in cache."""
        # Store in both tiers
        self.memory.put(key, value)
        self.disk.put(key, value)
        
    def clear(self) -> None:
        """Clear both caches."""
        self.memory.clear()
        self.disk.clear()
        
    def get_stats(self) -> Dict[str, CacheStats]:
        """Get cache statistics."""
        return {
            'memory': self.memory.get_stats(),
            'disk': self.disk.get_stats()
        }
