"""
Dynamic Navigation System for BharatVerse
Handles role-based navigation and page access control
"""

import streamlit as st
from streamlit_app.utils.demo_auth import demo_auth

def show_navigation_info():
    """Show navigation information in sidebar based on user role"""
    
    # Always show user info
    demo_auth.show_user_info()
    
    # Show role-based navigation info
    if demo_auth.is_authenticated():
        current_user = demo_auth.get_current_user()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🧭 Navigation Guide")
        
        if demo_auth.is_admin():
            st.sidebar.success("🛡️ **Admin Access**")
            st.sidebar.markdown("You have access to:")
            st.sidebar.markdown("• All community features")
            st.sidebar.markdown("• Admin dashboard")
            st.sidebar.markdown("• User management")
            st.sidebar.markdown("• System analytics")
        else:
            st.sidebar.info("👤 **User Access**")
            st.sidebar.markdown("You have access to:")
            st.sidebar.markdown("• Community features")
            st.sidebar.markdown("• Content creation")
            st.sidebar.markdown("• Profile management")
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("**Need admin access?**")
            st.sidebar.markdown("Login as 'demo_user' for admin privileges")
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔐 Login Required")
        st.sidebar.info("Login to access community features and personalized content")

def check_admin_access():
    """Check if current user has admin access"""
    if not demo_auth.is_authenticated():
        return False, "Please login to access this feature"
    
    if not demo_auth.is_admin():
        return False, "Admin privileges required"
    
    return True, "Access granted"

def show_access_denied(message="Access denied"):
    """Show access denied message with login options"""
    st.error(f"🚫 {message}")
    
    if not demo_auth.is_authenticated():
        st.info("Please login to continue")
        demo_auth.show_login_form()
    else:
        current_user = demo_auth.get_current_user()
        st.info(f"Logged in as: {current_user['full_name']} ({current_user['username']})")
        st.markdown("You don't have sufficient privileges for this action.")
        
        if st.button("🚪 Logout and Switch User"):
            demo_auth.logout()

def get_user_role_display():
    """Get user role for display purposes"""
    if not demo_auth.is_authenticated():
        return "Guest"
    
    if demo_auth.is_admin():
        return "Administrator"
    
    return "User"

def show_feature_access_info():
    """Show what features are available to current user"""
    role = get_user_role_display()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🎯 Available Features ({role})")
    
    if role == "Guest":
        st.sidebar.markdown("**Public Access:**")
        st.sidebar.markdown("• Browse public content")
        st.sidebar.markdown("• View documentation")
        st.sidebar.markdown("• Learn about BharatVerse")
        
    elif role == "User":
        st.sidebar.markdown("**User Features:**")
        st.sidebar.markdown("• 🤝 Community groups")
        st.sidebar.markdown("• 💬 Chat and discussions")
        st.sidebar.markdown("• 🎯 Challenges")
        st.sidebar.markdown("• 👤 Profile management")
        st.sidebar.markdown("• 🎤 Content creation")
        
    elif role == "Administrator":
        st.sidebar.markdown("**Admin Features:**")
        st.sidebar.markdown("• 🛡️ Admin dashboard")
        st.sidebar.markdown("• 👥 User management")
        st.sidebar.markdown("• 📊 System analytics")
        st.sidebar.markdown("• ⚙️ System configuration")
        st.sidebar.markdown("• All user features")

def require_authentication(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if not demo_auth.is_authenticated():
            st.warning("🔐 Authentication required")
            st.info("Please login to access this feature")
            demo_auth.show_login_form()
            return None
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin privileges for a function"""
    def wrapper(*args, **kwargs):
        if not demo_auth.is_authenticated():
            st.error("🔐 Authentication required")
            st.info("Please login as an administrator to access this feature")
            demo_auth.show_login_form()
            return None
        
        if not demo_auth.is_admin():
            st.error("🚫 Admin privileges required")
            current_user = demo_auth.get_current_user()
            st.info(f"Logged in as: {current_user['full_name']} ({current_user['username']})")
            st.markdown("You need administrator privileges to access this feature.")
            st.markdown("**Note:** Login as 'demo_user' for admin access")
            
            if st.button("🚪 Logout and Switch User"):
                demo_auth.logout()
            return None
            
        return func(*args, **kwargs)
    return wrapper