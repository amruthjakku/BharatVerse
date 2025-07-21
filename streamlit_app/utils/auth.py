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
        # Check if GitLab auth is disabled
        self.disabled = os.getenv('DISABLE_GITLAB_AUTH', '').lower() == 'true'
        
        if self.disabled:
            self.client_id = None
            self.client_secret = None
            self.redirect_uri = None
            self.base_url = None
            self.scopes = None
            return
        
        # Detect environment and set appropriate redirect URI
        self.redirect_uri = self._detect_redirect_uri()
        
        # Try to get from Streamlit secrets first, then environment variables
        try:
            self.client_id = st.secrets.get("gitlab", {}).get("client_id") or os.getenv('GITLAB_CLIENT_ID')
            self.client_secret = st.secrets.get("gitlab", {}).get("client_secret") or os.getenv('GITLAB_CLIENT_SECRET')
            # Use detected redirect URI, fallback to secrets/env if detection fails
            detected_uri = self._detect_redirect_uri()
            self.redirect_uri = detected_uri or st.secrets.get("gitlab", {}).get("redirect_uri") or os.getenv('GITLAB_REDIRECT_URI')
            self.base_url = st.secrets.get("gitlab", {}).get("base_url") or os.getenv('GITLAB_BASE_URL', 'https://code.swecha.org')
            self.scopes = st.secrets.get("gitlab", {}).get("scopes") or os.getenv('GITLAB_SCOPES', 'api read_user profile email')
        except Exception:
            # Fallback to environment variables only
            self.client_id = os.getenv('GITLAB_CLIENT_ID')
            self.client_secret = os.getenv('GITLAB_CLIENT_SECRET')
            detected_uri = self._detect_redirect_uri()
            self.redirect_uri = detected_uri or os.getenv('GITLAB_REDIRECT_URI')
            self.base_url = os.getenv('GITLAB_BASE_URL', 'https://code.swecha.org')
            self.scopes = os.getenv('GITLAB_SCOPES', 'api read_user profile email')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            # Only show error once per session
            if 'gitlab_config_error_shown' not in st.session_state:
                st.session_state.gitlab_config_error_shown = True
                st.error("🚨 GitLab OAuth configuration is incomplete!")
                
                # Show debug information
                st.markdown("### 🔍 Debug Information:")
                st.code(f"""
Client ID: {'✅ Set' if self.client_id else '❌ Missing'}
Client Secret: {'✅ Set' if self.client_secret else '❌ Missing'}
Redirect URI: {'✅ Set' if self.redirect_uri else '❌ Missing'}
Base URL: {self.base_url or '❌ Missing'}
Detected Environment: {os.getenv('APP_ENV', 'Not set')}
""")
                
                st.markdown("### 🔧 Required Environment Variables for Render:")
                st.code("""
GITLAB_CLIENT_ID=your_application_id_from_gitlab
GITLAB_CLIENT_SECRET=your_secret_from_gitlab
GITLAB_BASE_URL=https://code.swecha.org
GITLAB_SCOPES=api read_user profile email
APP_ENV=render
""")
                
                st.info("💡 Set these environment variables in your Render dashboard → Environment tab")
    
    def _detect_redirect_uri(self) -> Optional[str]:
        """Detect the appropriate redirect URI based on the current environment"""
        try:
            # Get the current URL from Streamlit
            if hasattr(st, 'get_option') and st.get_option('server.baseUrlPath'):
                # Running on Streamlit Cloud or with custom base URL
                base_url = st.get_option('server.baseUrlPath')
                return f"{base_url}/callback"
            
            # Check environment variables for explicit environment setting
            app_env = os.getenv("APP_ENV", "").lower()
            
            if app_env == "local" or app_env == "development":
                return "http://localhost:8501/callback"
            elif app_env == "render":
                return "https://bharatverse.onrender.com/callback"
            elif app_env == "streamlit" or app_env == "streamlit_cloud":
                return "https://amruth-bharatverse.streamlit.app/callback"
            
            # Try to detect from current URL context
            try:
                # This is a fallback method - may not always work in Streamlit
                import streamlit.web.server.server as server
                if hasattr(server, 'Server') and server.Server._singleton:
                    port = server.Server._singleton._port
                    if port == 8501:
                        return "http://localhost:8501/callback"
            except:
                pass
            
            # Check for common deployment indicators
            if os.getenv("RENDER"):
                return "https://bharatverse.onrender.com/callback"
            elif os.getenv("STREAMLIT_SHARING") or "streamlit.app" in os.getenv("HOSTNAME", ""):
                return "https://amruth-bharatverse.streamlit.app/callback"
            
            # Default fallback
            return "http://localhost:8501/callback"
            
        except Exception as e:
            # If detection fails, return None to use fallback from env/secrets
            return None
    
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
        # Skip state validation for now since it's working in simplified mode
        # TODO: Implement proper state management that survives OAuth redirects
        
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
        if self.disabled:
            return False
        return 'user_info' in st.session_state and 'access_token' in st.session_state
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info (GitLab data)"""
        if self.disabled:
            return None
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
        
        # Debug information (can be removed in production)
        # st.info(f"OAuth callback received - Code: {code[:10]}..., State: {state[:10]}...")
        # st.info(f"Current session state keys: {list(st.session_state.keys())}")
        
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
    
    # If GitLab auth is disabled, don't show anything
    if auth.disabled:
        return
    
    if not all([auth.client_id, auth.client_secret, auth.redirect_uri]):
        # Only show error once per session
        if 'gitlab_login_error_shown' not in st.session_state:
            st.session_state.gitlab_login_error_shown = True
            st.error("GitLab OAuth is not properly configured.")
            st.info("💡 Run `python scripts/fix_gitlab_oauth.py` to fix this issue.")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Custom GitLab login button with logo
        gitlab_button_html = """
        <style>
        .gitlab-login-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #FC6D26;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.3s ease;
            width: 100%;
            box-sizing: border-box;
        }
        .gitlab-login-btn:hover {
            background-color: #E24329;
            color: white;
            text-decoration: none;
        }
        .gitlab-logo {
            width: 24px;
            height: 24px;
            margin-right: 12px;
            filter: brightness(0) invert(1);
        }
        </style>
        """
        st.markdown(gitlab_button_html, unsafe_allow_html=True)
        
        # Custom GitLab login button with official logo
        gitlab_login_html = f"""
        <div style="margin-bottom: 16px;">
            <button onclick="window.location.href='{auth.get_authorization_url()}'" 
                    class="gitlab-login-btn" 
                    style="display: flex; align-items: center; justify-content: center; background-color: #FC6D26; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; text-decoration: none; transition: background-color 0.3s ease; width: 100%; box-sizing: border-box;">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwMCIgaGVpZ2h0PSIyMzA1IiB2aWV3Qm94PSIwIDAgMjU2IDIzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWluWU1pbiBtZWV0Ij48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc1bDQ3LjEwNC0xNDQuOTdIODAuOTdsNDcuMTA0IDE0NC45N3oiIGZpbGw9IiNFMjQzMjkiLz48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc0TDgwLjk3IDkxLjEwNEgxNC45NTZsMTEzLjExOSAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDRMLjY0MiAxMzUuMTZhOS43NTIgOS43NTIgMCAwIDAgMy41NDIgMTAuOTAzbDEyMy44OTEgOTAuMDEyLTExMy4xMi0xNDQuOTd6IiBmaWxsPSIjRkNBMzI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDVIODAuOTdMNTIuNjAxIDMuNzljLTEuNDYtNC40OTMtNy44MTYtNC40OTItOS4yNzUgMGwtMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjxwYXRoIGQ9Ik0xMjguMDc1IDIzNi4wNzRsNDcuMTA0LTE0NC45N2g2Ni4wMTVsLTExMy4xMiAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTI0MS4xOTQgOTEuMTA0bDE0LjMxNCA0NC4wNTZhOS43NTIgOS43NTIgMCAwIDEtMy41NDMgMTAuOTAzbC0xMjMuODkgOTAuMDEyIDExMy4xMTktMTQ0Ljk3eiIgZmlsbD0iI0ZDQTMyNiIvPjxwYXRoIGQ9Ik0yNDEuMTk0IDkxLjEwNWgtNjYuMDE1bDI4LjM3LTg3LjMxNWMxLjQ2LTQuNDkzIDcuODE2LTQuNDkyIDkuMjc1IDBsMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjwvc3ZnPg==" 
                     style="width: 24px; height: 24px; margin-right: 12px; filter: brightness(0) invert(1);" alt="GitLab Logo">
                Login with GitLab
            </button>
        </div>
        """
        st.markdown(gitlab_login_html, unsafe_allow_html=True)
        
        # Fallback button for cases where HTML button doesn't work
        if st.button("🔗 Login with GitLab (Fallback)", use_container_width=True, type="secondary", key="gitlab_login_fallback"):
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
    if 'code' in st.query_params:
        handle_oauth_callback()