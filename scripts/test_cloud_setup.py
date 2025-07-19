#!/usr/bin/env python3
"""
Test script for BharatVerse Free Cloud Setup
Verifies that all cloud components are properly configured
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Imports...")
    
    try:
        from utils.r2 import get_storage_manager
        print("✅ R2 Storage utilities imported successfully")
    except Exception as e:
        print(f"❌ R2 Storage import failed: {e}")
        return False
    
    try:
        from utils.db import get_database_manager
        print("✅ Database utilities imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from utils.inference import get_inference_manager
        print("✅ Inference utilities imported successfully")
    except Exception as e:
        print(f"❌ Inference import failed: {e}")
        return False
    
    try:
        from utils.redis_cache import get_cache_manager
        print("✅ Redis cache utilities imported successfully")
    except Exception as e:
        print(f"❌ Redis cache import failed: {e}")
        return False
    
    try:
        from core.cloud_ai_manager import get_cloud_ai_manager
        print("✅ Cloud AI manager imported successfully")
    except Exception as e:
        print(f"❌ Cloud AI manager import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration files"""
    print("\n🔧 Testing Configuration...")
    
    required_files = [
        "streamlit_secrets_template.toml",
        ".streamlit/config.toml",
        "requirements_cloud.txt",
        "runtime.txt", 
        "packages.txt"
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_present = False
    
    return all_present

def test_secrets_template():
    """Test secrets template structure"""
    print("\n🔐 Testing Secrets Template...")
    
    try:
        import toml
        with open("streamlit_secrets_template.toml", 'r') as f:
            secrets = toml.load(f)
        
        required_sections = ['postgres', 'redis', 'r2', 'inference', 'auth', 'app']
        
        all_sections = True
        for section in required_sections:
            if section in secrets:
                print(f"✅ Found section: [{section}]")
            else:
                print(f"❌ Missing section: [{section}]")
                all_sections = False
        
        return all_sections
        
    except Exception as e:
        print(f"❌ Error reading secrets template: {e}")
        return False

def test_ai_manager():
    """Test AI manager initialization (without secrets)"""
    print("\n🤖 Testing AI Manager...")
    
    try:
        # This will fail without secrets, but should import correctly
        from core.cloud_ai_manager import CloudAIManager
        print("✅ CloudAIManager class available")
        
        # Test system status method exists
        manager = CloudAIManager()
        status = manager.get_system_status()
        print("✅ System status method works")
        print(f"   - Services: {list(status.get('services', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Manager test failed: {e}")
        return False

def show_deployment_summary():
    """Show deployment summary"""
    print("""
🎉 **Free Cloud Deployment Architecture**

┌─────────────────┐    ┌─────────────────┐
│  🧑‍💻 User        │───▶│  🌐 Streamlit   │
│                 │    │    Cloud        │
└─────────────────┘    └─────────┬───────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
    ┌───────────▼─────────────┐  │  ┌─────────────▼─────────────┐
    │ 🔮 Hugging Face API    │  │  │ ⚡ Upstash Redis Cache    │
    │ - Whisper (Audio)       │  │  │ - Session management      │
    │ - RoBERTa (Text)        │  │  │ - AI result caching       │
    │ - BLIP (Vision)         │  │  │ - Rate limiting           │
    │ - NLLB (Translation)    │  │  └───────────────────────────┘
    └─────────────────────────┘  │
                                 │
    ┌─────────────────────────┬──▼──┐ ┌─────────────────────────┐
    │ 🐘 Supabase PostgreSQL  │     │ │ 🪣 Cloudflare R2        │
    │ - User accounts         │     │ │ - File uploads          │
    │ - Content storage       │     │ │ - Media storage         │
    │ - Analytics data        │     │ │ - Static assets         │
    └─────────────────────────┴─────┘ └─────────────────────────┘

**💰 Total Monthly Cost: $0** (All free tiers)

**🚀 Deployment Command:**
1. Push to GitHub
2. Deploy via Streamlit Cloud
3. Configure secrets
4. Launch!
    """)

def main():
    """Main test function"""
    print("🏛️ BharatVerse Free Cloud Setup Test")
    print("=" * 50)
    
    # Run all tests
    tests_passed = 0
    total_tests = 4
    
    if test_imports():
        tests_passed += 1
    
    if test_configuration():
        tests_passed += 1
    
    if test_secrets_template():
        tests_passed += 1
    
    if test_ai_manager():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your setup is ready for cloud deployment.")
        show_deployment_summary()
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Run the setup script again: python scripts/setup_free_cloud.py")

if __name__ == "__main__":
    main()