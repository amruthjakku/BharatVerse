import streamlit as st
import sys
from pathlib import Path
import requests
import os
from urllib.parse import urlencode

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def main():
    st.set_page_config(
        page_title="OAuth Debug - BharatVerse",
        page_icon="🔧",
        layout="wide"
    )
    
    st.markdown("# 🔧 OAuth Debug Tool")
    st.markdown("Debug GitLab OAuth configuration and test authentication flow")
    
    # Load configuration
    try:
        from streamlit_app.utils.auth import GitLabAuth, init_auth
        
        # Initialize auth
        try:
            init_auth()
        except Exception as e:
            st.warning(f"Auth initialization warning: {e}")
        
        auth = GitLabAuth()
        
        st.markdown("## 📋 Current Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔑 OAuth Settings")
            st.code(f"""
Client ID: {'✅ Set' if auth.client_id else '❌ Missing'}
Client Secret: {'✅ Set' if auth.client_secret else '❌ Missing'}
Base URL: {auth.base_url}
Redirect URI: {auth.redirect_uri}
Scopes: {auth.scopes}
Disabled: {auth.disabled}
Scopes: {auth.scopes or '❌ Missing'}
""")
    
    with col2:
        st.markdown("### 🌍 Environment")
        st.code(f"""
APP_ENV: {os.getenv('APP_ENV', 'Not set')}
DISABLE_GITLAB_AUTH: {os.getenv('DISABLE_GITLAB_AUTH', 'Not set')}
GITLAB_CLIENT_ID: {'✅ Set' if os.getenv('GITLAB_CLIENT_ID') else '❌ Missing'}
GITLAB_CLIENT_SECRET: {'✅ Set' if os.getenv('GITLAB_CLIENT_SECRET') else '❌ Missing'}
GITLAB_BASE_URL: {os.getenv('GITLAB_BASE_URL', 'Not set')}
""")
    
    st.markdown("---")
    
    # Query parameters
    st.markdown("## 🔗 Current URL Parameters")
    query_params = dict(st.query_params)
    if query_params:
        st.json(query_params)
        
        if 'code' in query_params:
            st.success("✅ OAuth callback detected!")
            st.info("The app should automatically handle this callback.")
    else:
        st.info("No query parameters in current URL")
    
    st.markdown("---")
    
    # Authentication status
    st.markdown("## 👤 Authentication Status")
    
    if auth.disabled:
        st.warning("🚫 GitLab authentication is disabled")
    elif not all([auth.client_id, auth.client_secret, auth.redirect_uri]):
        st.error("❌ OAuth configuration incomplete")
        st.markdown("**Missing configuration. Please set up GitLab OAuth credentials.**")
    else:
        # Check if authenticated
        is_authenticated = auth.is_authenticated()
        if is_authenticated:
            st.success("✅ User is authenticated")
            user_info = auth.get_current_user()
            if user_info:
                st.json(user_info)
        else:
            st.warning("⚠️ User is not authenticated")
            
            # Show OAuth URL
            try:
                oauth_url = auth.get_authorization_url()
                st.markdown("### 🔗 OAuth Authorization URL")
                st.code(oauth_url)
                st.markdown(f"**[Click here to login]({oauth_url})**")
            except Exception as e:
                st.error(f"Error generating OAuth URL: {e}")
    
    st.markdown("---")
    
    # Session state
    st.markdown("## 💾 Session State")
    if st.checkbox("Show session state"):
        session_keys = [k for k in st.session_state.keys() if not k.startswith('_')]
        if session_keys:
            session_data = {k: str(st.session_state[k])[:100] + "..." if len(str(st.session_state[k])) > 100 else st.session_state[k] for k in session_keys}
            st.json(session_data)
        else:
            st.info("No relevant session state data")
    
    st.markdown("---")
    
    # Manual callback test
    st.markdown("## 🧪 Manual Callback Test")
    if st.button("Test OAuth Callback Handler"):
        try:
            handle_oauth_callback()
            st.success("Callback handler executed successfully")
        except Exception as e:
            st.error(f"Callback handler error: {e}")
    
    # Clear session
    if st.button("🗑️ Clear Session State"):
        for key in list(st.session_state.keys()):
            if not key.startswith('_'):
                del st.session_state[key]
        st.success("Session state cleared")
        st.rerun()

if __name__ == "__main__":
    main()