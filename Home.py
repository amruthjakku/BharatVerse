import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import styling and authentication
from streamlit_app.utils.enhanced_styling import apply_enhanced_styling
from streamlit_app.utils.auth import GitLabAuth, handle_oauth_callback, render_login_button, init_auth
from streamlit_app.utils.user_manager import user_manager

def show_login_section():
    """Display login section with GitLab OAuth"""
    st.markdown("---")
    st.markdown("## 🔐 Login to Access Your Dashboard")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        **Login Required**: Please authenticate with your GitLab account to access:
        - 👤 Personal User Dashboard
        - 🛡️ Admin Dashboard (for administrators)
        - 🤝 Community Features
        - 📁 Content Management
        """)
        
        render_login_button()
        
        st.markdown("""<br>
        <div style='text-align: center; color: #666;'>
            <small>By logging in, you agree to our terms of service and privacy policy.</small>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="BharatVerse - Digital Cultural Heritage",
        page_icon="🇮🇳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize authentication
    auth = GitLabAuth()
    
    # Initialize auth system (handles OAuth callback)
    init_auth()
    
    # Apply enhanced styling
    apply_enhanced_styling()
    
    # Check authentication and redirect if logged in
    if auth.is_authenticated():
        db_user = auth.get_current_db_user()
        if db_user:
            # Show welcome message and redirect button
            st.markdown("""
            <div style='text-align: center; padding: 2rem 0;'>
                <h1 style='color: #FF6B35; font-size: 3.5rem; margin-bottom: 0.5rem;'>🇮🇳 BharatVerse</h1>
            </div>
            """, unsafe_allow_html=True)
            
            st.success(f"Welcome back, {db_user.get('name', 'User')}!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if db_user.get('role') == 'admin':
                    st.info("🛡️ You have administrator privileges.")
                    if st.button("📊 Go to Admin Dashboard", use_container_width=True, type="primary"):
                        st.switch_page("pages/01_📊_Dashboard.py")
                else:
                    st.info("👤 Welcome to your personal dashboard.")
                    if st.button("📊 Go to My Dashboard", use_container_width=True, type="primary"):
                        st.switch_page("pages/01_📊_Dashboard.py")
                
                if st.button("🚪 Logout", use_container_width=True):
                    auth.logout()
                    st.rerun()
            
            st.stop()
    
    # Main header for non-authenticated users
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #FF6B35; font-size: 3.5rem; margin-bottom: 0.5rem;'>🇮🇳 BharatVerse</h1>
        <h2 style='color: #2E86AB; font-size: 1.8rem; margin-bottom: 1rem;'>Digital Cultural Heritage Platform</h2>
        <p style='font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto;'>
            Preserve, share, and celebrate the rich cultural heritage of India through digital storytelling, 
            audio recordings, visual documentation, and community collaboration.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎵 Audio Heritage
        Record and preserve traditional songs, stories, and oral traditions from across India.
        - Folk songs and classical music
        - Oral histories and legends
        - Regional dialects and languages
        - Traditional ceremonies
        """)
        
    with col2:
        st.markdown("""
        ### 📚 Cultural Stories
        Document and share the rich tapestry of Indian culture through written narratives.
        - Family traditions and customs
        - Festival celebrations
        - Regional cuisines and recipes
        - Historical accounts
        """)
        
    with col3:
        st.markdown("""
        ### 🖼️ Visual Documentation
        Capture the visual essence of Indian heritage through photographs and artwork.
        - Traditional arts and crafts
        - Architecture and monuments
        - Cultural events and festivals
        - Regional costumes and jewelry
        """)
    
    # Quick start section
    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Record Audio", use_container_width=True, type="primary"):
            st.switch_page("pages/01_🎤_Audio_Capture.py")
    
    with col2:
        if st.button("📝 Share Story", use_container_width=True, type="primary"):
            st.switch_page("pages/02_📝_Text_Stories.py")
    
    with col3:
        if st.button("📸 Upload Image", use_container_width=True, type="primary"):
            st.switch_page("pages/03_📸_Visual_Heritage.py")
    
    with col4:
        if st.button("🔍 Explore", use_container_width=True, type="primary"):
            st.switch_page("pages/04_🔍_Discover.py")
    
    # Features overview
    st.markdown("---")
    st.markdown("## ✨ Platform Features")
    
    features = [
        {
            "icon": "🎵",
            "title": "Audio Recording & Preservation",
            "description": "High-quality audio recording with automatic transcription and metadata tagging"
        },
        {
            "icon": "📚",
            "title": "Story Documentation",
            "description": "Rich text editor with multimedia support for comprehensive cultural documentation"
        },
        {
            "icon": "🖼️",
            "title": "Visual Heritage Archive",
            "description": "Image upload with AI-powered tagging and cultural context recognition"
        },
        {
            "icon": "🔍",
            "title": "Smart Discovery",
            "description": "Advanced search and filtering to explore cultural content by region, type, and theme"
        },
        {
            "icon": "📊",
            "title": "Analytics & Insights",
            "description": "Data visualization and trends analysis of cultural contributions and engagement"
        },
        {
            "icon": "🤝",
            "title": "Community Collaboration",
            "description": "Connect with cultural enthusiasts, experts, and contributors from across India"
        },
        {
            "icon": "🤖",
            "title": "AI-Powered Insights",
            "description": "Machine learning analysis for content categorization, sentiment analysis, and recommendations"
        },
        {
            "icon": "👥",
            "title": "Project Management",
            "description": "Collaborative tools for organizing cultural preservation projects and team workflows"
        }
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; border-left: 4px solid #FF6B35;'>
                <h3 style='color: #2E86AB; margin: 0 0 0.5rem 0;'>{feature['icon']} {feature['title']}</h3>
                <p style='color: #666; margin: 0;'>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #FF6B35, #2E86AB); border-radius: 15px; color: white;'>
        <h2 style='margin-bottom: 1rem;'>Join the Cultural Preservation Movement</h2>
        <p style='font-size: 1.1rem; margin-bottom: 1.5rem;'>
            Every story, song, and image you contribute helps preserve India's rich cultural heritage for future generations.
        </p>
        <p style='font-size: 1rem; opacity: 0.9;'>
            Start by exploring the navigation menu on the left to begin your cultural documentation journey.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add authentication notice
    st.markdown("---")
    st.info("🔐 **Authentication**: This platform uses GitLab OAuth for secure authentication. Login with your GitLab account to access community features and content creation tools.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**👤 Authenticated Users can access:**")
        st.markdown("• Community groups and chat")
        st.markdown("• Discussion forums")
        st.markdown("• Challenges and leaderboards")
        st.markdown("• Profile management")
        st.markdown("• Content creation and upload")
        
    with col2:
        st.markdown("**🛡️ Admin Users can access:**")
        st.markdown("• All user features")
        st.markdown("• Admin dashboard")
        st.markdown("• User management")
        st.markdown("• System analytics")
        st.markdown("• Platform configuration")
        
    st.markdown("**Note:** Admin privileges are determined by your GitLab account permissions and platform configuration.")
    
    # Show login section at the bottom
    show_login_section()

if __name__ == "__main__":
    main()
