import streamlit as st
import sys
from pathlib import Path
import time
import json
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import performance utilities
from utils.performance_optimizer import get_performance_optimizer, show_performance_dashboard
# Safe memory manager import
try:
    from utils.memory_manager import get_memory_manager, show_memory_dashboard
except ImportError:
    from utils.fallback_memory import get_fallback_memory_manager as get_memory_manager, show_fallback_memory_dashboard as show_memory_dashboard
from utils.redis_cache import get_cache_manager
from utils.async_client import run_parallel_api_calls

def main():
    st.set_page_config(
        page_title="Performance Dashboard - BharatVerse",
        page_icon="⚡",
        layout="wide"
    )
    
    st.markdown("# ⚡ Performance Dashboard")
    st.markdown("Monitor and optimize BharatVerse performance in real-time")
    
    # Check admin access
    if st.session_state.get("user_role") != "admin":
        st.error("🔒 Admin access required for performance dashboard")
        st.info("Please log in as an administrator to access performance monitoring features.")
        return
    
    # Initialize performance components
    optimizer = get_performance_optimizer()
    memory_manager = get_memory_manager()
    cache_manager = get_cache_manager()
    
    # Performance overview
    st.markdown("## 📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Memory metrics
    memory_usage = memory_manager.get_memory_usage()
    with col1:
        memory_color = "normal"
        if memory_usage['rss_mb'] > 500:
            memory_color = "inverse"
        elif memory_usage['rss_mb'] > 300:
            memory_color = "off"
        
        st.metric(
            "Memory Usage",
            f"{memory_usage['rss_mb']:.1f} MB",
            f"{memory_usage['percent']:.1f}%",
            delta_color=memory_color
        )
    
    # Cache metrics
    with col2:
        if cache_manager and cache_manager.is_connected():
            cache_info = cache_manager.get_cache_info()
            hit_rate = cache_info.get('hit_rate', 0)
            st.metric(
                "Cache Hit Rate",
                f"{hit_rate:.1f}%",
                "Connected" if hit_rate > 0 else "No data"
            )
        else:
            st.metric("Cache Status", "Disconnected", "Redis unavailable")
    
    # Performance score
    with col3:
        perf_metrics = st.session_state.get("performance_metrics", {})
        if perf_metrics:
            avg_time = sum(m.get("execution_time", 0) for m in perf_metrics.values()) / len(perf_metrics)
            score = max(0, 100 - (avg_time * 10))  # Simple scoring
            st.metric("Performance Score", f"{score:.0f}/100", f"{avg_time:.2f}s avg")
        else:
            st.metric("Performance Score", "N/A", "No data")
    
    # System health
    with col4:
        health_status = "🟢 Healthy"
        if memory_usage['rss_mb'] > 500:
            health_status = "🔴 Critical"
        elif memory_usage['rss_mb'] > 300:
            health_status = "🟡 Warning"
        
        st.metric("System Health", health_status, "Auto-monitored")
    
    # Detailed monitoring sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Performance Metrics", 
        "💾 Memory Management", 
        "🗄️ Cache Management", 
        "🔧 System Tools",
        "📊 Analytics"
    ])
    
    with tab1:
        st.markdown("### 📈 Performance Metrics")
        show_performance_dashboard()
        
        # Performance history
        if "performance_history" not in st.session_state:
            st.session_state.performance_history = []
        
        # Add current metrics to history
        current_metrics = {
            "timestamp": datetime.now().isoformat(),
            "memory_mb": memory_usage['rss_mb'],
            "memory_percent": memory_usage['percent']
        }
        
        st.session_state.performance_history.append(current_metrics)
        
        # Keep only last 50 entries
        if len(st.session_state.performance_history) > 50:
            st.session_state.performance_history = st.session_state.performance_history[-50:]
        
        # Plot performance history
        if len(st.session_state.performance_history) > 1:
            import pandas as pd
            import plotly.express as px
            
            df_history = pd.DataFrame(st.session_state.performance_history)
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            
            fig = px.line(
                df_history, 
                x='timestamp', 
                y='memory_mb',
                title='Memory Usage Over Time',
                labels={'memory_mb': 'Memory (MB)', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 💾 Memory Management")
        show_memory_dashboard()
        
        # Memory cleanup controls
        st.markdown("#### 🧹 Memory Cleanup")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Streamlit Cache"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Streamlit cache cleared!")
        
        with col2:
            if st.button("🧹 Force Memory Cleanup"):
                cleanup_result = memory_manager.cleanup_memory(force=True)
                if cleanup_result["cleaned"]:
                    st.success(f"Memory cleaned! Freed {cleanup_result['memory_freed_mb']:.1f}MB")
                else:
                    st.info("No cleanup needed")
        
        with col3:
            if st.button("📊 Memory Report"):
                memory_stats = memory_manager.get_memory_top_stats()
                if memory_stats:
                    st.json(memory_stats[:5])
                else:
                    st.info("No detailed memory stats available")
    
    with tab3:
        st.markdown("### 🗄️ Cache Management")
        
        if cache_manager and cache_manager.is_connected():
            # Cache statistics
            cache_info = cache_manager.get_cache_info()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📊 Cache Statistics")
                st.json(cache_info)
            
            with col2:
                st.markdown("#### 🔧 Cache Controls")
                
                if st.button("🗑️ Clear All Cache"):
                    if cache_manager.clear_all():
                        st.success("All cache cleared!")
                    else:
                        st.error("Failed to clear cache")
                
                if st.button("🔍 Test Cache"):
                    test_key = f"test_{int(time.time())}"
                    test_value = "performance_test"
                    
                    # Test write
                    write_success = cache_manager.set(test_key, test_value, 60)
                    
                    # Test read
                    read_value = cache_manager.get(test_key)
                    
                    # Cleanup
                    cache_manager.delete(test_key)
                    
                    if write_success and read_value == test_value:
                        st.success("✅ Cache test passed!")
                    else:
                        st.error("❌ Cache test failed!")
        else:
            st.warning("🔌 Redis cache not connected")
            st.info("Configure Redis in secrets.toml to enable caching features")
    
    with tab4:
        st.markdown("### 🔧 System Tools")
        
        # API testing
        st.markdown("#### 🌐 API Performance Test")
        
        if st.button("🚀 Test Parallel API Calls"):
            with st.spinner("Testing API performance..."):
                test_apis = [
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                ]
                
                start_time = time.time()
                results = run_parallel_api_calls(test_apis)
                end_time = time.time()
                
                successful = len([r for r in results if r.get("status") != "error"])
                
                st.success(f"✅ API test completed in {end_time - start_time:.2f}s")
                st.info(f"Successful requests: {successful}/{len(test_apis)}")
        
        # Performance test runner
        st.markdown("#### 🏃‍♂️ Performance Test Suite")
        
        if st.button("🧪 Run Performance Tests"):
            with st.spinner("Running performance tests..."):
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python", "scripts/performance_test.py"],
                        cwd=project_root,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Performance tests completed!")
                        
                        # Try to load results
                        results_file = project_root / "performance_test_results.json"
                        if results_file.exists():
                            with open(results_file, 'r') as f:
                                test_results = json.load(f)
                            
                            summary = test_results.get("summary", {})
                            st.metric("Performance Score", f"{summary.get('performance_score', 0)}/100")
                            st.metric("Successful Tests", summary.get('successful_tests', 0))
                            st.metric("Failed Tests", summary.get('failed_tests', 0))
                            
                            with st.expander("📋 Detailed Results"):
                                st.json(test_results)
                    else:
                        st.error(f"❌ Performance tests failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    st.error("⏰ Performance tests timed out")
                except Exception as e:
                    st.error(f"❌ Error running tests: {e}")
        
        # System information
        st.markdown("#### 💻 System Information")
        
        import platform
        import psutil
        
        system_info = {
            "Platform": platform.platform(),
            "Python Version": platform.python_version(),
            "CPU Count": psutil.cpu_count(),
            "Total Memory": f"{psutil.virtual_memory().total / 1024**3:.1f} GB",
            "Available Memory": f"{psutil.virtual_memory().available / 1024**3:.1f} GB",
            "Disk Usage": f"{psutil.disk_usage('/').percent:.1f}%"
        }
        
        st.json(system_info)
    
    with tab5:
        st.markdown("### 📊 Performance Analytics")
        
        # Performance recommendations
        st.markdown("#### 💡 Recommendations")
        
        recommendations = []
        
        if memory_usage['rss_mb'] > 400:
            recommendations.append("🔴 High memory usage detected. Consider clearing caches or restarting the app.")
        
        if cache_manager and not cache_manager.is_connected():
            recommendations.append("🟡 Redis cache not connected. Enable caching for better performance.")
        
        if not recommendations:
            recommendations.append("✅ System performance is optimal!")
        
        for rec in recommendations:
            st.info(rec)
        
        # Performance trends
        st.markdown("#### 📈 Performance Trends")
        
        if len(st.session_state.get("performance_history", [])) > 5:
            df_history = pd.DataFrame(st.session_state.performance_history)
            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
            
            # Calculate trends
            recent_memory = df_history.tail(10)['memory_mb'].mean()
            older_memory = df_history.head(10)['memory_mb'].mean()
            
            memory_trend = "📈 Increasing" if recent_memory > older_memory else "📉 Decreasing"
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Memory Trend", memory_trend, f"{recent_memory - older_memory:.1f}MB")
            
            with col2:
                st.metric("Data Points", len(df_history), "Historical records")
        else:
            st.info("Collecting performance data... Check back in a few minutes for trends.")
    
    # Auto-refresh option
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()