import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Performance optimization imports
from utils.performance_optimizer import (
    get_performance_optimizer, 
    cached_analytics_data,
    show_performance_dashboard,
    optimize_dataframe_memory,
    progressive_loading_container
)

# Database imports with caching
try:
    from utils.supabase_db import (
        get_database_manager,
        get_cached_platform_stats,
        get_cached_contributions,
        get_cached_user_analytics,
        log_analytics_batched
    )
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Authentication imports
try:
    from streamlit_app.utils.auth import get_auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Try to import existing modules with fallback
try:
    from streamlit_app.utils.database import get_statistics
    from streamlit_app.utils.data_handler import get_contributions
    LEGACY_MODULES_AVAILABLE = True
except ImportError:
    LEGACY_MODULES_AVAILABLE = False

@st.cache_data(ttl=1800, show_spinner=False)
def get_supabase_analytics_data():
    """Get analytics data from Supabase"""
    if not SUPABASE_AVAILABLE:
        return None, None
    
    try:
        db = get_database_manager()
        
        # Get contributions
        contributions = db.get_contributions(limit=1000)
        
        # Calculate statistics
        stats = {
            'total_contributions': len(contributions),
            'text_count': len([c for c in contributions if c.get('content_type') == 'text']),
            'audio_count': len([c for c in contributions if c.get('content_type') == 'audio']),
            'image_count': len([c for c in contributions if c.get('content_type') == 'image']),
            'proverb_count': len([c for c in contributions if c.get('content_type') == 'proverb']),
            'languages': list(set([c.get('language', 'Unknown') for c in contributions if c.get('language')])),
            'regions': list(set([c.get('region', 'Unknown') for c in contributions if c.get('region')])),
            'recent_contributions': len([c for c in contributions if c.get('created_at', '') > (datetime.now() - timedelta(days=7)).isoformat()])
        }
        
        return stats, contributions
        
    except Exception as e:
        st.error(f"Error loading Supabase analytics: {e}")
        return None, None

@st.cache_data(ttl=1800, show_spinner=False)
def generate_analytics_charts(stats_data, contributions_data):
    """Generate analytics charts with caching"""
    charts = {}
    
    # Content type pie chart
    if stats_data:
        content_data = {
            'Type': ['Audio', 'Text', 'Image'],
            'Count': [
                stats_data.get('audio_count', 0), 
                stats_data.get('text_count', 0), 
                stats_data.get('image_count', 0)
            ]
        }
        df_content = pd.DataFrame(content_data)
        df_content = df_content[df_content['Count'] > 0]  # Filter out zero counts
        
        if not df_content.empty:
            charts['content_pie'] = px.pie(
                df_content, 
                values='Count', 
                names='Type',
                title='Content Type Distribution',
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
            charts['content_pie'].update_traces(textposition='inside', textinfo='percent+label')
    
    # Language distribution
    if contributions_data:
        lang_counts = {}
        for contrib in contributions_data:
            lang = contrib.get('language', 'Unknown')
            if lang and lang != 'Unknown':
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        if lang_counts:
            df_lang = pd.DataFrame(list(lang_counts.items()), columns=['Language', 'Count'])
            df_lang = df_lang.sort_values('Count', ascending=False).head(10)  # Top 10 languages
            charts['language_bar'] = px.bar(
                df_lang, 
                x='Language', 
                y='Count', 
                title='Top Languages Used',
                color='Count',
                color_continuous_scale='viridis'
            )
    
    return charts

@st.cache_data(ttl=3600, show_spinner=False)
def get_time_series_data(contributions_data):
    """Generate time series data with caching"""
    if not contributions_data:
        return None
    
    # Create time series from contributions
    dates = []
    for contrib in contributions_data:
        created_at = contrib.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                try:
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    dates.append(date.date())
                except:
                    continue
            else:
                dates.append(created_at.date())
    
    if dates:
        df_dates = pd.DataFrame({'date': dates})
        df_dates['count'] = 1
        df_timeline = df_dates.groupby('date').count().reset_index()
        df_timeline = df_timeline.sort_values('date')
        return df_timeline
    
    return None

def analytics_page():
    """Enhanced analytics dashboard with performance optimizations"""
    st.markdown("## 📊 Analytics Dashboard")
    st.markdown("Explore insights and trends from BharatVerse contributions")
    
    # Initialize performance optimizer
    optimizer = get_performance_optimizer()
    
    # Log page visit
    log_analytics_batched("analytics_page_visit", user_id=st.session_state.get("user_id"))
    
    # Progressive loading container
    container, progress_bar, status_text = progressive_loading_container()
    
    with container:
        # Step 1: Load basic stats
        status_text.text("Loading platform statistics...")
        progress_bar.progress(0.2)
        
        # Try to get data from Supabase first
        supabase_stats, supabase_contributions = get_supabase_analytics_data()
        
        if supabase_stats:
            stats = supabase_stats
            st.success("📊 Analytics loaded from Supabase Cloud Database")
        else:
            # Fallback to cached platform stats
            stats = get_cached_platform_stats()
            st.info("📊 Using cached analytics data")
        
        # Step 2: Load contributions data conditionally
        status_text.text("Loading contributions data...")
        progress_bar.progress(0.4)
        
        # Use lazy loading for contributions
        load_detailed_data = st.checkbox(
            "📈 Load Detailed Analytics", 
            value=False,
            help="Load detailed charts and trends (may take a moment)"
        )
        
        contributions = []
        if load_detailed_data:
            if supabase_contributions:
                contributions = supabase_contributions
                st.success("📈 Detailed analytics from Supabase")
            else:
                contributions = get_cached_contributions(limit=1000)  # Limit for performance
                st.info("📈 Using cached contributions data")
        
        progress_bar.progress(0.6)
    
    # Clear loading indicators
    progress_bar.progress(1.0)
    status_text.text("Analytics loaded successfully!")
    
    # Overview metrics
    st.markdown("### 🎯 Platform Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contributions", 
            stats.get('total_contributions', 0),
            delta=None,
            help="Total number of cultural contributions"
        )
    
    with col2:
        st.metric(
            "Languages Covered", 
            stats.get('languages_count', 0),
            delta=None,
            help="Number of unique languages represented"
        )
    
    with col3:
        st.metric(
            "Regions Active", 
            stats.get('regions_count', 0),
            delta=None,
            help="Number of regions with contributions"
        )
    
    with col4:
        st.metric(
            "Active Users", 
            stats.get('total_users', 0),
            delta=None,
            help="Total registered users"
        )
    
    # Detailed analytics (only if requested)
    if load_detailed_data:
        st.markdown("---")
        st.markdown("### 📈 Detailed Analytics")
        
        # Generate charts with caching
        charts = generate_analytics_charts(stats, contributions)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'content_pie' in charts:
                st.plotly_chart(charts['content_pie'], use_container_width=True)
            else:
                st.info("📊 No content distribution data available yet")
        
        with col2:
            if 'language_bar' in charts:
                st.plotly_chart(charts['language_bar'], use_container_width=True)
            else:
                st.info("🌐 No language distribution data available yet")
        
        # Time series analysis
        st.markdown("---")
        st.markdown("### 📅 Contribution Trends")
        
        time_series_data = get_time_series_data(contributions)
        
        if time_series_data is not None and not time_series_data.empty:
            fig_timeline = px.line(
                time_series_data, 
                x='date', 
                y='count',
                title='Daily Contributions Over Time',
                labels={'count': 'Number of Contributions', 'date': 'Date'}
            )
            fig_timeline.update_traces(line_color='#4ECDC4', line_width=3)
            fig_timeline.update_layout(
                xaxis_title="Date",
                yaxis_title="Contributions",
                hovermode='x unified'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("📈 No timeline data available yet")
        
        # Regional analysis
        if contributions:
            st.markdown("---")
            st.markdown("### 🗺️ Regional Distribution")
            
            region_counts = {}
            for contrib in contributions:
                region = contrib.get('region', 'Unknown')
                if region and region != 'Unknown':
                    region_counts[region] = region_counts.get(region, 0) + 1
            
            if region_counts:
                df_regions = pd.DataFrame(list(region_counts.items()), columns=['Region', 'Count'])
                df_regions = df_regions.sort_values('Count', ascending=True).tail(15)  # Top 15 regions
                
                fig_regions = px.bar(
                    df_regions, 
                    x='Count', 
                    y='Region',
                    orientation='h',
                    title='Top Regions by Contributions',
                    color='Count',
                    color_continuous_scale='plasma'
                )
                fig_regions.update_layout(height=500)
                st.plotly_chart(fig_regions, use_container_width=True)
            else:
                st.info("🗺️ No regional data available yet")
    
    else:
        st.info("👆 Check 'Load Detailed Analytics' above to see charts and trends")
    
    # Performance metrics for admins
    if st.session_state.get("user_role") == "admin":
        st.markdown("---")
        with st.expander("⚡ Performance Metrics", expanded=False):
            show_performance_dashboard()
    
    # Export functionality
    st.markdown("---")
    st.markdown("### 📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Statistics", help="Download platform statistics as JSON"):
            import json
            stats_json = json.dumps(stats, indent=2, default=str)
            st.download_button(
                label="Download Statistics",
                data=stats_json,
                file_name=f"bharatverse_stats_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        if load_detailed_data and contributions:
            if st.button("📋 Export Contributions", help="Download contributions data as CSV"):
                df_contributions = pd.DataFrame(contributions)
                df_contributions = optimize_dataframe_memory(df_contributions)
                csv_data = df_contributions.to_csv(index=False)
                st.download_button(
                    label="Download Contributions",
                    data=csv_data,
                    file_name=f"bharatverse_contributions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
