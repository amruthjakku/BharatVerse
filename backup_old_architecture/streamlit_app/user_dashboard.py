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
    
    # Get current user
    auth = GitLabAuth()
    db_user = auth.get_current_db_user()
    
    if not db_user:
        st.error("Unable to load user data")
        return
    
    user_id = db_user.get('id')
    
    # Get real user statistics from database
    try:
        contributions = user_manager.get_user_contributions(user_id)
        contribution_count = len(contributions) if contributions else 0
        
        # Calculate stats from actual data
        audio_count = len([c for c in contributions if c.get('type') == 'audio']) if contributions else 0
        photo_count = len([c for c in contributions if c.get('type') == 'photo']) if contributions else 0
        
        # Calculate points (simple: 10 points per contribution)
        total_points = contribution_count * 10
        
    except Exception as e:
        # Fallback if database methods don't exist yet
        contribution_count = 0
        audio_count = 0
        photo_count = 0
        total_points = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 Contributions",
            value=str(contribution_count),
            delta=None
        )
    
    with col2:
        st.metric(
            label="🎵 Audio Uploads",
            value=str(audio_count),
            delta=None
        )
    
    with col3:
        st.metric(
            label="📸 Photos Shared",
            value=str(photo_count),
            delta=None
        )
    
    with col4:
        st.metric(
            label="⭐ Points Earned",
            value=str(total_points),
            delta=None
        )

def show_recent_contributions():
    """Display user's recent contributions"""
    st.markdown("### 📚 Your Recent Contributions")
    
    # Get current user
    auth = GitLabAuth()
    db_user = auth.get_current_db_user()
    
    if not db_user:
        st.error("Unable to load user data")
        return
    
    user_id = db_user.get('id')
    
    try:
        # Get real contributions from database
        contributions = user_manager.get_user_contributions(user_id)
        
        if not contributions:
            st.info("🌟 You haven't made any contributions yet!")
            st.markdown("""
            **Get started by:**
            - 📝 Writing about your cultural experiences
            - 🎵 Sharing traditional songs or stories
            - 📸 Uploading photos of cultural events
            - 🎭 Documenting local traditions
            """)
            return
        
        # Convert to DataFrame for display
        contributions_data = []
        for contrib in contributions[:10]:  # Show last 10
            contributions_data.append({
                'Date': contrib.get('created_at', 'Unknown'),
                'Type': contrib.get('type', 'Unknown').title(),
                'Title': contrib.get('title', 'Untitled'),
                'Status': contrib.get('status', 'Unknown'),
                'Views': contrib.get('views', 0)
            })
        
        if contributions_data:
            df = pd.DataFrame(contributions_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No contributions found.")
            
    except Exception as e:
        # Fallback if database methods don't exist yet
        st.info("🌟 You haven't made any contributions yet!")
        st.markdown("""
        **Get started by:**
        - 📝 Writing about your cultural experiences
        - 🎵 Sharing traditional songs or stories
        - 📸 Uploading photos of cultural events
        - 🎭 Documenting local traditions
        """)
        
        # Show placeholder for development
        if st.checkbox("Show sample data structure (Development Mode)"):
            st.markdown("*This is how your contributions will appear:*")
            sample_data = {
                'Date': ['No contributions yet'],
                'Type': ['Sample'],
                'Title': ['Your contributions will appear here'],
                'Status': ['Ready'],
                'Views': [0]
            }
            df = pd.DataFrame(sample_data)
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
    
    try:
        # Get real community data
        all_users = user_manager.get_all_users(limit=100)
        
        # Featured content
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Trending This Week")
            
            # Try to get trending content from database
            # For now, show placeholder until content system is implemented
            trending_content = []
            
            if trending_content:
                for content in trending_content[:5]:
                    st.markdown(f"- **{content['title']}** - {content['views']} views")
            else:
                st.info("📈 Trending content will appear here as the community grows!")
                st.markdown("""
                *Coming soon:*
                - Most viewed contributions
                - Popular cultural stories
                - Trending audio recordings
                - Featured photo collections
                """)
        
        with col2:
            st.markdown("#### 🏆 Top Contributors")
            
            # Get top contributors from real data
            if all_users:
                # Sort users by contribution count (when available)
                top_contributors = []
                for user in all_users:
                    try:
                        contributions = user_manager.get_user_contributions(user['id'])
                        contrib_count = len(contributions) if contributions else 0
                        if contrib_count > 0:
                            top_contributors.append({
                                'name': user.get('name', user.get('username', 'Unknown')),
                                'username': user.get('username', 'unknown'),
                                'count': contrib_count
                            })
                    except:
                        pass
                
                # Sort by contribution count
                top_contributors.sort(key=lambda x: x['count'], reverse=True)
                
                if top_contributors:
                    for contributor in top_contributors[:5]:
                        st.markdown(f"- **{contributor['name']}** (@{contributor['username']}) - {contributor['count']} contributions")
                else:
                    st.info("🏆 Top contributors will appear here!")
                    st.markdown("""
                    *Be the first to contribute and see your name here!*
                    - Share your cultural stories
                    - Upload traditional music
                    - Document local festivals
                    - Preserve heritage knowledge
                    """)
            else:
                st.info("🏆 Top contributors will appear here as the community grows!")
                
    except Exception as e:
        # Fallback display
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Trending This Week")
            st.info("📈 Trending content will appear here as the community grows!")
        
        with col2:
            st.markdown("#### 🏆 Top Contributors")
            st.info("🏆 Top contributors will appear here as users start contributing!")

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