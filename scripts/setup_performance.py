#!/usr/bin/env python3
"""
Performance Setup Script for BharatVerse
Automatically configures and validates performance optimizations
"""

import os
import sys
import subprocess
from pathlib import Path
import json
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def check_dependencies():
    """Check if performance dependencies are installed"""
    print_step("1", "Checking Performance Dependencies")
    
    required_packages = [
        'aiohttp',
        'aiofiles', 
        'psutil',
        'redis',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def setup_environment():
    """Set up environment variables for immediate benefits"""
    print_step("2", "Setting Up Environment Variables")
    
    # Set performance environment variables
    performance_env = {
        'ENABLE_CACHING': 'true',
        'CACHE_TTL_HOURS': '24',
        'MEMORY_THRESHOLD_MB': '500',
        'MAX_CONCURRENT_REQUESTS': '5',
        'ENABLE_PERFORMANCE_MONITORING': 'true'
    }
    
    for key, value in performance_env.items():
        os.environ[key] = value
        print(f"✅ Set {key}={value}")
    
    print("✅ Environment variables configured for immediate performance benefits!")

def test_performance_components():
    """Test performance components"""
    print_step("3", "Testing Performance Components")
    
    try:
        # Test performance optimizer
        from utils.performance_optimizer import get_performance_optimizer
        optimizer = get_performance_optimizer()
        print("✅ Performance Optimizer - working")
        
        # Test memory manager
        from utils.memory_manager import get_memory_manager
        memory_manager = get_memory_manager()
        memory_usage = memory_manager.get_memory_usage()
        print(f"✅ Memory Manager - working (Current: {memory_usage['rss_mb']:.1f}MB)")
        
        # Test cache manager (may fail if Redis not configured)
        from utils.redis_cache import get_cache_manager
        cache_manager = get_cache_manager()
        if cache_manager and cache_manager.is_connected():
            print("✅ Redis Cache - connected")
        else:
            print("⚠️ Redis Cache - not connected (configure Redis for full benefits)")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance component test failed: {e}")
        return False

def create_performance_config():
    """Create performance configuration file"""
    print_step("4", "Creating Performance Configuration")
    
    config = {
        "performance": {
            "caching": {
                "enabled": True,
                "ttl_hours": 24,
                "memory_threshold_mb": 500
            },
            "parallel_processing": {
                "max_workers": 4,
                "max_concurrent_requests": 5
            },
            "monitoring": {
                "enabled": True,
                "memory_tracking": True,
                "performance_metrics": True
            }
        },
        "setup_timestamp": time.time(),
        "setup_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    config_file = project_root / "performance_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Performance configuration saved to: {config_file}")

def run_quick_performance_test():
    """Run a quick performance test"""
    print_step("5", "Running Quick Performance Test")
    
    try:
        # Test memory tracking
        from utils.memory_manager import MemoryTracker
        
        with MemoryTracker("setup_test") as tracker:
            # Simulate some work
            data = [i for i in range(10000)]
            processed = [x * 2 for x in data]
            del data, processed
        
        memory_delta = tracker.get_memory_delta()
        print(f"✅ Memory tracking test - Memory delta: {memory_delta:.1f}MB")
        
        # Test caching
        import streamlit as st
        
        @st.cache_data(ttl=60, show_spinner=False)
        def test_cached_function():
            return "cached_result"
        
        result = test_cached_function()
        print(f"✅ Caching test - Result: {result}")
        
        # Test parallel processing
        from utils.async_client import ParallelProcessor
        
        def simple_task(x):
            return x * 2
        
        with ParallelProcessor(max_workers=2) as processor:
            results = processor.parallel_execute(simple_task, [1, 2, 3, 4])
        
        print(f"✅ Parallel processing test - Results: {results}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick performance test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for full optimization"""
    print_step("6", "Next Steps for Full Optimization")
    
    print("🎯 IMMEDIATE BENEFITS ACTIVE:")
    print("   ✅ Streamlit caching enabled")
    print("   ✅ Memory monitoring active") 
    print("   ✅ Performance tracking enabled")
    print("   ✅ Parallel processing ready")
    
    print("\n🚀 FOR FULL BENEFITS, CONFIGURE:")
    print("   1. Redis Cache:")
    print("      export REDIS_URL='redis://your-redis-instance'")
    print("      # Or add to .streamlit/secrets.toml")
    
    print("\n   2. Supabase Database:")
    print("      export POSTGRES_HOST='your-supabase-host'")
    print("      export POSTGRES_PASSWORD='your-password'")
    print("      # Or add to .streamlit/secrets.toml")
    
    print("\n📊 MONITORING:")
    print("   • Access Performance Dashboard: http://localhost:8501/Performance")
    print("   • Run performance tests: python scripts/performance_test.py")
    print("   • Monitor memory: Check admin panel in the app")
    
    print("\n🔧 CONFIGURATION FILES:")
    print("   • Environment: .env.example (copy to .env)")
    print("   • Streamlit: .streamlit/secrets.toml")
    print("   • Performance: performance_config.json")

def main():
    """Main setup function"""
    print_header("BharatVerse Performance Setup")
    print("Setting up performance optimizations for immediate benefits...")
    
    success_steps = 0
    total_steps = 5
    
    # Step 1: Check dependencies
    if check_dependencies():
        success_steps += 1
    
    # Step 2: Setup environment
    setup_environment()
    success_steps += 1
    
    # Step 3: Test components
    if test_performance_components():
        success_steps += 1
    
    # Step 4: Create config
    create_performance_config()
    success_steps += 1
    
    # Step 5: Quick test
    if run_quick_performance_test():
        success_steps += 1
    
    # Show results
    print_header("Setup Complete!")
    print(f"✅ Successfully completed {success_steps}/{total_steps} setup steps")
    
    if success_steps == total_steps:
        print("🎉 PERFORMANCE OPTIMIZATIONS ARE ACTIVE!")
        print("   Your BharatVerse app now has immediate performance benefits.")
    elif success_steps >= 3:
        print("⚠️ PARTIAL SETUP COMPLETE")
        print("   Basic optimizations are active. Check errors above for full benefits.")
    else:
        print("❌ SETUP INCOMPLETE")
        print("   Please resolve errors above and run setup again.")
    
    show_next_steps()
    
    print("\n" + "="*60)
    print("🚀 Ready to launch with performance optimizations!")
    print("   Run: streamlit run Home.py")
    print("="*60)

if __name__ == "__main__":
    main()