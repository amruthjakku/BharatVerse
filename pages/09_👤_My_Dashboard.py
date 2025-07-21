"""
User Dashboard for BharatVerse
Personal dashboard for regular users to view their contributions and activity
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import utilities
from streamlit_app.utils.auth import get_auth_manager
from streamlit_app.utils.database import get_db_connection
from streamlit_app.utils.main_styling import load_custom_css

# Database imports
try:
    from utils.supabase_db import get_database_manager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Authentication imports
try:
    from streamlit_app.utils.auth import get_auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

def check_user_access():
    """Check if user is authenticated"""
    auth = get_auth_manager()
    if not auth.is_authenticated():
        st.error("🔒 Please login to access your dashboard")
        st.markdown("### 🔗 Login Required")
        from streamlit_app.utils.auth import render_login_button
        render_login_button()
        st.stop()
    
    user_info = auth.get_current_user()
    return user_info, auth

def get_user_contributions(username: str):
    """Get user's contributions from Supabase or local database"""
    try:
        # Try Supabase first
        if SUPABASE_AVAILABLE and AUTH_AVAILABLE:
            auth = get_auth_manager()
            if auth.is_authenticated():
                db_user = auth.get_current_db_user()
                if db_user:
                    db = get_database_manager()
                    
                    # Get user's contributions from Supabase
                    contributions = db.get_contributions(user_id=db_user['id'], limit=1000)
                    
                    if contributions:
                        # Process contributions to get stats
                        contrib_stats = {}
                        recent_contribs = []
                        
                        for contrib in contributions:
                            content_type = contrib.get('content_type', 'unknown')
                            created_at = contrib.get('created_at', '')
                            
                            # Update stats
                            if content_type not in contrib_stats:
                                contrib_stats[content_type] = {
                                    'count': 0,
                                    'first': created_at,
                                    'latest': created_at
                                }
                            
                            contrib_stats[content_type]['count'] += 1
                            if created_at < contrib_stats[content_type]['first']:
                                contrib_stats[content_type]['first'] = created_at
                            if created_at > contrib_stats[content_type]['latest']:
                                contrib_stats[content_type]['latest'] = created_at
                            
                            # Add to recent contributions
                            if len(recent_contribs) < 10:
                                recent_contribs.append((
                                    content_type,
                                    contrib.get('title', 'Untitled'),
                                    created_at
                                ))
                        
                        # Convert stats to expected format
                        stats_list = []
                        for content_type, stats in contrib_stats.items():
                            stats_list.append((
                                content_type,
                                stats['count'],
                                stats['first'],
                                stats['latest']
                            ))
                        
                        # Sort by count
                        stats_list.sort(key=lambda x: x[1], reverse=True)
                        
                        st.success("📊 Contributions loaded from Supabase")
                        return stats_list, recent_contribs
        
        # Fallback to local database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get contributions by type
        cursor.execute("""
            SELECT contribution_type, COUNT(*) as count,
                   MIN(created_at) as first_contribution,
                   MAX(created_at) as latest_contribution
            FROM contributions 
            WHERE user_id = ?
            GROUP BY contribution_type
            ORDER BY count DESC
        """, (username,))
        
        contrib_stats = cursor.fetchall()
        
        # Get recent contributions
        cursor.execute("""
            SELECT contribution_type, title, created_at
            FROM contributions 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (username,))
        
        recent_contribs = cursor.fetchall()
        
        conn.close()
        
        if contrib_stats or recent_contribs:
            st.info("📊 Contributions loaded from local database")
        
        return contrib_stats, recent_contribs
        
    except Exception as e:
        st.error(f"Error loading contributions: {e}")
        return [], []

def show_user_stats(user_info, auth):
    """Show user statistics and profile"""
    st.subheader("👤 Your Profile")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # User avatar
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=100)
        else:
            st.markdown("### 👤")
    
    with col2:
        st.markdown(f"### {user_info.get('name', 'Unknown User')}")
        st.markdown(f"**Username:** @{user_info.get('username', 'unknown')}")
        if user_info.get('email'):
            st.markdown(f"**Email:** {user_info['email']}")
        
        # User role
        db_user = auth.get_current_db_user()
        if db_user and db_user.get('role'):
            role = db_user['role']
            role_emoji = {"admin": "🛡️", "moderator": "🛠️", "user": "👤"}.get(role, "👤")
            st.markdown(f"**Role:** {role_emoji} {role.title()}")
        
        # Account info
        if db_user and db_user.get('created_at'):
            st.markdown(f"**Member since:** {db_user['created_at']}")

def show_contribution_summary(username: str):
    """Show user's contribution summary"""
    st.subheader("📊 Your Contributions")
    
    contrib_stats, recent_contribs = get_user_contributions(username)
    
    if contrib_stats:
        # Show contribution metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_contributions = sum([stat[1] for stat in contrib_stats])
        
        with col1:
            st.metric("Total Contributions", total_contributions)
        
        with col2:
            audio_count = next((stat[1] for stat in contrib_stats if stat[0] == 'audio'), 0)
            st.metric("🎤 Audio", audio_count)
        
        with col3:
            text_count = next((stat[1] for stat in contrib_stats if stat[0] == 'text'), 0)
            st.metric("📝 Text", text_count)
        
        with col4:
            image_count = next((stat[1] for stat in contrib_stats if stat[0] == 'image'), 0)
            st.metric("🖼️ Images", image_count)
        
        # Show contribution breakdown
        if len(contrib_stats) > 0:
            st.markdown("### 📈 Contribution Breakdown")
            contrib_data = []
            for stat in contrib_stats:
                contrib_data.append({
                    'Type': stat[0].title(),
                    'Count': stat[1],
                    'First': stat[2],
                    'Latest': stat[3]
                })
            
            df = pd.DataFrame(contrib_data)
            st.dataframe(df, use_container_width=True)
            
            # Simple bar chart
            chart_df = df[['Type', 'Count']].set_index('Type')
            st.bar_chart(chart_df)
    else:
        st.info("🎯 You haven't made any contributions yet!")
        st.markdown("### 🚀 Get Started:")
        st.markdown("- 🎤 **Audio Capture** - Record cultural stories and sounds")
        st.markdown("- 📝 **Text Stories** - Share written cultural narratives")
        st.markdown("- 🖼️ **Visual Heritage** - Upload cultural images and artwork")

def show_recent_activity(username: str):
    """Show user's recent activity"""
    st.subheader("📈 Recent Activity")
    
    _, recent_contribs = get_user_contributions(username)
    
    if recent_contribs:
        st.markdown("### 🕒 Your Latest Contributions")
        
        for contrib in recent_contribs[:5]:
            contrib_type = contrib[0]
            title = contrib[1] or "Untitled"
            created_at = contrib[2]
            
            type_emoji = {
                'audio': '🎤',
                'text': '📝', 
                'image': '🖼️',
                'video': '🎥'
            }.get(contrib_type, '📄')
            
            with st.expander(f"{type_emoji} {title} - {created_at}"):
                st.write(f"**Type:** {contrib_type.title()}")
                st.write(f"**Created:** {created_at}")
                st.write(f"**Title:** {title}")
    else:
        st.info("No recent activity to show")

def show_quick_actions():
    """Show quick action buttons"""
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎤 Audio")
        if st.button("Record Audio", use_container_width=True):
            st.switch_page("pages/01_🎤_Audio_Capture.py")
    
    with col2:
        st.markdown("#### 📝 Text")
        if st.button("Write Story", use_container_width=True):
            st.switch_page("pages/02_📝_Text_Stories.py")
    
    with col3:
        st.markdown("#### 🖼️ Images")
        if st.button("Upload Image", use_container_width=True):
            st.switch_page("pages/03_🖼️_Visual_Heritage.py")

def show_community_info():
    """Show community information"""
    st.subheader("🏘️ Community")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 Join Discussions", use_container_width=True):
            st.switch_page("pages/12_🏘️_Community.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/04_📊_Analytics.py")

def main():
    st.set_page_config(
        page_title="My Dashboard - BharatVerse",
        page_icon="👤",
        layout="wide"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Check user access
    user_info, auth = check_user_access()
    
    st.title("👤 My Dashboard")
    st.markdown("*Your personal BharatVerse activity center*")
    
    # Sidebar navigation
    st.sidebar.title("📋 Dashboard Menu")
    
    menu_option = st.sidebar.selectbox(
        "Choose section:",
        [
            "👤 Profile",
            "📊 My Contributions", 
            "📈 Recent Activity",
            "🚀 Quick Actions",
            "🏘️ Community"
        ]
    )
    
    username = user_info.get('username', 'unknown')
    
    if menu_option == "👤 Profile":
        show_user_stats(user_info, auth)
        
    elif menu_option == "📊 My Contributions":
        show_contribution_summary(username)
        
    elif menu_option == "📈 Recent Activity":
        show_recent_activity(username)
        
    elif menu_option == "🚀 Quick Actions":
        show_quick_actions()
        
    elif menu_option == "🏘️ Community":
        show_community_info()
    
    # Show admin notice if user is admin
    if auth.is_admin():
        st.markdown("---")
        st.info("🛡️ **Admin Access Available** - You have administrator privileges")
        if st.button("🛡️ Go to Admin Dashboard", type="primary"):
            st.switch_page("pages/08_🛡️_Admin_Dashboard.py")

if __name__ == "__main__":
    main()