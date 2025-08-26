"""
User Dashboard for BharatVerse
Personal dashboard for regular users to view their contributions and activity
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import utilities with error handling
AUTH_AVAILABLE = False
DATABASE_AVAILABLE = False
STYLING_AVAILABLE = False
SUPABASE_AVAILABLE = False

try:
    from streamlit_app.utils.auth import get_auth_manager
    AUTH_AVAILABLE = True
except ImportError as e:
    AUTH_AVAILABLE = False
    # Store error for later display
    AUTH_ERROR = str(e)

# Database disabled for simplified version
DATABASE_AVAILABLE = False

try:
    from streamlit_app.utils.main_styling import load_custom_css
    STYLING_AVAILABLE = True
except ImportError as e:
    STYLING_AVAILABLE = False
    STYLING_ERROR = str(e)

# Database disabled for simplified version
SUPABASE_AVAILABLE = False

def check_user_access():
    """Check if user is authenticated"""
    if not AUTH_AVAILABLE:
        # Use fallback auth
        try:
            from utils.fallback_auth import get_fallback_auth_manager, render_fallback_login
            auth = get_fallback_auth_manager()
            
            if not auth.is_authenticated():
                st.error("🔒 Please login to access your dashboard")
                render_fallback_login()
                st.stop()
            
            user_info = auth.get_current_user()
            return user_info, auth
        except ImportError:
            st.error("🔒 Authentication system not available")
            st.warning("User dashboard requires authentication to be configured.")
            st.stop()
    
    auth = get_auth_manager()
    if not auth.is_authenticated():
        st.error("🔒 Please login to access your dashboard")
        st.markdown("### 🔗 Login Required")
        try:
            from streamlit_app.utils.auth import render_login_button
            render_login_button()
        except ImportError:
            st.info("Please configure authentication to access your dashboard.")
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

def show_dashboard_header(user_info, auth):
    """Show enhanced dashboard header with user greeting"""
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "🌅 Good Morning"
    elif current_hour < 17:
        greeting = "☀️ Good Afternoon"
    else:
        greeting = "🌙 Good Evening"
    
    # Header with greeting
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title(f"{greeting}, {user_info.get('name', 'Friend')}!")
        st.markdown("*Welcome to your BharatVerse dashboard*")
    
    with col2:
        # Quick stats badge
        username = user_info.get('username', 'unknown')
        contrib_stats, _ = get_user_contributions(username)
        total_contributions = sum([stat[1] for stat in contrib_stats]) if contrib_stats else 0
        
        st.metric("🏆 Total Contributions", total_contributions)
    
    with col3:
        # User level/badge
        if total_contributions >= 50:
            level = "🌟 Cultural Master"
        elif total_contributions >= 20:
            level = "🎭 Heritage Keeper"
        elif total_contributions >= 5:
            level = "📚 Story Teller"
        else:
            level = "🌱 New Explorer"
        
        st.markdown(f"**Your Level:**")
        st.markdown(f"### {level}")

def show_achievement_system(username: str):
    """Show user achievements and progress"""
    st.subheader("🏆 Your Achievements")
    
    contrib_stats, recent_contribs = get_user_contributions(username)
    total_contributions = sum([stat[1] for stat in contrib_stats]) if contrib_stats else 0
    
    # Achievement definitions
    achievements = [
        {"name": "First Steps", "desc": "Make your first contribution", "icon": "🌱", "threshold": 1},
        {"name": "Story Teller", "desc": "Share 5 cultural stories", "icon": "📚", "threshold": 5},
        {"name": "Heritage Keeper", "desc": "Contribute 20 items", "icon": "🎭", "threshold": 20},
        {"name": "Cultural Master", "desc": "Reach 50 contributions", "icon": "🌟", "threshold": 50},
        {"name": "Community Leader", "desc": "Make 100 contributions", "icon": "👑", "threshold": 100},
    ]
    
    # Show achievements in a grid
    cols = st.columns(5)
    for i, achievement in enumerate(achievements):
        with cols[i]:
            earned = total_contributions >= achievement["threshold"]
            if earned:
                st.markdown(f"### {achievement['icon']}")
                st.markdown(f"**{achievement['name']}**")
                st.success("✅ Earned!")
            else:
                st.markdown(f"### 🔒")
                st.markdown(f"**{achievement['name']}**")
                progress = min(total_contributions / achievement["threshold"], 1.0)
                st.progress(progress)
                st.caption(f"{total_contributions}/{achievement['threshold']}")
    
    # Progress to next achievement
    next_achievement = None
    for achievement in achievements:
        if total_contributions < achievement["threshold"]:
            next_achievement = achievement
            break
    
    if next_achievement:
        st.markdown("### 🎯 Next Goal")
        progress = total_contributions / next_achievement["threshold"]
        st.progress(progress)
        remaining = next_achievement["threshold"] - total_contributions
        st.markdown(f"**{remaining} more contributions** to unlock **{next_achievement['name']}** {next_achievement['icon']}")

def show_contribution_calendar(username: str):
    """Show contribution activity calendar"""
    st.subheader("📅 Your Contribution Activity")
    
    contrib_stats, recent_contribs = get_user_contributions(username)
    
    if recent_contribs:
        # Create a simple activity visualization
        dates = []
        for contrib in recent_contribs:
            try:
                # Parse date from contribution
                date_str = contrib[2]  # created_at
                if isinstance(date_str, str):
                    # Try to parse different date formats
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    dates.append(date.date())
            except:
                continue
        
        if dates:
            # Count contributions by date
            date_counts = {}
            for date in dates:
                date_counts[date] = date_counts.get(date, 0) + 1
            
            # Create DataFrame for visualization
            df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Contributions'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Show chart
            st.line_chart(df.set_index('Date'))
            
            # Show streak info
            if dates:
                latest_date = max(dates)
                days_since_last = (datetime.now().date() - latest_date).days
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 Most Active Day", f"{max(date_counts.values())} contributions")
                with col2:
                    if days_since_last == 0:
                        st.metric("🔥 Last Contribution", "Today!")
                    elif days_since_last == 1:
                        st.metric("🔥 Last Contribution", "Yesterday")
                    else:
                        st.metric("🔥 Last Contribution", f"{days_since_last} days ago")
    else:
        st.info("Start contributing to see your activity calendar!")

def show_personalized_recommendations(username: str):
    """Show personalized recommendations based on user activity"""
    st.subheader("💡 Personalized Recommendations")
    
    contrib_stats, recent_contribs = get_user_contributions(username)
    
    # Analyze user's contribution patterns
    audio_count = next((stat[1] for stat in contrib_stats if stat[0] == 'audio'), 0)
    text_count = next((stat[1] for stat in contrib_stats if stat[0] == 'text'), 0)
    image_count = next((stat[1] for stat in contrib_stats if stat[0] == 'image'), 0)
    
    recommendations = []
    
    # Generate recommendations based on activity
    if audio_count == 0:
        recommendations.append({
            "title": "🎤 Try Audio Recording",
            "desc": "Share your voice! Record traditional songs, stories, or cultural practices.",
            "action": "Record Audio",
            "page": "pages/01_🎤_Audio_Capture.py"
        })
    
    if text_count == 0:
        recommendations.append({
            "title": "📝 Write Your Story",
            "desc": "Document family traditions, local legends, or cultural memories.",
            "action": "Write Story",
            "page": "pages/02_📝_Text_Stories.py"
        })
    
    if image_count == 0:
        recommendations.append({
            "title": "📸 Share Visual Heritage",
            "desc": "Upload photos of cultural artifacts, festivals, or traditional art.",
            "action": "Upload Images",
            "page": "pages/03_📸_Visual_Heritage.py"
        })
    
    # Add general recommendations
    if len(contrib_stats) > 0:
        recommendations.append({
            "title": "🔍 Explore Community",
            "desc": "Discover what others are sharing and connect with fellow contributors.",
            "action": "Browse Community",
            "page": "pages/06_🤝_Community.py"
        })
    
    if not recommendations:
        recommendations.append({
            "title": "🌟 You're doing great!",
            "desc": "Keep sharing your cultural heritage. Every contribution matters!",
            "action": "View Analytics",
            "page": "pages/05_📊_Analytics.py"
        })
    
    # Display recommendations
    for i, rec in enumerate(recommendations[:3]):  # Show top 3
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{rec['title']}**")
                st.markdown(rec['desc'])
            with col2:
                if st.button(rec['action'], key=f"rec_{i}"):
                    st.switch_page(rec['page'])

def main():
    st.set_page_config(
        page_title="My Dashboard - BharatVerse",
        page_icon="👤",
        layout="wide"
    )
    
    # Load custom CSS
    if STYLING_AVAILABLE:
        load_custom_css()
    
    # Custom CSS for dashboard enhancements
    st.markdown("""
    <style>
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .achievement-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    .achievement-earned {
        border-color: #4CAF50;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
    }
    .recommendation-card {
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check user access
    if not AUTH_AVAILABLE:
        st.error("🔒 Authentication system not available")
        st.warning("User dashboard requires authentication to be configured.")
        st.info("Please configure authentication to access your personal dashboard.")
        
        # Show debug information
        if st.checkbox("Show debug information"):
            st.code(f"Auth Error: {globals().get('AUTH_ERROR', 'Unknown error')}")
            if not DATABASE_AVAILABLE:
                st.code(f"Database Error: {globals().get('DATABASE_ERROR', 'Unknown error')}")
            if not SUPABASE_AVAILABLE:
                st.code(f"Supabase Error: {globals().get('SUPABASE_ERROR', 'Unknown error')}")
        
        st.stop()
    
    user_info, auth = check_user_access()
    username = user_info.get('username', 'unknown')
    
    # Enhanced dashboard header
    show_dashboard_header(user_info, auth)
    
    st.markdown("---")
    
    # Sidebar navigation with enhanced options
    st.sidebar.title("📋 Dashboard Menu")
    
    menu_option = st.sidebar.selectbox(
        "Choose section:",
        [
            "🏠 Overview",
            "👤 Profile",
            "📊 My Contributions", 
            "🏆 Achievements",
            "📅 Activity Calendar",
            "💡 Recommendations",
            "📈 Recent Activity",
            "🚀 Quick Actions",
            "🏘️ Community"
        ]
    )
    
    # Show user info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Your Info")
    st.sidebar.markdown(f"**Name:** {user_info.get('name', 'Unknown')}")
    st.sidebar.markdown(f"**Username:** @{username}")
    
    # Quick stats in sidebar
    contrib_stats, _ = get_user_contributions(username)
    total_contributions = sum([stat[1] for stat in contrib_stats]) if contrib_stats else 0
    st.sidebar.metric("🏆 Contributions", total_contributions)
    
    # Main content based on menu selection
    if menu_option == "🏠 Overview":
        # Overview dashboard with key highlights
        col1, col2 = st.columns([2, 1])
        
        with col1:
            show_contribution_summary(username)
            st.markdown("---")
            show_recent_activity(username)
        
        with col2:
            show_personalized_recommendations(username)
            st.markdown("---")
            show_quick_actions()
    
    elif menu_option == "👤 Profile":
        show_user_stats(user_info, auth)
        
    elif menu_option == "📊 My Contributions":
        show_contribution_summary(username)
        
    elif menu_option == "🏆 Achievements":
        show_achievement_system(username)
        
    elif menu_option == "📅 Activity Calendar":
        show_contribution_calendar(username)
        
    elif menu_option == "💡 Recommendations":
        show_personalized_recommendations(username)
        
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