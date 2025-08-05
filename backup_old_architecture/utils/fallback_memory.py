"""
Fallback Memory Manager for BharatVerse
Provides basic memory management when psutil is not available
"""

import streamlit as st
import gc
import sys
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FallbackMemoryTracker:
    """Fallback memory tracker that does nothing"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def get_memory_delta(self) -> float:
        return 0.0

class FallbackMemoryManager:
    """Fallback memory manager without psutil dependency"""
    
    def __init__(self):
        self.memory_threshold_mb = 500  # MB
        self.cleanup_interval = 300  # seconds
        self.last_cleanup = datetime.now()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get basic memory usage statistics without psutil"""
        return {
            "rss_mb": 0.0,
            "vms_mb": 0.0,
            "percent": 0.0,
            "available_mb": 1024.0,  # Assume 1GB available
            "total_mb": 2048.0,      # Assume 2GB total
            "psutil_available": False
        }
    
    def get_memory_top_stats(self, limit: int = 10) -> List[Dict]:
        """Get basic memory stats without detailed tracking"""
        return []
    
    def should_cleanup(self) -> bool:
        """Check if memory cleanup is needed based on time"""
        time_since_cleanup = (datetime.now() - self.last_cleanup).total_seconds()
        return time_since_cleanup > self.cleanup_interval
    
    def cleanup_memory(self, force: bool = False) -> Dict[str, Any]:
        """Perform basic memory cleanup"""
        if not force and not self.should_cleanup():
            return {"cleaned": False, "reason": "cleanup not needed"}
        
        # Clear Streamlit caches
        try:
            st.cache_data.clear()
            st.cache_resource.clear()
        except:
            pass
        
        # Clean up session state (keep important keys)
        important_keys = ['_persistent_auth', 'user_info', 'access_token']
        keys_to_remove = [
            key for key in st.session_state.keys() 
            if not key.startswith('_') and key not in important_keys
        ]
        
        for key in keys_to_remove:
            try:
                del st.session_state[key]
            except:
                pass
        
        # Force garbage collection
        collected = gc.collect()
        
        # Update last cleanup time
        self.last_cleanup = datetime.now()
        
        return {
            "cleaned": True,
            "objects_collected": collected,
            "method": "fallback",
            "psutil_available": False
        }
    
    def track_object(self, obj):
        """Placeholder for object tracking"""
        pass
    
    def get_session_size(self) -> int:
        """Get approximate session state size"""
        return len(st.session_state)

# Global fallback memory manager instance
@st.cache_resource
def get_fallback_memory_manager() -> FallbackMemoryManager:
    """Get cached fallback memory manager instance"""
    return FallbackMemoryManager()

def show_fallback_memory_dashboard():
    """Display basic memory dashboard without psutil"""
    memory_manager = get_fallback_memory_manager()
    
    st.subheader("💾 Basic Memory Management")
    st.info("ℹ️ Advanced memory monitoring requires psutil package")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Session Objects", memory_manager.get_session_size())
    
    with col2:
        st.metric("Status", "🟢 Basic")
    
    # Memory cleanup controls
    if st.button("🧹 Clean Memory (Basic)"):
        cleanup_result = memory_manager.cleanup_memory(force=True)
        if cleanup_result["cleaned"]:
            st.success(f"✅ Memory cleaned! Collected {cleanup_result['objects_collected']} objects")
        else:
            st.info("ℹ️ No cleanup needed")
    
    # Show session state info
    if st.checkbox("Show Session State Info"):
        session_keys = [k for k in st.session_state.keys() if not k.startswith('_')]
        st.write(f"Session state keys: {len(session_keys)}")
        if session_keys:
            st.write("Keys:", ", ".join(session_keys[:10]))
            if len(session_keys) > 10:
                st.write(f"... and {len(session_keys) - 10} more")