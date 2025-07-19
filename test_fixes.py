#!/usr/bin/env python3
"""
Test script to verify all the fixes for BharatVerse issues
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🔍 Testing database connection...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "bharatverse"),
            user=os.getenv("POSTGRES_USER", "bharatverse_user"),
            password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test community_groups table
            cursor.execute("SELECT COUNT(*) as count FROM community_groups")
            groups_count = cursor.fetchone()['count']
            print(f"✅ Community groups table: {groups_count} groups found")
            
            # Test content_metadata table
            cursor.execute("SELECT COUNT(*) as count FROM content_metadata")
            content_count = cursor.fetchone()['count']
            print(f"✅ Content metadata table: {content_count} content items found")
            
            # Test users table
            cursor.execute("SELECT COUNT(*) as count FROM users")
            users_count = cursor.fetchone()['count']
            print(f"✅ Users table: {users_count} users found")
        
        conn.close()
        print("✅ Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_api_connection():
    """Test API server connection"""
    print("\n🔍 Testing API server connection...")
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API root endpoint: {data['message']}")
        else:
            print(f"❌ API root endpoint failed: {response.status_code}")
            return False
        
        # Test search endpoint
        search_data = {
            "query": "bengali",
            "content_types": [],
            "languages": [],
            "regions": [],
            "limit": 5
        }
        response = requests.post("http://localhost:8000/api/v1/search", json=search_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint: Found {data['total']} results")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return False
        
        print("✅ API connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        return False

def test_data_handler():
    """Test data handler functionality"""
    print("\n🔍 Testing data handler...")
    try:
        from streamlit_app.utils.data_handler import get_contributions
        
        contributions = get_contributions()
        print(f"✅ Data handler: Retrieved {len(contributions)} contributions")
        
        if contributions:
            sample = contributions[0]
            print(f"✅ Sample contribution: {sample['title']} ({sample['type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Data handler test failed: {e}")
        return False

def test_community_service():
    """Test community service functionality"""
    print("\n🔍 Testing community service...")
    try:
        from core.database import DatabaseManager
        from core.community_service import CommunityService
        
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        # Test getting groups
        groups = community_service.get_all_groups()
        print(f"✅ Community service: Retrieved {len(groups)} groups")
        
        # Test getting challenges
        challenges = community_service.get_active_challenges()
        print(f"✅ Community service: Retrieved {len(challenges)} active challenges")
        
        return True
        
    except Exception as e:
        print(f"❌ Community service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 BharatVerse Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_api_connection,
        test_data_handler,
        test_community_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        print("\n📋 Summary of fixes applied:")
        print("✅ Created missing community tables in PostgreSQL")
        print("✅ Fixed data handler to use PostgreSQL instead of SQLite")
        print("✅ Started API server on port 8000")
        print("✅ Added sample community groups and challenges")
        print("✅ Added sample content for testing")
        print("✅ Created community admin interface")
        
        print("\n🎯 Next steps:")
        print("1. Access the Streamlit app at http://localhost:8501")
        print("2. Go to Community page to see the groups")
        print("3. Go to Community Admin page to manage groups and challenges")
        print("4. Use the Search page to find content")
        print("5. Add your own content through the various modules")
        
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    main()