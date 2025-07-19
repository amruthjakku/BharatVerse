#!/usr/bin/env python3
"""
Setup script to create the first admin user for BharatVerse
Run this script after the first user logs in to make them an admin
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from streamlit_app.utils.user_manager import user_manager

def setup_admin():
    """Setup the first admin user"""
    print("🛡️ BharatVerse Admin Setup")
    print("=" * 40)
    
    # Get all users
    users = user_manager.get_all_users()
    
    if not users:
        print("❌ No users found in the database.")
        print("Please have at least one user login via GitLab OAuth first.")
        return
    
    print(f"📋 Found {len(users)} users:")
    print()
    
    # Display users
    for i, user in enumerate(users, 1):
        role_emoji = {"admin": "🛡️", "moderator": "🛠️", "user": "👤"}.get(user['role'], "👤")
        print(f"{i}. {role_emoji} {user['name']} (@{user['username']}) - {user['role'].title()}")
        print(f"   Email: {user['email'] or 'Not provided'}")
        print(f"   GitLab ID: {user['gitlab_id']}")
        print(f"   Member since: {user['created_at']}")
        print()
    
    # Check if there are already admins
    admins = [user for user in users if user['role'] == 'admin']
    
    if admins:
        print(f"✅ Found {len(admins)} existing admin(s):")
        for admin in admins:
            print(f"   🛡️ {admin['name']} (@{admin['username']})")
        print()
        
        choice = input("Do you want to add another admin? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("👋 Goodbye!")
            return
    
    # Select user to make admin
    print("👆 Select a user to make admin:")
    
    try:
        selection = input("Enter user number: ").strip()
        user_index = int(selection) - 1
        
        if user_index < 0 or user_index >= len(users):
            print("❌ Invalid selection.")
            return
        
        selected_user = users[user_index]
        
        print(f"\n🎯 Selected user: {selected_user['name']} (@{selected_user['username']})")
        print(f"Current role: {selected_user['role'].title()}")
        
        if selected_user['role'] == 'admin':
            print("✅ This user is already an admin!")
            return
        
        # Confirm
        confirm = input(f"\n⚠️  Make {selected_user['name']} an admin? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            # Update user role
            success = user_manager.update_user_role(selected_user['id'], 'admin')
            
            if success:
                print(f"✅ Successfully made {selected_user['name']} an admin!")
                print(f"🎉 {selected_user['name']} can now access the admin dashboard.")
                
                # Log the activity
                user_manager.log_user_activity(
                    selected_user['id'], 
                    'role_change', 
                    {'old_role': selected_user['role'], 'new_role': 'admin', 'changed_by': 'setup_script'}
                )
                
                print("\n📋 Admin privileges include:")
                print("   • Access to admin dashboard")
                print("   • User management")
                print("   • Content moderation")
                print("   • System analytics")
                print("   • Role management")
                
            else:
                print("❌ Failed to update user role. Please check the database.")
        else:
            print("❌ Admin setup cancelled.")
    
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled.")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_users():
    """List all users and their roles"""
    print("👥 BharatVerse Users")
    print("=" * 30)
    
    users = user_manager.get_all_users()
    
    if not users:
        print("❌ No users found.")
        return
    
    # Group by role
    roles = {}
    for user in users:
        role = user['role']
        if role not in roles:
            roles[role] = []
        roles[role].append(user)
    
    for role, role_users in roles.items():
        role_emoji = {"admin": "🛡️", "moderator": "🛠️", "user": "👤"}.get(role, "👤")
        print(f"\n{role_emoji} {role.title()}s ({len(role_users)}):")
        
        for user in role_users:
            print(f"   • {user['name']} (@{user['username']})")
            print(f"     Email: {user['email'] or 'Not provided'}")
            print(f"     Last login: {user['last_login'] or 'Never'}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_users()
        elif command == 'setup':
            setup_admin()
        else:
            print("Usage:")
            print("  python setup_admin.py setup  - Setup admin user")
            print("  python setup_admin.py list   - List all users")
    else:
        setup_admin()

if __name__ == "__main__":
    main()