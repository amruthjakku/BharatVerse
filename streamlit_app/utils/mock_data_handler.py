"""
Mock Data Handler Utility for BharatVerse
This module provides consistent handling of mock data across all modules
"""

import streamlit as st


def should_use_real_data():
    """
    Check if the app should use real data or mock data
    
    Returns:
        bool: True if real data should be used, False for mock data
    """
    return st.session_state.get('use_real_data', False)


def show_mock_data_info(message: str):
    """
    Display an info message when mock data is being used
    
    Args:
        message (str): The message to display
    """
    if should_use_real_data():
        st.info(f"📊 {message}")
    

def show_real_data_placeholder(section_name: str):
    """
    Display a placeholder message for real data sections
    
    Args:
        section_name (str): The name of the section that would show real data
    """
    st.info(f"📊 Real {section_name} data would be displayed here when available from the API")


def conditional_mock_data(mock_data_func, section_name: str = None):
    """
    Conditionally execute mock data function based on real data setting
    
    Args:
        mock_data_func (callable): Function that generates/displays mock data
        section_name (str, optional): Name of the section for placeholder message
    """
    if should_use_real_data():
        if section_name:
            show_real_data_placeholder(section_name)
        else:
            st.info("📊 Real data would be displayed here when available from the API")
    else:
        mock_data_func()


def get_mock_or_real_metric(mock_value, mock_delta=None, real_value="N/A", real_delta="Real data not available"):
    """
    Get metric values based on real data setting
    
    Args:
        mock_value: The mock value to display
        mock_delta: The mock delta to display
        real_value: The real value to display (default: "N/A")
        real_delta: The real delta to display (default: "Real data not available")
    
    Returns:
        tuple: (value, delta) to use for the metric
    """
    if should_use_real_data():
        return real_value, real_delta
    else:
        return mock_value, mock_delta


def show_data_mode_warning():
    """
    Show a warning about the current data mode
    """
    if should_use_real_data():
        st.warning("⚠️ Real data mode is enabled. Some features may not work without a running API server.")
    else:
        st.info("ℹ️ Demo mode is active. All data shown is for demonstration purposes.")


import requests

API_BASE_URL = "http://localhost:8000/api/v1"

def get_contributions_data():
    """
    Get contributions data based on real data setting
    
    Returns:
        list: List of contribution objects
    """
    if should_use_real_data():
        try:
            response = requests.get(f"{API_BASE_URL}/content/recent")
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as e:
            st.error(f"Failed to fetch contributions data: {e}")
            return []
    else:
        # Return mock data
        return [
            {"type": "🎙️", "title": "Baul Song from Bengal", "lang": "Bengali", "time": "2 hours ago"},
            {"type": "📝", "title": "Pongal Recipe", "lang": "Tamil", "time": "5 hours ago"},
            {"type": "📷", "title": "Durga Puja Celebration", "lang": "Hindi", "time": "1 day ago"},
            {"type": "🎙️", "title": "Lavani Performance", "lang": "Marathi", "time": "2 days ago"}
        ]


def get_analytics_data():
    """
    Get analytics data based on real data setting
    
    Returns:
        dict: Dictionary containing analytics data
    """
    if should_use_real_data():
        try:
            response = requests.get(f"{API_BASE_URL}/stats")
            response.raise_for_status()
            api_data = response.json().get("stats", {})
            
            # Transform API data to match expected format
            return {
                "content_types": api_data.get("content_by_type", {}),
                "languages": list(api_data.get("language_distribution", {}).keys()),
                "regions": [],  # No region data in current API
                "time_series": [],  # No time series data in current API
                "quality_scores": []  # No quality scores in current API
            }
        except requests.RequestException as e:
            st.error(f"Failed to fetch analytics data: {e}")
            return {
                "content_types": {"Audio": 0, "Text": 0, "Images": 0},
                "languages": [],
                "regions": [],
                "time_series": [],
                "quality_scores": []
            }
    else:
        # Return mock data
        import numpy as np
        return {
            "content_types": {"Audio": 45, "Text": 67, "Images": 23},
            "languages": ["Hindi", "Bengali", "Tamil", "Telugu", "Marathi"],
            "regions": ["North India", "South India", "East India", "West India"],
            "time_series": np.random.randint(1, 10, 30).tolist(),
            "quality_scores": (np.random.beta(2, 1, 1000) * 100).tolist()
        }


def get_community_data():
    """
    Get community data based on real data setting
    
    Returns:
        dict: Dictionary containing community data
    """
    if should_use_real_data():
        try:
            # Fetch community stats
            stats_response = requests.get(f"{API_BASE_URL}/community/stats")
            stats_response.raise_for_status()
            stats = stats_response.json().get("stats", {})
            
            # Fetch leaderboard
            leaderboard_response = requests.get(f"{API_BASE_URL}/community/leaderboard")
            leaderboard_response.raise_for_status()
            leaderboard = leaderboard_response.json().get("leaderboard", [])
            
            return {
                "members": stats.get("total_members", 0),
                "experts": stats.get("experts", 0),
                "contributors": stats.get("total_contributors", 0),
                "projects": stats.get("projects", 0),
                "leaderboard": leaderboard,
                "challenges": [],  # Not implemented in API yet
                "discussions": []  # Not implemented in API yet
            }
        except requests.RequestException as e:
            st.error(f"Failed to fetch community data: {e}")
            return {
                "members": 0,
                "experts": 0,
                "contributors": 0,
                "projects": 0,
                "leaderboard": [],
                "challenges": [],
                "discussions": []
            }
    else:
        # Return mock data
        return {
            "members": 2847,
            "experts": 156,
            "contributors": 892,
            "projects": 34,
            "leaderboard": [
                {"rank": 1, "name": "Priya Sharma", "points": 2340},
                {"rank": 2, "name": "Rajesh Kumar", "points": 2180},
                {"rank": 3, "name": "Meera Nair", "points": 1950}
            ],
            "challenges": [
                {"title": "Festival Season Documentation", "participants": 45},
                {"title": "Endangered Languages Project", "participants": 23},
                {"title": "Recipe Revival Challenge", "participants": 67}
            ],
            "discussions": [
                {"title": "Best practices for recording folk songs", "replies": 34},
                {"title": "How to preserve family recipes?", "replies": 28},
                {"title": "Regional variations in wedding customs", "replies": 52}
            ]
        }
