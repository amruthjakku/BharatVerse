"""
Admin Dashboard for BharatVerse
Central hub for all administrative functions
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
from streamlit_app.utils.user_manager import UserManager
from streamlit_app.utils.main_styling import load_custom_css

# Safe imports
try:
    from utils.database_viewer import get_sqlite_user_stats, get_contribution_stats
    DATABASE_VIEWER_AVAILABLE = True
except ImportError:
    DATABASE_VIEWER_AVAILABLE = False

def check_admin_access():
    """Check if current user has admin access"""
    auth = get_auth_manager()
    if not auth.is_authenticated():
        st.error("🔒 Please login to access the Admin Dashboard")
        st.markdown("### 🔗 Login Required")
        from streamlit_app.utils.auth import render_login_button
        render_login_button()
        st.stop()
    
    # Check if user is admin
    if not auth.is_admin():
        st.error("🚫 **Admin Access Required**")
        st.warning("This dashboard is restricted to administrators only.")
        
        user_info = auth.get_current_user()
        if user_info:
            st.info(f"👤 Logged in as: **{user_info.get('name', 'Unknown')}**")
            st.markdown("Contact an administrator if you need access to this dashboard.")
        
        # Show available pages for regular users
        st.markdown("### 📋 Available Pages for Regular Users:")
        st.markdown("- 🎤 **Audio Capture** - Record and contribute audio")
        st.markdown("- 📝 **Text Stories** - Share cultural stories")
        st.markdown("- 🖼️ **Visual Heritage** - Upload cultural images")
        st.markdown("- 📊 **Analytics** - View your contributions")
        st.markdown("- 🏘️ **Community** - Join community discussions")
        
        st.stop()
    
    user_info = auth.get_current_user()
    return user_info

def show_admin_overview():
    """Show admin dashboard overview"""
    st.subheader("📊 System Overview")
    
    # Get system statistics
    if DATABASE_VIEWER_AVAILABLE:
        user_stats = get_sqlite_user_stats()
        contrib_stats = get_contribution_stats()
    else:
        user_stats = {'total_users': 0, 'active_users': 0, 'recent_users': 0}
        contrib_stats = {'total_contributions': 0, 'recent_contributions': 0}
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = user_stats.get('total_users', 0)
        st.metric("👥 Total Users", total_users)
    
    with col2:
        active_users = user_stats.get('active_users', 0)
        st.metric("🟢 Active Users", active_users)
    
    with col3:
        total_contributions = contrib_stats.get('total_contributions', 0)
        st.metric("📝 Total Contributions", total_contributions)
    
    with col4:
        recent_contributions = contrib_stats.get('recent_contributions', 0)
        st.metric("🆕 Recent (7d)", recent_contributions)
    
    # Show user roles distribution
    if 'roles' in user_stats and user_stats['roles']:
        st.markdown("### 👥 User Roles")
        roles_data = user_stats['roles']
        
        col1, col2 = st.columns(2)
        with col1:
            for role, count in roles_data.items():
                role_emoji = {"admin": "🛡️", "moderator": "🛠️", "user": "👤"}.get(role, "👤")
                st.metric(f"{role_emoji} {role.title()}", count)
    
    # Show contribution types
    if 'by_type' in contrib_stats and contrib_stats['by_type']:
        st.markdown("### 📊 Contributions by Type")
        contrib_data = contrib_stats['by_type']
        
        # Create a simple bar chart
        df = pd.DataFrame(list(contrib_data.items()), columns=['Type', 'Count'])
        st.bar_chart(df.set_index('Type'))

def show_admin_tools():
    """Show admin tools and quick actions"""
    st.subheader("🛠️ Admin Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🗄️ Database Management")
        if st.button("📊 Database Admin Panel", use_container_width=True):
            st.switch_page("pages/07_🗄️_Database_Admin.py")
        
        if st.button("👥 User Management", use_container_width=True):
            # Could link to a user management page
            st.info("User management features available in Database Admin")
    
    with col2:
        st.markdown("#### 🏘️ Community Management")
        if st.button("🛠️ Community Admin", use_container_width=True):
            st.switch_page("pages/13_🛠️_Community_Admin.py")
        
        if st.button("💬 Moderate Content", use_container_width=True):
            st.info("Content moderation features coming soon")
    
    with col3:
        st.markdown("#### ⚡ System Management")
        if st.button("📈 Performance Monitor", use_container_width=True):
            st.switch_page("pages/06_⚡_Performance.py")
        
        if st.button("🔧 System Settings", use_container_width=True):
            st.info("System settings panel coming soon")

def show_recent_activity():
    """Show recent system activity"""
    st.subheader("📈 Recent Activity")
    
    try:
        user_manager = UserManager()
        
        # Get recent users
        import sqlite3
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, full_name, created_at, last_login
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_users = cursor.fetchall()
        conn.close()
        
        if recent_users:
            st.markdown("#### 👥 Recent User Registrations")
            for user in recent_users[:5]:
                with st.expander(f"👤 {user['username']} - {user['full_name'] or 'No name'}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Registered:** {user['created_at']}")
                    with col2:
                        st.write(f"**Last Login:** {user['last_login'] or 'Never'}")
        else:
            st.info("No recent user activity")
            
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")

def show_system_health():
    """Show system health status"""
    st.subheader("🏥 System Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💾 Database Status")
        try:
            user_manager = UserManager()
            # Test database connection
            import sqlite3
            conn = sqlite3.connect(user_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            conn.close()
            
            st.success(f"✅ SQLite Database: {user_count} users")
        except Exception as e:
            st.error(f"❌ Database Error: {str(e)[:50]}...")
    
    with col2:
        st.markdown("#### 🔧 System Components")
        
        # Check memory manager
        try:
            from utils.memory_manager import get_memory_manager
            memory_manager = get_memory_manager()
            memory_usage = memory_manager.get_memory_usage()
            st.success("✅ Memory Manager: Active")
        except Exception:
            st.warning("⚠️ Memory Manager: Limited")
        
        # Check cache manager
        try:
            from utils.redis_cache import get_cache_manager
            cache_manager = get_cache_manager()
            st.success("✅ Cache Manager: Active")
        except Exception:
            st.warning("⚠️ Cache Manager: Unavailable")

def main():
    st.set_page_config(
        page_title="Admin Dashboard - BharatVerse",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Check admin access
    user_info = check_admin_access()
    
    st.title("🛡️ Admin Dashboard")
    st.markdown(f"**Welcome, Administrator {user_info.get('name', 'Unknown')}**")
    st.markdown("*Central control panel for BharatVerse administration*")
    
    # Sidebar navigation
    st.sidebar.title("🛡️ Admin Menu")
    
    menu_option = st.sidebar.selectbox(
        "Choose section:",
        [
            "📊 Overview",
            "🛠️ Admin Tools", 
            "📈 Recent Activity",
            "🏥 System Health",
            "⚙️ Quick Actions"
        ]
    )
    
    if menu_option == "📊 Overview":
        show_admin_overview()
        
    elif menu_option == "🛠️ Admin Tools":
        show_admin_tools()
        
    elif menu_option == "📈 Recent Activity":
        show_recent_activity()
        
    elif menu_option == "🏥 System Health":
        show_system_health()
        
    elif menu_option == "⚙️ Quick Actions":
        st.subheader("⚙️ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔄 System Actions")
            if st.button("🧹 Clear Cache", use_container_width=True):
                try:
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.success("✅ Cache cleared successfully")
                except Exception as e:
                    st.error(f"❌ Cache clear failed: {e}")
            
            if st.button("📊 Refresh Stats", use_container_width=True):
                st.rerun()
        
        with col2:
            st.markdown("#### 📥 Data Export")
            if st.button("📄 Export User Data", use_container_width=True):
                try:
                    from utils.user_lookup import export_all_users
                    csv_data = export_all_users()
                    
                    if not csv_data.startswith("Error"):
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv_data,
                            file_name=f"bharatverse_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        st.success("✅ Export ready for download")
                    else:
                        st.error(csv_data)
                except Exception as e:
                    st.error(f"Export failed: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗄️ Database", use_container_width=True):
            st.switch_page("pages/07_🗄️_Database_Admin.py")
    
    with col2:
        if st.button("🏘️ Community", use_container_width=True):
            st.switch_page("pages/13_🛠️_Community_Admin.py")
    
    with col3:
        if st.button("⚡ Performance", use_container_width=True):
            st.switch_page("pages/06_⚡_Performance.py")
    
    with col4:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")

if __name__ == "__main__":
    main()