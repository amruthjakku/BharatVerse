"""
User Dashboard Module for BharatVerse
Provides dashboard functionality for regular users
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from .utils.auth import GitLabAuth
from .utils.user_manager import user_manager

def show_user_stats():
    """Display user statistics and activity"""
    st.markdown("### 📈 Your Activity")
    
    # Mock user statistics (replace with actual data from database)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Contributions",
            value="12",
            delta="3 this month"
        )
    
    with col2:
        st.metric(
            label="🎵 Audio Uploads",
            value="8",
            delta="2 this week"
        )
    
    with col3:
        st.metric(
            label="📸 Photos Shared",
            value="25",
            delta="5 this month"
        )
    
    with col4:
        st.metric(
            label="⭐ Points Earned",
            value="340",
            delta="45 this week"
        )

def show_recent_contributions():
    """Display user's recent contributions"""
    st.markdown("### 📚 Your Recent Contributions")
    
    # Mock data (replace with actual database queries)
    contributions_data = {
        'Date': ['2024-01-15', '2024-01-12', '2024-01-10', '2024-01-08'],
        'Type': ['Audio Story', 'Photo Collection', 'Cultural Article', 'Folk Song'],
        'Title': [
            'Traditional Wedding Songs from Rajasthan',
            'Holi Festival Celebrations 2024',
            'The Art of Madhubani Painting',
            'Bhojpuri Folk Songs Collection'
        ],
        'Status': ['Published', 'Under Review', 'Published', 'Published'],
        'Views': [156, 23, 89, 234]
    }
    
    df = pd.DataFrame(contributions_data)
    st.dataframe(df, use_container_width=True)

def show_quick_actions():
    """Display quick action buttons for users"""
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 New Contribution", use_container_width=True, type="primary"):
            st.switch_page("pages/02_📝_Contribute.py")
    
    with col2:
        if st.button("🎵 Upload Audio", use_container_width=True):
            st.switch_page("pages/03_🎵_Audio_Stories.py")
    
    with col3:
        if st.button("📸 Share Photos", use_container_width=True):
            st.switch_page("pages/04_📸_Visual_Heritage.py")

def show_community_highlights():
    """Display community highlights and featured content"""
    st.markdown("### 🌟 Community Highlights")
    
    # Featured content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🔥 Trending This Week
        - **Diwali Celebrations Across India** - 1.2k views
        - **Traditional Cooking Methods** - 890 views  
        - **Folk Dance Forms of South India** - 756 views
        - **Ancient Temple Architecture** - 623 views
        """)
    
    with col2:
        st.markdown("""
        #### 🏆 Top Contributors
        - **Priya Sharma** - 15 contributions this month
        - **Rajesh Kumar** - 12 audio stories shared
        - **Meera Patel** - 8 photo collections
        - **Arjun Singh** - 6 cultural articles
        """)

def show_learning_resources():
    """Display learning resources and tutorials"""
    st.markdown("### 📖 Learning Resources")
    
    with st.expander("🎯 How to Create Quality Contributions"):
        st.markdown("""
        **Tips for great contributions:**
        - Use clear, descriptive titles
        - Provide detailed descriptions
        - Include relevant tags and categories
        - Add location information when applicable
        - Ensure good audio/image quality
        """)
    
    with st.expander("📱 Mobile App Features"):
        st.markdown("""
        **Coming Soon:**
        - Offline recording capabilities
        - GPS-based location tagging
        - Community challenges and events
        - Real-time collaboration tools
        """)

def show_profile_summary():
    """Display user profile summary"""
    auth = GitLabAuth()
    db_user = auth.get_current_db_user()
    
    if db_user:
        st.markdown("### 👤 Profile Summary")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Profile picture placeholder
            st.markdown("""
            <div style='width: 100px; height: 100px; border-radius: 50%; 
                        background: linear-gradient(45deg, #FF6B35, #F7931E); 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 2rem; color: white; margin: 0 auto;'>
                👤
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **Name:** {db_user.get('name', 'N/A')}  
            **Email:** {db_user.get('email', 'N/A')}  
            **Role:** {db_user.get('role', 'user').title()}  
            **Member Since:** {db_user.get('created_at', 'N/A')}  
            **GitLab:** @{db_user.get('gitlab_username', 'N/A')}
            """)
            
            if st.button("✏️ Edit Profile", key="edit_profile"):
                st.switch_page("pages/10_👤_My_Profile.py")

def user_dashboard_main():
    """Main function for user dashboard"""
    
    # Check authentication
    auth = GitLabAuth()
    if not auth.is_authenticated():
        st.error("Please login to access your dashboard.")
        return
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("## 👤 User Menu")
        
        db_user = auth.get_current_db_user()
        if db_user:
            st.success(f"Welcome, {db_user.get('name', 'User')}!")
            
            if st.button("🚪 Logout", use_container_width=True):
                auth.logout()
                st.switch_page("Home.py")
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        
        if st.button("📝 New Contribution", use_container_width=True):
            st.switch_page("pages/02_📝_Contribute.py")
        
        if st.button("👤 My Profile", use_container_width=True):
            st.switch_page("pages/10_👤_My_Profile.py")
        
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")
    
    # Main dashboard content
    show_profile_summary()
    st.markdown("---")
    
    show_user_stats()
    st.markdown("---")
    
    show_quick_actions()
    st.markdown("---")
    
    show_recent_contributions()
    st.markdown("---")
    
    show_community_highlights()
    st.markdown("---")
    
    show_learning_resources()