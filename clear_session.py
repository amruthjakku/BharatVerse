#!/usr/bin/env python3
"""
Clear Streamlit session and test with fresh user
"""

import os
import sys
sys.path.append('/Users/jakkuamruth/Documents/hackathon/bharatverse')

# Simulate a fresh user login
def test_fresh_user_login():
    """Test the user creation process with a fresh user"""
    
    from streamlit_app.utils.user_manager import UserManager
    
    # Create a new test user
    gitlab_user_data = {
        'id': 99999,  # Different GitLab ID
        'username': 'freshuser',
        'email': 'freshuser@example.com',
        'name': 'Fresh Test User',
        'avatar_url': 'https://example.com/fresh.jpg'
    }
    
    print("🔄 Creating fresh user...")
    user_manager = UserManager()
    user_data = user_manager.create_or_update_user(gitlab_user_data)
    
    print(f"✅ Fresh user created:")
    print(f"   SQLite ID: {user_data.get('id')}")
    print(f"   PostgreSQL ID: {user_data.get('postgres_id')}")
    
    # Test community service with this user
    if user_data.get('postgres_id'):
        from core.database import DatabaseManager
        from core.community_service import CommunityService
        
        db_manager = DatabaseManager()
        community_service = CommunityService(db_manager)
        
        print(f"\n🔍 Testing community service...")
        user_groups = community_service.get_user_groups(user_data['postgres_id'])
        print(f"✅ User groups query successful: {len(user_groups)} groups")
        
        # Test the exact scenario that was failing
        print(f"\n🔍 Testing with user ID: {user_data['postgres_id']}")
        print(f"   Type: {type(user_data['postgres_id'])}")
        
        return user_data['postgres_id']
    
    return None

if __name__ == "__main__":
    postgres_id = test_fresh_user_login()
    if postgres_id:
        print(f"\n🎉 Fresh user test successful!")
        print(f"Use this PostgreSQL ID for testing: {postgres_id}")
    else:
        print(f"\n❌ Fresh user test failed!")