import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import modules
from streamlit_app.audio_module import audio_page
from streamlit_app.text_module import text_page
from streamlit_app.image_module import image_page
from streamlit_app.analytics_module import analytics_page
from streamlit_app.search_module import search_page
from streamlit_app.community_module import community_page
from streamlit_app.ai_module import ai_insights_page
from streamlit_app.collaboration_module import collaboration_page
from streamlit_app.utils.database import init_db, get_statistics
from streamlit_app.utils.theme_styling import load_theme_css
from streamlit_app.utils.cache_manager import cache_manager

# Page configuration
st.set_page_config(
    page_title="BharatVerse - Preserving India's Culture",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Load theme-based CSS after getting theme selection
# This will be loaded after the sidebar is created

# Sidebar theme toggle and navigation
with st.sidebar:
    st.markdown("# 🇮🇳 BharatVerse")
    st.markdown("---")

    # Theme toggle
    theme = st.selectbox("Select Theme:", ["Light", "Dark"])
    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigate to:",
        ["Home", "Audio Capture", "Text Stories", "Visual Heritage", "🔍 Discover", "📊 Analytics", "🤝 Community", "🤖 AI Insights", "👥 Collaboration", "Browse Contributions", "About"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Live Statistics")
    
    # Get real statistics from database
    stats = get_statistics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Contributions", stats['total_contributions'])
    with col2:
        st.metric("Languages", stats['unique_languages'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Audio", stats['audio_count'])
    with col2:
        st.metric("Text", stats['text_count'])
    
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
            <h2>2,847</h2>
            <p>Active Contributors</p>
        </div>
        """, unsafe_allow_html=True)
    
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
        <div class='feature-card-1'>
            <h3 style='color: white !important;'>🎙️ Audio Magic</h3>
            <p style='color: white !important;'>Record and transcribe folk songs, stories, and oral traditions in 22+ Indian languages.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Recording", key="audio_btn", use_container_width=True):
            st.session_state.page = "Audio Capture"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class='feature-card-2'>
            <h3 style='color: white !important;'>📝 Story Keeper</h3>
            <p style='color: white !important;'>Document local customs, proverbs, recipes, and wisdom passed down through generations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Write Story", key="text_btn", use_container_width=True):
            st.session_state.page = "Text Stories"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class='feature-card-3'>
            <h3 style='color: white !important;'>📷 Visual Heritage</h3>
            <p style='color: white !important;'>Upload and caption images of festivals, art, architecture, and cultural symbols.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Image", key="image_btn", use_container_width=True):
            st.session_state.page = "Visual Heritage"
            st.rerun()
    
    # Recent contributions
    st.markdown("---")
    st.markdown("### 🎆 Recent Contributions")
    
    recent_cols = st.columns(4)
    contributions = [
        {"type": "🎙️", "title": "Baul Song from Bengal", "lang": "Bengali", "time": "2 hours ago"},
        {"type": "📝", "title": "Pongal Recipe", "lang": "Tamil", "time": "5 hours ago"},
        {"type": "📷", "title": "Durga Puja Celebration", "lang": "Hindi", "time": "1 day ago"},
        {"type": "🎙️", "title": "Lavani Performance", "lang": "Marathi", "time": "2 days ago"}
    ]
    
    for i, (col, contrib) in enumerate(zip(recent_cols, contributions)):
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
        {"label": "Stories Preserved", "value": "15,234", "delta": "+234 this week"},
        {"label": "Active Contributors", "value": "3,456", "delta": "+56 today"},
        {"label": "Languages Covered", "value": "22", "delta": "+2 this month"},
        {"label": "Research Downloads", "value": "45,678", "delta": "+1,234 this month"}
    ]
    
    for col, metric in zip(metric_cols, metrics):
        with col:
            st.metric(metric["label"], metric["value"], metric["delta"])

elif page == "Audio Capture":
    audio_page()

elif page == "Text Stories":
    text_page()

elif page == "Visual Heritage":
    image_page()

elif page == "🔍 Discover":
    search_page()

elif page == "📊 Analytics":
    analytics_page()

elif page == "🤝 Community":
    community_page()

elif page == "🤖 AI Insights":
    ai_insights_page()

elif page == "👥 Collaboration":
    collaboration_page()

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
    
    # Sample results
    for i in range(3):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("""
            <div style='background: #f0f2f6; padding: 2rem; border-radius: 8px; text-align: center;'>
                <h1>🎙️</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"### Traditional Folk Song #{i+1}")
            st.markdown("**Language:** Punjabi | **Region:** North India | **Duration:** 3:45")
            st.markdown("A beautiful rendition of a harvest song traditionally sung during Baisakhi celebrations...")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button(f"🎧 Play", key=f"play_{i}")
            with col2:
                st.button(f"📝 View Transcript", key=f"transcript_{i}")
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
