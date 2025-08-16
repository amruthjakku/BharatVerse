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
            
            # Priority order for redirect URI:
            # 1. Explicit redirect_uri in secrets (highest priority)
            # 2. Auto-detected URI based on environment
            # 3. Environment variable fallback
            secrets_redirect_uri = st.secrets.get("gitlab", {}).get("redirect_uri")
            detected_uri = self._detect_redirect_uri()
            env_redirect_uri = os.getenv('GITLAB_REDIRECT_URI')
            
            self.redirect_uri = secrets_redirect_uri or detected_uri or env_redirect_uri
            
            # Debug logging for redirect URI selection
            if hasattr(st, 'write') and st.secrets.get("app", {}).get("debug"):
                st.write("🔍 OAuth Debug Info:")
                st.write(f"- Secrets redirect URI: {secrets_redirect_uri}")
                st.write(f"- Detected redirect URI: {detected_uri}")
                st.write(f"- Env redirect URI: {env_redirect_uri}")
                st.write(f"- Final redirect URI: {self.redirect_uri}")
            
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
            # First check if we have an explicit override in secrets
            try:
                explicit_uri = st.secrets.get("gitlab", {}).get("redirect_uri")
                if explicit_uri:
                    return explicit_uri
            except:
                pass
            
            # Get the current URL from Streamlit
            if hasattr(st, 'get_option') and st.get_option('server.baseUrlPath'):
                # Running on Streamlit Cloud or with custom base URL
                base_url = st.get_option('server.baseUrlPath')
                return f"{base_url}/callback"
            
            # Check environment variables for explicit environment setting
            app_env = os.getenv("APP_ENV", "").lower()
            
            # Also check Streamlit secrets for APP_ENV
            try:
                if not app_env:
                    app_env = st.secrets.get("app", {}).get("APP_ENV", "").lower()
            except:
                pass
            
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
            elif (os.getenv("STREAMLIT_SHARING") or 
                  "streamlit.app" in os.getenv("HOSTNAME", "") or
                  "streamlit" in os.getenv("SERVER_NAME", "") or
                  os.getenv("STREAMLIT_SERVER_PORT")):
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
        
        # Debug information
        if st.secrets.get("app", {}).get("debug"):
            st.write("🔍 OAuth Token Exchange Debug:")
            st.write(f"- Token URL: {token_url}")
            st.write(f"- Client ID: {self.client_id[:10]}...")
            st.write(f"- Redirect URI: {self.redirect_uri}")
            st.write(f"- Code: {code[:10]}...")
        
        try:
            response = requests.post(token_url, data=data)
            
            # Debug response
            if st.secrets.get("app", {}).get("debug"):
                st.write(f"- Response Status: {response.status_code}")
                if response.status_code != 200:
                    st.write(f"- Response Text: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to exchange code for token: {e}")
            
            # Additional error details for debugging
            if hasattr(e, 'response') and e.response is not None:
                st.error(f"Response status: {e.response.status_code}")
                st.error(f"Response text: {e.response.text}")
                
                # Check for common OAuth errors
                if e.response.status_code == 401:
                    st.error("🚨 **OAuth Configuration Issue Detected**")
                    
                    # Try to parse the error response
                    try:
                        error_data = e.response.json()
                        error_type = error_data.get('error', 'unknown')
                        error_desc = error_data.get('error_description', 'No description')
                        
                        if error_type == 'invalid_client':
                            st.markdown(f"""
                            **Error:** `{error_type}`  
                            **Description:** {error_desc}
                            
                            **Most likely cause:** Redirect URI mismatch
                            
                            **Current redirect URI:** `{self.redirect_uri}`
                            
                            **To fix:**
                            1. Go to https://code.swecha.org/-/profile/applications
                            2. Find your application with Client ID: `{self.client_id[:10]}...`
                            3. Update the Redirect URI to exactly match: `{self.redirect_uri}`
                            4. Make sure there are no extra spaces or characters
                            
                            **Alternative:** Add multiple redirect URIs:
                            - `http://localhost:8501/callback` (for local development)
                            - `https://amruth-bharatverse.streamlit.app/callback` (for production)
                            """)
                        else:
                            st.markdown(f"""
                            **Error:** `{error_type}`  
                            **Description:** {error_desc}
                            
                            **Possible causes:**
                            1. **Client credentials mismatch** - Check if Client ID and Secret are correct
                            2. **Redirect URI mismatch** - The redirect URI must exactly match what's configured in GitLab
                            3. **Authorization code expired** - Try the login process again
                            4. **GitLab application not properly configured**
                            
                            **To fix:**
                            1. Go to https://code.swecha.org/-/profile/applications
                            2. Check your application settings
                            3. Ensure redirect URI is exactly: `{self.redirect_uri}`
                            4. Verify Client ID and Secret match your configuration
                            """)
                    except:
                        # Fallback if we can't parse the error response
                        st.markdown(f"""
                        **Possible causes:**
                        1. **Client credentials mismatch** - Check if Client ID and Secret are correct
                        2. **Redirect URI mismatch** - The redirect URI must exactly match what's configured in GitLab
                        3. **Authorization code expired** - Try the login process again
                        4. **GitLab application not properly configured**
                        
                        **Current redirect URI:** `{self.redirect_uri}`
                        
                        **To fix:**
                        1. Go to https://code.swecha.org/-/profile/applications
                        2. Check your application settings
                        3. Ensure redirect URI is exactly: `{self.redirect_uri}`
                        4. Verify Client ID and Secret match your configuration
                        """)
            
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
        """Temporarily disable admin role checks"""
        return False
    
    def is_moderator(self) -> bool:
        """Temporarily disable moderator role checks"""
        return False
    
    def save_persistent_login(self):
        """Save login state for persistence across sessions"""
        if not self.is_authenticated():
            return
            
        # Save to a persistent key in session state that survives page reloads
        persistent_data = {
            'user_info': st.session_state.get('user_info'),
            'access_token': st.session_state.get('access_token'),
            'refresh_token': st.session_state.get('refresh_token'),
            'token_expires_at': st.session_state.get('token_expires_at'),
            'saved_at': datetime.now().isoformat(),
            'remember_login': True
        }
        
        # Use a special key that's less likely to be cleared
        st.session_state['_persistent_auth'] = persistent_data
    
    def restore_persistent_login(self) -> bool:
        """Restore login state from persistent storage"""
        if self.disabled:
            return False
            
        persistent_data = st.session_state.get('_persistent_auth')
        if not persistent_data or not persistent_data.get('remember_login'):
            return False
        
        # Check if saved data is not too old (7 days max)
        saved_at = persistent_data.get('saved_at')
        if saved_at:
            saved_time = datetime.fromisoformat(saved_at)
            if datetime.now() - saved_time > timedelta(days=7):
                # Clear old persistent data
                if '_persistent_auth' in st.session_state:
                    del st.session_state['_persistent_auth']
                return False
        
        # Check if token is still valid
        token_expires_at = persistent_data.get('token_expires_at')
        if token_expires_at:
            expires_time = datetime.fromisoformat(token_expires_at)
            if datetime.now() > expires_time:
                # Try to refresh token if available
                refresh_token = persistent_data.get('refresh_token')
                if refresh_token:
                    token_data = self.refresh_token(refresh_token)
                    if token_data:
                        # Update with new token data
                        persistent_data['access_token'] = token_data['access_token']
                        if 'refresh_token' in token_data:
                            persistent_data['refresh_token'] = token_data['refresh_token']
                        
                        expires_in = token_data.get('expires_in', 7200)
                        expires_at = datetime.now() + timedelta(seconds=expires_in)
                        persistent_data['token_expires_at'] = expires_at.isoformat()
                        
                        # Save updated data
                        st.session_state['_persistent_auth'] = persistent_data
                    else:
                        # Refresh failed, clear persistent data
                        if '_persistent_auth' in st.session_state:
                            del st.session_state['_persistent_auth']
                        return False
                else:
                    # No refresh token, clear persistent data
                    if '_persistent_auth' in st.session_state:
                        del st.session_state['_persistent_auth']
                    return False
        
        # Restore session state
        st.session_state['user_info'] = persistent_data.get('user_info')
        st.session_state['access_token'] = persistent_data.get('access_token')
        st.session_state['refresh_token'] = persistent_data.get('refresh_token')
        st.session_state['token_expires_at'] = persistent_data.get('token_expires_at')
        
        return True
    
    def logout(self, clear_persistent: bool = True):
        """Clear authentication session"""
        keys_to_remove = [
            'user_info', 'access_token', 'refresh_token', 
            'token_expires_at', 'oauth_state'
        ]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        # Also clear persistent login if requested
        if clear_persistent and '_persistent_auth' in st.session_state:
            del st.session_state['_persistent_auth']
    
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
                
                # Save persistent login (remember me is enabled by default)
                auth.save_persistent_login()
                
                st.success(f"Successfully authenticated as {user_info.get('name', 'Unknown User')}!")
                st.info("✅ Login will be remembered for 7 days")
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
        # Get OAuth URL
        auth_url = auth.get_authorization_url()
        
        # Try to use st.link_button if available (Streamlit 1.29+)
        try:
            if st.link_button("🔗 Login with GitLab", auth_url, use_container_width=True, type="primary"):
                pass  # Link button handles the redirect
        except (AttributeError, TypeError):
            # Fallback for older Streamlit versions
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <a href="{auth_url}" target="_self" style="
                    display: inline-block;
                    background-color: #FC6D26;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 16px;
                    border: none;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    width: 100%;
                    box-sizing: border-box;
                    text-align: center;
                ">
                    🔗 Login with GitLab
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            # Also show as regular button for backup
            if st.button("🔗 Login with GitLab (Backup)", use_container_width=True, type="secondary", key="gitlab_login_backup"):
                st.success("🔄 Please use the orange link above to login with GitLab")
                st.markdown(f"**Direct link:** {auth_url}")
        
        # Always show a direct link as backup
        st.markdown("---")
        st.markdown("**Alternative:** If the button above doesn't work, use this direct link:")
        st.markdown(f"### 🔗 **[Login with GitLab (Direct Link)]({auth_url})**")
        
        # Remember me info
        st.markdown("---")
        st.info("🔒 **Auto-Remember:** Your login will be automatically remembered for 7 days for convenience.")
        
        # Show the OAuth URL for debugging
        if st.checkbox("🔍 Show OAuth Debug Info", key="oauth_debug"):
            st.code(f"OAuth URL: {auth_url}")
            
            # Show configuration details
            st.markdown("### Configuration Details:")
            st.code(f"""
Client ID: {'✅ Set' if auth.client_id else '❌ Missing'}
Client Secret: {'✅ Set' if auth.client_secret else '❌ Missing'}
Redirect URI: {auth.redirect_uri}
Base URL: {auth.base_url}
Scopes: {auth.scopes}
Environment: {os.getenv('APP_ENV', 'Not set')}
""")


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
        
        # Login persistence status
        persistent_data = st.session_state.get('_persistent_auth')
        if persistent_data and persistent_data.get('remember_login'):
            st.markdown("✅ **Login remembered**")
            st.caption("You'll stay logged in for 7 days")
        
        # User dashboard link
        st.markdown("---")
        if st.button("👤 My Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/09_👤_My_Dashboard.py")
        
        # Logout options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚪 Logout", use_container_width=True, help="Logout but keep login remembered"):
                auth.logout(clear_persistent=False)
                st.success("Logged out! Login will be restored next visit.")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Forget", use_container_width=True, help="Logout and forget login", type="secondary"):
                auth.logout(clear_persistent=True)
                st.success("Logged out and login forgotten!")
                st.rerun()
        
        # Admin panel for admins only
        if auth.is_admin():
            st.markdown("---")
            st.markdown("### 🛡️ Admin Panel")
            
            # Quick admin stats
            try:
                from utils.database_viewer import get_sqlite_user_stats
                stats = get_sqlite_user_stats()
                
                if 'error' not in stats:
                    st.metric("Total Users", stats['total_users'])
                    st.metric("Active Users", stats['active_users'])
                else:
                    st.caption("Stats unavailable")
                    
            except Exception as e:
                st.caption("Stats loading...")
            
            # Admin dashboard button
            if st.button("🛡️ Admin Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/08_🛡️_Admin_Dashboard.py")
            
            # Quick admin links
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗄️ Database", use_container_width=True):
                    st.switch_page("pages/07_🗄️_Database_Admin.py")
            with col2:
                st.caption("Performance page disabled")


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


# Global auth manager instance
_auth_manager = None

def get_auth_manager():
    """Get the global authentication manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GitLabAuth()
    return _auth_manager

# Initialize authentication on module import
def init_auth():
    """Initialize authentication system"""
    auth = get_auth_manager()
    
    # Try to restore persistent login first (if not already authenticated)
    if not auth.is_authenticated():
        restored = auth.restore_persistent_login()
        if restored:
            # Successfully restored login
            user_info = auth.get_current_user()
            if user_info:
                st.toast(f"Welcome back, {user_info.get('name', 'User')}! 👋", icon="✅")
    
    # Handle OAuth callback if present
    if 'code' in st.query_params:
        handle_oauth_callback()