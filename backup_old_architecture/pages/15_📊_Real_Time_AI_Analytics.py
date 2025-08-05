import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Try to import enhanced AI models
try:
    from core.enhanced_ai_models import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="Real-Time AI Analytics - BharatVerse",
        page_icon="📊",
        layout="wide"
    )
    
    st.markdown("# 📊 Real-Time AI Analytics")
    st.markdown("Live monitoring of AI model performance and cultural insights")
    
    if not AI_MODELS_AVAILABLE:
        st.error("🚫 Enhanced AI models not available")
        st.info("Install enhanced AI models to view real-time analytics:")
        st.code("python scripts/install_enhanced_ai.py")
        return
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 🔄 Live Dashboard")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=True)
    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Auto-refresh every 30 seconds
    if auto_refresh:
        time.sleep(1)  # Small delay to prevent too frequent updates
        st.rerun()
    
    # Get real-time analytics
    try:
        analytics = ai_manager.get_real_time_analytics()
        model_info = ai_manager.get_model_info()
        cultural_insights = ai_manager.get_cultural_insights()
        
        # Display main metrics
        display_main_metrics(analytics)
        
        # Display charts and insights
        col1, col2 = st.columns(2)
        
        with col1:
            display_processing_activity(analytics)
            display_language_distribution(analytics)
        
        with col2:
            display_model_performance(analytics)
            display_cultural_insights(cultural_insights)
        
        # Recent activity
        display_recent_activity(analytics)
        
        # Model status
        display_model_status(model_info)
        
    except Exception as e:
        st.error(f"❌ Error loading analytics: {str(e)}")
        st.info("💡 Try using the AI features first to generate analytics data")


def display_main_metrics(analytics):
    """Display main AI processing metrics"""
    daily_stats = analytics.get("daily_stats", {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🎵 Transcriptions Today",
            daily_stats.get("transcriptions_today", 0),
            help="Audio files transcribed today"
        )
    
    with col2:
        st.metric(
            "📝 Text Analyses",
            daily_stats.get("sentiment_analyses_today", 0),
            help="Text analyses performed today"
        )
    
    with col3:
        st.metric(
            "🔄 Translations",
            daily_stats.get("translations_today", 0),
            help="Translations completed today"
        )
    
    with col4:
        st.metric(
            "🖼️ Image Analyses",
            daily_stats.get("image_analyses_today", 0),
            help="Images analyzed today"
        )
    
    with col5:
        st.metric(
            "🏛️ Cultural Elements",
            daily_stats.get("cultural_elements_detected", 0),
            help="Cultural elements detected today"
        )


def display_processing_activity(analytics):
    """Display processing activity chart"""
    st.markdown("### 📈 Processing Activity")
    
    recent_activity = analytics.get("recent_activity", [])
    
    if recent_activity:
        # Create activity timeline
        activity_data = []
        for activity in recent_activity[-20:]:  # Last 20 activities
            activity_data.append({
                "Time": datetime.fromisoformat(activity["timestamp"]).strftime("%H:%M:%S"),
                "Type": activity["type"].replace("_", " ").title(),
                "Success": "✅" if activity.get("success", False) else "❌"
            })
        
        if activity_data:
            df = pd.DataFrame(activity_data)
            
            # Count by type
            type_counts = df["Type"].value_counts()
            
            fig = px.bar(
                x=type_counts.index,
                y=type_counts.values,
                title="Activity by Type",
                labels={"x": "Activity Type", "y": "Count"}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recent activity to display")
    else:
        st.info("No processing activity yet. Try using the AI features!")


def display_language_distribution(analytics):
    """Display language distribution"""
    st.markdown("### 🌐 Language Distribution")
    
    lang_dist = analytics.get("language_distribution", {})
    
    if lang_dist:
        # Create pie chart
        fig = px.pie(
            values=list(lang_dist.values()),
            names=list(lang_dist.keys()),
            title="Content by Language"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No language data available yet")


def display_model_performance(analytics):
    """Display model performance metrics"""
    st.markdown("### ⚡ Model Performance")
    
    model_perf = analytics.get("model_performance", {})
    
    if model_perf:
        perf_data = []
        for model, metrics in model_perf.items():
            perf_data.append({
                "Model": model.title(),
                "Avg Confidence": f"{metrics.get('average_confidence', 0):.2%}",
                "Avg Time (s)": f"{metrics.get('average_processing_time', 0):.2f}",
                "Operations": metrics.get("total_operations", 0)
            })
        
        if perf_data:
            df = pd.DataFrame(perf_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No performance data available")
    else:
        st.info("No model performance data yet")


def display_cultural_insights(cultural_insights):
    """Display cultural insights"""
    st.markdown("### 🏛️ Cultural Insights")
    
    if cultural_insights.get("error"):
        st.info("Cultural insights will appear after AI processing")
        return
    
    top_elements = cultural_insights.get("top_cultural_elements", [])
    total_elements = cultural_insights.get("total_elements_detected", 0)
    unique_elements = cultural_insights.get("unique_elements", 0)
    
    # Summary metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Elements", total_elements)
    with col2:
        st.metric("Unique Elements", unique_elements)
    
    # Top cultural elements
    if top_elements:
        st.markdown("#### 🔝 Most Detected Elements")
        for element, count in top_elements[:5]:
            st.write(f"• **{element}**: {count} times")
    else:
        st.info("No cultural elements detected yet")


def display_recent_activity(analytics):
    """Display recent activity table"""
    st.markdown("### 🕐 Recent Activity")
    
    recent_activity = analytics.get("recent_activity", [])
    
    if recent_activity:
        activity_data = []
        for activity in recent_activity[-10:]:  # Last 10 activities
            activity_data.append({
                "Time": datetime.fromisoformat(activity["timestamp"]).strftime("%H:%M:%S"),
                "Type": activity["type"].replace("_", " ").title(),
                "Status": "✅ Success" if activity.get("success", False) else "❌ Failed",
                "Language": activity.get("language", "N/A"),
                "Details": get_activity_details(activity)
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent activity to display")


def get_activity_details(activity):
    """Get activity-specific details"""
    activity_type = activity["type"]
    
    if activity_type == "transcription":
        duration = activity.get("duration", 0)
        word_count = activity.get("word_count", 0)
        return f"{duration:.1f}s, {word_count} words"
    
    elif activity_type == "text_analysis":
        word_count = activity.get("word_count", 0)
        sentiment = activity.get("sentiment", "unknown")
        return f"{word_count} words, {sentiment}"
    
    elif activity_type == "translation":
        source = activity.get("source_language", "unknown")
        target = activity.get("target_language", "unknown")
        return f"{source} → {target}"
    
    elif activity_type == "image_analysis":
        objects = activity.get("objects_detected", 0)
        quality = activity.get("quality_score", 0)
        return f"{objects} objects, quality: {quality:.1f}"
    
    return "N/A"


def display_model_status(model_info):
    """Display model status and capabilities"""
    st.markdown("---")
    st.markdown("### 🤖 AI Model Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎵 Audio Models")
        whisper_status = "🟢 Active" if model_info.get("whisper_available") else "🔴 Inactive"
        st.write(f"**Whisper**: {whisper_status}")
        st.write(f"**Model**: {model_info.get('models', {}).get('whisper', 'N/A')}")
    
    with col2:
        st.markdown("#### 📝 Text Models")
        text_status = "🟢 Active" if model_info.get("text_analysis_available") else "🔴 Inactive"
        st.write(f"**Text Analysis**: {text_status}")
        st.write(f"**Sentiment**: {model_info.get('models', {}).get('sentiment', 'N/A')}")
        st.write(f"**Translation**: {model_info.get('models', {}).get('translation', 'N/A')}")
    
    with col3:
        st.markdown("#### 🖼️ Vision Models")
        vision_status = "🟢 Active" if model_info.get("image_analysis_available") else "🔴 Inactive"
        st.write(f"**Image Analysis**: {vision_status}")
        st.write(f"**Caption**: {model_info.get('models', {}).get('image_caption', 'N/A')}")
        st.write(f"**Detection**: {model_info.get('models', {}).get('object_detection', 'N/A')}")
    
    # Tracking status
    tracking_enabled = model_info.get("tracking_enabled", False)
    tracking_status = "🟢 Enabled" if tracking_enabled else "🔴 Disabled"
    st.info(f"📊 **Real-time Tracking**: {tracking_status}")
    
    if tracking_enabled:
        total_ops = model_info.get("real_time_analytics", {}).get("total_operations", 0)
        st.success(f"✅ Total AI operations tracked: {total_ops}")


if __name__ == "__main__":
    main()