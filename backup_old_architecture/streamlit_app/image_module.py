import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io
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
def get_image_performance_components():
    """Get cached performance components for image module"""
    return {
        'optimizer': get_performance_optimizer(),
        'memory_manager': get_memory_manager(),
        'cache_manager': get_cache_manager()
    }

@st.cache_data(ttl=1800, show_spinner=False)
def get_image_processing_config():
    """Get cached image processing configuration"""
    return {
        'max_image_size_mb': 10,
        'supported_formats': ['jpg', 'jpeg', 'png', 'webp', 'bmp'],
        'max_dimensions': (2048, 2048),
        'compression_quality': 85,
        'thumbnail_size': (300, 300)
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
    from streamlit_app.utils.database import add_contribution
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

def image_page():
    st.markdown("## 📷 Visual Heritage")
    st.markdown("Upload and document images of festivals, art, architecture, and cultural symbols.")
    
    # Initialize performance components
    perf_components = get_image_performance_components()
    optimizer = perf_components['optimizer']
    memory_manager = perf_components['memory_manager']
    cache_manager = perf_components['cache_manager']
    
    # Get image processing configuration
    image_config = get_image_processing_config()
    
    # Performance monitoring for admins
    if st.session_state.get("user_role") == "admin":
        with st.expander("🔧 Performance Monitoring"):
            show_memory_dashboard()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'webp', 'bmp'],
        help="Upload images of cultural significance, festivals, art, architecture, etc."
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Image metadata
        st.markdown("### 📋 Image Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Format", image.format)
            st.metric("Width", f"{image.size[0]}px")
        with col2:
            st.metric("Height", f"{image.size[1]}px")
            st.metric("Mode", image.mode)
        with col3:
            file_size = len(uploaded_file.getvalue()) / 1024 / 1024
            st.metric("File Size", f"{file_size:.2f} MB")
        
        # Basic image details
        st.markdown("### 🏷️ Image Details")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", "Cultural Heritage Image")
            category = st.selectbox(
                "Category",
                ["Festival", "Architecture", "Art", "Ritual", "Food", "Clothing", "Craft", "Nature", "Daily Life"]
            )
            location = st.text_input("Location", "India")
        
        with col2:
            event = st.text_input("Event/Occasion", "")
            photographer = st.text_input("Photographer (Optional)", "")
            year_taken = st.number_input("Year Taken", 1900, 2024, 2024)
        
        # AI Analysis section
        st.markdown("---")
        st.markdown("### 🤖 AI Image Analysis")
        
        if st.button("Analyze Image", use_container_width=True):
            with st.spinner("Analyzing image..."):
                if AI_MODELS_AVAILABLE:
                    try:
                        # Try AI analysis
                        result = ai_manager.caption_image(image)
                        if result and result.get('success'):
                            st.success("✅ AI analysis completed!")
                            
                            # Show generated caption
                            caption = result.get('caption', '')
                            if caption:
                                st.text_area("🖼️ AI-Generated Caption", caption, height=100)
                            
                            # Show cultural elements if available
                            cultural_elements = result.get('cultural_elements', [])
                            if cultural_elements:
                                st.info(f"Cultural elements detected: {', '.join(cultural_elements)}")
                            
                            # Show detected objects if available
                            objects = result.get('objects', [])
                            if objects:
                                st.markdown("### 🎯 Detected Objects")
                                for obj in objects[:5]:  # Show top 5 objects
                                    st.write(f"• {obj.get('label', 'Unknown')} (confidence: {obj.get('confidence', 0):.2%})")
                        else:
                            st.warning("AI analysis completed with basic information only.")
                    except Exception as e:
                        st.warning(f"AI analysis failed: {str(e)}")
                        st.info("Please provide manual description below.")
                else:
                    st.info("AI models not available. Please provide manual description below.")
        
        # Manual description section
        st.markdown("---")
        st.markdown("### ✏️ Description & Context")
        
        description = st.text_area(
            "Describe the cultural significance",
            "",
            height=150,
            placeholder="Describe what this image represents, its cultural significance, historical context, etc."
        )
        
        # Tags
        tags = st.text_input(
            "Tags (comma-separated)",
            "",
            placeholder="festival, tradition, art, architecture, etc."
        )
        
        # Cultural context
        st.markdown("### 🎭 Cultural Context")
        col1, col2 = st.columns(2)
        with col1:
            cultural_significance = st.selectbox(
                "Cultural Significance",
                ["High", "Medium", "Low", "Historical", "Religious", "Artistic", "Social"]
            )
            region = st.text_input("Region/State", "")
        
        with col2:
            community = st.text_input("Community/Group", "")
            language_context = st.text_input("Language Context", "")

        # Consent checkbox
        consent = st.checkbox(
            "I confirm that I have the right to share this image and agree to the "
            "terms of use and CC-BY 4.0 license for the contributed data."
        )

        # Submit button
        if st.button("Submit Image", type="primary", use_container_width=True):
            if not title.strip():
                st.error("Please provide a title for your image.")
            elif not description.strip():
                st.error("Please provide a description for your image.")
            elif not consent:
                st.error("Please confirm that you have the right to share this image.")
            else:
                # Convert image to base64 for storage
                image_buffer = io.BytesIO()
                image.save(image_buffer, format=image.format or 'PNG')
                image_base64 = base64.b64encode(image_buffer.getvalue()).decode()
                
                # Prepare contribution data
                contribution_data = {
                    "title": title,
                    "description": description,
                    "content_type": "image",
                    "category": category,
                    "location": location,
                    "event": event,
                    "photographer": photographer,
                    "year_taken": year_taken,
                    "tags": tags,
                    "cultural_significance": cultural_significance,
                    "region": region,
                    "community": community,
                    "language_context": language_context,
                    "image_data": image_base64,
                    "image_format": image.format or 'PNG',
                    "image_size": image.size,
                    "file_size": len(uploaded_file.getvalue()),
                    "created_at": datetime.now().isoformat()
                }
                
                # Try to save to database
                success = False
                if DATABASE_AVAILABLE:
                    try:
                        add_contribution("image", contribution_data)
                        success = True
                        st.success("✅ Image submitted successfully to database!")
                    except Exception as e:
                        st.warning(f"Database save failed: {str(e)}")
                
                if not success:
                    # Fallback to session state
                    if 'local_image_contributions' not in st.session_state:
                        st.session_state.local_image_contributions = []
                    st.session_state.local_image_contributions.append(contribution_data)
                    st.success("✅ Image saved locally! It will be synced when database is available.")
                
                # Show success message
                st.balloons()
                st.markdown("### 🎉 Thank you for your contribution!")
                st.markdown("Your image has been added to the BharatVerse collection.")
                
                # Clear form
                if st.button("Submit Another Image"):
                    st.rerun()

if __name__ == "__main__":
    image_page()