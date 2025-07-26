#!/usr/bin/env python3
"""
Verify Supabase Setup for BharatVerse
Run this after executing the SQL script in Supabase dashboard
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def verify_supabase_setup():
    """Verify that Supabase is properly set up"""
    try:
        print("🔍 Verifying Supabase setup...")
        
        # Test the database manager
        from utils.supabase_db import get_database_manager
        
        db = get_database_manager()
        print("✅ Database manager initialized")
        
        # Test fetching contributions
        contributions = db.get_contributions(limit=10)
        print(f"✅ Found {len(contributions)} contributions")
        
        if contributions:
            print("\n📋 Sample contributions:")
            for contrib in contributions[:3]:
                title = contrib.get('title', 'Untitled')[:50]
                content_type = contrib.get('content_type', 'unknown')
                language = contrib.get('language', 'unknown')
                print(f"  - {title} ({content_type}, {language})")
        
        # Test creating a user (if not exists)
        try:
            user_id = db.create_user(
                username="test_user_" + str(hash("test") % 1000),
                email=f"test{hash('test') % 1000}@bharatverse.com",
                full_name="Test User"
            )
            if user_id:
                print(f"✅ Test user created with ID: {user_id}")
            else:
                print("ℹ️ User creation test skipped (may already exist)")
        except Exception as e:
            print(f"⚠️ User creation test failed: {e}")
        
        print("\n🎉 Supabase setup verification complete!")
        print("\n🚀 Your app is ready to:")
        print("  - Store text contributions in Supabase")
        print("  - Display contributions from cloud database")
        print("  - Track user analytics")
        print("  - Enable community interactions")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you executed the SQL script in Supabase dashboard")
        print("2. Check your secrets.toml configuration")
        print("3. Verify your Supabase project is active")
        return False

def test_text_operations():
    """Test text-specific operations"""
    try:
        print("\n📝 Testing text operations...")
        
        from streamlit_app.text_module import store_text_to_supabase
        
        # This would normally be called from Streamlit
        # Just test that the function exists and can be imported
        print("✅ Text storage functions available")
        
        from utils.supabase_db import get_database_manager
        db = get_database_manager()
        
        # Test fetching text contributions specifically
        contributions = db.get_contributions(limit=100)
        text_contribs = [c for c in contributions if c.get('content_type') in ['text', 'proverb']]
        
        print(f"✅ Found {len(text_contribs)} text/proverb contributions")
        
        if text_contribs:
            print("\n📚 Text contributions:")
            for contrib in text_contribs[:3]:
                title = contrib.get('title', 'Untitled')[:40]
                content_type = contrib.get('content_type', 'unknown')
                language = contrib.get('language', 'unknown')
                print(f"  - {title} ({content_type}, {language})")
        
        return True
        
    except Exception as e:
        print(f"❌ Text operations test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 BharatVerse Supabase Verification")
    print("=" * 50)
    
    # Basic setup verification
    if verify_supabase_setup():
        # Text operations verification
        test_text_operations()
        
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Run your Streamlit app: streamlit run BharatVerse.py")
        print("2. Login with GitLab")
        print("3. Go to 'Story Keeper' page")
        print("4. Submit a text story or proverb")
        print("5. Check 'Browse Contributions' to see it stored in Supabase")
        print("6. View 'Analytics' to see real-time data")
        
    else:
        print("\n❌ Setup incomplete. Please:")
        print("1. Execute the SQL script in your Supabase dashboard")
        print("2. Check your database connection")
        print("3. Run this verification again")

if __name__ == "__main__":
    main()