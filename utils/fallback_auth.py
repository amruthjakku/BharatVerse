"""
Fallback authentication system for when main auth is not available
"""

import streamlit as st

class FallbackAuthManager:
    """Simple fallback authentication for demo purposes"""
    
    def __init__(self):
        self.demo_user = {
            'id': 1,
            'username': 'demo_user',
            'name': 'Demo User',
            'email': 'demo@bharatverse.com',
            'role': 'user'
        }
    
    def is_authenticated(self):
        """Check if user is authenticated (always true for demo)"""
        return True
    
    def is_admin(self):
        """Check if user is admin"""
        return st.session_state.get('demo_admin_mode', False)
    
    def get_current_user(self):
        """Get current user info"""
        return self.demo_user
    
    def get_current_db_user(self):
        """Get database user info"""
        return self.demo_user
    
    def login(self, username, password):
        """Demo login"""
        return True
    
    def logout(self):
        """Demo logout"""
        if 'demo_admin_mode' in st.session_state:
            del st.session_state['demo_admin_mode']

def get_fallback_auth_manager():
    """Get fallback auth manager"""
    return FallbackAuthManager()

def render_fallback_login():
    """Render fallback login interface"""
    st.info("🔧 Demo Mode - Authentication system not configured")
    st.markdown("### 🎭 Demo Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Continue as Demo User", use_container_width=True):
            st.success("✅ Logged in as Demo User")
            st.rerun()
    
    with col2:
        if st.button("🛡️ Admin Demo Mode", use_container_width=True):
            st.session_state['demo_admin_mode'] = True
            st.success("✅ Admin demo mode enabled")
            st.rerun()
    
    st.markdown("---")
    st.markdown("**Note**: This is demo mode. Configure GitLab OAuth for full authentication.")