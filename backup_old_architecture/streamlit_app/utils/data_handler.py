import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def get_postgres_connection():
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
        st.error(f"Failed to connect to PostgreSQL: {e}")
        return None

def get_contributions():
    """Get contributions from PostgreSQL database"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return []
            
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get recent contributions with user info
            cursor.execute("""
                SELECT 
                    c.id,
                    c.title,
                    c.description,
                    c.content_type,
                    c.language,
                    c.region,
                    c.created_at,
                    u.full_name as contributor_name,
                    u.username as contributor_username
                FROM content_metadata c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.created_at DESC
                LIMIT 20
            """)
            
            contributions = []
            for row in cursor.fetchall():
                contrib = {
                    'id': str(row['id']),
                    'title': row['title'],
                    'description': row['description'] or '',
                    'type': row['content_type'],
                    'lang': row['language'] or 'Unknown',
                    'region': row['region'] or 'Unknown',
                    'time': row['created_at'].strftime('%Y-%m-%d %H:%M') if row['created_at'] else 'Unknown',
                    'contributor': row['contributor_name'] or 'Anonymous',
                    'username': row['contributor_username'] or 'unknown'
                }
                contributions.append(contrib)
        
        conn.close()
        return contributions
        
    except Exception as e:
        st.error(f"Failed to fetch contributions: {e}")
        return []
