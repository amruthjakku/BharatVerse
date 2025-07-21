"""
Memory Management Utilities for BharatVerse
Optimizes memory usage and prevents memory leaks in Streamlit apps
"""

import streamlit as st
import gc
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import weakref
from functools import wraps
import tracemalloc

# Safe psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Memory management utilities for Streamlit applications
    """
    
    def __init__(self):
        self.memory_threshold_mb = 500  # MB
        self.cleanup_interval = 300  # seconds
        self.last_cleanup = datetime.now()
        self.tracked_objects = weakref.WeakSet()
        
        # Start memory tracing if not already started
        if not tracemalloc.is_tracing():
            tracemalloc.start()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        if not PSUTIL_AVAILABLE:
            # Fallback memory stats without psutil
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "percent": 0.0,
                "available_mb": 1024.0,  # Assume 1GB available
                "total_mb": 2048.0,      # Assume 2GB total
                "psutil_available": False
            }
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "total_mb": psutil.virtual_memory().total / 1024 / 1024,
                "psutil_available": True
            }
        except Exception as e:
            logger.warning(f"Failed to get memory stats: {e}")
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "percent": 0.0,
                "available_mb": 1024.0,
                "total_mb": 2048.0,
                "psutil_available": False
            }
    
    def get_memory_top_stats(self, limit: int = 10) -> List[Dict]:
        """Get top memory consuming objects"""
        if not tracemalloc.is_tracing():
            return []
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        memory_stats = []
        for stat in top_stats[:limit]:
            memory_stats.append({
                "filename": stat.traceback.format()[-1] if stat.traceback else "Unknown",
                "size_mb": stat.size / 1024 / 1024,
                "count": stat.count
            })
        
        return memory_stats
    
    def should_cleanup(self) -> bool:
        """Check if memory cleanup is needed"""
        memory_usage = self.get_memory_usage()
        time_since_cleanup = (datetime.now() - self.last_cleanup).total_seconds()
        
        return (
            memory_usage["rss_mb"] > self.memory_threshold_mb or
            time_since_cleanup > self.cleanup_interval
        )
    
    def cleanup_memory(self, force: bool = False) -> Dict[str, Any]:
        """Perform memory cleanup"""
        if not force and not self.should_cleanup():
            return {"cleaned": False, "reason": "cleanup not needed"}
        
        memory_before = self.get_memory_usage()
        
        # Clear Streamlit caches
        try:
            st.cache_data.clear()
            st.cache_resource.clear()
        except:
            pass
        
        # Clean up session state
        self._cleanup_session_state()
        
        # Clean up pandas memory
        self._cleanup_pandas_memory()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Update last cleanup time
        self.last_cleanup = datetime.now()
        
        memory_after = self.get_memory_usage()
        
        return {
            "cleaned": True,
            "memory_before_mb": memory_before["rss_mb"],
            "memory_after_mb": memory_after["rss_mb"],
            "memory_freed_mb": memory_before["rss_mb"] - memory_after["rss_mb"],
            "objects_collected": collected,
            "timestamp": datetime.now().isoformat()
        }
    
    def _cleanup_session_state(self):
        """Clean up old session state data"""
        keys_to_remove = []
        
        for key in st.session_state.keys():
            # Remove old cached data
            if key.startswith(("cached_", "temp_", "processing_")):
                keys_to_remove.append(key)
            
            # Remove large objects that haven't been accessed recently
            if hasattr(st.session_state[key], '__dict__'):
                if sys.getsizeof(st.session_state[key]) > 10 * 1024 * 1024:  # 10MB
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            try:
                del st.session_state[key]
            except:
                pass
    
    def _cleanup_pandas_memory(self):
        """Clean up pandas memory usage"""
        # Force pandas to release memory
        try:
            pd.options.mode.chained_assignment = None
            gc.collect()
        except:
            pass
    
    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage"""
        if df is None or df.empty:
            return df
        
        # Create a copy to avoid modifying original
        df_optimized = df.copy()
        
        # Optimize numeric columns
        for col in df_optimized.select_dtypes(include=['int64']).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
        
        for col in df_optimized.select_dtypes(include=['float64']).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
        
        # Optimize string columns
        for col in df_optimized.select_dtypes(include=['object']).columns:
            if df_optimized[col].dtype == 'object':
                try:
                    # Convert to category if it saves memory
                    if df_optimized[col].nunique() / len(df_optimized) < 0.5:
                        df_optimized[col] = df_optimized[col].astype('category')
                except:
                    pass
        
        return df_optimized
    
    def track_object(self, obj: Any, name: str = None):
        """Track an object for memory monitoring"""
        self.tracked_objects.add(obj)
        if name:
            setattr(obj, '_memory_tracker_name', name)
    
    def get_tracked_objects_info(self) -> List[Dict]:
        """Get information about tracked objects"""
        objects_info = []
        
        for obj in self.tracked_objects:
            try:
                info = {
                    "name": getattr(obj, '_memory_tracker_name', str(type(obj))),
                    "type": str(type(obj)),
                    "size_bytes": sys.getsizeof(obj),
                    "id": id(obj)
                }
                objects_info.append(info)
            except:
                pass
        
        return sorted(objects_info, key=lambda x: x["size_bytes"], reverse=True)

# Global memory manager instance
@st.cache_resource
def get_memory_manager() -> MemoryManager:
    """Get cached memory manager instance"""
    return MemoryManager()

# Decorators for memory management
def memory_monitor(func):
    """Decorator to monitor function memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        memory_manager = get_memory_manager()
        memory_before = memory_manager.get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            memory_after = memory_manager.get_memory_usage()
            
            # Store memory metrics
            if "memory_metrics" not in st.session_state:
                st.session_state.memory_metrics = {}
            
            st.session_state.memory_metrics[func.__name__] = {
                "memory_before_mb": memory_before["rss_mb"],
                "memory_after_mb": memory_after["rss_mb"],
                "memory_delta_mb": memory_after["rss_mb"] - memory_before["rss_mb"],
                "last_executed": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Memory monitored function {func.__name__} failed: {e}")
            raise
    
    return wrapper

def auto_cleanup(threshold_mb: int = 500):
    """Decorator to automatically cleanup memory if threshold is exceeded"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            memory_manager = get_memory_manager()
            memory_manager.memory_threshold_mb = threshold_mb
            
            # Check if cleanup is needed before execution
            if memory_manager.should_cleanup():
                cleanup_result = memory_manager.cleanup_memory()
                if cleanup_result["cleaned"]:
                    st.info(f"🧹 Memory cleaned: {cleanup_result['memory_freed_mb']:.1f}MB freed")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Streamlit components for memory management
def show_memory_dashboard():
    """Display memory usage dashboard"""
    memory_manager = get_memory_manager()
    memory_usage = memory_manager.get_memory_usage()
    
    st.subheader("💾 Memory Usage")
    
    # Show warning if psutil is not available
    if not memory_usage.get('psutil_available', True):
        st.warning("⚠️ Advanced memory monitoring unavailable (psutil not installed). Showing basic stats only.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Memory Used", 
            f"{memory_usage['rss_mb']:.1f} MB",
            help="Resident Set Size - actual physical memory used"
        )
    
    with col2:
        st.metric(
            "Memory %", 
            f"{memory_usage['percent']:.1f}%",
            help="Percentage of total system memory used"
        )
    
    with col3:
        st.metric(
            "Available", 
            f"{memory_usage['available_mb']:.1f} MB",
            help="Available system memory"
        )
    
    with col4:
        memory_status = "🟢 Good" if memory_usage['rss_mb'] < 300 else "🟡 High" if memory_usage['rss_mb'] < 500 else "🔴 Critical"
        st.metric("Status", memory_status)
    
    # Memory cleanup controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Clean Memory"):
            cleanup_result = memory_manager.cleanup_memory(force=True)
            if cleanup_result["cleaned"]:
                st.success(f"Memory cleaned! Freed {cleanup_result['memory_freed_mb']:.1f}MB")
            else:
                st.info("No cleanup needed")
    
    with col2:
        if st.button("📊 Memory Details"):
            st.session_state.show_memory_details = not st.session_state.get("show_memory_details", False)
    
    # Detailed memory information
    if st.session_state.get("show_memory_details", False):
        st.markdown("---")
        st.subheader("🔍 Memory Details")
        
        # Top memory consumers
        top_stats = memory_manager.get_memory_top_stats()
        if top_stats:
            st.markdown("**Top Memory Consumers:**")
            for i, stat in enumerate(top_stats[:5], 1):
                st.text(f"{i}. {stat['filename']}: {stat['size_mb']:.2f}MB ({stat['count']} objects)")
        
        # Tracked objects
        tracked_objects = memory_manager.get_tracked_objects_info()
        if tracked_objects:
            st.markdown("**Tracked Objects:**")
            df_objects = pd.DataFrame(tracked_objects)
            df_objects['size_mb'] = df_objects['size_bytes'] / 1024 / 1024
            st.dataframe(df_objects[['name', 'type', 'size_mb']].head(10))
        
        # Session state memory usage
        if hasattr(st.session_state, 'keys'):
            st.markdown("**Session State Memory:**")
            session_memory = []
            for key in st.session_state.keys():
                try:
                    size_bytes = sys.getsizeof(st.session_state[key])
                    session_memory.append({
                        "key": key,
                        "size_mb": size_bytes / 1024 / 1024,
                        "type": str(type(st.session_state[key]))
                    })
                except:
                    pass
            
            if session_memory:
                df_session = pd.DataFrame(session_memory)
                df_session = df_session.sort_values('size_mb', ascending=False)
                st.dataframe(df_session.head(10))

@st.cache_data(ttl=60, show_spinner=False)
def get_memory_recommendations() -> List[str]:
    """Get memory optimization recommendations"""
    memory_manager = get_memory_manager()
    memory_usage = memory_manager.get_memory_usage()
    
    recommendations = []
    
    if memory_usage['rss_mb'] > 400:
        recommendations.append("🔴 High memory usage detected. Consider clearing caches.")
    
    if memory_usage['percent'] > 80:
        recommendations.append("⚠️ System memory is running low. Close other applications.")
    
    # Check session state size
    session_size = 0
    try:
        for key in st.session_state.keys():
            session_size += sys.getsizeof(st.session_state[key])
    except:
        pass
    
    if session_size > 50 * 1024 * 1024:  # 50MB
        recommendations.append("📦 Large session state detected. Consider using external storage.")
    
    if not recommendations:
        recommendations.append("✅ Memory usage is optimal.")
    
    return recommendations

# Utility functions
def optimize_large_dataframe(df: pd.DataFrame, chunk_size: int = 10000) -> pd.DataFrame:
    """Optimize large DataFrame by processing in chunks"""
    if len(df) <= chunk_size:
        return get_memory_manager().optimize_dataframe(df)
    
    optimized_chunks = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        optimized_chunk = get_memory_manager().optimize_dataframe(chunk)
        optimized_chunks.append(optimized_chunk)
    
    return pd.concat(optimized_chunks, ignore_index=True)

def memory_efficient_json_load(file_path: str, chunk_size: int = 1000):
    """Load large JSON files in a memory-efficient way"""
    import json
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # If it's a list, process in chunks
        if isinstance(data, list) and len(data) > chunk_size:
            for i in range(0, len(data), chunk_size):
                yield data[i:i+chunk_size]
        else:
            yield data
    
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        yield None

# Context manager for temporary memory tracking
class MemoryTracker:
    """Context manager for tracking memory usage of code blocks"""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.memory_manager = get_memory_manager()
        self.start_memory = None
        self.end_memory = None
    
    def __enter__(self):
        self.start_memory = self.memory_manager.get_memory_usage()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_memory = self.memory_manager.get_memory_usage()
        
        memory_delta = self.end_memory["rss_mb"] - self.start_memory["rss_mb"]
        
        if "memory_tracking" not in st.session_state:
            st.session_state.memory_tracking = {}
        
        st.session_state.memory_tracking[self.name] = {
            "memory_delta_mb": memory_delta,
            "start_memory_mb": self.start_memory["rss_mb"],
            "end_memory_mb": self.end_memory["rss_mb"],
            "timestamp": datetime.now().isoformat()
        }
        
        if memory_delta > 10:  # Log if memory increased by more than 10MB
            logger.warning(f"Memory increased by {memory_delta:.1f}MB during {self.name}")
    
    def get_memory_delta(self) -> float:
        """Get memory delta in MB"""
        if self.start_memory and self.end_memory:
            return self.end_memory["rss_mb"] - self.start_memory["rss_mb"]
        return 0.0