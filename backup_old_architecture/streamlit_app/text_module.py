import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Performance optimization imports
from utils.performance_optimizer import get_performance_optimizer
# Safe memory manager import
try:
    from utils.memory_manager import get_memory_manager, MemoryTracker, show_memory_dashboard
except ImportError:
    from utils.fallback_memory import (
        get_fallback_memory_manager as get_memory_manager, 
        show_fallback_memory_dashboard as show_memory_dashboard,
        FallbackMemoryTracker as MemoryTracker
    )
from utils.redis_cache import get_cache_manager

# Initialize performance components
@st.cache_resource
def get_text_performance_components():
    """Get cached performance components for text module"""
    return {
        'optimizer': get_performance_optimizer(),
        'memory_manager': get_memory_manager(),
        'cache_manager': get_cache_manager()
    }

@st.cache_data(ttl=1800, show_spinner=False)
def get_text_processing_config():
    """Get cached text processing configuration"""
    return {
        'max_text_length': 10000,
        'supported_languages': ['hi', 'en', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa'],
        'ai_processing_timeout': 30,
        'batch_size': 5
    }

# Try to import enhanced AI models
try:
    from core.enhanced_ai_models import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    try:
        from core.ai_models import ai_manager
        AI_MODELS_AVAILABLE = True
    except ImportError:
        AI_MODELS_AVAILABLE = False

# Database imports
try:
    from utils.supabase_db import get_database_manager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Authentication imports
try:
    from streamlit_app.utils.auth import get_auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Database utility imports
try:
    from streamlit_app.utils.database import add_contribution
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

def text_page():
    st.markdown("## 📝 Story Keeper")
    st.markdown("Document stories, proverbs, recipes, and wisdom from your culture.")
    
    # Initialize performance components
    perf_components = get_text_performance_components()
    optimizer = perf_components['optimizer']
    memory_manager = perf_components['memory_manager']
    cache_manager = perf_components['cache_manager']
    
    # Get text processing configuration
    text_config = get_text_processing_config()
    
    # Performance monitoring for admins
    if st.session_state.get("user_role") == "admin":
        with st.expander("🔧 Performance Monitoring"):
            show_memory_dashboard()
    
    # Language selection
    st.markdown("### 🌐 Language Selection")
    language = st.selectbox(
        "Select the language of your story:",
        ["Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Kannada", "Malayalam", "Punjabi", "English"],
        index=0
    )
    
    # Story type selection
    st.markdown("### 📖 Story Type")
    story_type = st.selectbox(
        "What type of content are you sharing?",
        ["Folk Tale", "Proverb", "Recipe", "Song", "Poem", "Historical Account", "Personal Story", "Other"]
    )
    
    # Title input
    title = st.text_input("Title", "")
    
    # Content input
    placeholders = {
        "content": "Share your story, recipe, proverb, or cultural wisdom here..."
    }
    
    content = st.text_area(
        "Story Content",
        "",
        height=200,
        placeholder=placeholders["content"]
    )

    # Simple analysis section
    if st.checkbox("Analyze Text"):
        st.markdown("---")
        st.markdown("### 🔄 Text Analysis")
        if st.button("Analyze", key="analyze_story"):
            if not content.strip():
                st.warning("Please enter some content to analyze.")
            else:
                with st.spinner("Analyzing text..."):
                    # Simple analysis
                    word_count = len(content.split())
                    char_count = len(content)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", word_count)
                    with col2:
                        st.metric("Character Count", char_count)
                    with col3:
                        st.metric("Language", language)
                    
                    if AI_MODELS_AVAILABLE:
                        try:
                            # Try AI analysis
                            result = ai_manager.analyze_text(content, language=language.lower()[:2])
                            if result and result.get('success'):
                                st.success("✅ AI analysis completed!")
                                
                                # Show sentiment if available
                                sentiment = result.get('sentiment', {})
                                if sentiment:
                                    st.info(f"Sentiment: {sentiment.get('label', 'Unknown')}")
                                
                                # Show cultural elements if available
                                cultural_elements = result.get('cultural_elements', [])
                                if cultural_elements:
                                    st.info(f"Cultural elements detected: {', '.join(cultural_elements)}")
                            else:
                                st.warning("AI analysis completed with basic metrics only.")
                        except Exception as e:
                            st.warning(f"AI analysis failed: {str(e)}")
                            st.info("Showing basic analysis only.")
                    else:
                        st.info("AI models not available. Showing basic analysis only.")

    # Metadata
    st.markdown("---")
    st.markdown("### 🏷️ Metadata & Tags")
    
    col1, col2 = st.columns(2)
    with col1:
        author = st.text_input("Author/Credited Contributor", "Anonymous")
        region = st.text_input("Region/State", "West Bengal")
    
    with col2:
        keywords = st.text_input("Keywords/Tags (comma-separated)", "tradition, culture")
        year_composed = st.number_input("Year Composed (Optional)", 1800, 2024, 2024)

    # Consent checkbox
    consent = st.checkbox(
        "I confirm that I have the right to share this content and agree to the "
        "terms of use and CC-BY 4.0 license for the contributed data."
    )

    # Submit button
    if st.button("Submit Story", type="primary", use_container_width=True):
        if not title.strip():
            st.error("Please provide a title for your story.")
        elif not content.strip():
            st.error("Please provide content for your story.")
        elif not consent:
            st.error("Please confirm that you have the right to share this content.")
        else:
            # Prepare contribution data
            contribution_data = {
                "title": title,
                "content": content,
                "content_type": "text",
                "language": language,
                "story_type": story_type,
                "author": author,
                "region": region,
                "keywords": keywords,
                "year_composed": year_composed,
                "created_at": datetime.now().isoformat()
            }
            
            # Try to save to database
            success = False
            if DATABASE_AVAILABLE:
                try:
                    add_contribution("text", contribution_data)
                    success = True
                    st.success("✅ Story submitted successfully to database!")
                except Exception as e:
                    st.warning(f"Database save failed: {str(e)}")
            
            if not success:
                # Fallback to session state
                if 'local_text_contributions' not in st.session_state:
                    st.session_state.local_text_contributions = []
                st.session_state.local_text_contributions.append(contribution_data)
                st.success("✅ Story saved locally! It will be synced when database is available.")
            
            # Show success message
            st.balloons()
            st.markdown("### 🎉 Thank you for your contribution!")
            st.markdown("Your story has been added to the BharatVerse collection.")
            
            # Clear form
            if st.button("Submit Another Story"):
                st.rerun()

if __name__ == "__main__":
    text_page()