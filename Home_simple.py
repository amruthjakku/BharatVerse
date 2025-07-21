import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Simple deployment-safe imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Detect deployment mode
DEPLOYMENT_MODE = os.getenv("AI_MODE", "cloud")
IS_CLOUD_DEPLOYMENT = True  # Force cloud mode for deployment

# Safe imports with fallbacks
try:
    from streamlit_app.utils.main_styling import load_custom_css
    STYLING_AVAILABLE = True
except ImportError:
    STYLING_AVAILABLE = False

try:
    from streamlit_app.utils.auth import GitLabAuth, handle_oauth_callback, render_login_button, init_auth
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

def main():
    """Main application function"""
    st.set_page_config(
        page_title="BharatVerse - Cultural Heritage Platform",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply styling if available
    if STYLING_AVAILABLE:
        try:
            load_custom_css()
        except Exception:
            pass
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #FF6B35; font-size: 3rem; margin-bottom: 0.5rem;">
            🏛️ BharatVerse
        </h1>
        <h2 style="color: #2E86AB; font-size: 1.5rem; margin-bottom: 2rem;">
            Preserving India's Cultural Heritage
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
                color: white; padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        <h3 style="color: white; margin-bottom: 1rem;">Welcome to BharatVerse! 🎉</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            Join thousands of cultural enthusiasts in preserving and sharing India's rich heritage.
        </p>
        <p style="font-size: 1rem; opacity: 0.9;">
            Document family stories, discover hidden cultural gems, and connect with like-minded heritage preservationists.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 4px solid #FF6B35;">
            <h4 style="color: #FF6B35; margin-bottom: 1rem;">🎤 Audio Stories</h4>
            <p>Record and preserve oral traditions, family stories, and cultural narratives.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 4px solid #2E86AB;">
            <h4 style="color: #2E86AB; margin-bottom: 1rem;">📝 Text Documentation</h4>
            <p>Write and share cultural stories, traditions, and historical accounts.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-top: 4px solid #A23B72;">
            <h4 style="color: #A23B72; margin-bottom: 1rem;">🖼️ Visual Heritage</h4>
            <p>Upload and analyze cultural artifacts, photographs, and artwork.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    st.markdown("### 🧭 Explore BharatVerse")
    
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("🎤 Audio Capture", use_container_width=True):
            st.switch_page("pages/01_🎤_Audio_Capture.py")
    
    with nav_col2:
        if st.button("📝 Text Stories", use_container_width=True):
            st.switch_page("pages/02_📝_Text_Stories.py")
    
    with nav_col3:
        if st.button("🖼️ Visual Heritage", use_container_width=True):
            st.switch_page("pages/03_🖼️_Visual_Heritage.py")
    
    with nav_col4:
        if st.button("🔍 Discover", use_container_width=True):
            st.switch_page("pages/04_🔍_Discover.py")
    
    # Community stats (mock data for demo)
    st.markdown("---")
    st.markdown("### 📊 Community Impact")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Cultural Stories", "2,547", "+127")
    
    with stat_col2:
        st.metric("Active Users", "1,234", "+89")
    
    with stat_col3:
        st.metric("Heritage Sites", "456", "+23")
    
    with stat_col4:
        st.metric("Languages", "28", "+2")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666;">
        <p>🏛️ <strong>BharatVerse</strong> - Preserving India's Cultural Heritage for Future Generations</p>
        <p style="font-size: 0.9rem;">Made with ❤️ for cultural preservation</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()