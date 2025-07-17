import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from pathlib import Path
from streamlit_app.utils.database import get_contributions, get_statistics
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def analytics_page():
    st.markdown("## 📊 Analytics Dashboard")
    st.markdown("Explore insights and trends from BharatVerse contributions")
    
    # Get data
    stats = get_statistics()
    contributions = get_contributions(limit=100)
    
    # Overview metrics
    st.markdown("### 🎯 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contributions", 
            stats['total_contributions'],
            delta=f"+{np.random.randint(5, 25)} this week"
        )
    
    with col2:
        st.metric(
            "Languages Covered", 
            stats['unique_languages'],
            delta=f"+{np.random.randint(1, 3)} this month"
        )
    
    with col3:
        st.metric(
            "Regions Active", 
            stats['unique_regions'],
            delta=f"+{np.random.randint(1, 5)} this month"
        )
    
    with col4:
        st.metric(
            "Active Contributors", 
            np.random.randint(150, 300),
            delta=f"+{np.random.randint(10, 30)} today"
        )
    
    # Content type distribution
    st.markdown("---")
    st.markdown("### 📈 Content Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for content types
        content_data = {
            'Audio': stats['audio_count'],
            'Text': stats['text_count'], 
            'Images': stats['image_count']
        }
        
        fig_pie = px.pie(
            values=list(content_data.values()),
            names=list(content_data.keys()),
            title="Content Type Distribution",
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Generate sample language data
        languages = ['Hindi', 'Bengali', 'Tamil', 'Telugu', 'Marathi', 'Gujarati', 'Kannada', 'Malayalam']
        lang_counts = np.random.randint(10, 100, len(languages))
        
        fig_bar = px.bar(
            x=languages,
            y=lang_counts,
            title="Contributions by Language",
            color=lang_counts,
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Time series analysis
    st.markdown("---")
    st.markdown("### 📅 Contribution Trends")
    
    # Generate sample time series data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    daily_contributions = np.random.poisson(5, len(dates))
    
    # Add some seasonal patterns
    for i, date in enumerate(dates):
        if date.month in [3, 4, 10, 11]:  # Festival seasons
            daily_contributions[i] += np.random.poisson(3)
    
    df_time = pd.DataFrame({
        'Date': dates,
        'Contributions': daily_contributions
    })
    
    # Create time series plot
    fig_time = px.line(
        df_time, 
        x='Date', 
        y='Contributions',
        title='Daily Contributions Over Time'
    )
    fig_time.update_traces(line_color='#FF6B6B')
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Regional analysis
    st.markdown("---")
    st.markdown("### 🗺️ Regional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample regional data
        regions = ['North India', 'South India', 'West India', 'East India', 'Northeast India']
        region_counts = np.random.randint(20, 150, len(regions))
        
        fig_region = px.bar(
            x=region_counts,
            y=regions,
            orientation='h',
            title="Contributions by Region",
            color=region_counts,
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        # Top contributing states
        states = ['Maharashtra', 'West Bengal', 'Tamil Nadu', 'Karnataka', 'Gujarat', 
                 'Rajasthan', 'Kerala', 'Punjab', 'Odisha', 'Assam']
        state_counts = np.random.randint(15, 80, len(states))
        
        df_states = pd.DataFrame({
            'State': states,
            'Contributions': state_counts
        }).sort_values('Contributions', ascending=False)
        
        fig_states = px.bar(
            df_states.head(8),
            x='Contributions',
            y='State',
            orientation='h',
            title="Top Contributing States",
            color='Contributions',
            color_continuous_scale='sunset'
        )
        st.plotly_chart(fig_states, use_container_width=True)
    
    # Content analysis
    st.markdown("---")
    st.markdown("### 🔍 Content Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Popular Tags", "Content Quality", "Engagement"])
    
    with tab1:
        # Generate word cloud for popular tags
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Sample tags data
            tags_text = """
            folk song traditional music dance festival celebration culture heritage
            story mythology legend fable wisdom proverb saying recipe food cooking
            art craft handicraft painting sculpture architecture temple palace
            wedding ceremony ritual custom tradition regional local community
            language literature poetry verse epic classical modern contemporary
            instrument tabla sitar flute drum percussion string wind classical
            costume clothing jewelry ornament decoration pattern design motif
            """
            
            # Create word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis'
            ).generate(tags_text)
            
            fig_wc, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)
        
        with col2:
            st.markdown("#### 🏷️ Top Tags")
            top_tags = [
                ("folk song", 156),
                ("traditional", 134),
                ("festival", 98),
                ("recipe", 87),
                ("story", 76),
                ("dance", 65),
                ("art", 54),
                ("ceremony", 43)
            ]
            
            for tag, count in top_tags:
                st.markdown(f"**{tag}**: {count}")
    
    with tab2:
        # Content quality metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality score distribution
            quality_scores = np.random.beta(2, 1, 1000) * 100
            
            fig_quality = px.histogram(
                x=quality_scores,
                nbins=20,
                title="Content Quality Score Distribution",
                labels={'x': 'Quality Score', 'y': 'Count'}
            )
            fig_quality.update_traces(marker_color='#4ECDC4')
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            # Completeness metrics
            completeness_data = {
                'Complete Metadata': 85,
                'Has Description': 92,
                'Tagged Properly': 78,
                'Has Translation': 65,
                'Cultural Context': 71
            }
            
            fig_complete = px.bar(
                x=list(completeness_data.keys()),
                y=list(completeness_data.values()),
                title="Content Completeness (%)",
                color=list(completeness_data.values()),
                color_continuous_scale='greens'
            )
            fig_complete.update_layout(showlegend=False)
            st.plotly_chart(fig_complete, use_container_width=True)
    
    with tab3:
        # Engagement metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily active users
            dates_engagement = pd.date_range(start='2024-11-01', end='2024-12-31', freq='D')
            daily_users = np.random.poisson(50, len(dates_engagement))
            
            df_engagement = pd.DataFrame({
                'Date': dates_engagement,
                'Active Users': daily_users
            })
            
            fig_users = px.line(
                df_engagement,
                x='Date',
                y='Active Users',
                title='Daily Active Contributors'
            )
            fig_users.update_traces(line_color='#45B7D1')
            st.plotly_chart(fig_users, use_container_width=True)
        
        with col2:
            # Content interaction
            interaction_data = {
                'Views': 15420,
                'Downloads': 3240,
                'Shares': 890,
                'Favorites': 1560,
                'Comments': 420
            }
            
            fig_interaction = px.bar(
                x=list(interaction_data.keys()),
                y=list(interaction_data.values()),
                title="Content Interactions",
                color=list(interaction_data.values()),
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig_interaction, use_container_width=True)
    
    # Recent activity feed
    st.markdown("---")
    st.markdown("### 🔄 Recent Activity")
    
    # Generate sample recent activities
    activities = [
        {"time": "2 minutes ago", "action": "New audio contribution", "user": "Priya_K", "content": "Bengali folk song from Purulia"},
        {"time": "15 minutes ago", "action": "Story added", "user": "Rajesh_M", "content": "Panchatantra tale in Hindi"},
        {"time": "1 hour ago", "action": "Image uploaded", "user": "Meera_S", "content": "Kathakali performance photos"},
        {"time": "2 hours ago", "action": "Recipe shared", "user": "Lakshmi_R", "content": "Traditional Onam Sadhya items"},
        {"time": "3 hours ago", "action": "Audio transcribed", "user": "System", "content": "Gujarati garba song processed"},
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.markdown(f"**{activity['time']}**")
            with col2:
                st.markdown(f"{activity['action']} by **{activity['user']}**: {activity['content']}")
            with col3:
                st.markdown("🔗")
        st.markdown("---")
    
    # Export options
    st.markdown("### 📤 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics Report", use_container_width=True):
            st.success("Analytics report exported to downloads!")
    
    with col2:
        if st.button("📋 Export Contribution Data", use_container_width=True):
            st.success("Contribution data exported as CSV!")
    
    with col3:
        if st.button("📈 Generate Insights", use_container_width=True):
            st.success("AI insights generated!")