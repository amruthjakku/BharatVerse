#!/usr/bin/env python3
"""
Quick Admin Promotion Tool for BharatVerse
Simple script to make any user an admin
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def get_database_path():
    """Get the database path"""
    return project_root / "data" / "users.db"

def list_users():
    """List all users in the database"""
    db_path = get_database_path()
    
    if not db_path.exists():
        print("❌ Database not found. Please ensure users have logged in first.")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, full_name, role, created_at, last_login
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        return [dict(user) for user in users]
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return []

def make_user_admin(username):
    """Make a user an admin"""
    db_path = get_database_path()
    
    if not db_path.exists():
        print("❌ Database not found. Please ensure users have logged in first.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find user by username
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found.")
            conn.close()
            return False
        
        # Check if already admin
        if user[6] == 'admin':  # role column
            print(f"✅ User '{username}' is already an admin.")
            conn.close()
            return True
        
        # Update role to admin
        cursor.execute("""
            UPDATE users 
            SET role = 'admin', updated_at = CURRENT_TIMESTAMP
            WHERE username = ?
        """, (username,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully made '{username}' an admin!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return False

def main():
    print("🛡️ BharatVerse Admin Promotion Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # Check for help
        if sys.argv[1] in ['-h', '--help', 'help']:
            print("Usage:")
            print("  python make_admin.py                 # Interactive mode")
            print("  python make_admin.py <username>      # Make specific user admin")
            print("  python make_admin.py --help          # Show this help")
            print()
            print("Examples:")
            print("  python make_admin.py                 # Shows all users, lets you select")
            print("  python make_admin.py john_doe        # Makes john_doe an admin")
            return
        
        # Command line usage
        username = sys.argv[1]
        make_user_admin(username)
        return
    
    # Interactive mode
    users = list_users()
    
    if not users:
        print("❌ No users found in the database.")
        print("Please have users login via GitLab OAuth first.")
        return
    
    print(f"📋 Found {len(users)} users:")
    print()
    
    # Display users
    for i, user in enumerate(users, 1):
        role_emoji = {"admin": "🛡️", "moderator": "🛠️", "user": "👤"}.get(user.get('role'), "👤")
        role = user.get('role') or 'user'
        name = user.get('full_name') or user.get('username')
        
        print(f"{i}. {role_emoji} {name} (@{user['username']}) - {role.title()}")
        print(f"   Email: {user.get('email') or 'Not provided'}")
        print(f"   Member since: {user.get('created_at')}")
        print()
    
    # Check if there are already admins
    admins = [user for user in users if user.get('role') == 'admin']
    
    if admins:
        print(f"✅ Found {len(admins)} existing admin(s):")
        for admin in admins:
            print(f"   🛡️ {admin.get('full_name') or admin['username']} (@{admin['username']})")
        print()
    
    # Get username to promote
    while True:
        username = input("👑 Enter username to make admin (or 'quit' to exit): ").strip()
        
        if username.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not username:
            print("Please enter a username.")
            continue
        
        # Check if user exists
        user_exists = any(user['username'] == username for user in users)
        if not user_exists:
            print(f"❌ User '{username}' not found. Available users:")
            for user in users:
                print(f"   - {user['username']}")
            continue
        
        # Confirm promotion
        confirm = input(f"🔄 Make '{username}' an admin? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            if make_user_admin(username):
                print(f"🎉 {username} is now an admin and can access all admin features!")
                break
        else:
            print("❌ Cancelled.")

if __name__ == "__main__":
    main()