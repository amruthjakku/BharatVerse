import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from streamlit_app.utils.enhanced_styling import apply_enhanced_styling

def main():
    st.set_page_config(
        page_title="Browse Contributions - BharatVerse",
        page_icon="📚",
        layout="wide"
    )
    
    # Apply enhanced styling
    apply_enhanced_styling()
    
    st.markdown("## 📚 Browse Contributions")
    st.markdown("Explore all cultural contributions from the community")
    
    # Filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        content_type = st.selectbox("Content Type", ["All", "Audio", "Text", "Images", "Videos"])
    
    with col2:
        region = st.selectbox("Region", ["All Regions", "North India", "South India", "East India", "West India", "Northeast India", "Central India"])
    
    with col3:
        language = st.selectbox("Language", ["All Languages", "Hindi", "English", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Assamese", "Odia", "Other"])
    
    with col4:
        category = st.selectbox("Category", ["All Categories", "Folk Songs", "Classical Music", "Stories", "Recipes", "Festivals", "Traditions", "Arts & Crafts", "Dance", "Theater"])
    
    # Search bar
    search_query = st.text_input("🔍 Search contributions...", placeholder="Search by title, description, or tags")
    
    # Sort options
    col1, col2 = st.columns([3, 1])
    with col2:
        sort_by = st.selectbox("Sort by", ["Recent", "Popular", "Most Liked", "Alphabetical"])
    
    st.markdown("---")
    
    # Results section
    st.info("📚 Contributions will be displayed here when content is available!")
    
    st.markdown("### 🎯 What you'll find here:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Audio Contributions:**
        - Traditional folk songs from different regions
        - Classical music recordings
        - Oral histories and stories
        - Regional dialects and languages
        - Ceremonial chants and prayers
        
        **Text Stories:**
        - Family traditions and customs
        - Historical accounts and legends
        - Festival celebrations and rituals
        - Traditional recipes and cooking methods
        - Cultural practices and beliefs
        """)
    
    with col2:
        st.markdown("""
        **Visual Heritage:**
        - Traditional arts and crafts
        - Cultural events and festivals
        - Historical monuments and architecture
        - Regional costumes and jewelry
        - Traditional tools and instruments
        
        **Community Projects:**
        - Collaborative documentation efforts
        - Regional cultural surveys
        - Preservation initiatives
        - Educational content creation
        - Cross-cultural exchange programs
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #FF6B35, #2E86AB); border-radius: 10px; color: white;'>
        <h3>Start Contributing Today!</h3>
        <p>Be the first to share your cultural heritage and help build this amazing collection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Add Audio", use_container_width=True):
            st.switch_page("pages/01_🎤_Audio_Capture.py")
    
    with col2:
        if st.button("📝 Share Story", use_container_width=True):
            st.switch_page("pages/02_📝_Text_Stories.py")
    
    with col3:
        if st.button("📸 Upload Image", use_container_width=True):
            st.switch_page("pages/03_📸_Visual_Heritage.py")
    
    with col4:
        if st.button("🔍 Discover More", use_container_width=True):
            st.switch_page("pages/04_🔍_Discover.py")

if __name__ == "__main__":
    main()