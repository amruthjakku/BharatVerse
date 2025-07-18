import json
import os
from datetime import datetime
from pathlib import Path

# Simple JSON-based database for demo purposes
DATA_DIR = Path("data")
CONTRIBUTIONS_FILE = DATA_DIR / "contributions.json"

def init_db():
    """Initialize the database directory and files"""
    DATA_DIR.mkdir(exist_ok=True)
    
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
    """Add a new contribution to the database"""
    try:
        with open(CONTRIBUTIONS_FILE, 'r') as f:
            db = json.load(f)
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        data['id'] = f"{contribution_type}_{db['metadata']['total_contributions'] + 1}"
        
        # Add to appropriate collection
        if contribution_type in db:
            db[contribution_type].append(data)
        
        # Update metadata
        db['metadata']['total_contributions'] += 1
        db['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save back to file
        with open(CONTRIBUTIONS_FILE, 'w') as f:
            json.dump(db, f, indent=2)
        
        return True, data['id']
    except Exception as e:
        print(f"Error adding contribution: {e}")
        return False, None

def get_contributions(contribution_type=None, limit=10):
    """Retrieve contributions from the database"""
    import streamlit as st
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        # Try to get real contributions from API
        try:
            import requests
            API_URL = os.getenv("API_URL", "http://localhost:8000")
            response = requests.get(f"{API_URL}/api/v1/content/recent?limit={limit}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
        except Exception as e:
            print(f"Error getting real contributions: {e}")
        
        # Return empty list for fresh start
        return []
    
    # Use local JSON file for demo mode
    try:
        with open(CONTRIBUTIONS_FILE, 'r') as f:
            db = json.load(f)
        
        if contribution_type:
            return db.get(contribution_type, [])[-limit:]
        else:
            # Return recent contributions across all types
            all_contributions = []
            for c_type in ['audio', 'text', 'image']:
                contributions = db.get(c_type, [])
                for contrib in contributions:
                    contrib['type'] = c_type
                    all_contributions.append(contrib)
            
            # Sort by timestamp and return most recent
            all_contributions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return all_contributions[:limit]
    except Exception as e:
        print(f"Error retrieving contributions: {e}")
        return []

def get_statistics():
    """Get database statistics"""
    import streamlit as st
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        # Try to get real statistics from API
        try:
            import requests
            API_URL = os.getenv("API_URL", "http://localhost:8000")
            response = requests.get(f"{API_URL}/api/v1/analytics", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'total_contributions': data.get('total_contributions', 0),
                    'audio_count': data.get('content_by_type', {}).get('audio', 0),
                    'text_count': data.get('content_by_type', {}).get('text', 0),
                    'image_count': data.get('content_by_type', {}).get('image', 0),
                    'unique_languages': len(data.get('languages', [])),
                    'unique_regions': len(data.get('regions', [])),
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error getting real statistics: {e}")
        
        # Return empty stats for fresh start
        return {
            'total_contributions': 0,
            'audio_count': 0,
            'text_count': 0,
            'image_count': 0,
            'unique_languages': 0,
            'unique_regions': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    # Use local JSON file for demo mode
    try:
        with open(CONTRIBUTIONS_FILE, 'r') as f:
            db = json.load(f)
        
        stats = {
            'total_contributions': db['metadata']['total_contributions'],
            'audio_count': len(db.get('audio', [])),
            'text_count': len(db.get('text', [])),
            'image_count': len(db.get('image', [])),
            'last_updated': db['metadata']['last_updated']
        }
        
        # Count unique languages and regions
        languages = set()
        regions = set()
        
        for c_type in ['audio', 'text', 'image']:
            for contrib in db.get(c_type, []):
                if 'language' in contrib:
                    languages.add(contrib['language'])
                if 'region' in contrib:
                    regions.add(contrib['region'])
        
        stats['unique_languages'] = len(languages)
        stats['unique_regions'] = len(regions)
        
        return stats
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_contributions': 0,
            'audio_count': 0,
            'text_count': 0,
            'image_count': 0,
            'unique_languages': 0,
            'unique_regions': 0,
            'last_updated': datetime.now().isoformat()
        }
