#!/usr/bin/env python3
"""
Admin Tools for BharatVerse
Command line utilities for user and admin management
"""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from streamlit_app.utils.user_manager import user_manager

def list_users():
    """List all users in the system"""
    users = user_manager.get_all_users()
    
    if not users:
        print("No users found in the system.")
        return
    
    print(f"\n{'ID':<5} {'Username':<20} {'Name':<25} {'Email':<30} {'Role':<10} {'Status':<8}")
    print("-" * 100)
    
    for user in users:
        status = "Active" if user.get('is_active') else "Inactive"
        print(f"{user['id']:<5} {user['username']:<20} {user.get('name', 'N/A'):<25} {user.get('email', 'N/A'):<30} {user['role']:<10} {status:<8}")

def make_admin(username_or_id):
    """Make a user an admin"""
    try:
        # Try to find user by ID first
        if username_or_id.isdigit():
            user_id = int(username_or_id)
            user = user_manager.get_user_by_id(user_id)
        else:
            # Find by username
            user = user_manager.get_user_by_username(username_or_id)
            user_id = user['id'] if user else None
        
        if not user:
            print(f"❌ User '{username_or_id}' not found.")
            return False
        
        if user['role'] == 'admin':
            print(f"✅ User '{user['username']}' is already an admin.")
            return True
        
        # Update role to admin
        success = user_manager.update_user_role(user_id, 'admin')
        
        if success:
            print(f"✅ Successfully made '{user['username']}' an admin!")
            print(f"   Name: {user.get('name', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to update user role.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def remove_admin(username_or_id):
    """Remove admin privileges from a user"""
    try:
        # Try to find user by ID first
        if username_or_id.isdigit():
            user_id = int(username_or_id)
            user = user_manager.get_user_by_id(user_id)
        else:
            # Find by username
            user = user_manager.get_user_by_username(username_or_id)
            user_id = user['id'] if user else None
        
        if not user:
            print(f"❌ User '{username_or_id}' not found.")
            return False
        
        if user['role'] != 'admin':
            print(f"ℹ️ User '{user['username']}' is not an admin.")
            return True
        
        # Update role to user
        success = user_manager.update_user_role(user_id, 'user')
        
        if success:
            print(f"✅ Successfully removed admin privileges from '{user['username']}'!")
            return True
        else:
            print(f"❌ Failed to update user role.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_admins():
    """List all admin users"""
    users = user_manager.get_all_users()
    admins = [user for user in users if user['role'] == 'admin']
    
    if not admins:
        print("No admin users found in the system.")
        return
    
    print(f"\n{'ID':<5} {'Username':<20} {'Name':<25} {'Email':<30}")
    print("-" * 80)
    
    for admin in admins:
        print(f"{admin['id']:<5} {admin['username']:<20} {admin.get('name', 'N/A'):<25} {admin.get('email', 'N/A'):<30}")

def main():
    parser = argparse.ArgumentParser(description='BharatVerse Admin Tools')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List users command
    list_parser = subparsers.add_parser('list', help='List all users')
    
    # List admins command
    admins_parser = subparsers.add_parser('admins', help='List all admin users')
    
    # Make admin command
    admin_parser = subparsers.add_parser('make-admin', help='Make a user an admin')
    admin_parser.add_argument('user', help='Username or User ID')
    
    # Remove admin command
    remove_parser = subparsers.add_parser('remove-admin', help='Remove admin privileges')
    remove_parser.add_argument('user', help='Username or User ID')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_users()
    elif args.command == 'admins':
        list_admins()
    elif args.command == 'make-admin':
        make_admin(args.user)
    elif args.command == 'remove-admin':
        remove_admin(args.user)
    else:
        parser.print_help()

if __name__ == "__main__":
    print("🛡️ BharatVerse Admin Tools")
    print("=" * 50)
    main()