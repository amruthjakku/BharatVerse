import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from streamlit_app.utils.database import get_statistics
from streamlit_app.utils.data_handler import get_contributions

def analytics_page():
    """Analytics dashboard page - demo mode removed"""
    st.markdown("## 📊 Analytics Dashboard")
    st.markdown("Explore insights and trends from BharatVerse contributions")
    
    # Get data from database
    stats = get_statistics()
    contributions = get_contributions()
    
    # Overview metrics
    st.markdown("### 🎯 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contributions", 
            stats['total_contributions'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Languages Covered", 
            stats['unique_languages'],
            delta=None
        )
    
    with col3:
        st.metric(
            "Regions Active", 
            stats['unique_regions'],
            delta=None
        )
    
    with col4:
        st.metric(
            "Active Contributors", 
            stats.get('active_contributors', 0),
            delta=None
        )
    
    # Content type distribution
    st.markdown("---")
    st.markdown("### 📈 Content Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Content type pie chart
        content_data = {
            'Type': ['Audio', 'Text', 'Image'],
            'Count': [stats['audio_count'], stats['text_count'], stats['image_count']]
        }
        df_content = pd.DataFrame(content_data)
        
        fig_pie = px.pie(
            df_content, 
            values='Count', 
            names='Type',
            title='Content Type Distribution',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Language distribution
        if contributions:
            # Get actual language data from contributions
            lang_counts = {}
            for contrib in contributions:
                lang = contrib.get('lang', 'Unknown')
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
            if lang_counts:
                df_lang = pd.DataFrame(list(lang_counts.items()), columns=['Language', 'Count'])
                fig_bar = px.bar(df_lang, x='Language', y='Count', title='Languages Used')
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No language data available yet")
        else:
            st.info("No contributions available yet")
    
    # Time series analysis
    st.markdown("---")
    st.markdown("### 📅 Contribution Trends")
    
    if contributions:
        # Create time series from actual contributions
        dates = []
        for contrib in contributions:
            try:
                # Parse the time string to datetime
                time_str = contrib.get('time', '')
                if 'ago' in time_str:
                    # Handle relative times like "2 hours ago"
                    dates.append(datetime.now() - timedelta(hours=2))
                else:
                    # Handle absolute dates
                    dates.append(datetime.strptime(time_str, '%Y-%m-%d %H:%M'))
            except:
                dates.append(datetime.now())
        
        # Group by date
        date_counts = {}
        for date in dates:
            date_key = date.strftime('%Y-%m-%d')
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        if date_counts:
            df_time = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Contributions'])
            df_time['Date'] = pd.to_datetime(df_time['Date'])
            
            fig_time = px.line(df_time, x='Date', y='Contributions', title='Contributions Over Time')
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No time series data available yet")
    else:
        st.info("No contributions available for time series analysis")
    
    # Regional analysis
    st.markdown("---")
    st.markdown("### 🗺️ Regional Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if contributions:
            # Get regional data from contributions
            region_counts = {}
            for contrib in contributions:
                # This would need to be extracted from contribution metadata
                region = "Unknown"  # Placeholder
                region_counts[region] = region_counts.get(region, 0) + 1
            
            if len(region_counts) > 1:
                df_region = pd.DataFrame(list(region_counts.items()), columns=['Region', 'Count'])
                fig_region = px.bar(df_region, x='Region', y='Count', title='Regional Distribution')
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.info("Regional data will be displayed when more contributions are available")
        else:
            st.info("No regional data available yet")
    
    with col2:
        st.info("State-wise distribution will be available with more detailed location data")
    
    # Content analysis
    st.markdown("---")
    st.markdown("### 🔍 Content Analysis")
    
    if contributions:
        st.markdown("#### 📝 Recent Contributions")
        
        # Show recent contributions table
        contrib_data = []
        for contrib in contributions[:10]:  # Show last 10
            contrib_data.append({
                'Title': contrib.get('title', 'Untitled'),
                'Type': contrib.get('type', 'Unknown'),
                'Language': contrib.get('lang', 'Unknown'),
                'Time': contrib.get('time', 'Unknown'),
                'Contributor': contrib.get('contributor', 'Anonymous')
            })
        
        if contrib_data:
            df_contrib = pd.DataFrame(contrib_data)
            st.dataframe(df_contrib, use_container_width=True)
        else:
            st.info("No contribution data available")
    else:
        st.info("No contributions available for analysis")
    
    # Quality metrics
    st.markdown("---")
    st.markdown("### 📊 Quality Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Quality metrics will be available as the system collects more data")
    
    with col2:
        st.info("Engagement metrics will be displayed when user interaction data is available")
    
    # Export options
    st.markdown("---")
    st.markdown("### 📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Statistics", use_container_width=True):
            st.download_button(
                label="Download CSV",
                data=pd.DataFrame([stats]).to_csv(index=False),
                file_name=f"bharatverse_stats_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Export Contributions", use_container_width=True):
            if contributions:
                df_export = pd.DataFrame(contributions)
                st.download_button(
                    label="Download CSV",
                    data=df_export.to_csv(index=False),
                    file_name=f"bharatverse_contributions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No contributions to export")
    
    with col3:
        if st.button("📈 Generate Report", use_container_width=True):
            st.info("Detailed report generation will be available soon")