"""
GitLab OAuth Authentication Module for BharatVerse
Handles OAuth flow with GitLab instance at code.swecha.org
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

class GitLabAuth:
    def __init__(self):
        self.client_id = os.getenv('GITLAB_CLIENT_ID')
        self.client_secret = os.getenv('GITLAB_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GITLAB_REDIRECT_URI')
        self.base_url = os.getenv('GITLAB_BASE_URL', 'https://code.swecha.org')
        self.scopes = os.getenv('GITLAB_SCOPES', 'api read_api read_user profile email')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            st.error("GitLab OAuth configuration is incomplete. Please check your environment variables.")
    
    def generate_state(self) -> str:
        """Generate a secure random state parameter for OAuth"""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self) -> str:
        """Generate GitLab OAuth authorization URL"""
        state = self.generate_state()
        st.session_state.oauth_state = state
        
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
        # Verify state parameter
        if state != st.session_state.get('oauth_state'):
            st.error("Invalid state parameter. Possible CSRF attack.")
            return None
        
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
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        token_url = f"{self.base_url}/oauth/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to refresh token: {e}")
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
            'token_expires_at', 'oauth_state'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        expires_at = st.session_state.get('token_expires_at')
        if not expires_at:
            return True
        return datetime.now() > datetime.fromisoformat(expires_at)


def handle_oauth_callback():
    """Handle OAuth callback from GitLab"""
    # Get query parameters from URL using new Streamlit API
    query_params = st.query_params
    
    if 'code' in query_params and 'state' in query_params:
        # Get code and state from query parameters
        code = query_params['code']
        state = query_params['state']
        
        auth = GitLabAuth()
        
        try:
            # Exchange code for token
            token_data = auth.exchange_code_for_token(code, state)
            if not token_data:
                st.error("Failed to exchange authorization code for token.")
                return
            
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
                # Create or update user in database
                db_user = user_manager.create_or_update_user(user_info)
                
                # Store both GitLab and database user info
                st.session_state.user_info = user_info
                st.session_state.db_user = db_user
                
                # Log login activity
                user_manager.log_user_activity(
                    db_user['id'], 
                    'login', 
                    {'method': 'gitlab_oauth', 'ip': 'unknown'}
                )
                
                st.success(f"Successfully authenticated as {user_info.get('name', 'Unknown User')}!")
                # Clear query parameters using new API
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Failed to get user information.")
                
        except Exception as e:
            st.error(f"Authentication error: {e}")
    
    elif 'error' in query_params:
        # Handle OAuth errors
        error = query_params['error']
        error_description = query_params.get('error_description', 'Unknown error')
        st.error(f"OAuth Error: {error} - {error_description}")


def render_login_button():
    """Render login button for GitLab OAuth"""
    auth = GitLabAuth()
    
    if not all([auth.client_id, auth.client_secret, auth.redirect_uri]):
        st.error("GitLab OAuth is not properly configured.")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Login with GitLab", use_container_width=True, type="primary"):
            auth_url = auth.get_authorization_url()
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            st.info("Redirecting to GitLab for authentication...")


def render_user_info():
    """Render authenticated user information"""
    auth = GitLabAuth()
    user_info = auth.get_current_user()
    
    if not user_info:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Profile")
        
        # User avatar and name
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=60)
        
        st.markdown(f"**{user_info.get('name', 'Unknown User')}**")
        st.markdown(f"@{user_info.get('username', 'unknown')}")
        
        if user_info.get('email'):
            st.markdown(f"📧 {user_info['email']}")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
            st.rerun()


def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        auth = GitLabAuth()
        if not auth.is_authenticated():
            st.warning("Please login to access this feature.")
            render_login_button()
            return None
        
        # Check if token is expired
        if auth.is_token_expired():
            st.warning("Your session has expired. Please login again.")
            auth.logout()
            render_login_button()
            return None
        
        return func(*args, **kwargs)
    
    return wrapper


def get_gitlab_api_headers() -> Optional[Dict[str, str]]:
    """Get authenticated GitLab API headers"""
    auth = GitLabAuth()
    if not auth.is_authenticated():
        return None
    
    access_token = st.session_state.get('access_token')
    if not access_token:
        return None
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


def make_gitlab_api_request(endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
    """Make authenticated request to GitLab API"""
    auth = GitLabAuth()
    headers = get_gitlab_api_headers()
    
    if not headers:
        return None
    
    url = f"{auth.base_url}/api/v4/{endpoint.lstrip('/')}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"GitLab API request failed: {e}")
        return None


# Initialize authentication on module import
def init_auth():
    """Initialize authentication system"""
    # Handle OAuth callback if present
    if 'code' in st.experimental_get_query_params():
        handle_oauth_callback()