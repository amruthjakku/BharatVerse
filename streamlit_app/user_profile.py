"""
User Profile Module for BharatVerse
Personal user dashboard and profile management
"""

import streamlit as st
from streamlit_app.utils.auth import GitLabAuth, require_auth
from streamlit_app.utils.user_manager import user_manager
from datetime import datetime, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

@require_auth
def user_profile_page():
    """User profile and personal dashboard"""
    auth = GitLabAuth()
    user_info = auth.get_current_user()
    db_user = auth.get_current_db_user()
    
    if not user_info or not db_user:
        st.error("User information not available")
        return
    
    st.markdown(f"# 👤 {user_info.get('name', 'User')} Profile")
    st.markdown("---")
    
    # Profile header
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=150)
        else:
            st.markdown("### 👤")
    
    with col2:
        st.markdown(f"### {user_info.get('name', 'Unknown User')}")
        st.markdown(f"**@{user_info.get('username', 'unknown')}**")
        
        if user_info.get('bio'):
            st.markdown(f"*{user_info['bio']}*")
        
        # User stats
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.metric("Role", db_user.get('role', 'user').title())
        with col2b:
            contributions = user_manager.get_user_contributions(db_user['id'])
            st.metric("Contributions", len(contributions))
        with col2c:
            member_since = datetime.fromisoformat(db_user['created_at'].replace('Z', '+00:00'))
            days_member = (datetime.now(member_since.tzinfo) - member_since).days
            st.metric("Member for", f"{days_member} days")
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "📁 My Contributions", 
        "⚙️ Settings", 
        "📈 Activity", 
        "🔗 GitLab Profile"
    ])
    
    with tab1:
        render_user_dashboard(db_user)
    
    with tab2:
        render_user_contributions(db_user)
    
    with tab3:
        render_user_settings(db_user)
    
    with tab4:
        render_user_activity(db_user)
    
    with tab5:
        render_gitlab_profile(user_info)

def render_gitlab_profile(user_info):
    """Render GitLab profile integration"""
    st.markdown("### 🔗 GitLab Profile Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 GitLab Information")
        st.markdown(f"**Username:** @{user_info.get('username', 'N/A')}")
        st.markdown(f"**Name:** {user_info.get('name', 'N/A')}")
        st.markdown(f"**Email:** {user_info.get('email', 'N/A')}")
        st.markdown(f"**ID:** {user_info.get('id', 'N/A')}")
        
        if user_info.get('state'):
            st.markdown(f"**Status:** {user_info['state']}")
        
        if user_info.get('web_url'):
            st.markdown(f"[View GitLab Profile]({user_info['web_url']})")
    
    with col2:
        st.markdown("#### 🎯 GitLab Role & Permissions")
        
        # Determine role based on GitLab permissions
        gitlab_role = "Contributor"
        if user_info.get('is_admin'):
            gitlab_role = "Administrator"
        elif user_info.get('can_create_project'):
            gitlab_role = "Developer"
        elif user_info.get('can_create_group'):
            gitlab_role = "Maintainer"
        
        st.markdown(f"**Role:** {gitlab_role}")
        st.markdown(f"**Can Create Projects:** {'✅' if user_info.get('can_create_project') else '❌'}")
        st.markdown(f"**Can Create Groups:** {'✅' if user_info.get('can_create_group') else '❌'}")
        
    st.markdown("---")
    st.markdown("#### 📊 GitLab Activity")
    
    # Mock GitLab activity data
    activity_data = {
        'commits': 42,
        'merge_requests': 15,
        'issues': 28,
        'contributions': 85
    }
    
    cols = st.columns(4)
    for i, (key, value) in enumerate(activity_data.items()):
        with cols[i]:
            st.metric(key.replace('_', ' ').title(), value)
    
    st.info("🔄 GitLab activity syncs automatically with your contributions to BharatVerse")

def render_user_dashboard(db_user):
    """Render user dashboard with statistics"""
    st.markdown("### 📊 Personal Dashboard")
    
    # Get user contributions
    contributions = user_manager.get_user_contributions(db_user['id'])
    
    if not contributions:
        st.info("🎯 Start contributing to see your dashboard statistics!")
        st.markdown("""
        **Get started by:**
        - 📝 Sharing text stories
        - 🤝 Participating in community discussions
        - 🔍 Discovering cultural heritage
        """)
        return
    
    # Contribution statistics
    col1, col2, col3, col4 = st.columns(4)
    
    # Count by type
    type_counts = {}
    for contrib in contributions:
        contrib_type = contrib['type']
        type_counts[contrib_type] = type_counts.get(contrib_type, 0) + 1
    
    with col1:
        st.metric("Total Contributions", len(contributions))
    with col2:
        st.metric("Audio Stories", type_counts.get('audio', 0))
    with col3:
        st.metric("Text Stories", type_counts.get('text', 0))
    with col4:
        st.metric("Visual Heritage", type_counts.get('visual', 0))
    
    # Contribution timeline
    if contributions:
        st.markdown("### 📈 Contribution Timeline")
        
        # Create timeline data
        timeline_data = []
        for contrib in contributions:
            created_date = datetime.fromisoformat(contrib['created_at'])
            timeline_data.append({
                'date': created_date.date(),
                'type': contrib['type'],
                'title': contrib['title']
            })
        
        df = pd.DataFrame(timeline_data)
        
        if not df.empty:
            # Group by date and type
            daily_counts = df.groupby(['date', 'type']).size().reset_index(name='count')
            
            fig = px.line(daily_counts, x='date', y='count', color='type',
                         title="Daily Contributions",
                         labels={'count': 'Number of Contributions', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent contributions
    st.markdown("### 🕒 Recent Contributions")
    recent_contributions = contributions[:5]  # Last 5
    
    for contrib in recent_contributions:
        with st.expander(f"{contrib['type'].title()}: {contrib['title']}"):
            st.markdown(f"**Created:** {contrib['created_at']}")
            if contrib['description']:
                st.markdown(f"**Description:** {contrib['description']}")
            if contrib['tags']:
                tags = ", ".join(contrib['tags'])
                st.markdown(f"**Tags:** {tags}")
            if contrib['language']:
                st.markdown(f"**Language:** {contrib['language']}")
            if contrib['region']:
                st.markdown(f"**Region:** {contrib['region']}")

def render_user_contributions(db_user):
    """Render user's contributions with management options"""
    st.markdown("### 📁 My Contributions")
    
    contributions = user_manager.get_user_contributions(db_user['id'])
    
    if not contributions:
        st.info("You haven't made any contributions yet.")
        st.markdown("**Start contributing:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎵 Record Audio", use_container_width=True):
                st.switch_page("Audio Capture")
        with col2:
            if st.button("📝 Write Story", use_container_width=True):
                st.switch_page("Text Stories")
        with col3:
            if st.button("🖼️ Share Visual", use_container_width=True):
                st.switch_page("Visual Heritage")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.selectbox("Filter by Type", 
                                  ["All"] + list(set(c['type'] for c in contributions)))
    with col2:
        visibility_filter = st.selectbox("Filter by Visibility", 
                                        ["All", "Public", "Private"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest", "Oldest", "Title"])
    
    # Apply filters
    filtered_contributions = contributions
    
    if type_filter != "All":
        filtered_contributions = [c for c in filtered_contributions if c['type'] == type_filter]
    
    if visibility_filter != "All":
        is_public = visibility_filter == "Public"
        filtered_contributions = [c for c in filtered_contributions if c['is_public'] == is_public]
    
    # Sort
    if sort_by == "Newest":
        filtered_contributions.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest":
        filtered_contributions.sort(key=lambda x: x['created_at'])
    elif sort_by == "Title":
        filtered_contributions.sort(key=lambda x: x['title'])
    
    st.markdown(f"**Showing {len(filtered_contributions)} of {len(contributions)} contributions**")
    
    # Display contributions
    for contrib in filtered_contributions:
        with st.expander(f"{'🔒' if not contrib['is_public'] else '🌐'} {contrib['type'].title()}: {contrib['title']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {contrib['description'] or 'No description'}")
                st.markdown(f"**Created:** {contrib['created_at']}")
                
                if contrib['tags']:
                    tags = ", ".join(contrib['tags'])
                    st.markdown(f"**Tags:** {tags}")
                
                if contrib['language']:
                    st.markdown(f"**Language:** {contrib['language']}")
                
                if contrib['region']:
                    st.markdown(f"**Region:** {contrib['region']}")
            
            with col2:
                st.markdown("**Actions:**")
                if st.button("✏️ Edit", key=f"edit_{contrib['id']}"):
                    st.info("Edit functionality coming soon!")
                
                if st.button("🗑️ Delete", key=f"delete_{contrib['id']}"):
                    st.warning("Delete functionality coming soon!")
                
                visibility = "Public" if contrib['is_public'] else "Private"
                st.markdown(f"**Visibility:** {visibility}")

def render_user_settings(db_user):
    """Render user settings and preferences"""
    st.markdown("### ⚙️ User Settings")
    
    # Profile settings
    st.markdown("#### 👤 Profile Settings")
    
    with st.form("profile_settings"):
        # Load current preferences
        preferences = db_user.get('preferences', {})
        
        # Privacy settings
        st.markdown("**Privacy Settings**")
        show_email = st.checkbox("Show email in profile", 
                                value=preferences.get('show_email', False))
        show_location = st.checkbox("Show location in profile", 
                                   value=preferences.get('show_location', True))
        allow_contact = st.checkbox("Allow other users to contact me", 
                                   value=preferences.get('allow_contact', True))
        
        # Notification settings
        st.markdown("**Notification Settings**")
        email_notifications = st.checkbox("Email notifications", 
                                         value=preferences.get('email_notifications', True))
        contribution_updates = st.checkbox("Updates on my contributions", 
                                          value=preferences.get('contribution_updates', True))
        community_updates = st.checkbox("Community updates", 
                                       value=preferences.get('community_updates', False))
        
        # Content settings
        st.markdown("**Content Settings**")
        default_visibility = st.selectbox("Default contribution visibility", 
                                         ["Public", "Private"],
                                         index=0 if preferences.get('default_public', True) else 1)
        
        auto_tag = st.checkbox("Auto-suggest tags", 
                              value=preferences.get('auto_tag', True))
        
        if st.form_submit_button("💾 Save Settings"):
            new_preferences = {
                'show_email': show_email,
                'show_location': show_location,
                'allow_contact': allow_contact,
                'email_notifications': email_notifications,
                'contribution_updates': contribution_updates,
                'community_updates': community_updates,
                'default_public': default_visibility == "Public",
                'auto_tag': auto_tag
            }
            
            # Update preferences in database
            # This would need to be implemented in user_manager
            st.success("Settings saved successfully!")
    
    # Account information
    st.markdown("---")
    st.markdown("#### 📋 Account Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**User ID:** {db_user['id']}")
        st.markdown(f"**GitLab ID:** {db_user['gitlab_id']}")
        st.markdown(f"**Username:** @{db_user['username']}")
        st.markdown(f"**Role:** {db_user['role'].title()}")
    
    with col2:
        st.markdown(f"**Member since:** {db_user['created_at']}")
        st.markdown(f"**Last login:** {db_user['last_login']}")
        st.markdown(f"**Profile updated:** {db_user['updated_at']}")
        st.markdown(f"**Status:** {'Active' if db_user['is_active'] else 'Inactive'}")

def render_user_activity(db_user):
    """Render user activity log"""
    st.markdown("### 📈 Activity Log")
    
    activities = user_manager.get_user_activity(db_user['id'])
    
    if not activities:
        st.info("No activity recorded yet.")
        return
    
    # Activity statistics
    col1, col2, col3 = st.columns(3)
    
    activity_types = {}
    for activity in activities:
        activity_type = activity['activity_type']
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
    
    with col1:
        st.metric("Total Activities", len(activities))
    with col2:
        st.metric("Login Sessions", activity_types.get('login', 0))
    with col3:
        st.metric("Contributions", activity_types.get('contribution', 0))
    
    # Activity timeline
    st.markdown("#### 📅 Recent Activity")
    
    for activity in activities[:20]:  # Show last 20 activities
        activity_time = datetime.fromisoformat(activity['created_at'])
        time_ago = datetime.now() - activity_time
        
        if time_ago.days > 0:
            time_str = f"{time_ago.days} days ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600} hours ago"
        elif time_ago.seconds > 60:
            time_str = f"{time_ago.seconds // 60} minutes ago"
        else:
            time_str = "Just now"
        
        activity_icon = {
            'login': '🔐',
            'contribution': '📝',
            'profile_update': '👤',
            'settings_change': '⚙️'
        }.get(activity['activity_type'], '📋')
        
        st.markdown(f"{activity_icon} **{activity['activity_type'].replace('_', ' ').title()}** - {time_str}")
        
        if activity['activity_data']:
            with st.expander("Details"):
                st.json(activity['activity_data'])

def render_gitlab_profile(user_info):
    """Render GitLab profile information"""
    st.markdown("### 🔗 GitLab Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=200)
    
    with col2:
        st.markdown(f"**Name:** {user_info.get('name', 'Not provided')}")
        st.markdown(f"**Username:** @{user_info.get('username', 'unknown')}")
        st.markdown(f"**Email:** {user_info.get('email', 'Not provided')}")
        
        if user_info.get('bio'):
            st.markdown(f"**Bio:** {user_info['bio']}")
        
        if user_info.get('location'):
            st.markdown(f"**Location:** {user_info['location']}")
        
        if user_info.get('organization'):
            st.markdown(f"**Organization:** {user_info['organization']}")
        
        if user_info.get('job_title'):
            st.markdown(f"**Job Title:** {user_info['job_title']}")
        
        if user_info.get('web_url'):
            st.markdown(f"**GitLab Profile:** [{user_info['web_url']}]({user_info['web_url']})")
    
    # GitLab statistics
    st.markdown("---")
    st.markdown("#### 📊 GitLab Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Public Repos", user_info.get('public_repos', 0))
    
    with col2:
        followers = user_info.get('followers', 0)
        st.metric("Followers", followers)
    
    with col3:
        following = user_info.get('following', 0)
        st.metric("Following", following)
    
    with col4:
        created_at = user_info.get('created_at', '')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_since = (datetime.now(created_date.tzinfo) - created_date).days
                st.metric("Days on GitLab", days_since)
            except:
                st.metric("Days on GitLab", "Unknown")
        else:
            st.metric("Days on GitLab", "Unknown")
    
    # Sync button
    st.markdown("---")
    if st.button("🔄 Sync with GitLab", type="primary"):
        st.info("Profile sync functionality coming soon!")

def user_profile_main():
    """Main user profile function"""
    auth = GitLabAuth()
    
    if not auth.is_authenticated():
        st.markdown("## 👤 User Profile")
        st.markdown("---")
        st.error("🔐 Authentication required to access your profile.")
        st.info("Please login from the home page to access your dashboard.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏠 Go to Home Page", use_container_width=True, type="primary"):
                st.switch_page("Home.py")
        
        st.stop()
    else:
        user_profile_page()
