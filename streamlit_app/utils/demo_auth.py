"""
Demo Authentication System for BharatVerse Community Features
Provides a simple authentication system for testing community features
"""

import streamlit as st
from typing import Optional, Dict, Any
import uuid

class DemoAuth:
    """Simple demo authentication system"""
    
    def __init__(self):
        self.demo_users = {
            "priya_kolkata": {
                "id": str(uuid.uuid4()),
                "username": "priya_kolkata",
                "full_name": "Priya Chatterjee",
                "email": "priya@example.com",
                "region": "West Bengal",
                "preferred_language": "Bengali",
                "bio": "Folk music enthusiast from Kolkata, passionate about preserving Bengali cultural heritage.",
                "languages": ["Bengali", "Hindi", "English"],
                "interests": ["Folk Music", "Traditional Dance", "Festival Celebrations"]
            },
            "rajesh_mumbai": {
                "id": str(uuid.uuid4()),
                "username": "rajesh_mumbai",
                "full_name": "Rajesh Sharma",
                "email": "rajesh@example.com",
                "region": "Maharashtra",
                "preferred_language": "Hindi",
                "bio": "Traditional recipe collector and food historian from Mumbai.",
                "languages": ["Hindi", "Marathi", "English"],
                "interests": ["Traditional Recipes", "Festival Celebrations", "Handicrafts & Arts"]
            },
            "anita_delhi": {
                "id": str(uuid.uuid4()),
                "username": "anita_delhi",
                "full_name": "Anita Singh",
                "email": "anita@example.com",
                "region": "Delhi",
                "preferred_language": "Hindi",
                "bio": "Cultural researcher and storyteller, documenting oral traditions of North India.",
                "languages": ["Hindi", "Punjabi", "English"],
                "interests": ["Oral Storytelling", "Folk Music", "Traditional Recipes"]
            },
            "demo_user": {
                "id": str(uuid.uuid4()),
                "username": "demo_user",
                "full_name": "Demo User",
                "email": "demo@example.com",
                "region": "India",
                "preferred_language": "English",
                "bio": "Demo user for testing BharatVerse community features.",
                "languages": ["English", "Hindi"],
                "interests": ["Folk Music", "Festival Celebrations", "Oral Storytelling"]
            }
        }
    
    def show_login_form(self):
        """Show simple login form for demo"""
        st.markdown("### 🔐 Demo Login")
        st.info("Choose a demo user to explore community features:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_user = st.selectbox(
                "Select Demo User:",
                options=list(self.demo_users.keys()),
                format_func=lambda x: f"{self.demo_users[x]['full_name']} ({x})"
            )
        
        with col2:
            if st.button("🚀 Login as Demo User", use_container_width=True):
                user_data = self.demo_users[selected_user]
                st.session_state['demo_user'] = user_data
                st.session_state['demo_authenticated'] = True
                st.rerun()
        
        # Show user info
        if selected_user:
            user = self.demo_users[selected_user]
            st.markdown(f"**{user['full_name']}**")
            st.markdown(f"📍 {user['region']}")
            st.markdown(f"🗣️ Languages: {', '.join(user['languages'])}")
            st.markdown(f"❤️ Interests: {', '.join(user['interests'])}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('demo_authenticated', False)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if self.is_authenticated():
            return st.session_state.get('demo_user')
        return None
    
    def get_current_db_user(self) -> Optional[Dict[str, Any]]:
        """Get current user in database format"""
        user = self.get_current_user()
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'email': user['email'],
                'region': user['region'],
                'preferred_language': user['preferred_language'],
                'role': 'user'  # Default role
            }
        return None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        user = self.get_current_user()
        return user and user.get('username') == 'demo_user'  # Demo user is admin
    
    def is_moderator(self) -> bool:
        """Check if current user is moderator or admin"""
        return self.is_admin()  # For demo, admin is also moderator
    
    def logout(self):
        """Logout current user"""
        if 'demo_user' in st.session_state:
            del st.session_state['demo_user']
        if 'demo_authenticated' in st.session_state:
            del st.session_state['demo_authenticated']
        st.rerun()
    
    def show_user_info(self):
        """Show current user info in sidebar"""
        if self.is_authenticated():
            user = self.get_current_user()
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Current User")
            st.sidebar.markdown(f"**{user['full_name']}**")
            st.sidebar.markdown(f"📍 {user['region']}")
            st.sidebar.markdown(f"🗣️ {user['preferred_language']}")
            
            if st.sidebar.button("🚪 Logout"):
                self.logout()
        else:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🔐 Authentication")
            st.sidebar.info("Please login to access community features")

# Global demo auth instance
demo_auth = DemoAuth()