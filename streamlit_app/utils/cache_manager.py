"""
Cache Manager for BharatVerse
Implements caching strategies for improved performance
"""

import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps
import pickle
from pathlib import Path

class CacheManager:
    """Manages caching for various operations in BharatVerse"""
    
    def __init__(self, cache_dir="data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}
        
    def get_cache_key(self, *args, **kwargs):
        """Generate a unique cache key based on arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cache_result(self, ttl_minutes=60):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.get_cache_key(func.__name__, *args, **kwargs)
                
                # Check memory cache first
                if cache_key in self.memory_cache:
                    cached_data, timestamp = self.memory_cache[cache_key]
                    if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
                        return cached_data
                
                # Check disk cache
                cache_file = self.cache_dir / f"{cache_key}.pkl"
                if cache_file.exists():
                    try:
                        with open(cache_file, 'rb') as f:
                            cached_data, timestamp = pickle.load(f)
                        if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
                            # Update memory cache
                            self.memory_cache[cache_key] = (cached_data, timestamp)
                            return cached_data
                    except:
                        pass
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                timestamp = datetime.now()
                
                # Save to memory cache
                self.memory_cache[cache_key] = (result, timestamp)
                
                # Save to disk cache
                try:
                    with open(cache_file, 'wb') as f:
                        pickle.dump((result, timestamp), f)
                except:
                    pass
                
                return result
            return wrapper
        return decorator
    
    def invalidate_cache(self, pattern=None):
        """Invalidate cache entries matching pattern"""
        # Clear memory cache
        if pattern:
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            if pattern is None or pattern in cache_file.stem:
                cache_file.unlink()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        memory_entries = len(self.memory_cache)
        disk_entries = len(list(self.cache_dir.glob("*.pkl")))
        
        total_disk_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        disk_size_mb = total_disk_size / (1024 * 1024)
        
        return {
            "memory_entries": memory_entries,
            "disk_entries": disk_entries,
            "disk_size_mb": round(disk_size_mb, 2)
        }

# Singleton instance
cache_manager = CacheManager()

# Streamlit-specific caching utilities
@st.cache_data(ttl=3600)
def cached_search_results(query, filters):
    """Cache search results in Streamlit"""
    # This would be replaced with actual search logic
    return perform_search(query, filters)

@st.cache_data(ttl=7200)
def cached_analytics_data(date_range, metrics):
    """Cache analytics data in Streamlit"""
    # This would be replaced with actual analytics logic
    return calculate_analytics(date_range, metrics)

@st.cache_resource
def get_ml_models():
    """Cache ML models in Streamlit (persists across reruns)"""
    # This would load ML models once and keep them in memory
    return load_ml_models()

# Helper functions (to be implemented)
def perform_search(query, filters):
    """Placeholder for search functionality"""
    pass

def calculate_analytics(date_range, metrics):
    """Placeholder for analytics calculation"""
    pass

def load_ml_models():
    """Placeholder for ML model loading"""
    pass
