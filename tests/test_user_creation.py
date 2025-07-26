#!/usr/bin/env python3
"""
Test user creation in both SQLite and PostgreSQL
"""

import os
import sys
sys.path.append('/Users/jakkuamruth/Documents/hackathon/bharatverse')

from streamlit_app.utils.user_manager import UserManager

def test_user_creation():
    """Test creating a user in both databases"""
    
    # Sample GitLab user data
    gitlab_user_data = {
        'id': 12345,
        'username': 'testuser123',
        'email': 'testuser123@example.com',
        'name': 'Test User 123',
        'avatar_url': 'https://example.com/avatar.jpg',
        'bio': 'Test user for BharatVerse',
        'location': 'Test City'
    }
    
    print("🚀 Testing User Creation")
    print("=" * 40)
    
    try:
        # Create user manager
        user_manager = UserManager()
        
        # Create or update user
        print("🔍 Creating user in both databases...")
        user_data = user_manager.create_or_update_user(gitlab_user_data)
        
        print(f"✅ User created successfully!")
        print(f"   SQLite ID: {user_data.get('id')}")
        print(f"   PostgreSQL ID: {user_data.get('postgres_id')}")
        print(f"   Username: {user_data.get('username')}")
        print(f"   Email: {user_data.get('email')}")
        
        # Test community service with this user
        if user_data.get('postgres_id'):
            print(f"\n🔍 Testing community service with PostgreSQL ID...")
            
            from core.database import DatabaseManager
            from core.community_service import CommunityService
            
            db_manager = DatabaseManager()
            community_service = CommunityService(db_manager)
            
            # Test getting user groups
            user_groups = community_service.get_user_groups(user_data['postgres_id'])
            print(f"✅ User has {len(user_groups)} group memberships")
            
            # Test joining a group
            groups = community_service.get_all_groups()
            if groups:
                group_id = groups[0]['id']
                print(f"🔍 Testing join group: {groups[0]['name']}")
                result = community_service.join_group(user_data['postgres_id'], group_id)
                print(f"✅ Join result: {result}")
                
                # Check memberships again
                user_groups_after = community_service.get_user_groups(user_data['postgres_id'])
                print(f"✅ User now has {len(user_groups_after)} group memberships")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_creation()
    if success:
        print("\n🎉 User creation test passed!")
        print("The authentication system should now work with community features.")
    else:
        print("\n⚠️ User creation test failed.")