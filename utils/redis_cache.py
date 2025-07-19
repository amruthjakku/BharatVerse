"""
Redis Cache Utilities for BharatVerse
Handles caching, session management, and temporary data storage
"""
import streamlit as st
import redis
import json
import pickle
from typing import Any, Optional, Dict, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisCacheManager:
    """Manages Redis cache operations for BharatVerse"""
    
    def __init__(self):
        """Initialize Redis client using Streamlit secrets"""
        try:
            redis_config = st.secrets.get("redis", {})
            
            if "url" in redis_config:
                # URL-based connection (Upstash format)
                self.client = redis.from_url(
                    redis_config["url"],
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            else:
                # Host/port based connection
                self.client = redis.Redis(
                    host=redis_config.get("host", "localhost"),
                    port=redis_config.get("port", 6379),
                    password=redis_config.get("password", None),
                    db=redis_config.get("db", 0),
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            
            # Test connection
            self.client.ping()
            logger.info("Redis Cache Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def set(self, key: str, value: Any, expiry_seconds: int = None) -> bool:
        """
        Set a value in Redis cache
        
        Args:
            key: Cache key
            value: Value to cache (will be serialized)
            expiry_seconds: Optional expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value).encode('utf-8')
            elif isinstance(value, str):
                serialized_value = value.encode('utf-8')
            else:
                serialized_value = pickle.dumps(value)
            
            # Set with optional expiry
            if expiry_seconds:
                return self.client.setex(key, expiry_seconds, serialized_value)
            else:
                return self.client.set(key, serialized_value)
        
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON first
            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                try:
                    return pickle.loads(value)
                except (pickle.UnpicklingError, pickle.PickleError):
                    # Return as string if all else fails
                    try:
                        return value.decode('utf-8')
                    except UnicodeDecodeError:
                        return value
        
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis cache"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check existence of cache key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Failed to set expiration for cache key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get time-to-live for a key"""
        if not self.client:
            return -2
        
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for cache key {key}: {e}")
            return -2
    
    def keys_pattern(self, pattern: str) -> List[str]:
        """Get keys matching a pattern"""
        if not self.client:
            return []
        
        try:
            keys = self.client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        if not self.client:
            return 0
        
        try:
            keys = self.keys_pattern(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to flush keys with pattern {pattern}: {e}")
            return 0
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value"""
        if not self.client:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {e}")
            return None
    
    def set_hash(self, key: str, mapping: Dict[str, Any], expiry_seconds: int = None) -> bool:
        """Set a hash in Redis"""
        if not self.client:
            return False
        
        try:
            # Serialize hash values
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v)
                elif isinstance(v, str):
                    serialized_mapping[k] = v
                else:
                    serialized_mapping[k] = str(v)
            
            result = self.client.hmset(key, serialized_mapping)
            
            if expiry_seconds:
                self.client.expire(key, expiry_seconds)
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to set hash {key}: {e}")
            return False
    
    def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a hash from Redis"""
        if not self.client:
            return None
        
        try:
            hash_data = self.client.hgetall(key)
            if not hash_data:
                return None
            
            # Deserialize hash values
            result = {}
            for k, v in hash_data.items():
                k = k.decode('utf-8') if isinstance(k, bytes) else k
                v = v.decode('utf-8') if isinstance(v, bytes) else v
                
                # Try to parse as JSON
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, ValueError):
                    result[k] = v
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to get hash {key}: {e}")
            return None
    
    def cache_ai_result(self, input_hash: str, result: Dict, expiry_hours: int = 24) -> bool:
        """Cache AI processing result"""
        key = f"ai_result:{input_hash}"
        expiry_seconds = expiry_hours * 3600
        
        cached_data = {
            "result": result,
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
        }
        
        return self.set(key, cached_data, expiry_seconds)
    
    def get_cached_ai_result(self, input_hash: str) -> Optional[Dict]:
        """Get cached AI processing result"""
        key = f"ai_result:{input_hash}"
        cached_data = self.get(key)
        
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get("result")
        
        return None
    
    def cache_user_session(self, session_id: str, user_data: Dict, expiry_hours: int = 24) -> bool:
        """Cache user session data"""
        key = f"session:{session_id}"
        expiry_seconds = expiry_hours * 3600
        
        session_data = {
            "user_data": user_data,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
        }
        
        return self.set(key, session_data, expiry_seconds)
    
    def get_user_session(self, session_id: str) -> Optional[Dict]:
        """Get user session data"""
        key = f"session:{session_id}"
        session_data = self.get(key)
        
        if session_data and isinstance(session_data, dict):
            return session_data.get("user_data")
        
        return None
    
    def invalidate_user_session(self, session_id: str) -> bool:
        """Invalidate user session"""
        key = f"session:{session_id}"
        return self.delete(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        if not self.client:
            return {"connected": False}
        
        try:
            info = self.client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "Unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"connected": False, "error": str(e)}

# Global cache manager instance
@st.cache_resource
def get_cache_manager() -> RedisCacheManager:
    """Get cached Redis manager instance"""
    return RedisCacheManager()

# Convenience functions
def cache_set(key: str, value: Any, expiry_seconds: int = None) -> bool:
    """Set cache using global manager"""
    cache = get_cache_manager()
    return cache.set(key, value, expiry_seconds)

def cache_get(key: str) -> Optional[Any]:
    """Get cache using global manager"""
    cache = get_cache_manager()
    return cache.get(key)

def cache_delete(key: str) -> bool:
    """Delete cache using global manager"""
    cache = get_cache_manager()
    return cache.delete(key)

def cache_ai_result(input_hash: str, result: Dict, expiry_hours: int = 24) -> bool:
    """Cache AI result using global manager"""
    cache = get_cache_manager()
    return cache.cache_ai_result(input_hash, result, expiry_hours)

def get_cached_ai_result(input_hash: str) -> Optional[Dict]:
    """Get cached AI result using global manager"""
    cache = get_cache_manager()
    return cache.get_cached_ai_result(input_hash)