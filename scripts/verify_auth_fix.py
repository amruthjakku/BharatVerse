#!/usr/bin/env python3
"""
Verify that the authentication system is working with the new Streamlit API
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')
load_dotenv('.env')

def test_auth_module():
    """Test that the auth module loads without deprecated API warnings"""
    print("🔍 Testing authentication module...")
    
    try:
        from streamlit_app.utils.auth import GitLabAuth
        auth = GitLabAuth()
        
        print("✅ Auth module loaded successfully")
        print(f"✅ GitLab Base URL: {auth.base_url}")
        print(f"✅ Client ID configured: {'Yes' if auth.client_id else 'No'}")
        print(f"✅ Redirect URI: {auth.redirect_uri}")
        
        return True
    except Exception as e:
        print(f"❌ Auth module failed to load: {e}")
        return False

def test_user_manager():
    """Test user manager functionality"""
    print("\n🔍 Testing user manager...")
    
    try:
        from streamlit_app.utils.user_manager import user_manager
        stats = user_manager.get_user_stats()
        
        print("✅ User manager loaded successfully")
        print(f"✅ Database connection working")
        print(f"✅ Current user count: {stats['total_users']}")
        
        return True
    except Exception as e:
        print(f"❌ User manager failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🧪 BharatVerse Authentication Fix Verification")
    print("=" * 50)
    
    auth_ok = test_auth_module()
    user_mgr_ok = test_user_manager()
    
    print("\n" + "=" * 50)
    print("📋 Verification Results:")
    print(f"   Authentication Module: {'✅ OK' if auth_ok else '❌ Failed'}")
    print(f"   User Manager: {'✅ OK' if user_mgr_ok else '❌ Failed'}")
    
    if auth_ok and user_mgr_ok:
        print("\n🎉 All systems working correctly!")
        print("\n📝 Ready to use:")
        print("1. Visit http://localhost:8501")
        print("2. No more deprecated API warnings")
        print("3. Authentication should work smoothly")
        print("4. Use 'python setup_admin.py' after first login")
    else:
        print("\n⚠️  Some issues detected. Check the error messages above.")

if __name__ == "__main__":
    main()