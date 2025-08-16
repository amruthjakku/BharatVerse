import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')  # Load local env first
load_dotenv('.env')        # Then load default env

# Import modules
from streamlit_app.text_module import text_page
from streamlit_app.analytics_module import analytics_page
from streamlit_app.search_module import search_page
from streamlit_app.community_module import community_page
from streamlit_app.gitlab_module import gitlab_page
from streamlit_app.user_profile import user_profile_page
from streamlit_app.admin_dashboard import admin_dashboard_main
from streamlit_app.utils.database import init_db, get_statistics
from streamlit_app.utils.theme_styling import load_theme_css
from streamlit_app.utils.cache_manager import cache_manager
from streamlit_app.utils.data_handler import get_contributions
from streamlit_app.utils.auth import GitLabAuth, handle_oauth_callback, render_login_button, render_user_info, init_auth

# Page configuration
st.set_page_config(
    page_title="BharatVerse - Preserving India's Culture",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and authentication
init_db()
init_auth()

# Handle OAuth callback if present
handle_oauth_callback()

# Load theme-based CSS after getting theme selection
# This will be loaded after the sidebar is created

# Sidebar theme toggle and navigation
with st.sidebar:
    st.markdown("# 🇮🇳 BharatVerse")
    st.markdown("---")

    # Demo mode completely removed - always use real data from database

    # Theme toggle
    theme = st.selectbox("Select Theme:", ["Light", "Dark"])
    st.markdown("---")

    # Navigation
    auth = GitLabAuth()
    nav_options = ["Home", "Text Stories", "🔍 Discover", "📊 Analytics", "🤝 Community", "🔗 GitLab", "Browse Contributions", "About"]
    
    # Add authenticated user options
    if auth.is_authenticated():
        nav_options.insert(-2, "👤 My Profile")  # Insert before "About"
        
        # Add admin option for admins
        if auth.is_admin():
            nav_options.insert(-2, "🛡️ Admin Dashboard")
    
    page = st.radio("Navigate to:", nav_options)
    
    st.markdown("---")
    st.markdown("### 📊 Live Statistics")
    
    # Get real statistics from database
    stats = get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Contributions", stats['total_contributions'])
    with col2:
        st.metric("Languages", stats['unique_languages'])
    
    # Simplified type metrics
    st.metric("Text Contributions", stats['text_count'])
    
    st.markdown("---")
    
    # Authentication section
    if auth.is_authenticated():
        render_user_info()
    else:
        st.markdown("### 🔐 Authentication")
        st.info("Login with GitLab to contribute and access personalized features.")
        render_login_button()
    
    st.markdown("---")
    st.markdown("### 🌐 Resources")
    st.markdown("[📚 Documentation](https://github.com/bharatverse/bharatverse)")
    st.markdown("[🤗 API Access](https://api.bharatverse.org)")
    st.markdown("[📧 Contact Us](mailto:team@bharatverse.org)")

# Load theme CSS based on selection
load_theme_css(theme)

# Main content
if page == "Home":
    # Enhanced Hero section
    st.markdown("""
    <div class='hero-gradient'>
        <h1 style='font-size: 3.5rem; margin-bottom: 1rem; font-weight: 700; color: white !important;'>🇮🇳 BharatVerse</h1>
        <h2 style='font-size: 1.5rem; margin-bottom: 1rem; font-weight: 400; color: white !important; opacity: 0.95;'>Preserving India's Culture, One Voice at a Time</h2>
        <p style='font-size: 1.1rem; color: white !important; opacity: 0.9; max-width: 600px; margin: 0 auto;'>
            Join thousands of contributors in documenting and preserving India's rich cultural heritage through stories, songs, recipes, and traditions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    stats = get_statistics()
    
    with col1:
        st.markdown("""
        <div class='info-card'>
            <h2>{}</h2>
            <p>Total Contributions</p>
        </div>
        """.format(stats['total_contributions']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
            <h2>{}</h2>
            <p>Languages</p>
        </div>
        """.format(stats['unique_languages']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='info-card'>
            <h2>{}</h2>
            <p>Active Contributors</p>
        </div>
        """.format(stats.get('active_contributors', 0)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='info-card'>
            <h2>{}</h2>
            <p>Regions Covered</p>
        </div>
        """.format(stats['unique_regions']), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card-2'>
            <h3 style='color: white !important;'>📝 Story Keeper</h3>
            <p style='color: white !important;'>Document local customs, proverbs, recipes, and wisdom passed down through generations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Write Story", key="text_btn", use_container_width=True):
            st.session_state.page = "Text Stories"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class='feature-card-3'>
            <h3 style='color: white !important;'>🤝 Community</h3>
            <p style='color: white !important;'>Join groups, collaborate, and participate in challenges with the community.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Community", key="community_btn", use_container_width=True):
            st.session_state.page = "🤝 Community"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class='feature-card-1'>
            <h3 style='color: white !important;'>🔍 Discover</h3>
            <p style='color: white !important;'>Search stories and contributions from across BharatVerse.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Discovering", key="discover_btn", use_container_width=True):
            st.session_state.page = "🔍 Discover"
            st.rerun()
    
    # Recent contributions
    st.markdown("---")
    st.markdown("### 🎆 Recent Contributions")
    
    contributions = get_contributions()
    if not contributions:
        st.info("No contributions found. Upload something to get started!")
    else:
        recent_cols = st.columns(min(4, len(contributions)))
        for i, (col, contrib) in enumerate(zip(recent_cols, contributions[:4])):
            with col:
                st.markdown(f"""
                <div class='contribution-card'>
                    <h2>{contrib['type']}</h2>
                    <h5>{contrib['title']}</h5>
                    <p>{contrib['lang']} • {contrib['time']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Impact metrics
    st.markdown("---")
    st.markdown("### 📈 Our Impact")
    
    metric_cols = st.columns(4)
    metrics = [
        {"label": "Stories Preserved", "value": str(stats['total_contributions']), "delta": "+0 this week"},
        {"label": "Active Contributors", "value": str(stats.get('active_contributors', 0)), "delta": "+0 today"},
        {"label": "Languages Covered", "value": str(stats['unique_languages']), "delta": "+0 this month"},
        {"label": "Research Downloads", "value": "0", "delta": "+0 this month"}
    ]
    
    for col, metric in zip(metric_cols, metrics):
        with col:
            st.metric(metric["label"], metric["value"], metric["delta"])

elif page == "Text Stories":
    text_page()

elif page == "🔍 Discover":
    search_page()

elif page == "📊 Analytics":
    analytics_page()

elif page == "🤝 Community":
    community_page()

elif page == "🔗 GitLab":
    gitlab_page()

elif page == "👤 My Profile":
    user_profile_page()

elif page == "🛡️ Admin Dashboard":
    admin_dashboard_main()

elif page == "Browse Contributions":
    st.markdown("## 🔍 Browse Cultural Contributions")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        language = st.selectbox("Language", ["All", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati"])
    with col2:
        content_type = st.selectbox("Type", ["All", "Audio", "Text", "Image"])
    with col3:
        region = st.selectbox("Region", ["All", "North", "South", "East", "West", "Northeast"])
    with col4:
        time_range = st.selectbox("Time", ["All Time", "Today", "This Week", "This Month"])
    
    # Search
    search = st.text_input("🔍 Search contributions...", placeholder="Search by keyword, tag, or contributor")
    
    # Results grid
    st.markdown("---")
    st.markdown("### 📚 Results")
    
    # Get actual contributions from database
    contributions = get_contributions()
    if not contributions:
        st.info("No contributions found. Upload something to get started!")
    else:
        for i, contrib in enumerate(contributions):
            col1, col2 = st.columns([1, 4])
            with col1:
                icon = {"audio": "🎙️", "text": "📝", "image": "📷"}.get(contrib['type'], "📄")
                st.markdown(f"""
                <div style='background: #f0f2f6; padding: 2rem; border-radius: 8px; text-align: center;'>
                    <h1>{icon}</h1>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"### {contrib['title']}")
                st.markdown(f"**Language:** {contrib['lang']} | **Type:** {contrib['type'].title()} | **Time:** {contrib['time']}")
                if contrib.get('description'):
                    st.markdown(contrib['description'][:100] + "..." if len(contrib.get('description', '')) > 100 else contrib.get('description', ''))
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button(f"👁️ View", key=f"view_{i}")
                with col2:
                    st.button(f"📝 Details", key=f"details_{i}")
                with col3:
                    st.button(f"💾 Download", key=f"download_{i}")
            st.markdown("---")

elif page == "About":
    st.markdown("""
    ## 🎆 About BharatVerse
    
    BharatVerse is an open-source platform dedicated to preserving and celebrating India's rich cultural heritage. 
    Our mission is to create a comprehensive digital archive of India's diverse traditions, languages, and customs.
    
    ### 🎯 Our Mission
    - **Preserve** endangered languages and oral traditions
    - **Document** cultural practices before they're lost
    - **Share** knowledge across generations and communities
    - **Empower** communities to tell their own stories
    
    ### 🤝 How to Contribute
    1. **Record** audio of folk songs, stories, or local traditions
    2. **Write** about customs, recipes, or cultural practices
    3. **Upload** images of festivals, art, or cultural symbols
    4. **Tag** content appropriately for easy discovery
    5. **Share** with your community and invite others
    
    ### 📞 Contact Us
    - **Email:** team@bharatverse.org
    - **GitHub:** [github.com/bharatverse](https://github.com/bharatverse)
    - **Twitter:** [@bharatverse](https://twitter.com/bharatverse)
    
    ### 📜 License
    - **Code:** MIT License
    - **Data:** CC-BY 4.0
    
    ---
    
    <div style='text-align: center; padding: 2rem;'>
        <p>Made with ❤️ for India's cultural heritage</p>
    </div>
    """, unsafe_allow_html=True)
