"""
Clean Page Template for BharatVerse
Provides a consistent structure for all pages with proper service management
"""

import streamlit as st
from typing import List, Optional, Callable, Dict, Any
from functools import wraps
from .service_manager import get_service_manager
from .config_manager import get_config_manager, get_ui_config
from .error_handler import error_boundary, show_service_status, show_error_message
from .module_loader import load_module

class PageTemplate:
    """Base template for BharatVerse pages"""
    
    def __init__(
        self,
        title: str,
        icon: str,
        description: str = "",
        required_services: List[str] = None,
        optional_services: List[str] = None
    ):
        self.title = title
        self.icon = icon
        self.description = description
        self.required_services = required_services or []
        self.optional_services = optional_services or []
        self.service_manager = get_service_manager()
        self.config_manager = get_config_manager()
    
    def setup_page(self):
        """Setup page configuration"""
        ui_config = get_ui_config()
        st.set_page_config(
            page_title=f"{self.title} - BharatVerse",
            page_icon=self.icon,
            **ui_config
        )
        
        # Apply styling if available
        with error_boundary("Failed to load styling", show_error=False):
            styling_module = load_module("streamlit_app.utils.main_styling")
            if styling_module and hasattr(styling_module, "load_custom_css"):
                styling_module.load_custom_css()
    
    def check_requirements(self) -> bool:
        """Check if all required services are available"""
        missing_services = []
        
        for service in self.required_services:
            if not self.service_manager.is_available(service):
                missing_services.append(service)
        
        if missing_services:
            st.error(f"🚫 Required services not available: {', '.join(missing_services)}")
            
            # Show service status
            show_service_status(self.service_manager, self.required_services + self.optional_services)
            
            # Show specific error messages
            for service in missing_services:
                error = self.service_manager.get_error(service)
                if error:
                    with st.expander(f"🔍 {service.title()} Error Details"):
                        st.code(error)
            
            return False
        
        return True
    
    def render_header(self):
        """Render page header"""
        st.markdown(f"# {self.icon} {self.title}")
        if self.description:
            st.markdown(self.description)
    
    def render_service_status(self, show_admin_only: bool = True):
        """Render service status for debugging"""
        if show_admin_only and st.session_state.get("user_role") != "admin":
            return
        
        with st.expander("🔧 Service Status", expanded=False):
            show_service_status(
                self.service_manager, 
                self.required_services + self.optional_services
            )
    
    def render(self, content_func: Callable):
        """Render the complete page"""
        self.setup_page()
        
        if not self.check_requirements():
            return
        
        self.render_header()
        self.render_service_status()
        
        # Render main content with error boundary
        with error_boundary(f"Error in {self.title}"):
            content_func()

def create_page(
    title: str,
    icon: str,
    description: str = "",
    required_services: List[str] = None,
    optional_services: List[str] = None
):
    """Decorator to create a clean page"""
    def decorator(func):
        @wraps(func)
        def wrapper():
            template = PageTemplate(
                title=title,
                icon=icon,
                description=description,
                required_services=required_services,
                optional_services=optional_services
            )
            template.render(func)
        return wrapper
    return decorator

def require_auth(redirect_to_login: bool = True):
    """Decorator to require authentication"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service_manager = get_service_manager()
            
            if not service_manager.is_available("auth"):
                show_error_message("auth_required", "Authentication service not available")
                return
            
            auth_service = service_manager.get_service("auth")
            
            # Check if user is authenticated (implementation depends on auth service)
            if not st.session_state.get("authenticated", False):
                if redirect_to_login:
                    st.warning("🔒 Please log in to access this page")
                    # Add login interface here
                    return
                else:
                    show_error_message("auth_required")
                    return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """Decorator to require admin privileges"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if st.session_state.get("user_role") != "admin":
                show_error_message("admin_required")
                return
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Common page configurations
COMMON_PAGES = {
    "audio": {
        "title": "Audio Capture",
        "icon": "🎤",
        "description": "Record folk songs, stories, and oral traditions in your language.",
        "required_services": ["audio"],
        "optional_services": ["ai", "storage", "database"]
    },
    "text": {
        "title": "Text Stories",
        "icon": "📝",
        "description": "Write and share cultural stories, traditions, and historical accounts.",
        "required_services": [],
        "optional_services": ["ai", "database", "storage"]
    },
    "visual": {
        "title": "Visual Heritage",
        "icon": "📸",
        "description": "Upload and analyze cultural artifacts, photographs, and artwork.",
        "required_services": ["storage"],
        "optional_services": ["ai", "database"]
    },
    "community": {
        "title": "Community",
        "icon": "🤝",
        "description": "Connect with other cultural heritage enthusiasts.",
        "required_services": ["database", "auth"],
        "optional_services": ["storage"]
    },
    "admin": {
        "title": "Admin Dashboard",
        "icon": "🛡️",
        "description": "Administrative tools and system monitoring.",
        "required_services": ["auth", "database"],
        "optional_services": ["storage", "cache", "memory"]
    }
}

def get_page_config(page_type: str) -> Dict[str, Any]:
    """Get configuration for a common page type"""
    return COMMON_PAGES.get(page_type, {})

# Example usage:
# @create_page(**get_page_config("audio"))
# def audio_page():
#     st.write("Audio page content here")
#
# if __name__ == "__main__":
#     audio_page()