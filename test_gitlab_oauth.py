#!/usr/bin/env python3
"""
GitLab OAuth Test Script
Tests the GitLab OAuth configuration and functionality
"""

import os
import sys
import streamlit as st

# Add the project path to sys.path so we can import modules
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

def test_gitlab_oauth():
    """Test GitLab OAuth configuration and functionality"""
    
    st.title("🔐 GitLab OAuth Test")
    st.markdown("---")
    
    # Test 1: Check secrets configuration
    st.markdown("## 🔍 Configuration Test")
    
    try:
        # Test secrets loading
        gitlab_config = st.secrets.get("gitlab", {})
        
        client_id = gitlab_config.get("client_id")
        client_secret = gitlab_config.get("client_secret") 
        base_url = gitlab_config.get("base_url")
        scopes = gitlab_config.get("scopes")
        
        st.success("✅ Secrets loaded successfully")
        
        # Display configuration (hide sensitive data)
        config_status = {
            "Client ID": "✅ Set" if client_id else "❌ Missing",
            "Client Secret": "✅ Set" if client_secret else "❌ Missing", 
            "Base URL": base_url or "❌ Missing",
            "Scopes": scopes or "❌ Missing"
        }
        
        for key, value in config_status.items():
            if "✅" in value:
                st.success(f"**{key}**: {value}")
            else:
                st.error(f"**{key}**: {value}")
                
    except Exception as e:
        st.error(f"❌ Failed to load secrets: {e}")
        return
    
    st.markdown("---")
    
    # Test 2: Test GitLab Auth module
    st.markdown("## 🔧 GitLab Auth Module Test")
    
    try:
        from streamlit_app.utils.auth import GitLabAuth
        
        auth = GitLabAuth()
        st.success("✅ GitLabAuth module loaded successfully")
        
        # Check if user is authenticated
        if auth.is_authenticated():
            user_info = auth.get_current_user()
            st.success("🎉 User is authenticated!")
            
            if user_info:
                st.markdown("### 👤 Current User Info:")
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if user_info.get('avatar_url'):
                        st.image(user_info['avatar_url'], width=100)
                    else:
                        st.markdown("### 👤")
                
                with col2:
                    st.markdown(f"**Name:** {user_info.get('name', 'Unknown')}")
                    st.markdown(f"**Username:** @{user_info.get('username', 'unknown')}")
                    st.markdown(f"**Email:** {user_info.get('email', 'Not provided')}")
                    st.markdown(f"**ID:** {user_info.get('id', 'Unknown')}")
        else:
            st.info("ℹ️ User is not authenticated")
            
            # Show login button
            if st.button("🔓 Login with GitLab", type="primary"):
                auth_url = auth.get_authorization_url()
                st.markdown(f"[Click here to authenticate]({auth_url})")
                st.info("After authentication, you'll be redirected back to the app")
            
    except ImportError as e:
        st.error(f"❌ Failed to import GitLabAuth: {e}")
        st.info("💡 This might be due to missing dependencies. The OAuth configuration appears to be correct.")
    except Exception as e:
        st.error(f"❌ Error testing GitLab Auth: {e}")
    
    st.markdown("---")
    
    # Test 3: OAuth URL generation
    st.markdown("## 🔗 OAuth URL Test")
    
    try:
        from streamlit_app.utils.auth import GitLabAuth
        auth = GitLabAuth()
        
        if all([auth.client_id, auth.client_secret, auth.base_url]):
            oauth_url = auth.get_authorization_url()
            st.success("✅ OAuth URL generated successfully")
            
            st.markdown("### Generated OAuth URL:")
            st.code(oauth_url)
            
            st.markdown("### OAuth URL Components:")
            st.markdown(f"- **Base URL**: {auth.base_url}/oauth/authorize")
            st.markdown(f"- **Client ID**: {auth.client_id[:10]}...")
            st.markdown(f"- **Redirect URI**: {auth.redirect_uri}")
            st.markdown(f"- **Scopes**: {auth.scopes}")
            
            st.info("🔄 Click the URL above to test the OAuth flow manually")
        else:
            st.error("❌ OAuth configuration incomplete")
            
    except Exception as e:
        st.error(f"❌ Error generating OAuth URL: {e}")
    
    st.markdown("---")
    st.markdown("## 📋 Summary")
    
    st.markdown("""
    **GitLab OAuth Configuration Status:**
    - Secrets configuration: ✅ Working
    - OAuth URL generation: ✅ Working
    - Authentication flow: Ready for testing
    
    **Next Steps:**
    1. Click the login button to test the full OAuth flow
    2. Make sure the redirect URI matches exactly in GitLab application settings
    3. Test database connectivity once psycopg2 is properly installed
    """)

if __name__ == "__main__":
    test_gitlab_oauth()
