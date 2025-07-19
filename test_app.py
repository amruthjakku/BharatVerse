#!/usr/bin/env python3
"""
Quick test to verify the application is working
"""

import os
import sys
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

def test_database():
    """Test database connection and data"""
    print("🔍 Testing database...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "bharatverse"),
            user=os.getenv("POSTGRES_USER", "bharatverse_user"),
            password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test community groups
            cursor.execute("SELECT COUNT(*) as count FROM community_groups")
            groups_count = cursor.fetchone()['count']
            print(f"✅ Community groups: {groups_count}")
            
            # Test challenges
            cursor.execute("SELECT COUNT(*) as count FROM community_challenges")
            challenges_count = cursor.fetchone()['count']
            print(f"✅ Community challenges: {challenges_count}")
            
            # Show sample groups
            cursor.execute("SELECT name, group_type, group_category FROM community_groups LIMIT 3")
            groups = cursor.fetchall()
            print("📋 Sample groups:")
            for group in groups:
                print(f"   - {group['name']} ({group['group_type']}: {group['group_category']})")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api():
    """Test API endpoints"""
    print("\n🔍 Testing API...")
    try:
        # Test search endpoint
        response = requests.post("http://localhost:8000/api/v1/search", 
                               json={"query": "bengali", "limit": 5}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search API: {data['total']} results found")
            return True
        else:
            print(f"❌ Search API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_data_handler():
    """Test data handler"""
    print("\n🔍 Testing data handler...")
    try:
        sys.path.append('/Users/jakkuamruth/Documents/hackathon/bharatverse')
        from streamlit_app.utils.data_handler import get_contributions
        
        contributions = get_contributions()
        print(f"✅ Data handler: {len(contributions)} contributions retrieved")
        return True
    except Exception as e:
        print(f"❌ Data handler test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BharatVerse Application Test")
    print("=" * 40)
    
    tests = [test_database, test_api, test_data_handler]
    passed = sum(1 for test in tests if test())
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All systems working! You can now:")
        print("1. 🌐 Access Streamlit app: http://localhost:8501")
        print("2. 🏠 View Community page to see groups")
        print("3. 🛠️ Use Community Admin page to manage data")
        print("4. 🔍 Search for content")
        print("5. ➕ Add your own content and groups")
    else:
        print("\n⚠️ Some issues remain. Check the errors above.")