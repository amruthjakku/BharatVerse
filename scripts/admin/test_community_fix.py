#!/usr/bin/env python3
"""
Test the community service with proper UUID handling
"""

import os
import sys
sys.path.append('/Users/jakkuamruth/Documents/hackathon/bharatverse')

from core.database import DatabaseManager
from core.community_service import CommunityService
import psycopg2
from psycopg2.extras import RealDictCursor

def test_community_with_real_user():
    """Test community service with a real user UUID"""
    
    # Get a real user ID from the database
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "bharatverse"),
        user=os.getenv("POSTGRES_USER", "bharatverse_user"),
        password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        
        if not user_result:
            print("❌ No users found in database")
            return False
        
        user_id = user_result['id']
        print(f"✅ Found user ID: {user_id} (type: {type(user_id)})")
    
    conn.close()
    
    # Test community service
    try:
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        # Test getting all groups
        print("\n🔍 Testing get_all_groups...")
        groups = community_service.get_all_groups()
        print(f"✅ Found {len(groups)} groups")
        
        # Test getting user groups (should work now)
        print(f"\n🔍 Testing get_user_groups with UUID: {user_id}")
        user_groups = community_service.get_user_groups(user_id)
        print(f"✅ User has {len(user_groups)} group memberships")
        
        # Test with integer (this should fail)
        print(f"\n🔍 Testing get_user_groups with integer: 1")
        try:
            user_groups_int = community_service.get_user_groups(1)
            print(f"✅ Integer test worked: {len(user_groups_int)} memberships")
        except Exception as e:
            print(f"❌ Integer test failed (expected): {e}")
        
        # Test joining a group
        if groups:
            group_id = groups[0]['id']
            print(f"\n🔍 Testing join_group with group: {group_id}")
            result = community_service.join_group(user_id, group_id)
            print(f"✅ Join group result: {result}")
            
            # Check if user is now in the group
            user_groups_after = community_service.get_user_groups(user_id)
            print(f"✅ User now has {len(user_groups_after)} group memberships")
        
        return True
        
    except Exception as e:
        print(f"❌ Community service test failed: {e}")
        return False

def test_with_string_conversion():
    """Test the string conversion fix"""
    
    # Get a real user ID
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "bharatverse"),
        user=os.getenv("POSTGRES_USER", "bharatverse_user"),
        password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        user_id = user_result['id']
    
    conn.close()
    
    # Test community service with different input types
    try:
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        print(f"\n🔍 Testing with UUID string: {user_id}")
        groups1 = community_service.get_user_groups(user_id)
        print(f"✅ UUID string: {len(groups1)} groups")
        
        print(f"\n🔍 Testing with integer: 1")
        groups2 = community_service.get_user_groups(1)
        print(f"✅ Integer: {len(groups2)} groups")
        
        print(f"\n🔍 Testing with string '1'")
        groups3 = community_service.get_user_groups("1")
        print(f"✅ String '1': {len(groups3)} groups")
        
        return True
        
    except Exception as e:
        print(f"❌ String conversion test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Community Service UUID Handling")
    print("=" * 50)
    
    test1 = test_community_with_real_user()
    test2 = test_with_string_conversion()
    
    if test1 and test2:
        print("\n🎉 All tests passed! Community service is working correctly.")
    else:
        print("\n⚠️ Some tests failed.")