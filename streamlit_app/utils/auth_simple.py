"""
Simplified GitLab OAuth Authentication Module for BharatVerse
Temporarily disables state validation to get OAuth working
"""

import os
import streamlit as st
import requests
import json
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
from .user_manager import user_manager

class GitLabAuthSimple:
    def __init__(self):
        self.client_id = os.getenv('GITLAB_CLIENT_ID')
        self.client_secret = os.getenv('GITLAB_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GITLAB_REDIRECT_URI')
        self.base_url = os.getenv('GITLAB_BASE_URL', 'https://code.swecha.org')
        self.scopes = os.getenv('GITLAB_SCOPES', 'api read_api read_user profile email')
    
    def generate_state(self) -> str:
        """Generate a random state parameter for CSRF protection"""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self) -> str:
        """Generate GitLab OAuth authorization URL"""
        # Don't store state for now - just generate it
        state = self.generate_state()
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scopes,
            'state': state
        }
        
        return f"{self.base_url}/oauth/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        # Skip state validation for now
        st.info("Skipping state validation (simplified mode)")
        
        token_url = f"{self.base_url}/oauth/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to exchange code for token: {e}")
            st.error(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from GitLab API"""
        headers = {'Authorization': f'Bearer {access_token}'}
        user_url = f"{self.base_url}/api/v4/user"
        
        try:
            response = requests.get(user_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to get user info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return 'user_info' in st.session_state and 'access_token' in st.session_state
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info (GitLab data)"""
        return st.session_state.get('user_info')
    
    def get_current_db_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info (Database data)"""
        return st.session_state.get('db_user')
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        db_user = self.get_current_db_user()
        return db_user and db_user.get('role') == 'admin'
    
    def is_moderator(self) -> bool:
        """Check if current user is moderator or admin"""
        db_user = self.get_current_db_user()
        return db_user and db_user.get('role') in ['admin', 'moderator']
    
    def logout(self):
        """Clear authentication session"""
        keys_to_remove = [
            'user_info', 'access_token', 'refresh_token', 
            'token_expires_at', 'db_user'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]


def handle_oauth_callback_simple():
    """Handle OAuth callback from GitLab (simplified version)"""
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']
        
        st.info(f"OAuth callback received - Code: {code[:10]}..., State: {state[:10]}...")
        
        auth = GitLabAuthSimple()
        
        try:
            # Exchange code for token
            token_data = auth.exchange_code_for_token(code, state)
            if not token_data:
                st.error("Failed to exchange authorization code for token.")
                return
            
            st.success("✅ Token exchange successful!")
            
            # Store token information
            st.session_state.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                st.session_state.refresh_token = token_data['refresh_token']
            
            # Calculate token expiration
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            st.session_state.token_expires_at = expires_at.isoformat()
            
            # Get user information
            user_info = auth.get_user_info(token_data['access_token'])
            if user_info:
                st.success("✅ User info retrieved!")
                
                # Create or update user in database
                db_user = user_manager.create_or_update_user(user_info)
                
                # Store both GitLab and database user info
                st.session_state.user_info = user_info
                st.session_state.db_user = db_user
                
                # Log login activity
                user_manager.log_user_activity(
                    db_user['id'], 
                    'login', 
                    {'method': 'gitlab_oauth_simple', 'ip': 'unknown'}
                )
                
                st.success(f"🎉 Successfully authenticated as {user_info.get('name', 'Unknown User')}!")
                st.info(f"Welcome @{user_info.get('username', 'unknown')}!")
                
                # Clear query parameters
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Failed to get user information.")
                
        except Exception as e:
            st.error(f"Authentication error: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
    
    elif 'error' in query_params:
        error = query_params['error']
        error_description = query_params.get('error_description', 'Unknown error')
        st.error(f"OAuth Error: {error} - {error_description}")


def render_login_button_simple():
    """Render login button for GitLab OAuth (simplified)"""
    auth = GitLabAuthSimple()
    
    if not all([auth.client_id, auth.client_secret, auth.redirect_uri]):
        st.error("OAuth configuration incomplete. Please check environment variables.")
        return
    
    auth_url = auth.get_authorization_url()
    
    st.markdown("### 🔐 Login with GitLab")
    st.markdown(f"**GitLab Instance:** {auth.base_url}")
    
    if st.button("🦊 Login with GitLab", type="primary", use_container_width=True):
        st.markdown(f"[Click here if not redirected automatically]({auth_url})")
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)


def render_user_info_simple():
    """Render user information (simplified)"""
    auth = GitLabAuthSimple()
    user_info = auth.get_current_user()
    db_user = auth.get_current_db_user()
    
    if user_info and db_user:
        st.markdown("### 👤 Logged In")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if user_info.get('avatar_url'):
                st.image(user_info['avatar_url'], width=60)
        
        with col2:
            st.markdown(f"**{user_info.get('name', 'Unknown')}**")
            st.markdown(f"@{user_info.get('username', 'unknown')}")
            st.markdown(f"Role: {db_user.get('role', 'user').title()}")
        
        if st.button("🚪 Logout", type="secondary"):
            auth.logout()
            st.rerun()