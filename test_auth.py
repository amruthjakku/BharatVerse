"""
Simple test script for GitLab OAuth authentication
This script tests the authentication without requiring database connections
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env.local')

# Import authentication modules
from streamlit_app.utils.auth import GitLabAuth, handle_oauth_callback, render_login_button, render_user_info, init_auth

# Page configuration
st.set_page_config(
    page_title="BharatVerse - GitLab OAuth Test",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication
init_auth()

# Handle OAuth callback if present
handle_oauth_callback()

# Main content
st.markdown("# 🦊 GitLab OAuth Authentication Test")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## 🔐 Authentication Status")
    
    auth = GitLabAuth()
    if auth.is_authenticated():
        st.success("✅ Authenticated")
        render_user_info()
    else:
        st.warning("❌ Not Authenticated")
        st.markdown("### Login Required")
        render_login_button()

# Main content area
auth = GitLabAuth()

if auth.is_authenticated():
    user_info = auth.get_current_user()
    
    st.success(f"🎉 Successfully authenticated as **{user_info.get('name', 'Unknown User')}**!")
    
    # Display user information
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=150)
        else:
            st.markdown("### 👤")
    
    with col2:
        st.markdown("### User Information")
        st.markdown(f"**Name:** {user_info.get('name', 'Not provided')}")
        st.markdown(f"**Username:** @{user_info.get('username', 'unknown')}")
        st.markdown(f"**Email:** {user_info.get('email', 'Not provided')}")
        st.markdown(f"**GitLab ID:** {user_info.get('id', 'Unknown')}")
        
        if user_info.get('bio'):
            st.markdown(f"**Bio:** {user_info['bio']}")
        
        if user_info.get('web_url'):
            st.markdown(f"**Profile:** [{user_info['web_url']}]({user_info['web_url']})")
    
    st.markdown("---")
    
    # Test API functionality
    st.markdown("### 🛠️ API Test")
    
    from streamlit_app.utils.auth import make_gitlab_api_request
    
    if st.button("🔄 Test API - Get User Info"):
        with st.spinner("Making API request..."):
            result = make_gitlab_api_request("user")
            if result:
                st.success("✅ API request successful!")
                st.json(result)
            else:
                st.error("❌ API request failed")
    
    if st.button("📁 Test API - Get Projects"):
        with st.spinner("Loading projects..."):
            result = make_gitlab_api_request("projects?owned=true&per_page=5")
            if result:
                st.success(f"✅ Found {len(result)} projects!")
                for project in result:
                    st.markdown(f"- **{project.get('name', 'Unnamed')}**: {project.get('description', 'No description')}")
            else:
                st.error("❌ Failed to load projects")

else:
    st.info("👋 Welcome to the GitLab OAuth authentication test!")
    st.markdown("""
    This test page demonstrates the GitLab OAuth integration for BharatVerse.
    
    **Features:**
    - 🔐 Secure OAuth 2.0 authentication with GitLab
    - 👤 User profile information retrieval
    - 🛠️ GitLab API integration
    - 🔄 Token management and refresh
    
    **To test:**
    1. Click the "Login with GitLab" button in the sidebar
    2. You'll be redirected to GitLab for authentication
    3. After successful login, you'll be redirected back here
    4. Your user information and API access will be displayed
    
    **Configuration:**
    - GitLab Instance: `https://code.swecha.org`
    - Callback URL: `http://localhost:8502/callback`
    - Scopes: API access, user info, repositories, and more
    """)
    
    # Display configuration info
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")
    
    config_info = {
        "GitLab Base URL": os.getenv('GITLAB_BASE_URL', 'Not configured'),
        "Client ID": os.getenv('GITLAB_CLIENT_ID', 'Not configured')[:20] + "..." if os.getenv('GITLAB_CLIENT_ID') else 'Not configured',
        "Redirect URI": os.getenv('GITLAB_REDIRECT_URI', 'Not configured'),
        "Scopes": os.getenv('GITLAB_SCOPES', 'Not configured')
    }
    
    for key, value in config_info.items():
        st.markdown(f"**{key}:** `{value}`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🦊 GitLab OAuth Test for BharatVerse | Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)