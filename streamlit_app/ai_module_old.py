import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import matplotlib.pyplot as plt

# Optional imports with fallbacks
try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

def ai_insights_page():
    st.markdown("## 🤖 AI-Powered Cultural Insights")
    st.markdown("Discover patterns, trends, and insights from cultural data using artificial intelligence")
    
    # Always use real data - demo mode removed
    st.info("🤖 **Real AI Mode**: Analysis based on your actual contributions")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Content Analysis", 
        "🔮 Trend Prediction", 
        "🌐 Language Insights", 
        "🎨 Visual Analysis",
        "💡 Recommendations"
    ])
    
    with tab1:
        content_analysis_section()
    
    with tab2:
        trend_prediction_section()
    
    with tab3:
        language_insights_section()
    
    with tab4:
        visual_analysis_section()
    
    with tab5:
        recommendations_section()

def content_analysis_section():
    st.markdown("### 📊 Content Quality & Sentiment Analysis")
    
    # Always use real data - demo mode removed
    # Try to get real content from API
    try:
        import requests
        import os
        
        API_URL = os.getenv("API_URL", "http://localhost:8000")
        response = requests.get(f"{API_URL}/api/v1/content/recent?limit=10", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            real_content = data.get('results', [])
            
            if real_content:
                # Create content dictionary from real data
                content_texts = {}
                for item in real_content:
                    title = item.get('title', 'Untitled')
                    description = item.get('description', '')
                    if description:
                        content_texts[title] = description
                    
                    if content_texts:
                        # Content selector
                        selected_content = st.selectbox("Select content to analyze:", list(content_texts.keys()))
                        
                        if selected_content:
                            analyze_content_text(selected_content, content_texts[selected_content])
                        return
                        
        except Exception as e:
            st.warning(f"Could not fetch real content: {e}")
        
        # No real content available
        st.info("🔍 No content available for analysis yet!")
        st.markdown("**To see AI insights:**")
        st.markdown("- Upload audio files in the Audio module")
        st.markdown("- Add text content in the Text module")
        st.markdown("- Upload images in the Image module")
        st.markdown("- Come back here to see AI analysis of your content")
        return
    
    # Demo mode - use sample content
    sample_texts = {
        "Hindi Folk Song": "यह एक पारंपरिक लोक गीत है जो हमारे पूर्वजों द्वारा गाया जाता था। इसमें प्रेम, प्रकृति और जीवन की सुंदरता का वर्णन है।",
        "Bengali Story": "এটি একটি ঐতিহ্যবাহী বাংলা গল্প যা আমাদের সংস্কৃতির গভীর অর্থ বহন করে। গল্পটি মানবিক মূল্যবোধ এবং নৈতিকতার শিক্ষা দেয়।",
        "Tamil Recipe": "இது ஒரு பாரம்பரிய தமிழ் உணவு செய்முறை. இந்த உணவு நமது முன்னோர்களால் தலைமுறை தலைமুறையாக கடத்தப்பட்டு வருகிறது।",
        "English Description": "This is a traditional Indian cultural practice that has been preserved for centuries. It represents the rich heritage and values of our ancestors."
    }
    
    # Content selector
    selected_content = st.selectbox("Select content to analyze:", list(sample_texts.keys()))
    
    if selected_content:
        analyze_content_text(selected_content, sample_texts[selected_content])

def analyze_content_text(title, content_text):
    """Analyze a piece of content text"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Content")
        st.text_area("Text Content", content_text, height=150, disabled=True)
        
        # Basic analysis
        st.markdown("#### 📈 Basic Metrics")
        word_count = len(content_text.split())
        char_count = len(content_text)
        
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Word Count", word_count)
            st.metric("Character Count", char_count)
        
        with metrics_col2:
            # Language detection
            if LANGDETECT_AVAILABLE:
                try:
                    detected_lang = detect(content_text)
                    lang_names = {
                        'hi': 'Hindi', 'bn': 'Bengali', 'ta': 'Tamil', 
                        'te': 'Telugu', 'mr': 'Marathi', 'gu': 'Gujarati',
                        'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi',
                        'or': 'Odia', 'as': 'Assamese', 'ur': 'Urdu', 'en': 'English'
                    }
                    st.metric("Detected Language", lang_names.get(detected_lang, detected_lang.upper()))
                except:
                    st.metric("Detected Language", "Unknown")
            else:
                st.metric("Detected Language", "N/A")
            
            # Reading difficulty
            if TEXTSTAT_AVAILABLE:
                try:
                    reading_ease = flesch_reading_ease(content_text)
                    st.metric("Reading Ease", f"{reading_ease:.1f}")
                except:
                    st.metric("Reading Ease", "N/A")
            else:
                st.metric("Reading Ease", "N/A")
    
    with col2:
        st.markdown("#### 🎯 AI Analysis")
        
        # Simulated sentiment analysis
        sentiments = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
        sentiment_scores = [0.9, 0.7, 0.5, 0.3, 0.1]
        
        # Simple sentiment based on content
        if any(word in content_text.lower() for word in ['love', 'beautiful', 'good', 'प्रेम', 'সুন্দর', 'அழகு']):
            sentiment = "Positive"
            score = 0.8
        elif any(word in content_text.lower() for word in ['traditional', 'heritage', 'culture', 'पारंपरिक', 'ঐতিহ্যবাহী', 'பாரம்பரிய']):
            sentiment = "Very Positive"
            score = 0.9
        else:
            sentiment = "Neutral"
            score = 0.5
        
        st.metric("Sentiment", sentiment, f"{score:.1f}")
        
        # Cultural significance
        cultural_keywords = ['traditional', 'heritage', 'culture', 'ancestors', 'पारंपरिक', 'ঐতিহ্যবাহী', 'பாரம்பரிய']
        cultural_score = sum(1 for word in cultural_keywords if word in content_text.lower()) / len(cultural_keywords)
        st.metric("Cultural Significance", f"{cultural_score:.2f}")
        
        # Topic classification
        if 'song' in title.lower() or 'गीत' in content_text:
            topic = "Music & Songs"
        elif 'story' in title.lower() or 'গল্প' in content_text:
            topic = "Stories & Literature"
        elif 'recipe' in title.lower() or 'செய்முறை' in content_text:
            topic = "Food & Recipes"
        else:
            topic = "Cultural Practice"
        
        st.metric("Topic Category", topic)
        
        # Quality indicators
        st.markdown("#### ✨ Quality Indicators")
        quality_metrics = {
            "Authenticity": min(1.0, cultural_score + 0.3),
            "Completeness": min(1.0, word_count / 50),
            "Clarity": 0.8 if word_count > 20 else 0.6
        }
        
        for metric, value in quality_metrics.items():
            st.progress(value, text=f"{metric}: {value:.2f}")

def trend_prediction_section():
    st.markdown("### 🔮 Cultural Trend Predictions")
    
    # Demo mode removed
    
    # Always use real data
        st.info("🔍 No trend data available yet. Upload more content to see predictions!")
        st.markdown("**Trend analysis will show:**")
        st.markdown("- Popular cultural themes")
        st.markdown("- Language usage patterns")
        st.markdown("- Regional content distribution")
        st.markdown("- Seasonal cultural activities")
        return
    
    # Demo trends
    st.markdown("#### 📈 Trending Cultural Themes")
    
    trend_data = {
        "Theme": ["Festival Celebrations", "Traditional Music", "Regional Cuisine", "Folk Stories", "Wedding Customs"],
        "Growth": [45, 32, 28, 25, 18],
        "Popularity": [85, 78, 72, 68, 65]
    }
    
    df = pd.DataFrame(trend_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df, x="Theme", y="Growth", title="Growth Rate (%)")
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(df, values="Popularity", names="Theme", title="Current Popularity")
        st.plotly_chart(fig, use_container_width=True)

def language_insights_section():
    st.markdown("### 🌐 Language Distribution & Insights")
    
    # Demo mode removed
    
    # Always use real data
        st.info("🔍 No language data available yet. Upload content in different languages!")
        return
    
    # Demo language data
    language_data = {
        "Language": ["Hindi", "Bengali", "Tamil", "Telugu", "Marathi", "Gujarati", "English"],
        "Content Count": [45, 32, 28, 25, 18, 15, 12],
        "Contributors": [23, 18, 15, 12, 10, 8, 8]
    }
    
    df = pd.DataFrame(language_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df, x="Language", y="Content Count", title="Content by Language")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(df, x="Contributors", y="Content Count", 
                        size="Content Count", hover_name="Language",
                        title="Contributors vs Content")
        st.plotly_chart(fig, use_container_width=True)

def visual_analysis_section():
    st.markdown("### 🎨 Visual Content Analysis")
    
    # Demo mode removed
    
    # Always use real data
        st.info("🔍 No visual content available yet. Upload images to see analysis!")
        return
    
    st.markdown("#### 📊 Demo Visual Insights")
    
    # Demo visual analysis
    visual_categories = ["Traditional Art", "Festivals", "Architecture", "Clothing", "Food", "Nature"]
    counts = [25, 20, 15, 12, 10, 8]
    
    fig = px.pie(values=counts, names=visual_categories, title="Visual Content Categories")
    st.plotly_chart(fig, use_container_width=True)

def recommendations_section():
    st.markdown("### 💡 AI Recommendations")
    
    # Demo mode removed
    
    # Always use real data
        st.info("🔍 No recommendations available yet. Upload content to get personalized suggestions!")
        st.markdown("**AI will recommend:**")
        st.markdown("- Similar cultural content to explore")
        st.markdown("- Missing cultural elements to document")
        st.markdown("- Collaboration opportunities")
        st.markdown("- Content improvement suggestions")
        return
    
    # Demo recommendations
    st.markdown("#### 🎯 Content Suggestions")
    
    recommendations = [
        {
            "title": "Document Holi Celebrations",
            "description": "Based on your interest in festivals, consider documenting regional Holi traditions",
            "priority": "High",
            "type": "Content Gap"
        },
        {
            "title": "Add Audio to Stories",
            "description": "Your Bengali stories would benefit from audio narrations",
            "priority": "Medium", 
            "type": "Enhancement"
        },
        {
            "title": "Connect with Tamil Contributors",
            "description": "Collaborate with Tamil food experts for authentic recipes",
            "priority": "Medium",
            "type": "Collaboration"
        }
    ]
    
    for rec in recommendations:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{rec['title']}**")
                st.markdown(rec['description'])
            
            with col2:
                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                st.markdown(f"{priority_color[rec['priority']]} {rec['priority']}")
            
            with col3:
                st.markdown(f"*{rec['type']}*")
            
            st.markdown("---")