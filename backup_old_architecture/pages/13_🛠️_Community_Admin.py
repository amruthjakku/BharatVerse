import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from streamlit_app.community_admin import community_admin_page
from streamlit_app.utils.auth import GitLabAuth

# Initialize auth
auth = GitLabAuth()

def main():
    """Main function for Community Admin page"""
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        st.markdown("## 🔐 Authentication Required")
        st.warning("Please log in with your GitLab account to access the community administration panel.")
        
        if st.button("🔗 Login with GitLab", type="primary"):
            auth_url = auth.get_authorization_url()
            st.markdown(f"[Click here to login with GitLab]({auth_url})")
            st.info("You will be redirected to GitLab for authentication.")
        return
    
    # Check if user is admin
    if not auth.is_admin():
        st.error("🚫 **Admin Access Required**")
        st.warning("This page is restricted to administrators only.")
        
        current_user = auth.get_current_user()
        if current_user:
            st.info(f"👤 Logged in as: **{current_user.get('name', 'Unknown')}**")
            st.markdown("Contact an administrator if you need access to this panel.")
        
        # Show available pages for regular users
        st.markdown("### 📋 Available Pages:")
        st.markdown("- 🎤 **Audio Capture** - Record and contribute audio")
        st.markdown("- 📝 **Text Stories** - Share cultural stories")
        st.markdown("- 🖼️ **Visual Heritage** - Upload cultural images")
        st.markdown("- 📊 **Analytics** - View your contributions")
        st.markdown("- 🏘️ **Community** - Join community discussions")
        return
    
    current_user = auth.get_current_user()
    if not current_user:
        st.error("Failed to get user information")
        return
    
    st.success(f"👋 Welcome, Admin {current_user.get('name', current_user.get('username', 'User'))}!")
    
    # Show admin interface
    community_admin_page()

if __name__ == "__main__":
    main()