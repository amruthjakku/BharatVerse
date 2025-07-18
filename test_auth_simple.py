#!/usr/bin/env python3
"""
Simple test script to verify authentication system is working
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

from streamlit_app.utils.user_manager import user_manager
from streamlit_app.utils.auth import GitLabAuth

def test_database():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        stats = user_manager.get_user_stats()
        print(f"✅ Database connected successfully!")
        print(f"📊 Current stats: {stats}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_oauth_config():
    """Test OAuth configuration"""
    print("\n🔍 Testing OAuth configuration...")
    
    auth = GitLabAuth()
    
    config_items = [
        ("Client ID", auth.client_id),
        ("Client Secret", auth.client_secret),
        ("Redirect URI", auth.redirect_uri),
        ("Base URL", auth.base_url),
        ("Scopes", auth.scopes)
    ]
    
    all_configured = True
    
    for name, value in config_items:
        if value:
            print(f"✅ {name}: {'*' * 20 if 'secret' in name.lower() else value}")
        else:
            print(f"❌ {name}: Not configured")
            all_configured = False
    
    if all_configured:
        print("✅ OAuth configuration complete!")
        
        # Test authorization URL generation
        try:
            auth_url = auth.get_authorization_url()
            print(f"✅ Authorization URL generated successfully")
            print(f"🔗 URL: {auth_url[:100]}...")
        except Exception as e:
            print(f"❌ Failed to generate authorization URL: {e}")
            all_configured = False
    
    return all_configured

def main():
    """Main test function"""
    print("🧪 BharatVerse Authentication System Test")
    print("=" * 50)
    
    # Test database
    db_ok = test_database()
    
    # Test OAuth config
    oauth_ok = test_oauth_config()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Database: {'✅ OK' if db_ok else '❌ Failed'}")
    print(f"   OAuth Config: {'✅ OK' if oauth_ok else '❌ Failed'}")
    
    if db_ok and oauth_ok:
        print("\n🎉 All systems ready!")
        print("\n📝 Next steps:")
        print("1. Visit http://localhost:8501")
        print("2. Click 'Login with GitLab' in the sidebar")
        print("3. Authorize the application")
        print("4. Run 'python setup_admin.py' to make yourself admin")
    else:
        print("\n⚠️  Some issues need to be resolved before using the system.")

if __name__ == "__main__":
    main()