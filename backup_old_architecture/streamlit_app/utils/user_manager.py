"""
User Management System for BharatVerse
Handles user profiles, permissions, and data isolation
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib
import os
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    # Create mock classes for when PostgreSQL is not available
    class RealDictCursor:
        pass

class UserManager:
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_user_db()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_postgres_connection(self):
        """Get PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DB", "bharatverse"),
                user=os.getenv("POSTGRES_USER", "bharatverse_user"),
                password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
            )
            return conn
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            return None
    
    def init_user_db(self):
        """Initialize user database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gitlab_id INTEGER UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                name TEXT,
                avatar_url TEXT,
                bio TEXT,
                location TEXT,
                organization TEXT,
                job_title TEXT,
                web_url TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                profile_data TEXT,
                preferences TEXT
            )
        ''')
        
        # User contributions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contribution_type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                file_path TEXT,
                metadata TEXT,
                tags TEXT,
                language TEXT,
                region TEXT,
                is_public BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE,
                gitlab_access_token TEXT,
                gitlab_refresh_token TEXT,
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_or_update_user(self, gitlab_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update user from GitLab data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        gitlab_id = gitlab_user_data.get('id')
        username = gitlab_user_data.get('username')
        email = gitlab_user_data.get('email')
        name = gitlab_user_data.get('name')
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE gitlab_id = ?', (gitlab_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Update existing user
            cursor.execute('''
                UPDATE users SET
                    username = ?, email = ?, name = ?, avatar_url = ?,
                    bio = ?, location = ?, organization = ?, job_title = ?,
                    web_url = ?, updated_at = CURRENT_TIMESTAMP,
                    last_login = CURRENT_TIMESTAMP,
                    profile_data = ?
                WHERE gitlab_id = ?
            ''', (
                username, email, name, gitlab_user_data.get('avatar_url'),
                gitlab_user_data.get('bio'), gitlab_user_data.get('location'),
                gitlab_user_data.get('organization'), gitlab_user_data.get('job_title'),
                gitlab_user_data.get('web_url'), json.dumps(gitlab_user_data),
                gitlab_id
            ))
            user_id = existing_user[0]
        else:
            # Check if this should be an initial admin
            initial_role = self._check_initial_admin(username, email)
            
            # Create new user
            cursor.execute('''
                INSERT INTO users (
                    gitlab_id, username, email, name, avatar_url,
                    bio, location, organization, job_title, web_url,
                    role, last_login, profile_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (
                gitlab_id, username, email, name, gitlab_user_data.get('avatar_url'),
                gitlab_user_data.get('bio'), gitlab_user_data.get('location'),
                gitlab_user_data.get('organization'), gitlab_user_data.get('job_title'),
                gitlab_user_data.get('web_url'), initial_role, json.dumps(gitlab_user_data)
            ))
            user_id = cursor.lastrowid
        
        conn.commit()
        
        # Get updated user data
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        # Also create/update user in PostgreSQL for community features
        postgres_user_id = self._create_or_update_postgres_user(gitlab_user_data, user_id)
        
        if user_row:
            user_dict = self._row_to_user_dict(user_row)
            # Add PostgreSQL UUID for community features
            user_dict['postgres_id'] = postgres_user_id
            return user_dict
        return {}
    
    def _check_initial_admin(self, username: str, email: str) -> str:
        """Check if user should be made initial admin based on environment variables"""
        initial_admin_username = os.getenv('INITIAL_ADMIN_USERNAME', '').strip()
        initial_admin_email = os.getenv('INITIAL_ADMIN_EMAIL', '').strip()
        
        # Check if username or email matches initial admin config
        if initial_admin_username and username == initial_admin_username:
            return 'admin'
        if initial_admin_email and email == initial_admin_email:
            return 'admin'
        
        return 'user'
    
    def _create_or_update_postgres_user(self, gitlab_user_data: Dict[str, Any], sqlite_user_id: int) -> Optional[str]:
        """Create or update user in PostgreSQL database for community features"""
        try:
            conn = self.get_postgres_connection()
            if not conn:
                return None
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                username = gitlab_user_data.get('username')
                email = gitlab_user_data.get('email')
                full_name = gitlab_user_data.get('name')
                
                # Check if user exists by username or email
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE username = %s OR email = %s
                """, (username, email))
                
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Update existing user
                    cursor.execute("""
                        UPDATE users 
                        SET full_name = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id
                    """, (full_name, existing_user['id']))
                    result = cursor.fetchone()
                    user_id = result['id'] if result else existing_user['id']
                else:
                    # Create new user
                    cursor.execute("""
                        INSERT INTO users (username, email, full_name)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (username, email, full_name))
                    result = cursor.fetchone()
                    user_id = result['id'] if result else None
                
                conn.commit()
            
            conn.close()
            return str(user_id) if user_id else None
            
        except Exception as e:
            print(f"Failed to create/update PostgreSQL user: {e}")
            return None
    
    def get_user_by_gitlab_id(self, gitlab_id: int) -> Optional[Dict[str, Any]]:
        """Get user by GitLab ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE gitlab_id = ?', (gitlab_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            return self._row_to_user_dict(user_row)
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by internal ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            return self._row_to_user_dict(user_row)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            return self._row_to_user_dict(user_row)
        return None
    
    def update_user_role(self, user_id: int, role: str) -> bool:
        """Update user role (admin, moderator, user)"""
        if role not in ['admin', 'moderator', 'user']:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (role, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        users = []
        for row in cursor.fetchall():
            users.append(self._row_to_user_dict(row))
        
        conn.close()
        return users
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Active users (logged in last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE last_login > datetime('now', '-30 days')
        ''')
        active_users = cursor.fetchone()[0]
        
        # Users by role
        cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
        roles = dict(cursor.fetchall())
        
        # New users this month
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE created_at > datetime('now', 'start of month')
        ''')
        new_users_month = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'roles': roles,
            'new_users_month': new_users_month
        }
    
    def add_user_contribution(self, user_id: int, contribution_data: Dict[str, Any]) -> int:
        """Add a user contribution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_contributions (
                user_id, contribution_type, title, description,
                file_path, metadata, tags, language, region, is_public
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            contribution_data.get('type'),
            contribution_data.get('title'),
            contribution_data.get('description'),
            contribution_data.get('file_path'),
            json.dumps(contribution_data.get('metadata', {})),
            json.dumps(contribution_data.get('tags', [])),
            contribution_data.get('language'),
            contribution_data.get('region'),
            contribution_data.get('is_public', True)
        ))
        
        contribution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return contribution_id
    
    def get_user_contributions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's contributions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_contributions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        contributions = []
        for row in cursor.fetchall():
            contributions.append(self._contribution_row_to_dict(row))
        
        conn.close()
        return contributions
    
    def log_user_activity(self, user_id: int, activity_type: str, activity_data: Dict = None):
        """Log user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        ''', (user_id, activity_type, json.dumps(activity_data or {})))
        
        conn.commit()
        conn.close()
    
    def get_user_activity(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_activity 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'id': row[0],
                'activity_type': row[2],
                'activity_data': json.loads(row[3] or '{}'),
                'created_at': row[6]
            })
        
        conn.close()
        return activities
    
    def _row_to_user_dict(self, row) -> Dict[str, Any]:
        """Convert database row to user dictionary"""
        return {
            'id': row[0],
            'gitlab_id': row[1],
            'username': row[2],
            'email': row[3],
            'name': row[4],
            'avatar_url': row[5],
            'bio': row[6],
            'location': row[7],
            'organization': row[8],
            'job_title': row[9],
            'web_url': row[10],
            'role': row[11],
            'is_active': bool(row[12]),
            'created_at': row[13],
            'updated_at': row[14],
            'last_login': row[15],
            'profile_data': json.loads(row[16] or '{}'),
            'preferences': json.loads(row[17] or '{}')
        }
    
    def _contribution_row_to_dict(self, row) -> Dict[str, Any]:
        """Convert contribution row to dictionary"""
        return {
            'id': row[0],
            'user_id': row[1],
            'type': row[2],
            'title': row[3],
            'description': row[4],
            'file_path': row[5],
            'metadata': json.loads(row[6] or '{}'),
            'tags': json.loads(row[7] or '[]'),
            'language': row[8],
            'region': row[9],
            'is_public': bool(row[10]),
            'created_at': row[11],
            'updated_at': row[12]
        }

# Global user manager instance
user_manager = UserManager()