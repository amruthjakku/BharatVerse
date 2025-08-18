"""
Page initialization helper with authentication and common setup
"""
import streamlit as st
from typing import Optional, Dict, Any
from .auth import init_auth


def init_page(
    page_title: str,
    page_icon: str = "🏛️",
    layout: str = "wide",
    require_auth: bool = True,
    require_admin: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Initialize a page with common settings and authentication
    
    Args:
        page_title: Title of the page
        page_icon: Icon for the page
        layout: Page layout (wide, centered)
        require_auth: Whether authentication is required
        require_admin: Whether admin privileges are required
        
    Returns:
        User information if authenticated, None if auth not required
    """
    # Set page config
    st.set_page_config(
        page_title=f"{page_title} - BharatVerse",
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    
    # Initialize authentication
    user_info = init_auth()
    
    # Check authentication requirements
    if require_auth and not user_info:
        st.warning("🔒 Please log in to access this page")
        st.stop()
        return None
    
    # Check admin requirements
    if require_admin and user_info:
        # Check if user has admin role
        # For now, we'll check if username is in a list of admins
        # Later this should check the database for user roles
        admin_users = ["admin", "aj3"]  # Add your admin usernames here
        
        if user_info.get('username') not in admin_users:
            st.error("⛔ Access denied. Admin privileges required.")
            st.stop()
            return None
    
    return user_info


def show_page_header(title: str, subtitle: str = "", icon: str = ""):
    """
    Display a consistent page header
    
    Args:
        title: Main title of the page
        subtitle: Optional subtitle
        icon: Optional icon to display
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        ">
            {icon} {title}
        </h1>
        {f'<p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def show_construction_message(feature_name: str = "This feature"):
    """
    Display a construction message for features being built
    
    Args:
        feature_name: Name of the feature being built
    """
    st.info(f"🚧 {feature_name} is currently under construction. Check back soon!")
    
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        text-align: center;
    ">
        <h3>Coming Soon</h3>
        <p>We're working hard to bring you this feature. In the meantime, feel free to explore other sections of the platform!</p>
    </div>
    """, unsafe_allow_html=True)


def check_database_connection() -> bool:
    """
    Check if database connection is available
    
    Returns:
        True if database is connected, False otherwise
    """
    try:
        from core.database import get_db_manager
        db_manager = get_db_manager()
        return db_manager.is_connected() if db_manager else False
    except:
        return False
