"""
Redis Cache Manager for BharatVerse Cloud Deployment
Caches AI processing results and handles lightweight session data

Module: redis_cache.py
Purpose: Performance optimization through intelligent caching
- Caches AI model results to avoid repeated API calls
- Stores lightweight session data (user preferences, temp state)
- Manages rate limiting counters and usage tracking
- Note: Streamlit is stateless, so session data is minimal and optional
"""
import streamlit as st
import json
import pickle
import requests
from typing import Any, Optional, Dict, List
import logging
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class RedisCacheManager:
    """Manages Redis cache operations for BharatVerse"""
    
    def __init__(self):
        """Initialize Redis client using Streamlit secrets"""
        self.use_rest_api = False
        self.rest_url = None
        self.rest_token = None
        
        try:
            redis_config = st.secrets.get("redis", {})
            
            if "url" in redis_config and "token" in redis_config:
                # Upstash Redis connection (preferred method)
                url = redis_config["url"]
                token = redis_config["token"]
                
                # Extract host from URL
                if url.startswith("https://"):
                    host = url.replace("https://", "")
                elif url.startswith("redis://"):
                    host = url.replace("redis://", "")
                else:
                    host = url
                
                # Use HTTPS connection method (optimized for Streamlit Cloud)
                self.client = redis.Redis(
                    host=host,
                    port=6379,
                    password=token,
                    decode_responses=False,
                    ssl=True,
                    ssl_cert_reqs=None,  # Disable SSL certificate verification for cloud
                    socket_connect_timeout=15,  # Longer timeout for cloud
                    socket_timeout=15,
                    retry_on_timeout=True,
                    retry_on_error=[redis.ConnectionError, redis.TimeoutError],
                    health_check_interval=60
                )
            elif "url" in redis_config:
                # Fallback to URL-based connection
                self.client = redis.from_url(
                    redis_config["url"],
                    decode_responses=False,
                    socket_connect_timeout=10,
                    socket_timeout=10,
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
                    socket_connect_timeout=10,
                    socket_timeout=10,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            
            # Test connection
            self.client.ping()
            logger.info("Redis Cache Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            # Fallback to REST API for cloud environments
            redis_config = st.secrets.get("redis", {})
            if "url" in redis_config and "token" in redis_config:
                logger.info("Falling back to Upstash REST API")
                self.use_rest_api = True
                self.rest_url = redis_config["url"]
                self.rest_token = redis_config["token"]
                self.client = None
                
                # Test REST API connection
                if self._test_rest_api():
                    logger.info("REST API fallback successful")
                else:
                    logger.error("REST API fallback also failed")
            else:
                self.client = None
    
    def _test_rest_api(self) -> bool:
        """Test Upstash REST API connection"""
        try:
            headers = {"Authorization": f"Bearer {self.rest_token}"}
            response = requests.post(f"{self.rest_url}/ping", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"REST API test failed: {e}")
            return False
    
    def _set_rest_api(self, key: str, value: Any, expiry_seconds: int = None) -> bool:
        """Set value using REST API"""
        try:
            headers = {"Authorization": f"Bearer {self.rest_token}"}
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif isinstance(value, str):
                serialized_value = value
            else:
                serialized_value = json.dumps(str(value))
            
            # Prepare command
            if expiry_seconds:
                data = ["SETEX", key, expiry_seconds, serialized_value]
            else:
                data = ["SET", key, serialized_value]
            
            response = requests.post(f"{self.rest_url}", headers=headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"REST API set failed: {e}")
            return False
    
    def _get_rest_api(self, key: str) -> Optional[Any]:
        """Get value using REST API"""
        try:
            headers = {"Authorization": f"Bearer {self.rest_token}"}
            data = ["GET", key]
            
            response = requests.post(f"{self.rest_url}", headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("result"):
                    try:
                        return json.loads(result["result"])
                    except:
                        return result["result"]
            return None
        except Exception as e:
            logger.error(f"REST API get failed: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected with enhanced cloud compatibility"""
        if self.use_rest_api:
            return self._test_rest_api()
            
        if not self.client:
            logger.warning("Redis client not initialized")
            return False
        
        try:
            # Try ping with timeout
            result = self.client.ping()
            if result:
                logger.info("Redis ping successful")
                return True
            else:
                logger.warning("Redis ping returned False")
                return False
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            # Try to reconnect once
            try:
                self._reconnect()
                result = self.client.ping()
                return bool(result)
            except Exception as reconnect_error:
                logger.error(f"Redis reconnection failed: {reconnect_error}")
                return False
        except redis.TimeoutError as e:
            logger.error(f"Redis timeout error: {e}")
            return False
        except Exception as e:
            logger.error(f"Redis unexpected error: {e}")
            return False
    
    def _reconnect(self):
        """Attempt to reconnect to Redis"""
        try:
            redis_config = st.secrets.get("redis", {})
            
            if "url" in redis_config and "token" in redis_config:
                url = redis_config["url"]
                token = redis_config["token"]
                
                # Extract host from URL
                if url.startswith("https://"):
                    host = url.replace("https://", "")
                elif url.startswith("redis://"):
                    host = url.replace("redis://", "")
                else:
                    host = url
                
                # Create new connection with cloud-optimized settings
                self.client = redis.Redis(
                    host=host,
                    port=6379,
                    password=token,
                    decode_responses=False,
                    ssl=True,
                    ssl_cert_reqs=None,  # Disable SSL certificate verification for cloud
                    socket_connect_timeout=15,  # Longer timeout for cloud
                    socket_timeout=15,
                    retry_on_timeout=True,
                    retry_on_error=[redis.ConnectionError, redis.TimeoutError],
                    health_check_interval=60
                )
                logger.info("Redis reconnection attempt completed")
            else:
                logger.error("Redis configuration missing for reconnection")
        except Exception as e:
            logger.error(f"Failed to reconnect to Redis: {e}")
            raise
    
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
        if self.use_rest_api:
            return self._set_rest_api(key, value, expiry_seconds)
            
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
        if self.use_rest_api:
            return self._get_rest_api(key)
            
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

@st.cache_resource
def get_cache_manager() -> RedisCacheManager:
    """Get cached Redis manager instance (singleton using Streamlit cache)"""
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