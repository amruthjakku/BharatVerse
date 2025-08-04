"""
Admin Dashboard for BharatVerse
Administrative interface for user and content management
"""

import streamlit as st
from streamlit_app.utils.auth import GitLabAuth
from streamlit_app.utils.user_manager import user_manager
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def require_admin(func):
    """Decorator to require admin privileges"""
    def wrapper(*args, **kwargs):
        auth = GitLabAuth()
        if not auth.is_authenticated():
            st.error("Authentication required")
            return None
        
        if not auth.is_admin():
            st.error("🚫 Admin privileges required to access this page.")
            st.info("Contact an administrator if you need access.")
            return None
        
        return func(*args, **kwargs)
    
    return wrapper

@require_admin
def admin_dashboard_page():
    """Main admin dashboard"""
    # Enhanced header with time-based greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "🌅 Good Morning"
    elif current_hour < 17:
        greeting = "☀️ Good Afternoon"
    else:
        greeting = "🌙 Good Evening"
    
    auth = GitLabAuth()
    admin_user = auth.get_current_db_user()
    admin_name = admin_user.get('name', 'Administrator') if admin_user else 'Administrator'
    
    st.markdown(f"# 🛡️ {greeting}, {admin_name}!")
    st.markdown("*Welcome to the BharatVerse Administrative Control Center*")
    
    # System status indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📊 System Status")
    with col2:
        st.success("🟢 System Online")
    with col3:
        st.metric("⏰ Uptime", "99.9%")
    
    st.markdown("---")
    
    # Enhanced quick stats with better visualization
    try:
        stats = user_manager.get_user_stats()
        
        # Main metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "👥 Total Users", 
                stats.get('total_users', 0),
                delta=f"+{stats.get('new_users_today', 0)} today"
            )
        
        with col2:
            st.metric(
                "🟢 Active Users", 
                stats.get('active_users', 0),
                delta=f"{stats.get('active_percentage', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                "📅 New This Month", 
                stats.get('new_users_month', 0),
                delta=f"+{stats.get('growth_rate', 0):.1f}%"
            )
        
        with col4:
            admin_count = stats.get('roles', {}).get('admin', 0)
            st.metric("🛡️ Admins", admin_count)
        
        with col5:
            # Calculate total contributions
            total_contributions = stats.get('total_contributions', 0)
            st.metric("📝 Contributions", total_contributions)
        
        # Secondary metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎤 Audio Files", stats.get('audio_count', 0))
        
        with col2:
            st.metric("📝 Text Stories", stats.get('text_count', 0))
        
        with col3:
            st.metric("🖼️ Images", stats.get('image_count', 0))
        
        with col4:
            st.metric("💾 Storage Used", f"{stats.get('storage_used_gb', 0):.1f} GB")
            
    except Exception as e:
        st.error(f"Error loading system statistics: {e}")
        # Fallback stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", "Loading...")
        with col2:
            st.metric("Active Users", "Loading...")
        with col3:
            st.metric("New This Month", "Loading...")
        with col4:
            st.metric("Admins", "Loading...")
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", 
        "🛡️ Admin Management",
        "👥 User Management", 
        "📁 Content Management", 
        "📈 Analytics", 
        "⚙️ System Settings"
    ])
    
    with tab1:
        render_admin_overview(stats)
    
    with tab2:
        render_admin_management()
    
    with tab3:
        render_user_management()
    
    with tab4:
        render_content_management()
    
    with tab5:
        render_admin_analytics()
    
    with tab6:
        render_system_settings()

def render_admin_overview(stats):
    """Render admin overview dashboard"""
    st.markdown("### 📊 System Overview")
    
    # User role distribution
    if stats['roles']:
        st.markdown("#### 👥 User Roles Distribution")
        
        roles_df = pd.DataFrame(list(stats['roles'].items()), columns=['Role', 'Count'])
        fig = px.pie(roles_df, values='Count', names='Role', title="User Roles")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("#### 🕒 Recent System Activity")
    
    # Get recent users
    recent_users = user_manager.get_all_users(limit=10)
    
    if recent_users:
        st.markdown("**Recently Registered Users:**")
        for user in recent_users[:5]:
            created_date = datetime.fromisoformat(user['created_at'])
            days_ago = (datetime.now() - created_date).days
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{user['name']}** (@{user['username']})")
            with col2:
                st.markdown(f"Role: {user['role'].title()}")
            with col3:
                st.markdown(f"{days_ago} days ago")
    
    # System health indicators
    st.markdown("---")
    st.markdown("#### 🏥 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Database status (simplified check)
        try:
            test_users = user_manager.get_all_users(limit=1)
            db_status = "🟢 Healthy"
        except:
            db_status = "🔴 Error"
        st.markdown(f"**Database:** {db_status}")
    
    with col2:
        # Authentication status
        auth = GitLabAuth()
        if auth.client_id and auth.client_secret:
            auth_status = "🟢 Configured"
        else:
            auth_status = "🟡 Incomplete"
        st.markdown(f"**OAuth:** {auth_status}")
    
    with col3:
        # Storage status (placeholder)
        storage_status = "🟢 Available"
        st.markdown(f"**Storage:** {storage_status}")

def render_admin_management():
    """Render admin management interface"""
    st.markdown("### 🛡️ Admin Management")
    
    # Current admins
    all_users = user_manager.get_all_users(limit=1000)
    admins = [user for user in all_users if user['role'] == 'admin']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 👑 Current Administrators")
        
        if not admins:
            st.warning("⚠️ No administrators found in the system!")
            st.info("Use the command line tool or environment variables to create the first admin.")
        else:
            for admin in admins:
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    
                    with col_a:
                        st.markdown(f"**{admin['name']}** (@{admin['username']})")
                        st.markdown(f"📧 {admin['email']}")
                        st.markdown(f"🗓️ Admin since: {admin['created_at']}")
                    
                    with col_b:
                        st.markdown("**Status**")
                        status = "🟢 Active" if admin['is_active'] else "🔴 Inactive"
                        st.markdown(status)
                    
                    with col_c:
                        st.markdown("**Actions**")
                        # Don't allow removing the last admin
                        if len(admins) > 1:
                            if st.button("⬇️ Remove Admin", key=f"remove_admin_{admin['id']}"):
                                if user_manager.update_user_role(admin['id'], 'user'):
                                    st.success(f"Removed admin privileges from {admin['username']}")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove admin privileges")
                        else:
                            st.info("Last admin")
                    
                    st.markdown("---")
    
    with col2:
        st.markdown("#### ➕ Add New Admin")
        
        # Quick add by username
        with st.form("add_admin_form"):
            st.markdown("**Promote User to Admin**")
            username_input = st.text_input("Username", placeholder="Enter GitLab username")
            
            if st.form_submit_button("🛡️ Make Admin", type="primary"):
                if username_input:
                    user = user_manager.get_user_by_username(username_input.strip())
                    if user:
                        if user['role'] == 'admin':
                            st.warning(f"User '{username_input}' is already an admin!")
                        else:
                            if user_manager.update_user_role(user['id'], 'admin'):
                                st.success(f"✅ Successfully made '{username_input}' an admin!")
                                st.rerun()
                            else:
                                st.error("Failed to update user role")
                    else:
                        st.error(f"User '{username_input}' not found. They must login first.")
                else:
                    st.error("Please enter a username")
        
        # Command line instructions
        st.markdown("---")
        st.markdown("#### 💻 Command Line Tool")
        st.code("""
# List all users
python admin_tools.py list

# Make user admin
python admin_tools.py make-admin <username>

# Remove admin privileges  
python admin_tools.py remove-admin <username>

# List current admins
python admin_tools.py admins
        """, language="bash")
        
        # Environment variable instructions
        st.markdown("#### ⚙️ Environment Setup")
        st.markdown("Set in `.env` file for auto-admin on first login:")
        st.code("""
INITIAL_ADMIN_USERNAME=your_gitlab_username
INITIAL_ADMIN_EMAIL=your@email.com
        """, language="bash")

def render_user_management():
    """Render user management interface"""
    st.markdown("### 👥 User Management")
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Username or name...")
    
    with col2:
        role_filter = st.selectbox("Filter by role", ["All", "admin", "moderator", "user"])
    
    with col3:
        status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive"])
    
    # Get users
    all_users = user_manager.get_all_users(limit=100)
    
    # Apply filters
    filtered_users = all_users
    
    if search_term:
        filtered_users = [
            user for user in filtered_users 
            if search_term.lower() in user['username'].lower() 
            or search_term.lower() in (user['name'] or '').lower()
        ]
    
    if role_filter != "All":
        filtered_users = [user for user in filtered_users if user['role'] == role_filter]
    
    if status_filter != "All":
        is_active = status_filter == "Active"
        filtered_users = [user for user in filtered_users if user['is_active'] == is_active]
    
    st.markdown(f"**Showing {len(filtered_users)} of {len(all_users)} users**")
    
    # User list
    for user in filtered_users:
        with st.expander(f"👤 {user['name']} (@{user['username']}) - {user['role'].title()}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Email:** {user['email'] or 'Not provided'}")
                st.markdown(f"**GitLab ID:** {user['gitlab_id']}")
                st.markdown(f"**Member since:** {user['created_at']}")
                st.markdown(f"**Last login:** {user['last_login'] or 'Never'}")
                
                if user['location']:
                    st.markdown(f"**Location:** {user['location']}")
                
                if user['organization']:
                    st.markdown(f"**Organization:** {user['organization']}")
            
            with col2:
                st.markdown("**Current Role:**")
                current_role = user['role']
                new_role = st.selectbox(
                    "Change role", 
                    ["user", "moderator", "admin"],
                    index=["user", "moderator", "admin"].index(current_role),
                    key=f"role_{user['id']}"
                )
                
                if new_role != current_role:
                    if st.button(f"Update Role", key=f"update_role_{user['id']}"):
                        if user_manager.update_user_role(user['id'], new_role):
                            st.success(f"Role updated to {new_role}")
                            st.rerun()
                        else:
                            st.error("Failed to update role")
            
            with col3:
                st.markdown("**Actions:**")
                
                # Get user contributions
                contributions = user_manager.get_user_contributions(user['id'])
                st.markdown(f"**Contributions:** {len(contributions)}")
                
                if st.button("📊 View Details", key=f"details_{user['id']}"):
                    st.session_state[f"show_user_details_{user['id']}"] = True
                
                if st.button("📝 Activity Log", key=f"activity_{user['id']}"):
                    activities = user_manager.get_user_activity(user['id'], limit=10)
                    st.json(activities)
                
                # Status toggle
                status_text = "Deactivate" if user['is_active'] else "Activate"
                if st.button(f"🔄 {status_text}", key=f"toggle_{user['id']}"):
                    st.info("User status toggle functionality coming soon!")

def render_content_management():
    """Render content management interface"""
    st.markdown("### 📁 Content Management")
    
    # Content statistics
    st.markdown("#### 📊 Content Overview")
    
    # Get all users to calculate content stats
    all_users = user_manager.get_all_users(limit=1000)
    
    total_contributions = 0
    content_types = {}
    
    for user in all_users:
        contributions = user_manager.get_user_contributions(user['id'])
        total_contributions += len(contributions)
        
        for contrib in contributions:
            content_type = contrib['type']
            content_types[content_type] = content_types.get(content_type, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contributions", total_contributions)
    with col2:
        st.metric("Audio Stories", content_types.get('audio', 0))
    with col3:
        st.metric("Text Stories", content_types.get('text', 0))
    with col4:
        st.metric("Visual Heritage", content_types.get('visual', 0))
    
    # Content type distribution
    if content_types:
        st.markdown("#### 📈 Content Distribution")
        content_df = pd.DataFrame(list(content_types.items()), columns=['Type', 'Count'])
        fig = px.bar(content_df, x='Type', y='Count', title="Content by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent contributions
    st.markdown("#### 🕒 Recent Contributions")
    
    # Get recent contributions from all users
    recent_contributions = []
    for user in all_users[:20]:  # Check recent users
        contributions = user_manager.get_user_contributions(user['id'], limit=5)
        for contrib in contributions:
            contrib['user_name'] = user['name']
            contrib['username'] = user['username']
            recent_contributions.append(contrib)
    
    # Sort by creation date
    recent_contributions.sort(key=lambda x: x['created_at'], reverse=True)
    
    for contrib in recent_contributions[:10]:
        with st.expander(f"{contrib['type'].title()}: {contrib['title']} by @{contrib['username']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Author:** {contrib['user_name']} (@{contrib['username']})")
                st.markdown(f"**Description:** {contrib['description'] or 'No description'}")
                st.markdown(f"**Created:** {contrib['created_at']}")
                
                if contrib['tags']:
                    tags = ", ".join(contrib['tags'])
                    st.markdown(f"**Tags:** {tags}")
                
                visibility = "Public" if contrib['is_public'] else "Private"
                st.markdown(f"**Visibility:** {visibility}")
            
            with col2:
                st.markdown("**Admin Actions:**")
                if st.button("👁️ View", key=f"view_{contrib['id']}"):
                    st.info("View functionality coming soon!")
                
                if st.button("✏️ Edit", key=f"admin_edit_{contrib['id']}"):
                    st.info("Admin edit functionality coming soon!")
                
                if st.button("🗑️ Remove", key=f"admin_delete_{contrib['id']}"):
                    st.warning("Admin delete functionality coming soon!")

def render_admin_analytics():
    """Render analytics dashboard"""
    st.markdown("### 📈 Analytics Dashboard")
    
    # User growth analytics
    st.markdown("#### 👥 User Growth")
    
    all_users = user_manager.get_all_users(limit=1000)
    
    if all_users:
        # Create user registration timeline
        user_dates = []
        for user in all_users:
            created_date = datetime.fromisoformat(user['created_at'])
            user_dates.append(created_date.date())
        
        # Group by date
        date_counts = {}
        for date in user_dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        # Create cumulative data
        sorted_dates = sorted(date_counts.keys())
        cumulative_users = []
        total = 0
        
        for date in sorted_dates:
            total += date_counts[date]
            cumulative_users.append({'date': date, 'total_users': total, 'new_users': date_counts[date]})
        
        df = pd.DataFrame(cumulative_users)
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.line(df, x='date', y='total_users', title="Cumulative User Growth")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(df, x='date', y='new_users', title="New Users by Date")
                st.plotly_chart(fig2, use_container_width=True)
    
    # Activity analytics
    st.markdown("#### 📊 Activity Analytics")
    
    # User activity summary
    active_users_7d = 0
    active_users_30d = 0
    
    for user in all_users:
        if user['last_login']:
            last_login = datetime.fromisoformat(user['last_login'])
            days_since_login = (datetime.now() - last_login).days
            
            if days_since_login <= 7:
                active_users_7d += 1
            if days_since_login <= 30:
                active_users_30d += 1
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active (7 days)", active_users_7d)
    with col2:
        st.metric("Active (30 days)", active_users_30d)
    with col3:
        retention_rate = (active_users_30d / len(all_users) * 100) if all_users else 0
        st.metric("30-day Retention", f"{retention_rate:.1f}%")

def render_system_settings():
    """Render system settings"""
    st.markdown("### ⚙️ System Settings")
    
    st.markdown("#### 🔧 Configuration")
    
    # OAuth settings display
    st.markdown("**OAuth Configuration:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**GitLab Base URL:** {os.getenv('GITLAB_BASE_URL', 'Not set')}")
        st.markdown(f"**Client ID:** {os.getenv('GITLAB_CLIENT_ID', 'Not set')[:20]}...")
        st.markdown(f"**Redirect URI:** {os.getenv('GITLAB_REDIRECT_URI', 'Not set')}")
    
    with col2:
        st.markdown(f"**Scopes:** {os.getenv('GITLAB_SCOPES', 'Not set')}")
        st.markdown(f"**Debug Mode:** {os.getenv('DEBUG', 'False')}")
        st.markdown(f"**Log Level:** {os.getenv('LOG_LEVEL', 'INFO')}")
    
    # Database management
    st.markdown("---")
    st.markdown("#### 🗄️ Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Stats"):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Data"):
            st.info("Data export functionality coming soon!")
    
    with col3:
        if st.button("🧹 Cleanup"):
            st.warning("Database cleanup functionality coming soon!")
    
    # System maintenance
    st.markdown("---")
    st.markdown("#### 🛠️ System Maintenance")
    
    st.warning("⚠️ Maintenance functions should be used with caution!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset User Sessions"):
            st.info("Session reset functionality coming soon!")
    
    with col2:
        if st.button("📝 View System Logs"):
            st.info("System logs functionality coming soon!")

def admin_dashboard_main():
    """Main admin dashboard function"""
    auth = GitLabAuth()
    
    if not auth.is_authenticated():
        st.markdown("## 🛡️ Admin Dashboard")
        st.markdown("---")
        st.error("🔐 Authentication required to access the admin dashboard.")
        st.info("Please login from the home page to access this dashboard.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏠 Go to Home Page", use_container_width=True, type="primary"):
                st.switch_page("Home.py")
        
        st.stop()
        
    elif not auth.is_admin():
        st.markdown("## 🛡️ Admin Dashboard")
        st.markdown("---")
        st.error("🚫 Admin privileges required to access this page.")
        st.info("You are logged in, but you don't have administrator privileges.")
        
        # Show current user info
        current_user = auth.get_current_user()
        if current_user:
            st.markdown(f"**Current User:** {current_user.get('name', 'Unknown')}")
            st.markdown(f"**Username:** {current_user.get('username', 'Unknown')}")
            st.markdown("**Role:** User")
            
        st.markdown("---")
        st.markdown("**Note:** Contact an administrator to request admin privileges.")
        
        if st.button("🚪 Logout"):
            auth.logout()
            
    else:
        # User is authenticated and is admin
        admin_dashboard_page()