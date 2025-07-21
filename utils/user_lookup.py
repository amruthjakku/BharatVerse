"""
Quick User Lookup Utilities for BharatVerse
Simple functions to find and display user information
"""

import streamlit as st
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime

def quick_user_lookup(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Quick lookup for a user by username, email, or ID
    
    Args:
        identifier: Username, email, or user ID to search for
        
    Returns:
        User data dictionary or None if not found
    """
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search by username, email, or ID
        cursor.execute("""
            SELECT * FROM users 
            WHERE username = ? OR email = ? OR id = ?
            LIMIT 1
        """, (identifier, identifier, identifier))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
        
    except Exception as e:
        st.error(f"User lookup error: {e}")
        return None

def get_user_count() -> int:
    """Get total number of users in the database"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
        
    except Exception:
        return 0

def get_recent_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Get most recently registered users"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, email, full_name, created_at, role
            FROM users 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return users
        
    except Exception:
        return []

def display_user_card(user_data: Dict[str, Any]):
    """Display a user information card"""
    if not user_data:
        st.error("No user data provided")
        return
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # User avatar placeholder
            st.markdown("👤")
        
        with col2:
            st.markdown(f"**{user_data.get('full_name', 'No name')}**")
            st.markdown(f"@{user_data.get('username', 'unknown')}")
            st.caption(f"📧 {user_data.get('email', 'No email')}")
            
            # Additional info
            if user_data.get('role'):
                st.badge(user_data['role'].title())
            
            if user_data.get('region'):
                st.caption(f"📍 {user_data['region']}")
            
            if user_data.get('created_at'):
                created = user_data['created_at']
                st.caption(f"📅 Joined: {created}")

def show_user_search_widget():
    """Display a user search widget"""
    st.subheader("🔍 Quick User Search")
    
    search_term = st.text_input("Enter username, email, or user ID:")
    
    if search_term:
        user = quick_user_lookup(search_term)
        
        if user:
            st.success("✅ User found!")
            display_user_card(user)
            
            # Show additional details in expander
            with st.expander("📋 Full User Details"):
                st.json(user)
                
        else:
            st.warning(f"❌ No user found matching '{search_term}'")

def show_recent_users_widget(limit: int = 5):
    """Display recent users widget"""
    st.subheader("👥 Recent Users")
    
    users = get_recent_users(limit)
    
    if users:
        for user in users:
            with st.expander(f"👤 {user.get('username', 'Unknown')}"):
                display_user_card(user)
    else:
        st.info("No recent users found")

def show_user_stats_widget():
    """Display user statistics widget"""
    st.subheader("📊 User Statistics")
    
    total_users = get_user_count()
    recent_users = get_recent_users(7)  # Last 7 users
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Users", total_users)
    
    with col2:
        st.metric("Recent Signups", len(recent_users))

# Streamlit component functions
def user_lookup_component():
    """Complete user lookup component for Streamlit pages"""
    st.title("👥 User Lookup")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📊 Stats", "👥 Recent"])
    
    with tab1:
        show_user_search_widget()
    
    with tab2:
        show_user_stats_widget()
    
    with tab3:
        show_recent_users_widget()

# Admin helper functions
def is_user_admin(username: str) -> bool:
    """Check if a user has admin role"""
    user = quick_user_lookup(username)
    return user and user.get('role') == 'admin'

def get_admin_users() -> List[Dict[str, Any]]:
    """Get all admin users"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, email, full_name, created_at
            FROM users 
            WHERE role = 'admin'
            ORDER BY created_at ASC
        """)
        
        admins = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return admins
        
    except Exception:
        return []

def show_admin_users():
    """Display all admin users"""
    st.subheader("👑 Admin Users")
    
    admins = get_admin_users()
    
    if admins:
        for admin in admins:
            with st.expander(f"👑 {admin.get('username', 'Unknown')}"):
                display_user_card(admin)
    else:
        st.info("No admin users found")

# Quick access functions for debugging
def debug_user_info():
    """Debug function to show current user info"""
    from streamlit_app.utils.auth import get_auth_manager
    
    auth = get_auth_manager()
    if auth.is_authenticated():
        user_info = auth.get_current_user()
        db_user = auth.get_current_db_user()
        
        st.subheader("🐛 Debug: Current User Info")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**GitLab User Info:**")
            st.json(user_info)
        
        with col2:
            st.markdown("**Database User Info:**")
            st.json(db_user)
    else:
        st.warning("No user logged in")

# Export function
def export_all_users():
    """Export all users to CSV"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        import pandas as pd
        
        user_manager = UserManager()
        conn = sqlite3.connect(user_manager.db_path)
        
        df = pd.read_sql_query("""
            SELECT username, email, full_name, region, role,
                   created_at, last_login, login_count
            FROM users 
            ORDER BY created_at DESC
        """, conn)
        
        conn.close()
        
        return df.to_csv(index=False)
        
    except Exception as e:
        return f"Error exporting users: {e}"