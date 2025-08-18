import streamlit as st
from datetime import datetime
from utils.supabase_db import DatabaseManager

# Use Supabase/Postgres exclusively via DatabaseManager
_db = None

def get_db():
    global _db
    if _db is None:
        _db = DatabaseManager()
    return _db

def get_contributions(limit: int = 20):
    """Get recent public contributions from Supabase/Postgres"""
    try:
        db = get_db()
        rows = db.get_contributions(limit=limit)
        contributions = []
        for row in rows:
            # Map to UI structure used by Home.py and pages
            created_at = row.get('created_at')
            # created_at may be datetime or string
            if isinstance(created_at, str):
                time_str = created_at.replace('T', ' ')[:16]
            elif created_at:
                time_str = created_at.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = 'Unknown'
            contributions.append({
                'id': str(row.get('id')),
                'title': row.get('title'),
                'description': row.get('content') or '',
                'type': row.get('content_type'),
                'lang': row.get('language') or 'Unknown',
                'region': row.get('region') or 'Unknown',
                'time': time_str,
                'contributor': row.get('full_name') or row.get('username') or 'Anonymous',
                'username': row.get('username') or 'unknown',
            })
        return contributions
    except Exception as e:
        st.error(f"Failed to fetch contributions: {e}")
        return []
