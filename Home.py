import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Detect deployment mode
DEPLOYMENT_MODE = os.getenv("AI_MODE", "cloud")  # Default to cloud for free deployment
IS_CLOUD_DEPLOYMENT = DEPLOYMENT_MODE == "cloud"

# Import styling and authentication
from streamlit_app.utils.main_styling import load_custom_css
from streamlit_app.utils.auth import GitLabAuth, handle_oauth_callback, render_login_button, init_auth
from streamlit_app.utils.user_manager import user_manager

# Import performance optimizations (with fallbacks for cloud deployment)
try:
    from utils.performance_optimizer import (
        get_performance_optimizer, 
        show_performance_dashboard,
        clear_all_caches
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

try:
    from utils.memory_manager import get_memory_manager
    MEMORY_MANAGER_AVAILABLE = True
except ImportError:
    MEMORY_MANAGER_AVAILABLE = False

try:
    from utils.redis_cache import get_cache_manager
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Import cloud AI manager if in cloud mode
if IS_CLOUD_DEPLOYMENT:
    try:
        from core.cloud_ai_manager import get_cloud_ai_manager
        CLOUD_AI_AVAILABLE = True
    except ImportError as e:
        st.error(f"Cloud AI Manager not available: {e}")
        CLOUD_AI_AVAILABLE = False
else:
    CLOUD_AI_AVAILABLE = False

@st.cache_data(ttl=3600, show_spinner=False)
def get_platform_features():
    """Get platform features (cached for performance)"""
    return [
        {
            "icon": "🎵",
            "title": "Audio Recording & Preservation",
            "description": "High-quality audio recording with automatic transcription and metadata tagging"
        },
        {
            "icon": "📚",
            "title": "Story Documentation",
            "description": "Rich text editor with multimedia support for comprehensive cultural documentation"
        },
        {
            "icon": "🖼️",
            "title": "Visual Heritage Archive",
            "description": "Image upload with AI-powered tagging and cultural context recognition"
        },
        {
            "icon": "🔍",
            "title": "Smart Discovery",
            "description": "Advanced search and filtering to explore cultural content by region, type, and theme"
        },
        {
            "icon": "📊",
            "title": "Analytics & Insights",
            "description": "Data visualization and trends analysis of cultural contributions and engagement"
        },
        {
            "icon": "🤝",
            "title": "Community Collaboration",
            "description": "Connect with cultural enthusiasts, experts, and contributors from across India"
        },
        {
            "icon": "🤖",
            "title": "AI-Powered Insights",
            "description": "Machine learning analysis for content categorization, sentiment analysis, and recommendations"
        },
        {
            "icon": "👥",
            "title": "Project Management",
            "description": "Collaborative tools for organizing cultural preservation projects and team workflows"
        }
    ]

@st.cache_data(ttl=1800, show_spinner=False)
def get_system_status():
    """Get cached system status"""
    if IS_CLOUD_DEPLOYMENT and CLOUD_AI_AVAILABLE:
        try:
            ai_manager = get_cloud_ai_manager()
            return ai_manager.get_system_status()
        except Exception as e:
            return {"error": str(e), "services": {}}
    return {"services": {}}

def show_performance_section():
    """Show performance metrics section for admins"""
    if st.session_state.get("user_role") == "admin":
        with st.expander("⚡ Performance Dashboard", expanded=False):
            show_performance_dashboard()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧹 Clear All Caches"):
                    clear_all_caches()
            
            with col2:
                if st.button("🔥 Warm Up Services"):
                    optimizer = get_performance_optimizer()
                    warmup_results = optimizer.warm_up_services()
                    
                    for service, status in warmup_results.items():
                        if status:
                            st.success(f"✅ {service.title()} warmed up")
                        else:
                            st.error(f"❌ {service.title()} warmup failed")

def show_login_section():
    """Display login section with GitLab OAuth"""
    st.markdown("---")
    st.markdown("## 🔐 Login to Access Your Dashboard")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("""
        **Login Required**: Please authenticate with your GitLab account to access:
        - 👤 Personal User Dashboard
        - 🛡️ Admin Dashboard (for administrators)
        - 🤝 Community Features
        - 📁 Content Management
        """)
        
        render_login_button()
        
        st.markdown("""<br>
        <div style='text-align: center; color: #666;'>
            <small>By logging in, you agree to our terms of service and privacy policy.</small>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="BharatVerse - Digital Cultural Heritage",
        page_icon="🇮🇳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize authentication
    auth = GitLabAuth()
    
    # Initialize auth system (handles OAuth callback)
    init_auth()
    
    # Apply custom styling
    load_custom_css()
    
    # Check authentication and redirect if logged in
    if auth.is_authenticated():
        db_user = auth.get_current_db_user()
        if db_user:
            # Show welcome message and redirect button
            st.markdown("""
            <div style='text-align: center; padding: 2rem 0;'>
                <h1 style='color: #FF6B35; font-size: 3.5rem; margin-bottom: 0.5rem;'>🇮🇳 BharatVerse</h1>
            </div>
            """, unsafe_allow_html=True)
            
            st.success(f"Welcome back, {db_user.get('name', 'User')}!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if db_user.get('role') == 'admin':
                    st.info("🛡️ You have administrator privileges.")
                    if st.button("📊 Go to Analytics Dashboard", use_container_width=True, type="primary"):
                        st.switch_page("pages/05_📊_Analytics.py")
                else:
                    st.info("👤 Welcome to your personal dashboard.")
                    if st.button("👤 Go to My Profile", use_container_width=True, type="primary"):
                        st.switch_page("pages/10_👤_My_Profile.py")
                
                if st.button("🚪 Logout", use_container_width=True):
                    auth.logout()
                    st.rerun()
            
            st.stop()
    
    # Main header for non-authenticated users
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #FF6B35; font-size: 3.5rem; margin-bottom: 0.5rem;'>🇮🇳 BharatVerse</h1>
        <h2 style='color: #2E86AB; font-size: 1.8rem; margin-bottom: 1rem;'>Digital Cultural Heritage Platform</h2>
        <p style='font-size: 1.2rem; color: #666; max-width: 800px; margin: 0 auto;'>
            Preserve, share, and celebrate the rich cultural heritage of India through digital storytelling, 
            audio recordings, visual documentation, and community collaboration.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show cloud deployment status with caching
    if IS_CLOUD_DEPLOYMENT:
        with st.expander("☁️ Cloud Deployment Status", expanded=False):
            if CLOUD_AI_AVAILABLE:
                status = get_system_status()
                
                if "error" in status:
                    st.error(f"Status check failed: {status['error']}")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**🔮 AI Services**")
                        inference_status = status.get("services", {}).get("inference_api", {})
                        if inference_status.get("status") == "available":
                            st.success("AI APIs: Online")
                        else:
                            st.error("AI APIs: Offline")
                    
                    with col2:
                        st.markdown("**💾 Database & Cache**")
                        db_status = status.get("services", {}).get("database", {}).get("status")
                        cache_status = status.get("services", {}).get("redis_cache", {}).get("status")
                        
                        if db_status == "connected":
                            st.success("Database: Connected")
                        else:
                            st.warning("Database: Limited")
                        
                        if cache_status == "connected":
                            st.success("Cache: Active")
                        else:
                            st.warning("Cache: Disabled")
                    
                    with col3:
                        st.markdown("**📊 Performance**")
                        st.info(f"Mode: Free Cloud Tier")
                        st.info("Storage: Cloudflare R2")
                    
                    # Show rate limits
                    rate_limits = status.get("rate_limits", {})
                    if rate_limits:
                        st.markdown(f"**Rate Limits:** {rate_limits.get('api_calls_per_minute', 'N/A')} calls/minute")
            else:
                st.error("Cloud AI Manager not available. Check configuration.")
    else:
        st.info("💻 Running in local mode")
    
    # Show performance section for admins
    show_performance_section()
    
    # Initialize performance monitoring
    if "performance_initialized" not in st.session_state:
        optimizer = get_performance_optimizer()
        memory_manager = get_memory_manager()
        
        # Show performance status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            memory_usage = memory_manager.get_memory_usage()
            st.metric(
                "Memory Usage", 
                f"{memory_usage['rss_mb']:.0f}MB",
                f"{memory_usage['percent']:.1f}%"
            )
        
        with col2:
            cache_manager = get_cache_manager()
            if cache_manager and cache_manager.is_connected():
                st.metric("Cache Status", "🟢 Connected", "Redis active")
            else:
                st.metric("Cache Status", "🟡 Local only", "Redis not configured")
        
        with col3:
            st.metric("Performance", "⚡ Optimized", "All systems active")
        
        # Warm up services
        warmup_results = optimizer.warm_up_services()
        st.session_state.performance_initialized = True
        
        # Show performance info
        with st.expander("⚡ Performance Status", expanded=False):
            st.markdown("### 🎯 Active Optimizations:")
            st.markdown("- ✅ **Streamlit Caching**: Automatic caching for expensive operations")
            st.markdown("- ✅ **Memory Management**: Real-time monitoring and cleanup")
            st.markdown("- ✅ **Parallel Processing**: Async operations for better performance")
            st.markdown("- ✅ **Performance Tracking**: Detailed metrics and monitoring")
            
            if cache_manager and cache_manager.is_connected():
                st.markdown("- ✅ **Redis Caching**: External cache for cross-session persistence")
            else:
                st.markdown("- ⚠️ **Redis Caching**: Not configured (using local cache only)")
            
            st.markdown("### 📊 Performance Dashboard:")
            st.markdown("Access detailed performance metrics at: **Performance** page")
            
            if st.session_state.get("user_role") == "admin":
                st.markdown("### 🔧 Admin Tools:")
                if st.button("🧹 Clean Memory"):
                    cleanup_result = memory_manager.cleanup_memory(force=True)
                    if cleanup_result["cleaned"]:
                        st.success(f"Memory cleaned! Freed {cleanup_result['memory_freed_mb']:.1f}MB")
                    else:
                        st.info("No cleanup needed")
    
    # Welcome section
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎵 Audio Heritage
        Record and preserve traditional songs, stories, and oral traditions from across India.
        - Folk songs and classical music
        - Oral histories and legends
        - Regional dialects and languages
        - Traditional ceremonies
        """)
        
    with col2:
        st.markdown("""
        ### 📚 Cultural Stories
        Document and share the rich tapestry of Indian culture through written narratives.
        - Family traditions and customs
        - Festival celebrations
        - Regional cuisines and recipes
        - Historical accounts
        """)
        
    with col3:
        st.markdown("""
        ### 🖼️ Visual Documentation
        Capture the visual essence of Indian heritage through photographs and artwork.
        - Traditional arts and crafts
        - Architecture and monuments
        - Cultural events and festivals
        - Regional costumes and jewelry
        """)
    
    # Quick start section
    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎤 Record Audio", use_container_width=True, type="primary"):
            st.switch_page("pages/01_🎤_Audio_Capture.py")
    
    with col2:
        if st.button("📝 Share Story", use_container_width=True, type="primary"):
            st.switch_page("pages/02_📝_Text_Stories.py")
    
    with col3:
        if st.button("📸 Upload Image", use_container_width=True, type="primary"):
            st.switch_page("pages/03_📸_Visual_Heritage.py")
    
    with col4:
        if st.button("🔍 Explore", use_container_width=True, type="primary"):
            st.switch_page("pages/04_🔍_Discover.py")
    
    # Features overview
    st.markdown("---")
    st.markdown("## ✨ Platform Features")
    
    # Use cached features data
    features = get_platform_features()
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; border-left: 4px solid #FF6B35;'>
                <h3 style='color: #2E86AB; margin: 0 0 0.5rem 0;'>{feature['icon']} {feature['title']}</h3>
                <p style='color: #666; margin: 0;'>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #FF6B35, #2E86AB); border-radius: 15px; color: white;'>
        <h2 style='margin-bottom: 1rem;'>Join the Cultural Preservation Movement</h2>
        <p style='font-size: 1.1rem; margin-bottom: 1.5rem;'>
            Every story, song, and image you contribute helps preserve India's rich cultural heritage for future generations.
        </p>
        <p style='font-size: 1rem; opacity: 0.9;'>
            Start by exploring the navigation menu on the left to begin your cultural documentation journey.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add authentication notice
    st.markdown("---")
    st.info("🔐 **Authentication**: This platform uses GitLab OAuth for secure authentication. Login with your GitLab account to access community features and content creation tools.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**👤 Authenticated Users can access:**")
        st.markdown("• Community groups and chat")
        st.markdown("• Discussion forums")
        st.markdown("• Challenges and leaderboards")
        st.markdown("• Profile management")
        st.markdown("• Content creation and upload")
        
    with col2:
        st.markdown("**🛡️ Admin Users can access:**")
        st.markdown("• All user features")
        st.markdown("• Admin dashboard")
        st.markdown("• User management")
        st.markdown("• System analytics")
        st.markdown("• Platform configuration")
        
    st.markdown("**Note:** Admin privileges are determined by your GitLab account permissions and platform configuration.")
    
    # Show login section at the bottom
    show_login_section()

if __name__ == "__main__":
    main()
