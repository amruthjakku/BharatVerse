import os
import streamlit as st
import requests

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000") + "/api/v1"

def should_use_real_data():
    return st.session_state.get("use_real_data", False)

def get_real_contributions():
    try:
        response = requests.get(f"{API_BASE_URL}/content/recent", timeout=5)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        st.error("Failed to fetch real data from API.")
        return []

def get_mock_contributions():
    return [
        {"type": "🎙️", "title": "Baul Song from Bengal", "lang": "Bengali", "time": "2 hours ago"},
        {"type": "📝", "title": "Pongal Recipe", "lang": "Tamil", "time": "5 hours ago"},
        {"type": "📷", "title": "Durga Puja Celebration", "lang": "Hindi", "time": "1 day ago"},
        {"type": "🎙️", "title": "Lavani Performance", "lang": "Marathi", "time": "2 days ago"}
    ]

from datetime import datetime

def get_real_data_start_time():
    return st.session_state.get("real_data_start_time")

def get_contributions():
    if should_use_real_data():
        data = get_real_contributions()
        start_time = get_real_data_start_time()
        
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                # Filter to show only content created *after* the toggle time
                return [c for c in data if datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")) > start_dt]
            except (ValueError, TypeError):
                return [] # Return empty if timestamps are invalid
        else:
            # If no start time is set, it means the toggle was just turned on, so show nothing yet
            return []
    else:
        return get_mock_contributions()
