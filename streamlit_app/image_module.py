import streamlit as st
from datetime import datetime
import base64
from PIL import Image
import io
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import enhanced AI models
try:
    from core.ai_models_enhanced import ai_manager
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
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
        help="Upload images of cultural significance"
    )
    
    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Image Info")
            st.write(f"**Format:** {image.format}")
            st.write(f"**Size:** {image.size}")
            st.write(f"**Mode:** {image.mode}")
        
        # Image details
        st.markdown("---")
        st.markdown("### 📝 Image Details")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title", "Durga Puja Pandal")
            category = st.selectbox(
                "Category",
                ["Festival", "Architecture", "Art", "Ritual", "Food", "Clothing", "Craft", "Nature", "Daily Life"]
            )
            location = st.text_input("Location", "Kolkata, West Bengal")
        
        with col2:
            event = st.text_input("Event/Occasion", "Durga Puja 2023")
            photographer = st.text_input("Photographer (Optional)", "")
            year_taken = st.number_input("Year Taken", 1900, 2024, 2023)
        
        # AI-generated caption and analysis
        st.markdown("---")
        st.markdown("### 🤖 AI Image Analysis")
        
        if st.button("Analyze Image", use_container_width=True):
            with st.spinner("Analyzing image with AI..."):
                use_real_data = st.session_state.get('use_real_data', False)
                
                if use_real_data and AI_MODELS_AVAILABLE:
                    try:
                        # Use enhanced AI models for image analysis
                        st.info("🤖 Using real AI models for image analysis...")
                        
                        # Convert image to bytes
                        image_buffer = io.BytesIO()
                        image.save(image_buffer, format=image.format or 'PNG')
                        image_bytes = image_buffer.getvalue()
                        
                        result = ai_manager.process_image(image_bytes)
                        
                        if result.get('success'):
                            st.success("✅ Image analysis complete!")
                            
                            # Show generated caption
                            caption = result.get('caption', '')
                            st.text_area("AI-Generated Caption", caption, height=100)
                            
                            # Show image analysis details
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                dimensions = result.get('dimensions', {})
                                st.metric("Width", f"{dimensions.get('width', 0)}px")
                                st.metric("Height", f"{dimensions.get('height', 0)}px")
                            
                            with col2:
                                aspect_ratio = result.get('aspect_ratio', 0)
                                st.metric("Aspect Ratio", f"{aspect_ratio:.2f}")
                                
                                analysis = result.get('analysis', {})
                                brightness = analysis.get('brightness', 0)
                                st.metric("Brightness", f"{brightness:.2%}")
                            
                            with col3:
                                complexity = analysis.get('complexity', 0)
                                st.metric("Complexity", f"{complexity:.2%}")
                                
                                dominant_colors = analysis.get('dominant_colors', [])
                                if dominant_colors:
                                    st.write("**Colors:**")
                                    st.write(", ".join(dominant_colors[:3]))
                            
                            # Cultural elements detected
                            cultural_elements = result.get('cultural_elements', [])
                            if cultural_elements:
                                st.markdown("### 🏛️ Cultural Elements Detected")
                                st.write(", ".join(cultural_elements))
                            
                            # Store results for submission
                            st.session_state.image_analysis_result = result
                            
                        else:
                            st.error(f"Image analysis failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error during image analysis: {str(e)}")
                        # Fallback to API call
                        st.info("Falling back to API analysis...")
                        try:
                            import requests
                            import os
                            
                            # Prepare image for API
                            image_buffer = io.BytesIO()
                            image.save(image_buffer, format=image.format or 'PNG')
                            image_buffer.seek(0)
                            
                            API_URL = os.getenv("API_URL", "http://localhost:8000")
                            files = {'file': (uploaded_file.name, image_buffer, uploaded_file.type)}
                            
                            response = requests.post(
                                f"{API_URL}/api/v1/image/analyze",
                                files=files
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                if result.get('success'):
                                    caption = result.get('caption', '')
                                    cultural_elements = result.get('cultural_elements', [])
                                    
                                    st.success("API Caption generated!")
                                    st.text_area("Generated Caption", caption, height=100)
                                    
                                    if cultural_elements:
                                        st.info(f"Detected cultural elements: {', '.join(cultural_elements)}")
                                else:
                                    st.error(f"Caption generation failed: {result.get('error', 'Unknown error')}")
                            else:
                                st.error(f"API error: {response.status_code}")
                        except Exception as api_e:
                            st.error(f"API fallback also failed: {str(api_e)}")
                
                elif use_real_data and not AI_MODELS_AVAILABLE:
                    st.warning("🚧 Real AI models not available. Install dependencies with: pip install -r requirements.txt")
                    # Show demo caption as fallback
                    caption = "A beautifully decorated Durga Puja pandal featuring intricate artwork and traditional Bengali motifs. The goddess Durga is shown in her fierce form, defeating the demon Mahishasura, symbolizing the victory of good over evil."
                    st.text_area("Demo Generated Caption", caption, height=100)
                    st.info("Detected cultural elements: festival, traditional, art, religious, decoration")
                
                else:
                    # Demo mode - show demo caption
                    st.info("🟡 Demo Mode: Using sample caption")
                    caption = "A beautifully decorated Durga Puja pandal featuring intricate artwork and traditional Bengali motifs. The goddess Durga is shown in her fierce form, defeating the demon Mahishasura, symbolizing the victory of good over evil."
                    st.text_area("Generated Caption", caption, height=100)
                    st.info("Detected cultural elements: festival, traditional, art, religious, decoration")
        
        # Manual description
        st.markdown("### ✏️ Your Description")
        use_real_data = st.session_state.get('use_real_data', False)
        
        if use_real_data:
            description = st.text_area(
                "Describe the cultural significance",
                "",
                height=150,
                placeholder="Enter your description of the cultural significance..."
            )
        else:
            description = st.text_area(
                "Describe the cultural significance",
                "This pandal represents the annual celebration of Durga Puja, one of the most important festivals in Bengali culture. The artistic decorations showcase traditional craftsmanship passed down through generations.",
                height=150
            )
        
        # Tags
        if use_real_data:
            tags = st.text_input(
                "Tags (comma-separated)",
                "",
                placeholder="Enter tags separated by commas..."
            )
        else:
            tags = st.text_input(
                "Tags (comma-separated)",
                "durga puja, bengali festival, pandal, goddess durga, kolkata, tradition"
            )
        
        # Cultural context
        st.markdown("### 🎭 Cultural Context")
        
        col1, col2 = st.columns(2)
        with col1:
            region = st.text_input("Region/State", "West Bengal")
            community = st.text_input("Community", "Bengali Hindu")
        
        with col2:
            significance = st.selectbox(
                "Significance Level",
                ["Local", "Regional", "National", "International"]
            )
            frequency = st.selectbox(
                "How often does this occur?",
                ["Annual", "Seasonal", "Once in lifetime", "Daily", "Special occasions"]
            )
        
        # Additional notes
        notes = st.text_area(
            "Additional Notes",
            "Any stories, memories, or historical context related to this image...",
            height=100
        )
        
        # Consent
        consent = st.checkbox(
            "I confirm that I have the right to share this image and agree to the "
            "terms of use and CC-BY 4.0 license for the contributed data."
        )
        
        # Submit
        if consent:
            if st.button("📤 Submit Image", type="primary", use_container_width=True):
                st.success("🎉 Thank you! Your image has been added to BharatVerse.")
                st.balloons()
                
                # Show summary
                st.markdown("### 📋 Contribution Summary")
                st.json({
                    "type": "image",
                    "title": title,
                    "category": category,
                    "location": location,
                    "event": event,
                    "year": year_taken,
                    "tags": tags.split(", "),
                    "region": region,
                    "community": community,
                    "timestamp": datetime.now().isoformat()
                })
    
    # Gallery examples
    st.markdown("---")
    st.markdown("### 🖼️ Example Contributions")
    
    example_cols = st.columns(3)
    examples = [
        {
            "title": "Kathakali Performer",
            "category": "Art",
            "location": "Kerala",
            "description": "Traditional Kathakali makeup and costume"
        },
        {
            "title": "Rajasthani Handicraft",
            "category": "Craft",
            "location": "Jaipur",
            "description": "Intricate blue pottery work"
        },
        {
            "title": "Pongal Celebration",
            "category": "Festival",
            "location": "Tamil Nadu",
            "description": "Traditional harvest festival cooking"
        }
    ]
    
    for col, example in zip(example_cols, examples):
        with col:
            st.markdown(f"**{example['title']}**")
            # Placeholder for example images
            st.markdown(f"""
            <div style='background: #f0f2f6; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 8px;'>
                <h1>📷</h1>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"{example['category']} • {example['location']}")
            st.write(example['description'])
    
    # Photography tips
    with st.expander("📸 Photography Tips"):
        st.markdown("""
        ### Tips for Cultural Photography:
        
        - **Respect**: Always ask permission before photographing people or religious ceremonies
        - **Context**: Include surroundings to show the cultural setting
        - **Details**: Capture close-ups of intricate artwork, patterns, or craftsmanship
        - **Natural Light**: Use natural lighting when possible for authentic colors
        - **Story**: Try to capture moments that tell a story about the culture
        - **Diversity**: Show different aspects - people, places, objects, activities
        
        ### What to Photograph:
        
        - Traditional clothing and jewelry
        - Festival decorations and celebrations
        - Religious or cultural ceremonies
        - Traditional crafts being made
        - Architectural details of temples, homes, monuments
        - Food preparation and presentation
        - Daily life activities with cultural significance
        """)
