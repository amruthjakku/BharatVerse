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
            SELECT c.*, u.name as contributor_name, u.username as contributor_username
            FROM contributions c
            LEFT JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT 20
        """)
        
        contributions = []
        for row in cursor.fetchall():
            contrib = {
                'id': row[0],
                'type': row[2],  # content_type
                'title': row[3],
                'lang': row[5] or 'Unknown',  # language
                'time': row[8].strftime('%Y-%m-%d %H:%M') if row[8] else 'Unknown',  # created_at
                'description': row[4] or '',  # description
                'contributor': row[10] or 'Anonymous',  # contributor_name
                'username': row[11] or 'unknown'  # contributor_username
            }
            contributions.append(contrib)
        
        conn.close()
        return contributions
        
    except Exception as e:
        st.error(f"Failed to fetch contributions: {e}")
        return []
