"""
Database Viewer Utilities for BharatVerse
Helper functions for database administration and user management
"""

import streamlit as st
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Safe imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

def get_sqlite_user_stats() -> Dict[str, Any]:
    """Get comprehensive user statistics from SQLite"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        # Users by role
        cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
        roles = {row['role'] or 'user': row['count'] for row in cursor.fetchall()}
        
        # Recent users (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) as recent FROM users WHERE created_at > ?", (week_ago,))
        recent_users = cursor.fetchone()['recent']
        
        # Active users (have logged in)
        cursor.execute("SELECT COUNT(*) as active FROM users WHERE last_login IS NOT NULL")
        active_users = cursor.fetchone()['active']
        
        # Top regions
        cursor.execute("""
            SELECT region, COUNT(*) as count 
            FROM users 
            WHERE region IS NOT NULL 
            GROUP BY region 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_regions = {row['region']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_users': total_users,
            'roles': roles,
            'recent_users': recent_users,
            'active_users': active_users,
            'top_regions': top_regions,
            'database_type': 'SQLite'
        }
        
    except Exception as e:
        return {'error': str(e), 'database_type': 'SQLite'}

def get_user_activity_timeline() -> List[Dict[str, Any]]:
    """Get user registration timeline"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as registrations
            FROM users 
            WHERE created_at IS NOT NULL
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        """)
        
        timeline = []
        for row in cursor.fetchall():
            timeline.append({
                'date': row[0],
                'registrations': row[1]
            })
        
        conn.close()
        return timeline
        
    except Exception as e:
        return [{'error': str(e)}]

def search_users(search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search users across all fields"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, full_name, gitlab_id, 
                   created_at, last_login, login_count, role, region
            FROM users 
            WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ? 
               OR gitlab_id LIKE ? OR region LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", 
              f"%{search_term}%", f"%{search_term}%", limit))
        
        users = []
        for row in cursor.fetchall():
            users.append(dict(row))
        
        conn.close()
        return users
        
    except Exception as e:
        return [{'error': str(e)}]

def get_contribution_stats() -> Dict[str, Any]:
    """Get contribution statistics"""
    try:
        from streamlit_app.utils.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total contributions
        cursor.execute("SELECT COUNT(*) as total FROM contributions")
        total = cursor.fetchone()[0]
        
        # By type
        cursor.execute("""
            SELECT contribution_type, COUNT(*) as count
            FROM contributions 
            GROUP BY contribution_type
            ORDER BY count DESC
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent contributions (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) as recent FROM contributions WHERE created_at > ?", (week_ago,))
        recent = cursor.fetchone()[0]
        
        # By user (top contributors)
        cursor.execute("""
            SELECT user_id, COUNT(*) as count
            FROM contributions 
            WHERE user_id IS NOT NULL
            GROUP BY user_id
            ORDER BY count DESC
            LIMIT 10
        """)
        top_contributors = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_contributions': total,
            'by_type': by_type,
            'recent_contributions': recent,
            'top_contributors': top_contributors
        }
        
    except Exception as e:
        return {'error': str(e)}

def execute_safe_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a safe read-only query"""
    # Only allow SELECT queries for safety
    if not query.strip().upper().startswith('SELECT'):
        return [{'error': 'Only SELECT queries are allowed'}]
    
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        conn.close()
        return results
        
    except Exception as e:
        return [{'error': str(e)}]

def get_database_schema() -> Dict[str, List[str]]:
    """Get database schema information"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]  # row[1] is column name
            schema[table] = columns
        
        conn.close()
        return schema
        
    except Exception as e:
        return {'error': str(e)}

def export_users_to_csv() -> str:
    """Export users to CSV format"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        
        df = pd.read_sql_query("""
            SELECT username, email, full_name, gitlab_id, region,
                   created_at, last_login, login_count, role
            FROM users 
            ORDER BY created_at DESC
        """, conn)
        
        conn.close()
        return df.to_csv(index=False)
        
    except Exception as e:
        return f"Error exporting data: {e}"

def get_user_details(user_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific user"""
    try:
        from streamlit_app.utils.user_manager import UserManager
        user_manager = UserManager()
        
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = ? OR username = ?", (user_id, user_id))
        user = cursor.fetchone()
        
        if not user:
            return {'error': 'User not found'}
        
        user_data = dict(user)
        
        # Get user's contributions
        from streamlit_app.utils.database import get_db_connection
        contrib_conn = get_db_connection()
        contrib_cursor = contrib_conn.cursor()
        
        contrib_cursor.execute("""
            SELECT contribution_type, COUNT(*) as count
            FROM contributions 
            WHERE user_id = ?
            GROUP BY contribution_type
        """, (user_data['username'],))
        
        contributions = {row[0]: row[1] for row in contrib_cursor.fetchall()}
        
        contrib_conn.close()
        conn.close()
        
        user_data['contributions'] = contributions
        return user_data
        
    except Exception as e:
        return {'error': str(e)}

# Streamlit display functions
def display_user_stats():
    """Display user statistics in Streamlit"""
    stats = get_sqlite_user_stats()
    
    if 'error' in stats:
        st.error(f"Error loading stats: {stats['error']}")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'])
    
    with col2:
        st.metric("Active Users", stats['active_users'])
    
    with col3:
        st.metric("New (7 days)", stats['recent_users'])
    
    with col4:
        admin_count = stats['roles'].get('admin', 0)
        st.metric("Admins", admin_count)
    
    # Show roles distribution
    if stats['roles']:
        st.subheader("👥 Users by Role")
        role_df = pd.DataFrame(list(stats['roles'].items()), columns=['Role', 'Count'])
        st.bar_chart(role_df.set_index('Role'))
    
    # Show top regions
    if stats['top_regions']:
        st.subheader("🌍 Top Regions")
        region_df = pd.DataFrame(list(stats['top_regions'].items()), columns=['Region', 'Users'])
        st.bar_chart(region_df.set_index('Region'))

def display_contribution_stats():
    """Display contribution statistics"""
    stats = get_contribution_stats()
    
    if 'error' in stats:
        st.error(f"Error loading contribution stats: {stats['error']}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Contributions", stats['total_contributions'])
    
    with col2:
        st.metric("Recent (7 days)", stats['recent_contributions'])
    
    # Show contributions by type
    if stats['by_type']:
        st.subheader("📊 Contributions by Type")
        type_df = pd.DataFrame(list(stats['by_type'].items()), columns=['Type', 'Count'])
        st.bar_chart(type_df.set_index('Type'))