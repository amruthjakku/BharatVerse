#!/usr/bin/env python3
"""
Simple test for community features without database initialization
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_community_imports():
    """Test that community modules can be imported"""
    try:
        print("Testing community service import...")
        # Test that the file can be compiled without importing database
        with open('core/community_service.py', 'r') as f:
            content = f.read()
            compile(content, 'core/community_service.py', 'exec')
        print("✅ CommunityService syntax is valid")
        
        print("Testing community styling import...")
        from streamlit_app.utils.community_styling import apply_community_styling
        print("✅ Community styling imported successfully")
        
        print("Testing community module import...")
        # We can't fully test this without streamlit running, but we can check syntax
        with open('streamlit_app/community_module.py', 'r') as f:
            content = f.read()
            compile(content, 'streamlit_app/community_module.py', 'exec')
        print("✅ Community module syntax is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_database_schema():
    """Test that database schema is properly defined"""
    try:
        print("Testing database schema...")
        with open('docker/init-db.sql', 'r') as f:
            schema = f.read()
        
        # Check for key community tables
        required_tables = [
            'community_groups',
            'group_memberships', 
            'discussion_topics',
            'discussion_replies',
            'chat_messages',
            'message_reactions',
            'user_profiles',
            'community_challenges',
            'challenge_participations',
            'activity_feed'
        ]
        
        for table in required_tables:
            if f"CREATE TABLE IF NOT EXISTS {table}" in schema:
                print(f"✅ Table {table} defined")
            else:
                print(f"❌ Table {table} missing")
                return False
        
        print("✅ All required tables are defined in schema")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    try:
        print("Testing file structure...")
        
        required_files = [
            'core/community_service.py',
            'streamlit_app/community_module.py',
            'streamlit_app/utils/community_styling.py',
            'docker/init-db.sql',
            'COMMUNITY_FEATURES.md'
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        print("✅ All required files exist")
        return True
        
    except Exception as e:
        print(f"❌ File structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤝 BharatVerse Community Features Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Database Schema", test_database_schema),
        ("Module Imports", test_community_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test...")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Community features are ready to use.")
        print("\nNext steps:")
        print("1. Start the database: docker-compose -f docker-compose-db.yml up -d")
        print("2. Start the application: streamlit run Home.py")
        print("3. Navigate to the Community page")
        print("4. Log in and start using community features!")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)