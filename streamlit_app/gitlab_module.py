"""
GitLab Integration Module for BharatVerse
Demonstrates authenticated GitLab API usage
"""

import streamlit as st
from streamlit_app.utils.auth import GitLabAuth, require_auth, make_gitlab_api_request
from datetime import datetime
import json

@require_auth
def gitlab_integration_page():
    """GitLab integration page with authenticated features"""
    # GitLab header with official logo
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwMCIgaGVpZ2h0PSIyMzA1IiB2aWV3Qm94PSIwIDAgMjU2IDIzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWluWU1pbiBtZWV0Ij48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc1bDQ3LjEwNC0xNDQuOTdIODAuOTdsNDcuMTA0IDE0NC45N3oiIGZpbGw9IiNFMjQzMjkiLz48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc0TDgwLjk3IDkxLjEwNEgxNC45NTZsMTEzLjExOSAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDRMLjY0MiAxMzUuMTZhOS43NTIgOS43NTIgMCAwIDAgMy41NDIgMTAuOTAzbDEyMy44OTEgOTAuMDEyLTExMy4xMi0xNDQuOTd6IiBmaWxsPSIjRkNBMzI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDVIODAuOTdMNTIuNjAxIDMuNzljLTEuNDYtNC40OTMtNy44MTYtNC40OTItOS4yNzUgMGwtMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjxwYXRoIGQ9Ik0xMjguMDc1IDIzNi4wNzRsNDcuMTA0LTE0NC45N2g2Ni4wMTVsLTExMy4xMiAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTI0MS4xOTQgOTEuMTA0bDE0LjMxNCA0NC4wNTZhOS43NTIgOS43NTIgMCAwIDEtMy41NDMgMTAuOTAzbC0xMjMuODkgOTAuMDEyIDExMy4xMTktMTQ0Ljk3eiIgZmlsbD0iI0ZDQTMyNiIvPjxwYXRoIGQ9Ik0yNDEuMTk0IDkxLjEwNWgtNjYuMDE1bDI4LjM3LTg3LjMxNWMxLjQ2LTQuNDkzIDcuODE2LTQuNDkyIDkuMjc1IDBsMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjwvc3ZnPg==" 
             style="width: 32px; height: 32px; margin-right: 12px;" alt="GitLab Logo">
        <h2 style="margin: 0; color: #FC6D26;">GitLab Integration</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    auth = GitLabAuth()
    user_info = auth.get_current_user()
    
    if not user_info:
        st.error("Authentication required")
        return
    
    # User profile section
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if user_info.get('avatar_url'):
            st.image(user_info['avatar_url'], width=150)
        else:
            st.markdown("### 👤")
    
    with col2:
        st.markdown(f"### Welcome, {user_info.get('name', 'Unknown User')}!")
        st.markdown(f"**Username:** @{user_info.get('username', 'unknown')}")
        st.markdown(f"**Email:** {user_info.get('email', 'Not provided')}")
        st.markdown(f"**GitLab ID:** {user_info.get('id', 'Unknown')}")
        
        if user_info.get('bio'):
            st.markdown(f"**Bio:** {user_info['bio']}")
        
        if user_info.get('web_url'):
            st.markdown(f"**Profile:** [{user_info['web_url']}]({user_info['web_url']})")
        
        # Logout section
        st.markdown("---")
        col_logout1, col_logout2 = st.columns(2)
        
        with col_logout1:
            if st.button("🚪 Logout", use_container_width=True, help="Logout but remember login"):
                auth.logout(clear_persistent=False)
                st.success("Logged out! You'll be automatically logged in next time.")
                st.rerun()
        
        with col_logout2:
            if st.button("🗑️ Forget Login", use_container_width=True, type="secondary", help="Logout and forget login"):
                auth.logout(clear_persistent=True)
                st.success("Logged out and login forgotten!")
                st.rerun()
    
    st.markdown("---")
    
    # Tabs for different GitLab features
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Profile Stats", "📁 Projects", "🔑 Access Tokens", "🛠️ API Test"])
    
    with tab1:
        st.markdown("### 📊 Profile Statistics")
        
        # Display user stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Public Projects", user_info.get('public_repos', 0))
        
        with col2:
            followers = user_info.get('followers', 0)
            st.metric("Followers", followers)
        
        with col3:
            following = user_info.get('following', 0)
            st.metric("Following", following)
        
        with col4:
            created_at = user_info.get('created_at', '')
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    days_since = (datetime.now(created_date.tzinfo) - created_date).days
                    st.metric("Days on GitLab", days_since)
                except:
                    st.metric("Days on GitLab", "Unknown")
            else:
                st.metric("Days on GitLab", "Unknown")
        
        # Additional profile information
        if user_info.get('location'):
            st.markdown(f"**📍 Location:** {user_info['location']}")
        
        if user_info.get('organization'):
            st.markdown(f"**🏢 Organization:** {user_info['organization']}")
        
        if user_info.get('job_title'):
            st.markdown(f"**💼 Job Title:** {user_info['job_title']}")
    
    with tab2:
        st.markdown("### 📁 Your Projects")
        
        if st.button("🔄 Load Projects", type="primary"):
            with st.spinner("Loading your projects..."):
                projects = make_gitlab_api_request("projects?owned=true&per_page=10")
                
                if projects:
                    st.session_state.user_projects = projects
                    st.success(f"Loaded {len(projects)} projects")
                else:
                    st.warning("No projects found or failed to load projects")
        
        # Display cached projects
        if 'user_projects' in st.session_state:
            projects = st.session_state.user_projects
            
            if projects:
                for project in projects:
                    with st.expander(f"📁 {project.get('name', 'Unnamed Project')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Description:** {project.get('description', 'No description')}")
                            st.markdown(f"**Visibility:** {project.get('visibility', 'Unknown')}")
                            st.markdown(f"**Language:** {project.get('default_branch', 'Unknown')}")
                            
                            if project.get('web_url'):
                                st.markdown(f"**URL:** [{project['web_url']}]({project['web_url']})")
                        
                        with col2:
                            st.metric("Stars", project.get('star_count', 0))
                            st.metric("Forks", project.get('forks_count', 0))
                            st.metric("Issues", project.get('open_issues_count', 0))
            else:
                st.info("No projects found")
    
    with tab3:
        st.markdown("### 🔑 Access Token Information")
        
        # Display current token info (without showing the actual token)
        if 'access_token' in st.session_state:
            st.success("✅ Access token is active")
            
            expires_at = st.session_state.get('token_expires_at')
            if expires_at:
                try:
                    exp_time = datetime.fromisoformat(expires_at)
                    time_left = exp_time - datetime.now()
                    
                    if time_left.total_seconds() > 0:
                        hours_left = int(time_left.total_seconds() // 3600)
                        minutes_left = int((time_left.total_seconds() % 3600) // 60)
                        st.info(f"⏰ Token expires in {hours_left}h {minutes_left}m")
                    else:
                        st.warning("⚠️ Token has expired")
                except:
                    st.info("⏰ Token expiration time unknown")
            
            # Token scopes
            st.markdown("**🔐 Granted Scopes:**")
            scopes = auth.scopes.split()
            for scope in scopes:
                st.markdown(f"- `{scope}`")
        else:
            st.error("❌ No access token found")
    
    with tab4:
        st.markdown("### 🛠️ API Test")
        st.markdown("Test GitLab API endpoints with your authenticated session.")
        
        # API endpoint tester
        endpoint = st.text_input(
            "API Endpoint (relative to /api/v4/)",
            value="user",
            help="Enter a GitLab API endpoint to test (e.g., 'user', 'projects', 'groups')"
        )
        
        method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])
        
        if method in ["POST", "PUT"]:
            json_data = st.text_area(
                "JSON Data (optional)",
                value="{}",
                help="Enter JSON data for POST/PUT requests"
            )
        else:
            json_data = None
        
        if st.button("🚀 Test API Call"):
            with st.spinner(f"Making {method} request to {endpoint}..."):
                try:
                    data = None
                    if json_data and method in ["POST", "PUT"]:
                        data = json.loads(json_data)
                    
                    result = make_gitlab_api_request(endpoint, method, data)
                    
                    if result:
                        st.success("✅ API call successful!")
                        st.json(result)
                    else:
                        st.error("❌ API call failed")
                        
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON data")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # Common API endpoints
        st.markdown("**🔗 Common Endpoints:**")
        common_endpoints = [
            ("user", "Get current user info"),
            ("projects", "List user projects"),
            ("groups", "List user groups"),
            ("user/activities", "Get user activities"),
            ("projects?starred=true", "Get starred projects"),
            ("user/keys", "Get SSH keys"),
        ]
        
        for endpoint_path, description in common_endpoints:
            if st.button(f"📋 {endpoint_path}", key=f"common_{endpoint_path}"):
                st.code(endpoint_path)
                st.info(description)


def gitlab_page():
    """Main GitLab page function"""
    auth = GitLabAuth()
    
    # If GitLab auth is disabled, show disabled message
    if auth.disabled:
        # GitLab header with official logo
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwMCIgaGVpZ2h0PSIyMzA1IiB2aWV3Qm94PSIwIDAgMjU2IDIzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWluWU1pbiBtZWV0Ij48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc1bDQ3LjEwNC0xNDQuOTdIODAuOTdsNDcuMTA0IDE0NC45N3oiIGZpbGw9IiNFMjQzMjkiLz48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc0TDgwLjk3IDkxLjEwNEgxNC45NTZsMTEzLjExOSAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDRMLjY0MiAxMzUuMTZhOS43NTIgOS43NTIgMCAwIDAgMy41NDIgMTAuOTAzbDEyMy44OTEgOTAuMDEyLTExMy4xMi0xNDQuOTd6IiBmaWxsPSIjRkNBMzI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDVIODAuOTdMNTIuNjAxIDMuNzljLTEuNDYtNC40OTMtNy44MTYtNC40OTItOS4yNzUgMGwtMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjxwYXRoIGQ9Ik0xMjguMDc1IDIzNi4wNzRsNDcuMTA0LTE0NC45N2g2Ni4wMTVsLTExMy4xMiAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTI0MS4xOTQgOTEuMTA0bDE0LjMxNCA0NC4wNTZhOS43NTIgOS43NTIgMCAwIDEtMy41NDMgMTAuOTAzbC0xMjMuODkgOTAuMDEyIDExMy4xMTktMTQ0Ljk3eiIgZmlsbD0iI0ZDQTMyNiIvPjxwYXRoIGQ9Ik0yNDEuMTk0IDkxLjEwNWgtNjYuMDE1bDI4LjM3LTg3LjMxNWMxLjQ2LTQuNDkzIDcuODE2LTQuNDkyIDkuMjc1IDBsMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjwvc3ZnPg==" 
                 style="width: 32px; height: 32px; margin-right: 12px;" alt="GitLab Logo">
            <h2 style="margin: 0; color: #FC6D26;">GitLab Integration</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.info("🚫 GitLab integration is currently disabled for local development.")
        st.markdown("""
        **To enable GitLab integration:**
        1. Run `python scripts/fix_gitlab_oauth.py`
        2. Choose option 2 to configure GitLab OAuth
        3. Provide your GitLab application credentials
        """)
        return
    
    if not auth.is_authenticated():
        # GitLab header with official logo
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjUwMCIgaGVpZ2h0PSIyMzA1IiB2aWV3Qm94PSIwIDAgMjU2IDIzNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWluWU1pbiBtZWV0Ij48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc1bDQ3LjEwNC0xNDQuOTdIODAuOTdsNDcuMTA0IDE0NC45N3oiIGZpbGw9IiNFMjQzMjkiLz48cGF0aCBkPSJNMTI4LjA3NSAyMzYuMDc0TDgwLjk3IDkxLjEwNEgxNC45NTZsMTEzLjExOSAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDRMLjY0MiAxMzUuMTZhOS43NTIgOS43NTIgMCAwIDAgMy41NDIgMTAuOTAzbDEyMy44OTEgOTAuMDEyLTExMy4xMi0xNDQuOTd6IiBmaWxsPSIjRkNBMzI2Ii8+PHBhdGggZD0iTTE0Ljk1NiA5MS4xMDVIODAuOTdMNTIuNjAxIDMuNzljLTEuNDYtNC40OTMtNy44MTYtNC40OTItOS4yNzUgMGwtMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjxwYXRoIGQ9Ik0xMjguMDc1IDIzNi4wNzRsNDcuMTA0LTE0NC45N2g2Ni4wMTVsLTExMy4xMiAxNDQuOTd6IiBmaWxsPSIjRkM2RDI2Ii8+PHBhdGggZD0iTTI0MS4xOTQgOTEuMTA0bDE0LjMxNCA0NC4wNTZhOS43NTIgOS43NTIgMCAwIDEtMy41NDMgMTAuOTAzbC0xMjMuODkgOTAuMDEyIDExMy4xMTktMTQ0Ljk3eiIgZmlsbD0iI0ZDQTMyNiIvPjxwYXRoIGQ9Ik0yNDEuMTk0IDkxLjEwNWgtNjYuMDE1bDI4LjM3LTg3LjMxNWMxLjQ2LTQuNDkzIDcuODE2LTQuNDkyIDkuMjc1IDBsMjguMzcgODcuMzE1eiIgZmlsbD0iI0UyNDMyOSIvPjwvc3ZnPg==" 
                 style="width: 32px; height: 32px; margin-right: 12px;" alt="GitLab Logo">
            <h2 style="margin: 0; color: #FC6D26;">GitLab Integration</h2>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.info("Please login with GitLab to access integration features.")
        
        from streamlit_app.utils.auth import render_login_button
        render_login_button()
    else:
        gitlab_integration_page()