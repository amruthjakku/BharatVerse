"""
Performance Optimizer for BharatVerse
Implements comprehensive caching, lazy loading, and performance strategies
"""

import streamlit as st
import asyncio
import concurrent.futures
import hashlib
import json
import time
from functools import wraps
from typing import Any, Dict, List, Optional, Callable
import logging
from datetime import datetime, timedelta

# Import existing utilities with fallbacks
from utils.redis_cache import get_cache_manager
from utils.supabase_db import get_database_manager

try:
    from utils.minio_storage import get_storage_manager
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    from utils.fallback_storage import get_fallback_storage_manager as get_storage_manager

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Comprehensive performance optimization manager
    Implements caching, lazy loading, and async operations
    """
    
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.db_manager = get_database_manager()
        self.storage_manager = get_storage_manager()
        
        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "db_queries": 0,
            "api_calls": 0,
            "load_times": []
        }
    
    def track_performance(self, operation_name: str):
        """Decorator to track operation performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Store metrics in session state
                    if "performance_metrics" not in st.session_state:
                        st.session_state.performance_metrics = {}
                    
                    st.session_state.performance_metrics[operation_name] = {
                        "last_execution_time": execution_time,
                        "last_executed": datetime.now().isoformat(),
                        "success": True
                    }
                    
                    self.metrics["load_times"].append(execution_time)
                    logger.info(f"{operation_name} completed in {execution_time:.3f}s")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    if "performance_metrics" not in st.session_state:
                        st.session_state.performance_metrics = {}
                    
                    st.session_state.performance_metrics[operation_name] = {
                        "last_execution_time": execution_time,
                        "last_executed": datetime.now().isoformat(),
                        "success": False,
                        "error": str(e)
                    }
                    
                    logger.error(f"{operation_name} failed after {execution_time:.3f}s: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def lazy_load_component(self, component_key: str, loader_func: Callable, 
                           trigger_condition: bool = True, 
                           cache_ttl: int = 3600) -> Any:
        """
        Lazy load components with caching
        
        Args:
            component_key: Unique key for the component
            loader_func: Function to load the component
            trigger_condition: Condition to trigger loading
            cache_ttl: Cache time-to-live in seconds
        """
        if not trigger_condition:
            return None
        
        # Check session state first
        session_key = f"lazy_loaded_{component_key}"
        if session_key in st.session_state:
            return st.session_state[session_key]
        
        # Check Redis cache
        cache_key = f"lazy_component:{component_key}"
        if self.cache_manager and self.cache_manager.is_connected():
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                st.session_state[session_key] = cached_data
                self.metrics["cache_hits"] += 1
                return cached_data
        
        # Load component
        try:
            with st.spinner(f"Loading {component_key}..."):
                data = loader_func()
                
                # Cache in session state
                st.session_state[session_key] = data
                
                # Cache in Redis
                if self.cache_manager and self.cache_manager.is_connected():
                    self.cache_manager.set(cache_key, data, cache_ttl)
                
                self.metrics["cache_misses"] += 1
                return data
                
        except Exception as e:
            logger.error(f"Failed to lazy load {component_key}: {e}")
            return None
    
    def batch_database_operations(self, operations: List[Dict]) -> List[Any]:
        """
        Batch multiple database operations for efficiency
        
        Args:
            operations: List of operation dictionaries with 'query' and 'params'
        """
        if not self.db_manager:
            return []
        
        results = []
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    for operation in operations:
                        cursor.execute(operation['query'], operation.get('params', {}))
                        if cursor.description:
                            results.append([dict(row) for row in cursor.fetchall()])
                        else:
                            results.append(None)
                    conn.commit()
            
            self.metrics["db_queries"] += len(operations)
            logger.info(f"Executed {len(operations)} database operations in batch")
            
        except Exception as e:
            logger.error(f"Batch database operations failed: {e}")
            results = [None] * len(operations)
        
        return results
    
    def parallel_api_calls(self, api_functions: List[Callable]) -> List[Any]:
        """
        Execute multiple API calls in parallel using ThreadPoolExecutor
        
        Args:
            api_functions: List of callable functions for API calls
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_func = {executor.submit(func): func for func in api_functions}
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_func):
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                except Exception as e:
                    logger.error(f"Parallel API call failed: {e}")
                    results.append(None)
        
        self.metrics["api_calls"] += len(api_functions)
        return results
    
    def warm_up_services(self) -> Dict[str, bool]:
        """
        Warm up external services to avoid cold starts
        """
        warmup_results = {}
        
        # Warm up Redis
        if self.cache_manager:
            try:
                self.cache_manager.set("warmup_test", "test", 60)
                self.cache_manager.get("warmup_test")
                warmup_results["redis"] = True
            except Exception as e:
                logger.error(f"Redis warmup failed: {e}")
                warmup_results["redis"] = False
        
        # Warm up Database
        if self.db_manager:
            try:
                self.db_manager.execute_query("SELECT 1")
                warmup_results["database"] = True
            except Exception as e:
                logger.error(f"Database warmup failed: {e}")
                warmup_results["database"] = False
        
        # Warm up Storage
        if self.storage_manager:
            try:
                # Test storage connection
                warmup_results["storage"] = self.storage_manager.test_connection()
            except Exception as e:
                logger.error(f"Storage warmup failed: {e}")
                warmup_results["storage"] = False
        
        return warmup_results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (self.metrics["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
        
        avg_load_time = sum(self.metrics["load_times"]) / len(self.metrics["load_times"]) if self.metrics["load_times"] else 0
        
        return {
            "cache_hit_rate": round(cache_hit_rate, 2),
            "total_cache_operations": cache_total,
            "database_queries": self.metrics["db_queries"],
            "api_calls": self.metrics["api_calls"],
            "average_load_time": round(avg_load_time, 3),
            "session_metrics": st.session_state.get("performance_metrics", {})
        }

# Global optimizer instance
@st.cache_resource
def get_performance_optimizer() -> PerformanceOptimizer:
    """Get cached performance optimizer instance"""
    return PerformanceOptimizer()

# Streamlit-specific optimizations
@st.cache_data(ttl=3600, show_spinner=False)
def cached_user_contributions(user_id: int, limit: int = 50) -> List[Dict]:
    """Cache user contributions with Streamlit caching"""
    db_manager = get_database_manager()
    if db_manager:
        return db_manager.get_contributions(user_id=user_id, limit=limit)
    return []

@st.cache_data(ttl=1800, show_spinner=False)
def cached_analytics_data(date_range: tuple, metrics: List[str]) -> Dict[str, Any]:
    """Cache analytics data with Streamlit caching"""
    db_manager = get_database_manager()
    if not db_manager:
        return {}
    
    # Implement analytics query based on date_range and metrics
    # This is a placeholder - implement actual analytics logic
    return {
        "total_contributions": 0,
        "active_users": 0,
        "popular_languages": [],
        "engagement_metrics": {}
    }

@st.cache_data(ttl=7200, show_spinner=False)
def cached_search_results(query: str, filters: Dict, limit: int = 50) -> List[Dict]:
    """Cache search results with Streamlit caching"""
    db_manager = get_database_manager()
    if not db_manager:
        return []
    
    # Implement search logic based on query and filters
    # This is a placeholder - implement actual search logic
    return []

@st.cache_resource
def get_ml_models():
    """Cache ML models in memory (persists across reruns)"""
    # This would load and cache ML models
    # Placeholder for actual model loading
    return {
        "text_classifier": None,
        "sentiment_analyzer": None,
        "language_detector": None
    }

# Performance monitoring utilities
def show_performance_dashboard():
    """Display performance metrics dashboard"""
    optimizer = get_performance_optimizer()
    metrics = optimizer.get_performance_metrics()
    
    st.subheader("⚡ Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cache Hit Rate", f"{metrics['cache_hit_rate']}%")
    
    with col2:
        st.metric("Avg Load Time", f"{metrics['average_load_time']}s")
    
    with col3:
        st.metric("DB Queries", metrics['database_queries'])
    
    with col4:
        st.metric("API Calls", metrics['api_calls'])
    
    # Show session metrics
    if metrics['session_metrics']:
        st.subheader("📊 Session Operations")
        for operation, data in metrics['session_metrics'].items():
            with st.expander(f"{operation} - {data['last_execution_time']:.3f}s"):
                st.json(data)

def clear_all_caches():
    """Clear all caches for fresh start"""
    # Clear Streamlit caches
    st.cache_data.clear()
    st.cache_resource.clear()
    
    # Clear Redis cache
    cache_manager = get_cache_manager()
    if cache_manager and cache_manager.is_connected():
        cache_manager.flush_pattern("*")
    
    # Clear session state
    for key in list(st.session_state.keys()):
        if key.startswith(("lazy_loaded_", "cached_", "performance_")):
            del st.session_state[key]
    
    st.success("🧹 All caches cleared successfully!")

# Loading indicators and UX improvements
@st.fragment
def show_loading_placeholder(message: str = "Loading..."):
    """Show loading placeholder with spinner"""
    placeholder = st.empty()
    with placeholder:
        with st.spinner(message):
            time.sleep(0.1)  # Brief pause for visual feedback
    return placeholder

def progressive_loading_container():
    """Create a container for progressive loading"""
    container = st.container()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    return container, progress_bar, status_text

# Memory optimization utilities
def optimize_dataframe_memory(df):
    """Optimize pandas DataFrame memory usage"""
    if df is None or df.empty:
        return df
    
    # Optimize numeric columns
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Optimize string columns
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # If less than 50% unique values
            df[col] = df[col].astype('category')
    
    return df