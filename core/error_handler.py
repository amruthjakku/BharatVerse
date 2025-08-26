"""
Simplified Error Handling for BharatVerse
Replaces scattered try/except blocks with consistent error handling
"""

import streamlit as st
import logging
from typing import Any
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class BharatVerseError(Exception):
    """Base exception for BharatVerse"""

class ServiceUnavailableError(BharatVerseError):
    """Raised when a required service is unavailable"""

class ConfigurationError(BharatVerseError):
    """Raised when configuration is invalid"""

def handle_errors(
    fallback_value: Any = None,
    show_error: bool = True,
    error_message: str = None,
    log_error: bool = True
):
    """Decorator for consistent error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}")
                
                if show_error:
                    display_message = error_message or f"Error in {func.__name__}: {str(e)}"
                    st.error(display_message)
                
                return fallback_value
        return wrapper
    return decorator

@contextmanager
def error_boundary(
    error_message: str = "An error occurred",
    show_error: bool = True,
    log_error: bool = True
):
    """Context manager for error boundaries"""
    try:
        yield
    except Exception as e:
        if log_error:
            logger.error(f"Error in boundary: {e}")
        
        if show_error:
            st.error(f"{error_message}: {str(e)}")

def safe_import(module_name: str, fallback=None):
    """Safely import a module with fallback"""
    try:
        parts = module_name.split('.')
        module = __import__(module_name)
        for part in parts[1:]:
            module = getattr(module, part)
        return module
    except ImportError as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        return fallback

def require_service_ui(service_name: str, service_manager, alternative_message: str = None):
    """UI helper to require a service and show alternatives if not available"""
    if not service_manager.is_available(service_name):
        error_msg = service_manager.get_error(service_name)
        
        st.error(f"🚫 {service_name.title()} service is not available")
        
        if error_msg:
            with st.expander("🔍 Error Details"):
                st.code(error_msg)
        
        if alternative_message:
            st.info(alternative_message)
        
        return False
    return True

def show_service_status(service_manager, services: list = None):
    """Show service status in UI"""
    if services is None:
        services = list(service_manager.list_services().keys())
    
    st.subheader("🔧 Service Status")
    
    cols = st.columns(min(len(services), 4))
    
    for i, service in enumerate(services):
        with cols[i % len(cols)]:
            status = service_manager.get_status(service)
            if status.value == "available":
                st.success(f"✅ {service.title()}")
            elif status.value == "error":
                st.error(f"❌ {service.title()}")
                error = service_manager.get_error(service)
                if error:
                    st.caption(f"Error: {error[:50]}...")
            else:
                st.warning(f"⚠️ {service.title()}")

class GracefulDegradation:
    """Helper for graceful feature degradation"""
    
    @staticmethod
    def audio_features(service_manager):
        """Handle audio feature degradation"""
        audio_service = service_manager.get_service("audio")
        
        if not audio_service:
            st.warning("🎤 Audio recording not available")
            st.info("📁 You can still upload pre-recorded audio files")
            return "upload_only"
        
        backend = audio_service.get("backend", "unknown")
        
        if backend == "upload_only":
            st.info("🎤 Live recording not available in this environment")
            st.info("📁 File upload is supported")
            return "upload_only"
        
        return "full"
    
    @staticmethod
    def ai_features(service_manager):
        """Handle AI feature degradation"""
        if service_manager.is_available("ai"):
            return "full"
        elif service_manager.is_available("cloud_ai"):
            st.info("🤖 Using cloud AI services")
            return "cloud"
        else:
            st.warning("🤖 AI features not available")
            st.info("📝 Basic text processing is still available")
            return "basic"
    
    @staticmethod
    def storage_features(service_manager):
        """Handle storage feature degradation"""
        if service_manager.is_available("minio"):
            return "full"
        elif service_manager.is_available("storage"):
            st.info("💾 Using fallback storage (session-based)")
            st.warning("⚠️ Files will be lost when session ends")
            return "fallback"
        else:
            st.error("💾 No storage available")
            return "none"

def create_feature_gate(service_name: str, feature_name: str):
    """Create a feature gate that checks service availability"""
    def gate_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from core.service_manager import get_service_manager
            service_manager = get_service_manager()
            
            if not service_manager.is_available(service_name):
                st.warning(f"🚫 {feature_name} is not available")
                error = service_manager.get_error(service_name)
                if error:
                    with st.expander("🔍 Details"):
                        st.code(error)
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return gate_decorator

# Common error messages
ERROR_MESSAGES = {
    "auth_required": "🔒 Authentication required to access this feature",
    "admin_required": "👑 Admin privileges required",
    "service_unavailable": "🚫 This service is currently unavailable",
    "configuration_error": "⚙️ Configuration error - please check your settings",
    "network_error": "🌐 Network error - please check your connection",
    "file_error": "📁 File operation failed",
    "database_error": "🗄️ Database operation failed",
}

def show_error_message(error_type: str, details: str = None):
    """Show standardized error message"""
    message = ERROR_MESSAGES.get(error_type, "❌ An error occurred")
    st.error(message)
    
    if details:
        with st.expander("🔍 Error Details"):
            st.code(details)