import time
from typing import Dict, Any, Optional


class CacheManager:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl_minutes: int):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_minutes * 60
    
    def _is_expired(self, timestamp: float) -> bool:
        """Check if a cache entry is expired."""
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value from cache if it exists and is not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if self._is_expired(entry["timestamp"]):
            # Remove expired entry
            del self.cache[key]
            return None
        
        return entry["data"]
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Set a value in cache with current timestamp."""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count of removed entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if self._is_expired(entry["timestamp"])
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        expired_count = self.cleanup_expired()
        active_entries = len(self.cache)
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_cleaned": expired_count,
            "ttl_seconds": self.ttl_seconds
        }
