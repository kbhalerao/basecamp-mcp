"""SQLite-based cache manager for Basecamp API responses."""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from pathlib import Path


class CacheManager:
    """Manages API response caching using SQLite with TTL support."""
    
    def __init__(self, db_path: str = "basecamp_cache.db"):
        """Initialize cache manager and create database if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL,
                    hits INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            """)
            conn.commit()
    
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get value from cache if it exists and hasn't expired."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value, expires_at, hits FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            value_json, expires_at, hits = row
            
            # Check if expired
            if expires_at < datetime.now().timestamp():
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return None
            
            # Update hit count
            conn.execute(
                "UPDATE cache SET hits = ? WHERE key = ?",
                (hits + 1, key)
            )
            conn.commit()
            
            return json.loads(value_json)
    
    def set(self, key: str, value: dict[str, Any], ttl: int = 300) -> None:
        """Set value in cache with TTL in seconds."""
        expires_at = (datetime.now() + timedelta(seconds=ttl)).timestamp()
        created_at = datetime.now().timestamp()
        value_json = json.dumps(value)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache 
                (key, value, expires_at, created_at, hits)
                VALUES (?, ?, ?, ?, 0)
                """,
                (key, value_json, expires_at, created_at)
            )
            conn.commit()
    
    def delete(self, key: str) -> None:
        """Delete a specific cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries. Returns count of deleted entries."""
        now = datetime.now().timestamp()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at < ?",
                (now,)
            )
            conn.commit()
            return cursor.rowcount
    
    def clear_all(self) -> int:
        """Clear all cache entries. Returns count of deleted entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM cache")
            conn.commit()
            return cursor.rowcount
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now().timestamp()
        with sqlite3.connect(self.db_path) as conn:
            # Total entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total = cursor.fetchone()[0]
            
            # Valid entries (not expired)
            cursor = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at > ?",
                (now,)
            )
            valid = cursor.fetchone()[0]
            
            # Expired entries
            cursor = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at <= ?",
                (now,)
            )
            expired = cursor.fetchone()[0]
            
            # Total hits
            cursor = conn.execute("SELECT SUM(hits) FROM cache")
            hits = cursor.fetchone()[0] or 0
            
            # Cache size in bytes
            cursor = conn.execute("SELECT SUM(LENGTH(value)) FROM cache")
            size_bytes = cursor.fetchone()[0] or 0
            
            return {
                "total_entries": total,
                "valid_entries": valid,
                "expired_entries": expired,
                "total_hits": hits,
                "cache_size_bytes": size_bytes,
                "cache_size_mb": round(size_bytes / (1024 * 1024), 2),
            }
