import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import modules
from streamlit_app.audio_module import audio_page
from streamlit_app.text_module import text_page
from streamlit_app.image_module import image_page
from streamlit_app.utils.database import init_db
from streamlit_app.utils.styling import load_custom_css

# Page configuration
st.set_page_config(
    page_title="BharatVerse - Preserving India's Culture",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Load custom CSS
load_custom_css()

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🇮🇳 BharatVerse")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigate to:",
        ["Home", "Audio Capture", "Text Stories", "Visual Heritage", "Browse Contributions", "About"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Contributions", "1,234")
    with col2:
        st.metric("Languages", "22")
    
    st.markdown("---")
    st.markdown("### 🌐 Resources")
    st.markdown("[📚 Documentation](https://github.com/bharatverse/bharatverse)")
    st.markdown("[🤗 API Access](https://api.bharatverse.org)")
    st.markdown("[📧 Contact Us](mailto:team@bharatverse.org)")

# Main content
if page == "Home":
    # Hero section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>🇮🇳 BharatVerse</h1>
        <h3 style='color: #666; margin-bottom: 2rem;'>Preserving India's Culture, One Voice at a Time</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; height: 200px;'>
            <h3>🎙️ Audio Magic</h3>
            <p>Record and transcribe folk songs, stories, and oral traditions in 22+ Indian languages.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Recording", key="audio_btn", use_container_width=True):
            st.session_state.page = "Audio Capture"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 10px; color: white; height: 200px;'>
            <h3>📝 Story Keeper</h3>
            <p>Document local customs, proverbs, recipes, and wisdom passed down through generations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Write Story", key="text_btn", use_container_width=True):
            st.session_state.page = "Text Stories"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 2rem; border-radius: 10px; color: white; height: 200px;'>
            <h3>📷 Visual Heritage</h3>
            <p>Upload and caption images of festivals, art, architecture, and cultural symbols.</p>
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
            <div style='background: #f0f2f6; padding: 1rem; border-radius: 8px; text-align: center;'>
                <h2>{contrib['type']}</h2>
                <h5>{contrib['title']}</h5>
                <p style='color: #666; font-size: 0.9rem;'>{contrib['lang']} • {contrib['time']}</p>
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
