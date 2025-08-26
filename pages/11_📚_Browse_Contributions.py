import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from streamlit_app.utils.main_styling import load_custom_css

# Database imports
try:
    from utils.supabase_db import get_database_manager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Authentication imports
try:
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="Browse Contributions - BharatVerse",
        page_icon="📚",
        layout="wide"
    )
    
    # Apply enhanced styling
    load_custom_css()
    
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
    display_contributions(content_type, region, language, category, search_query, sort_by)

def display_contributions(content_type, region, language, category, search_query, sort_by):
    """Display contributions from Supabase"""
    
    if not SUPABASE_AVAILABLE:
        st.warning("🔄 Supabase not available - showing demo content")
        display_demo_contributions()
        return
    
    try:
        # Get database manager
        db = get_database_manager()
        
        # Fetch contributions from Supabase
        contributions = db.get_contributions(limit=50)
        
        if not contributions:
            st.info("📚 No contributions found. Be the first to contribute!")
            return
        
        # Filter contributions based on selected criteria
        filtered_contributions = filter_contributions(
            contributions, content_type, region, language, category, search_query
        )
        
        if not filtered_contributions:
            st.info("🔍 No contributions match your search criteria. Try adjusting the filters.")
            return
        
        # Sort contributions
        sorted_contributions = sort_contributions(filtered_contributions, sort_by)
        
        # Display contributions
        st.markdown(f"### 📊 Found {len(sorted_contributions)} contributions")
        
        for contribution in sorted_contributions:
            display_contribution_card(contribution)
            
    except Exception as e:
        st.error(f"Error loading contributions: {e}")
        st.info("Showing demo content instead...")
        display_demo_contributions()

def filter_contributions(contributions, content_type, region, language, category, search_query):
    """Filter contributions based on criteria"""
    filtered = contributions
    
    # Filter by content type
    if content_type != "All":
        filtered = [c for c in filtered if c.get('content_type', '').lower() == content_type.lower()]
    
    # Filter by region
    if region != "All Regions":
        filtered = [c for c in filtered if c.get('region', '').lower() in region.lower()]
    
    # Filter by language
    if language != "All Languages":
        filtered = [c for c in filtered if c.get('language', '').lower() == language.lower()]
    
    # Search filter
    if search_query:
        query = search_query.lower()
        filtered = [c for c in filtered if 
                   query in c.get('title', '').lower() or 
                   query in c.get('content', '').lower() or
                   any(query in tag.lower() for tag in c.get('tags', []))]
    
    return filtered

def sort_contributions(contributions, sort_by):
    """Sort contributions based on criteria"""
    if sort_by == "Recent":
        return sorted(contributions, key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == "Alphabetical":
        return sorted(contributions, key=lambda x: x.get('title', '').lower())
    elif sort_by == "Popular":
        # Sort by view count or engagement (if available)
        return sorted(contributions, key=lambda x: x.get('view_count', 0), reverse=True)
    else:
        return contributions

def display_contribution_card(contribution):
    """Display a single contribution card"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Title and basic info
            title = contribution.get('title', 'Untitled')
            content_type = contribution.get('content_type', 'unknown')
            language = contribution.get('language', 'Unknown')
            
            # Content type emoji
            type_emoji = {
                'text': '📝',
                'audio': '🎤',
                'image': '🖼️',
                'video': '🎥',
                'proverb': '🗣️'
            }.get(content_type, '📄')
            
            st.markdown(f"### {type_emoji} {title}")
            
            # Content preview
            content = contribution.get('content', '')
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                st.markdown(f"*{preview}*")
            
            # Tags
            tags = contribution.get('tags', [])
            if tags:
                tag_str = " ".join([f"`{tag}`" for tag in tags[:5]])
                st.markdown(f"**Tags:** {tag_str}")
        
        with col2:
            # Metadata
            st.markdown(f"**Language:** {language}")
            
            region = contribution.get('region')
            if region:
                st.markdown(f"**Region:** {region}")
            
            created_at = contribution.get('created_at', '')
            if created_at:
                st.markdown(f"**Created:** {created_at[:10]}")
            
            # Author info
            username = contribution.get('username', 'Anonymous')
            st.markdown(f"**By:** @{username}")
        
        # Expandable full content
        with st.expander("📖 View Full Content"):
            if content:
                st.markdown(content)
            
            # Metadata
            metadata = contribution.get('metadata')
            if metadata:
                try:
                    import json
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    
                    st.markdown("**Additional Information:**")
                    for key, value in metadata.items():
                        if key not in ['submitted_by', 'submission_timestamp']:
                            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                except:
                    pass
            
            # AI Analysis
            ai_analysis = contribution.get('ai_analysis')
            if ai_analysis:
                try:
                    if isinstance(ai_analysis, str):
                        ai_analysis = json.loads(ai_analysis)
                    
                    if ai_analysis:
                        st.markdown("**AI Analysis:**")
                        
                        # Sentiment
                        sentiment = ai_analysis.get('sentiment')
                        if sentiment:
                            st.markdown(f"- **Sentiment:** {sentiment}")
                        
                        # Themes
                        themes = ai_analysis.get('themes', [])
                        if themes:
                            st.markdown(f"- **Themes:** {', '.join(themes)}")
                        
                        # Cultural significance
                        cultural_score = ai_analysis.get('cultural_significance')
                        if cultural_score:
                            st.markdown(f"- **Cultural Significance:** {cultural_score:.2f}/1.0")
                except:
                    pass
        
        st.markdown("---")

def display_demo_contributions():
    """Display demo contributions when Supabase is not available"""
    st.markdown("### 📊 Demo Contributions")
    
    demo_contributions = [
        {
            'title': 'Traditional Bengali Folk Song',
            'content': 'আমার সোনার বাংলা, আমি তোমায় ভালোবাসি...',
            'content_type': 'text',
            'language': 'Bengali',
            'region': 'West Bengal',
            'tags': ['folk', 'song', 'traditional'],
            'username': 'demo_user',
            'created_at': '2024-01-15'
        },
        {
            'title': 'Hindi Proverb about Wisdom',
            'content': 'जैसी करनी वैसी भरनी - As you sow, so shall you reap',
            'content_type': 'proverb',
            'language': 'Hindi',
            'region': 'North India',
            'tags': ['proverb', 'wisdom', 'karma'],
            'username': 'wisdom_keeper',
            'created_at': '2024-01-14'
        },
        {
            'title': 'Tamil Cultural Story',
            'content': 'ஒரு காலத்தில் ஒரு சிறிய கிராமத்தில்...',
            'content_type': 'text',
            'language': 'Tamil',
            'region': 'Tamil Nadu',
            'tags': ['story', 'culture', 'village'],
            'username': 'story_teller',
            'created_at': '2024-01-13'
        }
    ]
    
    for contribution in demo_contributions:
        display_contribution_card(contribution)
    
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