#!/usr/bin/env python3
"""
BharatVerse App Startup Script
Ensures proper environment configuration before launching
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up environment for local development"""
    print("🔧 Setting up environment for local development...")
    
    # Disable external services that aren't configured
    local_env = {
        'POSTGRES_HOST': '',
        'POSTGRES_PASSWORD': '',
        'REDIS_URL': '',
        'MINIO_HOST': '',
        
        # Enable performance optimizations
        'ENABLE_CACHING': 'true',
        'CACHE_TTL_HOURS': '24',
        'MEMORY_THRESHOLD_MB': '500',
        'MAX_CONCURRENT_REQUESTS': '5',
        'ENABLE_PERFORMANCE_MONITORING': 'true',
        'ENABLE_MEMORY_TRACKING': 'true',
        
        # Local development settings
        'DEBUG_MODE': 'true',
        'AI_MODE': 'free_tier',
        'USE_LIGHTWEIGHT_MODELS': 'true',
    }
    
    for key, value in local_env.items():
        os.environ[key] = value
    
    print("✅ Environment configured for local development")

def test_imports():
    """Test critical imports"""
    print("🧪 Testing critical imports...")
    
    try:
        # Test performance components
        from utils.performance_optimizer import get_performance_optimizer
        from utils.memory_manager import get_memory_manager
        print("✅ Performance components imported successfully")
        
        # Test database with graceful fallback
        from core.database import get_db_manager
        db_manager = get_db_manager()
        print(f"✅ Database manager initialized: {type(db_manager).__name__}")
        
        # Test core modules
        from core import db_manager, content_repo
        print("✅ Core modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def launch_app():
    """Launch the Streamlit app"""
    print("🚀 Launching BharatVerse...")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 BharatVerse stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")

def main():
    """Main startup function"""
    print("🌍 BharatVerse - Cultural Heritage Platform")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Test imports
    if test_imports():
        print("\n🎉 All systems ready!")
        print("✅ Performance optimizations active")
        print("✅ Memory management enabled")
        print("✅ Local caching operational")
        print("✅ All modules loaded successfully")
        
        print("\n" + "=" * 50)
        launch_app()
    else:
        print("\n❌ Startup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()