import os
import streamlit as st
from streamlit_app.utils.database import get_db_connection
from datetime import datetime

def get_contributions():
    """Get contributions from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent contributions with user info
        cursor.execute("""
            SELECT c.*, u.full_name as contributor_name, u.username as contributor_username
            FROM content_metadata c
            LEFT JOIN users u ON c.user_id = u.id::text
            ORDER BY c.created_at DESC
            LIMIT 20
        """)
        
        contributions = []
        for row in cursor.fetchall():
            contrib = {
                'id': row[0],  # id
                'title': row[1],  # title
                'description': row[2] or '',  # description
                'type': row[3],  # content_type
                'lang': row[4] or 'Unknown',  # language
                'region': row[5] or 'Unknown',  # region
                'time': row[11].strftime('%Y-%m-%d %H:%M') if row[11] else 'Unknown',  # created_at
                'contributor': row[13] or 'Anonymous',  # contributor_name
                'username': row[14] or 'unknown'  # contributor_username
            }
            contributions.append(contrib)
        
        conn.close()
        return contributions
        
    except Exception as e:
        st.error(f"Failed to fetch contributions: {e}")
        return []
