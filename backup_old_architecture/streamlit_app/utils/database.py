import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Database configuration
DATA_DIR = Path("data")
CONTRIBUTIONS_FILE = DATA_DIR / "contributions.json"  # Keep for backward compatibility
DB_FILE = DATA_DIR / "bharatverse.db"

def get_db_connection():
    """Get SQLite database connection"""
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    return conn

def init_db():
    """Initialize the SQLite database and create tables"""
    DATA_DIR.mkdir(exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            gitlab_id INTEGER UNIQUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create contributions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            language TEXT,
            region TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_type ON contributions(content_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_user ON contributions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contributions_created ON contributions(created_at)')
    
    conn.commit()
    conn.close()
    
    # Keep JSON file creation for backward compatibility
    if not CONTRIBUTIONS_FILE.exists():
        with open(CONTRIBUTIONS_FILE, 'w') as f:
            json.dump({
                "audio": [],
                "text": [],
                "image": [],
                "metadata": {
                    "total_contributions": 0,
                    "languages": [],
                    "regions": [],
                    "last_updated": datetime.now().isoformat()
                }
            }, f, indent=2)

def add_contribution(contribution_type, data):
    """Add a new contribution to the SQLite database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert contribution
        cursor.execute('''
            INSERT INTO contributions (user_id, content_type, title, description, language, region, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('user_id'),
            contribution_type,
            data.get('title', ''),
            data.get('description', ''),
            data.get('language'),
            data.get('region'),
            data.get('file_path')
        ))
        
        contribution_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Also update JSON file for backward compatibility
        try:
            with open(CONTRIBUTIONS_FILE, 'r') as f:
                db = json.load(f)
            
            # Add timestamp and id for JSON compatibility
            json_data = data.copy()
            json_data['timestamp'] = datetime.now().isoformat()
            json_data['id'] = f"{contribution_type}_{contribution_id}"
            
            # Add to appropriate collection
            if contribution_type in db:
                db[contribution_type].append(json_data)
            
            # Update metadata
            db['metadata']['total_contributions'] += 1
            db['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(CONTRIBUTIONS_FILE, 'w') as f:
                json.dump(db, f, indent=2)
        except:
            pass  # JSON update is optional
        
        return True, contribution_id
    except Exception as e:
        print(f"Error adding contribution: {e}")
        return False, None

# Old get_contributions function removed - now using data_handler.py version

def get_statistics():
    """Get database statistics from SQLite database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total contributions
        cursor.execute("SELECT COUNT(*) FROM contributions")
        total_contributions = cursor.fetchone()[0]
        
        # Get contributions by type
        cursor.execute("SELECT content_type, COUNT(*) FROM contributions GROUP BY content_type")
        type_counts = dict(cursor.fetchall())
        
        # Get unique languages
        cursor.execute("SELECT COUNT(DISTINCT language) FROM contributions WHERE language IS NOT NULL")
        unique_languages = cursor.fetchone()[0]
        
        # Get unique regions
        cursor.execute("SELECT COUNT(DISTINCT region) FROM contributions WHERE region IS NOT NULL")
        unique_regions = cursor.fetchone()[0]
        
        # Get active contributors (users who have made contributions)
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM contributions WHERE user_id IS NOT NULL")
        active_contributors = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_contributions': total_contributions,
            'audio_count': type_counts.get('audio', 0),
            'text_count': type_counts.get('text', 0),
            'image_count': type_counts.get('image', 0),
            'unique_languages': unique_languages,
            'unique_regions': unique_regions,
            'active_contributors': active_contributors,
            'last_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_contributions': 0,
            'audio_count': 0,
            'text_count': 0,
            'image_count': 0,
            'unique_languages': 0,
            'unique_regions': 0,
            'active_contributors': 0,
            'last_updated': datetime.now().isoformat()
        }
