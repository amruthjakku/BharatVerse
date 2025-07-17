import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import plotly.express as px
import plotly.graph_objects as go
from textstat import flesch_reading_ease, flesch_kincaid_grade
from langdetect import detect, DetectorFactory
import cv2
from PIL import Image
import matplotlib.pyplot as plt

# Set seed for consistent language detection
DetectorFactory.seed = 0

def ai_insights_page():
    st.markdown("## 🤖 AI-Powered Cultural Insights")
    st.markdown("Discover patterns, trends, and insights from cultural data using artificial intelligence")
    
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
    
    # Sample content for analysis
    sample_texts = {
        "Hindi Folk Song": "यह एक पारंपरिक लोक गीत है जो हमारे पूर्वजों द्वारा गाया जाता था। इसमें प्रेम, प्रकृति और जीवन की सुंदरता का वर्णन है।",
        "Bengali Story": "এটি একটি ঐতিহ্যবাহী বাংলা গল্প যা আমাদের সংস্কৃতির গভীর অর্থ বহন করে। গল্পটি মানবিক মূল্যবোধ এবং নৈতিকতার শিক্ষা দেয়।",
        "Tamil Recipe": "இது ஒரு பாரம்பரிய தமிழ் உணவு செய்முறை. இந்த உணவு நமது முன்னோர்களால் தலைமுறை தலைமுறையாக கடத்தப்பட்டு வருகிறது।",
        "English Description": "This is a traditional Indian cultural practice that has been preserved for centuries. It represents the rich heritage and values of our ancestors."
    }
    
    # Content selector
    selected_content = st.selectbox("Select content to analyze:", list(sample_texts.keys()))
    
    if selected_content:
        content_text = sample_texts[selected_content]
        
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
                try:
                    detected_lang = detect(content_text)
                    lang_names = {
                        'hi': 'Hindi', 'bn': 'Bengali', 'ta': 'Tamil', 
                        'te': 'Telugu', 'mr': 'Marathi', 'gu': 'Gujarati',
                        'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi',
                        'or': 'Odia', 'as': 'Assamese', 'en': 'English'
                    }
                    st.metric("Detected Language", lang_names.get(detected_lang, detected_lang))
                except:
                    st.metric("Detected Language", "Unknown")
                
                # Readability (for English content)
                if 'english' in selected_content.lower():
                    try:
                        readability = flesch_reading_ease(content_text)
                        st.metric("Readability Score", f"{readability:.1f}")
                    except:
                        st.metric("Readability Score", "N/A")
        
        with col2:
            st.markdown("#### 🎯 AI Analysis Results")
            
            # Simulated AI analysis results
            analysis_results = {
                "Cultural Significance": np.random.randint(75, 95),
                "Authenticity Score": np.random.randint(80, 98),
                "Emotional Tone": ["Positive", "Nostalgic", "Reverent"][np.random.randint(0, 3)],
                "Content Category": ["Traditional", "Folk", "Religious", "Ceremonial"][np.random.randint(0, 4)],
                "Preservation Priority": ["High", "Medium", "Critical"][np.random.randint(0, 3)]
            }
            
            for key, value in analysis_results.items():
                if isinstance(value, int):
                    st.metric(key, f"{value}%")
                else:
                    st.metric(key, value)
            
            # Sentiment visualization
            st.markdown("#### 😊 Sentiment Analysis")
            sentiment_data = {
                'Positive': np.random.randint(60, 85),
                'Neutral': np.random.randint(10, 25),
                'Negative': np.random.randint(5, 15)
            }
            
            fig_sentiment = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                color_discrete_sequence=['#51cf66', '#ffd43b', '#ff6b6b']
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Batch analysis
    st.markdown("---")
    st.markdown("### 📊 Batch Content Analysis")
    
    if st.button("🚀 Analyze All Recent Contributions", type="primary"):
        with st.spinner("Analyzing content..."):
            # Simulate batch analysis
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
            
            # Display results
            st.success("Analysis completed!")
            
            # Sample batch results
            batch_results = pd.DataFrame({
                'Content Type': ['Audio', 'Text', 'Image', 'Recipe', 'Story'],
                'Average Quality': [87, 92, 85, 89, 94],
                'Cultural Significance': [91, 88, 86, 93, 96],
                'Authenticity Score': [89, 94, 82, 91, 98]
            })
            
            fig_batch = px.bar(
                batch_results.melt(id_vars=['Content Type'], var_name='Metric', value_name='Score'),
                x='Content Type',
                y='Score',
                color='Metric',
                barmode='group',
                title="Batch Analysis Results"
            )
            st.plotly_chart(fig_batch, use_container_width=True)

def trend_prediction_section():
    st.markdown("### 🔮 Cultural Trend Predictions")
    
    # Time series prediction
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Contribution Trends")
        
        # Generate sample time series data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        historical_data = np.random.poisson(8, len(dates[:300]))  # Historical
        predicted_data = np.random.poisson(12, len(dates[300:]))  # Predicted
        
        df_trend = pd.DataFrame({
            'Date': dates,
            'Contributions': np.concatenate([historical_data, predicted_data]),
            'Type': ['Historical'] * 300 + ['Predicted'] * (len(dates) - 300)
        })
        
        fig_trend = px.line(
            df_trend,
            x='Date',
            y='Contributions',
            color='Type',
            title='Predicted Contribution Growth'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌟 Emerging Cultural Topics")
        
        trending_topics = [
            {"topic": "Digital Storytelling", "growth": "+156%", "confidence": 89},
            {"topic": "Regional Festivals", "growth": "+134%", "confidence": 92},
            {"topic": "Traditional Crafts", "growth": "+98%", "confidence": 85},
            {"topic": "Folk Music Revival", "growth": "+87%", "confidence": 91},
            {"topic": "Heritage Recipes", "growth": "+76%", "confidence": 88}
        ]
        
        for topic in trending_topics:
            st.markdown(f"""
            <div style='background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #667eea;'>
                <h4 style='margin: 0; color: #333;'>{topic['topic']}</h4>
                <p style='margin: 0.5rem 0; color: #666;'>Growth: <span style='color: #51cf66; font-weight: bold;'>{topic['growth']}</span></p>
                <p style='margin: 0; color: #666;'>Confidence: {topic['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Regional predictions
    st.markdown("---")
    st.markdown("#### 🗺️ Regional Cultural Activity Predictions")
    
    regions = ['North India', 'South India', 'East India', 'West India', 'Northeast India']
    predicted_activity = np.random.randint(70, 150, len(regions))
    current_activity = np.random.randint(50, 120, len(regions))
    
    df_regional = pd.DataFrame({
        'Region': regions,
        'Current Activity': current_activity,
        'Predicted Activity': predicted_activity,
        'Growth %': ((predicted_activity - current_activity) / current_activity * 100).round(1)
    })
    
    fig_regional = px.bar(
        df_regional,
        x='Region',
        y=['Current Activity', 'Predicted Activity'],
        barmode='group',
        title='Regional Activity Predictions'
    )
    st.plotly_chart(fig_regional, use_container_width=True)
    
    # AI recommendations
    st.markdown("#### 🎯 AI Recommendations")
    
    recommendations = [
        "Focus on documenting winter festival traditions - predicted 40% increase in interest",
        "Expand recipe collection from Northeast India - underrepresented region with high potential",
        "Create video tutorials for traditional crafts - visual content showing 60% higher engagement",
        "Collaborate with schools for cultural education programs - youth engagement opportunity",
        "Develop mobile app features for audio recording - mobile usage increasing by 25%"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")

def language_insights_section():
    st.markdown("### 🌐 Language Diversity & Analysis")
    
    # Language distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Language Distribution")
        
        languages = ['Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati', 'Kannada', 'Malayalam', 'Punjabi', 'Odia']
        contributions = np.random.randint(20, 150, len(languages))
        
        fig_lang = px.pie(
            values=contributions,
            names=languages,
            title="Content by Language"
        )
        st.plotly_chart(fig_lang, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔤 Script Analysis")
        
        scripts = ['Devanagari', 'Bengali', 'Tamil', 'Telugu', 'Gujarati', 'Gurmukhi', 'Odia', 'Kannada', 'Malayalam']
        script_usage = np.random.randint(15, 100, len(scripts))
        
        df_scripts = pd.DataFrame({
            'Script': scripts,
            'Usage': script_usage
        }).sort_values('Usage', ascending=True)
        
        fig_scripts = px.bar(
            df_scripts,
            x='Usage',
            y='Script',
            orientation='h',
            title='Script Usage Distribution'
        )
        st.plotly_chart(fig_scripts, use_container_width=True)
    
    # Language complexity analysis
    st.markdown("---")
    st.markdown("#### 🧮 Language Complexity Metrics")
    
    complexity_data = {
        'Language': ['Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi'],
        'Vocabulary Richness': np.random.randint(70, 95, 5),
        'Grammatical Complexity': np.random.randint(65, 90, 5),
        'Cultural Depth': np.random.randint(80, 98, 5)
    }
    
    df_complexity = pd.DataFrame(complexity_data)
    
    fig_complexity = px.radar(
        df_complexity,
        r='Vocabulary Richness',
        theta='Language',
        title='Language Complexity Analysis'
    )
    st.plotly_chart(fig_complexity, use_container_width=True)
    
    # Endangered languages alert
    st.markdown("#### ⚠️ Language Preservation Alerts")
    
    endangered_langs = [
        {"name": "Bodo", "speakers": "1.4M", "status": "Vulnerable", "contributions": 12},
        {"name": "Santali", "speakers": "6.2M", "status": "Safe", "contributions": 34},
        {"name": "Manipuri", "speakers": "1.8M", "status": "Vulnerable", "contributions": 8},
        {"name": "Konkani", "speakers": "2.3M", "status": "Vulnerable", "contributions": 15}
    ]
    
    for lang in endangered_langs:
        status_color = {"Vulnerable": "#ff6b6b", "Safe": "#51cf66", "Critical": "#ff4757"}
        
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid {status_color[lang["status"]]};'>
            <h4 style='margin: 0; color: #333;'>{lang['name']}</h4>
            <p style='margin: 0.5rem 0; color: #666;'>Speakers: {lang['speakers']} | Status: <span style='color: {status_color[lang["status"]]};'>{lang['status']}</span></p>
            <p style='margin: 0; color: #666;'>TeluguVerse Contributions: {lang['contributions']}</p>
        </div>
        """, unsafe_allow_html=True)

def visual_analysis_section():
    st.markdown("### 🎨 Visual Content Analysis")
    
    # Image analysis demo
    st.markdown("#### 📷 Upload Image for Cultural Analysis")
    
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.markdown("#### 🔍 AI Analysis Results")
            
            # Simulated image analysis
            with st.spinner("Analyzing image..."):
                # Simulate processing time
                import time
                time.sleep(2)
                
                analysis_results = {
                    "Cultural Category": np.random.choice(["Traditional Dance", "Festival", "Art & Craft", "Architecture", "Costume"]),
                    "Region Detected": np.random.choice(["North India", "South India", "East India", "West India"]),
                    "Time Period": np.random.choice(["Ancient", "Medieval", "Colonial", "Modern"]),
                    "Authenticity Score": f"{np.random.randint(75, 98)}%",
                    "Cultural Significance": f"{np.random.randint(80, 95)}%"
                }
                
                for key, value in analysis_results.items():
                    st.metric(key, value)
                
                # Color analysis
                st.markdown("#### 🎨 Color Palette Analysis")
                
                # Convert PIL image to numpy array for color analysis
                img_array = np.array(image)
                if len(img_array.shape) == 3:
                    # Get dominant colors (simplified)
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                    percentages = np.random.dirichlet(np.ones(5)) * 100
                    
                    color_df = pd.DataFrame({
                        'Color': colors,
                        'Percentage': percentages
                    })
                    
                    fig_colors = px.pie(
                        color_df,
                        values='Percentage',
                        names='Color',
                        color='Color',
                        color_discrete_map={color: color for color in colors}
                    )
                    st.plotly_chart(fig_colors, use_container_width=True)
    
    # Visual trends
    st.markdown("---")
    st.markdown("#### 📈 Visual Content Trends")
    
    visual_categories = ['Traditional Dance', 'Festivals', 'Art & Crafts', 'Architecture', 'Costumes', 'Food']
    monthly_uploads = np.random.randint(10, 50, len(visual_categories))
    
    fig_visual_trends = px.bar(
        x=visual_categories,
        y=monthly_uploads,
        title="Visual Content Categories - This Month",
        color=monthly_uploads,
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig_visual_trends, use_container_width=True)

def recommendations_section():
    st.markdown("### 💡 Personalized Recommendations")
    
    # User preferences (simulated)
    st.markdown("#### 🎯 Based on Your Interests")
    
    user_interests = st.multiselect(
        "Select your cultural interests:",
        ["Music", "Dance", "Food", "Stories", "Festivals", "Art", "Crafts", "History", "Language", "Religion"],
        default=["Music", "Food", "Festivals"]
    )
    
    if user_interests:
        # Generate recommendations based on interests
        recommendations = []
        
        if "Music" in user_interests:
            recommendations.extend([
                {"title": "Rajasthani Folk Songs Collection", "type": "Audio", "match": "95%", "reason": "Matches your music interest"},
                {"title": "Classical Ragas Tutorial", "type": "Educational", "match": "88%", "reason": "Advanced music content"}
            ])
        
        if "Food" in user_interests:
            recommendations.extend([
                {"title": "Traditional Bengali Sweets", "type": "Recipe", "match": "92%", "reason": "Popular food content"},
                {"title": "Festival Cooking Methods", "type": "Video", "match": "87%", "reason": "Combines food and festivals"}
            ])
        
        if "Festivals" in user_interests:
            recommendations.extend([
                {"title": "Diwali Celebrations Across India", "type": "Story", "match": "94%", "reason": "Festival documentation"},
                {"title": "Regional Holi Traditions", "type": "Image", "match": "89%", "reason": "Visual festival content"}
            ])
        
        # Display recommendations
        for rec in recommendations[:6]:  # Show top 6
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <h4 style='margin: 0 0 0.5rem 0; color: #333;'>{rec['title']}</h4>
                <p style='margin: 0.5rem 0; color: #666;'>Type: {rec['type']} | Match: <span style='color: #51cf66; font-weight: bold;'>{rec['match']}</span></p>
                <p style='margin: 0; color: #888; font-size: 0.9rem;'>{rec['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Trending recommendations
    st.markdown("---")
    st.markdown("#### 🔥 Trending Now")
    
    trending_items = [
        {"title": "Winter Festival Preparations", "engagement": "↗️ +45%", "category": "Seasonal"},
        {"title": "Traditional Weaving Techniques", "engagement": "↗️ +38%", "category": "Crafts"},
        {"title": "Regional Wedding Songs", "engagement": "↗️ +32%", "category": "Music"},
        {"title": "Harvest Season Stories", "engagement": "↗️ +28%", "category": "Stories"}
    ]
    
    cols = st.columns(2)
    for i, item in enumerate(trending_items):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 1rem; border-radius: 8px; color: white; margin: 0.5rem 0;'>
                <h4 style='margin: 0; color: white;'>{item['title']}</h4>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>{item['category']} | {item['engagement']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # AI-powered discovery
    st.markdown("---")
    st.markdown("#### 🤖 AI Discovery Engine")
    
    discovery_query = st.text_input(
        "Ask AI to find cultural content:",
        placeholder="e.g., 'Find stories about monsoon festivals' or 'Show me traditional dance from Kerala'"
    )
    
    if discovery_query:
        with st.spinner("AI is searching..."):
            time.sleep(1)  # Simulate AI processing
            
            st.success("Found relevant content!")
            
            # Simulated AI search results
            ai_results = [
                {"title": "Monsoon Folk Songs from Assam", "relevance": "96%", "type": "Audio"},
                {"title": "Rain Festival Celebrations", "relevance": "94%", "type": "Story"},
                {"title": "Traditional Rain Dance", "relevance": "91%", "type": "Video"},
                {"title": "Monsoon Recipes", "relevance": "87%", "type": "Recipe"}
            ]
            
            for result in ai_results:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{result['title']}**")
                with col2:
                    st.markdown(f"*{result['type']}*")
                with col3:
                    st.markdown(f"**{result['relevance']}**")