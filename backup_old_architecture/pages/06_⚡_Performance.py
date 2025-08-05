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
try:
    from utils.redis_cache import get_cache_manager
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from utils.async_client import run_parallel_api_calls
    ASYNC_CLIENT_AVAILABLE = True
except ImportError:
    ASYNC_CLIENT_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="Performance Dashboard - BharatVerse",
        page_icon="⚡",
        layout="wide"
    )
    
    st.markdown("# ⚡ Performance Dashboard")
    st.markdown("Monitor and optimize BharatVerse performance in real-time")
    
    # Check admin access
    from streamlit_app.utils.auth import get_auth_manager
    auth = get_auth_manager()
    
    if not auth.is_authenticated():
        st.error("🔒 Please login to access the Performance dashboard")
        from streamlit_app.utils.auth import render_login_button
        render_login_button()
        return
    
    if not auth.is_admin():
        st.error("🚫 **Admin Access Required**")
        st.warning("Performance monitoring is restricted to administrators only.")
        
        user_info = auth.get_current_user()
        if user_info:
            st.info(f"👤 Logged in as: **{user_info.get('name', 'Unknown')}**")
            st.markdown("Contact an administrator if you need access to performance monitoring.")
        
        # Show available pages for regular users
        st.markdown("### 📋 Available Pages:")
        st.markdown("- 🎤 **Audio Capture** - Record and contribute audio")
        st.markdown("- 📝 **Text Stories** - Share cultural stories")
        st.markdown("- 🖼️ **Visual Heritage** - Upload cultural images")
        st.markdown("- 📊 **Analytics** - View your contributions")
        return
    
    # Initialize performance components
    optimizer = get_performance_optimizer()
    memory_manager = get_memory_manager()
    
    # Initialize cache manager conditionally
    if REDIS_AVAILABLE:
        cache_manager = get_cache_manager()
    else:
        cache_manager = None
    
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Performance Metrics", 
        "💾 Memory Management", 
        "🗄️ Cache Management", 
        "🧵 Threading Monitor",
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
        st.markdown("### 🧵 Threading Monitor")
        
        try:
            from utils.threading_manager import get_threading_manager, get_threading_metrics
            
            # Threading manager status
            manager = get_threading_manager()
            metrics = get_threading_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Max Workers", manager.max_workers)
            
            with col2:
                active_tasks = manager.get_active_tasks()
                st.metric("Active Tasks", len(active_tasks))
            
            with col3:
                thread_metrics = metrics.get_metrics()
                st.metric("Completed Tasks", thread_metrics['completed_tasks'])
            
            with col4:
                st.metric("Failed Tasks", thread_metrics['failed_tasks'])
            
            # Active tasks details
            if active_tasks:
                st.markdown("#### 🔄 Active Tasks")
                for task_id, task_info in active_tasks.items():
                    with st.expander(f"Task: {task_info['name']}"):
                        st.write(f"**ID:** {task_id}")
                        st.write(f"**Running Time:** {task_info['running_time']:.2f}s")
                        st.write(f"**Status:** {'✅ Done' if task_info['done'] else '🔄 Running'}")
            
            # Threading performance metrics
            st.markdown("#### 📊 Threading Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                avg_time = thread_metrics['average_task_time']
                st.metric("Average Task Time", f"{avg_time:.3f}s")
                
                total_tasks = thread_metrics['total_tasks']
                st.metric("Total Tasks Processed", total_tasks)
            
            with col2:
                active_threads = thread_metrics['active_threads']
                st.metric("Active Threads", active_threads)
                
                if total_tasks > 0:
                    success_rate = (thread_metrics['completed_tasks'] / total_tasks) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Threading controls
            st.markdown("#### 🔧 Threading Controls")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🧪 Test Threading"):
                    import time
                    import random
                    
                    def test_task(task_id):
                        time.sleep(random.uniform(0.1, 0.5))
                        return f"Task {task_id} completed"
                    
                    # Submit test tasks
                    futures = []
                    for i in range(5):
                        future = manager.submit_task(test_task, i, task_name=f"test_task_{i}")
                        futures.append(future)
                    
                    # Wait for completion
                    results = manager.wait_for_completion(futures, timeout=10)
                    
                    st.success(f"✅ Threading test completed! {len([r for r in results if r])} tasks succeeded")
            
            with col2:
                if st.button("📊 Performance Benchmark"):
                    from utils.threading_manager import parallel_map
                    import time
                    
                    def benchmark_task(x):
                        # Simulate CPU-bound work
                        result = sum(i * i for i in range(x * 1000))
                        return result
                    
                    # Test data
                    test_data = list(range(1, 21))  # 20 tasks
                    
                    # Sequential execution
                    start_time = time.time()
                    sequential_results = [benchmark_task(x) for x in test_data]
                    sequential_time = time.time() - start_time
                    
                    # Parallel execution
                    start_time = time.time()
                    parallel_results = parallel_map(benchmark_task, test_data, max_workers=4)
                    parallel_time = time.time() - start_time
                    
                    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
                    
                    st.success(f"🚀 Benchmark completed!")
                    st.info(f"Sequential: {sequential_time:.2f}s")
                    st.info(f"Parallel: {parallel_time:.2f}s")
                    st.info(f"Speedup: {speedup:.2f}x")
            
            with col3:
                if st.button("🗑️ Clear Metrics"):
                    # Reset metrics
                    metrics.__init__()
                    st.success("Threading metrics cleared!")
                    st.rerun()
        
        except ImportError:
            st.warning("🔌 Threading manager not available")
            st.info("Threading utilities are not properly configured")
    
    with tab5:
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
                
                if ASYNC_CLIENT_AVAILABLE:
                    start_time = time.time()
                    results = run_parallel_api_calls(test_apis)
                    end_time = time.time()
                    
                    successful = len([r for r in results if r.get("status") != "error"])
                    
                    st.success(f"✅ API test completed in {end_time - start_time:.2f}s")
                    st.info(f"Successful requests: {successful}/{len(test_apis)}")
                else:
                    st.warning("⚠️ Async client not available. Install aiohttp to enable API testing.")
                    st.info("Run: `pip install aiohttp` to enable this feature.")
        
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