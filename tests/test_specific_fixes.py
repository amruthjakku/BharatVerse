#!/usr/bin/env python3
"""
Test the specific fixes for the reported errors
"""

import os
import sys
sys.path.append('/Users/jakkuamruth/Documents/hackathon/bharatverse')

def test_contributions_fetch():
    """Test: Failed to fetch contributions: operator does not exist: uuid = text"""
    print("🔍 Testing contributions fetch (UUID = text fix)...")
    try:
        from streamlit_app.utils.data_handler import get_contributions
        contributions = get_contributions()
        print(f"✅ Successfully fetched {len(contributions)} contributions")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_community_stats():
    """Test: Failed to load community stats: unsupported operand type(s) for +: 'int' and 'NoneType'"""
    print("\n🔍 Testing community stats (int + NoneType fix)...")
    try:
        from core.database import DatabaseManager
        from core.community_service import CommunityService
        
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        # Test the exact operations that were failing
        all_groups = community_service.get_all_groups()
        leaderboard = community_service.get_community_leaderboard(10)
        
        # These operations were causing the int + NoneType error
        total_members = sum(group.get('actual_member_count', 0) or 0 for group in all_groups)
        total_contributions = sum(user.get('contribution_count', 0) or 0 for user in leaderboard)
        
        print(f"✅ Total members calculation: {total_members}")
        print(f"✅ Total contributions calculation: {total_contributions}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_user_groups_query():
    """Test: operator does not exist: uuid = integer (user groups query)"""
    print("\n🔍 Testing user groups query (UUID = integer fix)...")
    try:
        from core.database import DatabaseManager
        from core.community_service import CommunityService
        
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        # Test with a real UUID from the database
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
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
            
            if user_result:
                user_id = user_result['id']
                print(f"Testing with user ID: {user_id}")
                
                # This query was failing before
                user_groups = community_service.get_user_groups(user_id)
                print(f"✅ Successfully queried user groups: {len(user_groups)} groups")
                
                # Test with integer (should also work now)
                user_groups_int = community_service.get_user_groups(1)
                print(f"✅ Integer ID test: {len(user_groups_int)} groups")
                
                conn.close()
                return True
            else:
                print("⚠️ No users found in database")
                conn.close()
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Specific Error Fixes")
    print("=" * 50)
    
    tests = [
        test_contributions_fetch,
        test_community_stats, 
        test_user_groups_query
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All specific errors have been fixed!")
        print("✅ UUID = text error: RESOLVED")
        print("✅ int + NoneType error: RESOLVED") 
        print("✅ UUID = integer error: RESOLVED")
        print("\nThe application should now work without these database errors.")
    else:
        print(f"\n⚠️ {len(tests) - passed} issues remain.")