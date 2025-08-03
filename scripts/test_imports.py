#!/usr/bin/env python3
"""
Test script to check import issues
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_imports():
    print("🧪 Testing imports...")
    
    # Test utils imports
    print("\n1. Testing utils package...")
    try:
        from utils import get_performance_optimizer, get_cache_manager, get_memory_manager
        print("✅ Utils package imports successful")
        
        # Test lazy loading
        perf_opt = get_performance_optimizer()
        print(f"✅ Performance optimizer: {type(perf_opt)}")
        
        cache_mgr = get_cache_manager()
        print(f"✅ Cache manager: {type(cache_mgr)}")
        
        mem_mgr = get_memory_manager()
        print(f"✅ Memory manager: {type(mem_mgr)}")
        
    except Exception as e:
        print(f"❌ Utils package error: {e}")
    
    # Test auth imports
    print("\n2. Testing auth module...")
    try:
        from streamlit_app.utils.auth import get_auth_manager, GitLabAuth
        print("✅ Auth module imports successful")
        
        auth_mgr = get_auth_manager()
        print(f"✅ Auth manager: {type(auth_mgr)}")
        
    except Exception as e:
        print(f"❌ Auth module error: {e}")
    
    # Test performance optimizer
    print("\n3. Testing performance optimizer...")
    try:
        from utils.performance_optimizer import get_performance_optimizer
        perf_opt = get_performance_optimizer()
        print(f"✅ Performance optimizer direct import: {type(perf_opt)}")
    except Exception as e:
        print(f"❌ Performance optimizer error: {e}")
    
    # Test supabase
    print("\n4. Testing supabase...")
    try:
        from utils.supabase_db import get_database_manager
        db_mgr = get_database_manager()
        print(f"✅ Database manager: {type(db_mgr)}")
    except Exception as e:
        print(f"❌ Database manager error: {e}")
    
    print("\n✅ Import test completed!")

if __name__ == "__main__":
    test_imports()