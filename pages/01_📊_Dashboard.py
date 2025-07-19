import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import required modules
from streamlit_app.utils.enhanced_styling import apply_enhanced_styling
from streamlit_app.utils.auth import GitLabAuth, init_auth
from streamlit_app.admin_dashboard import admin_dashboard_main
from streamlit_app.user_dashboard import user_dashboard_main

def main():
    st.set_page_config(
        page_title="Dashboard - BharatVerse",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize authentication
    auth = GitLabAuth()
    init_auth()
    
    # Apply enhanced styling
    apply_enhanced_styling()
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        st.error("🔒 Access Denied")
        st.warning("Please login to access your dashboard.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏠 Go to Home Page", use_container_width=True, type="primary"):
                st.switch_page("Home.py")
        st.stop()
    
    # Get current user from database
    db_user = auth.get_current_db_user()
    if not db_user:
        st.error("❌ User data not found")
        st.warning("Please try logging in again.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Logout and Return Home", use_container_width=True, type="primary"):
                auth.logout()
                st.switch_page("Home.py")
        st.stop()
    
    # Get user role
    user_role = db_user.get('role', 'user')
    user_name = db_user.get('name', 'User')
    
    # Show role-based dashboard
    if user_role == 'admin':
        # Admin Dashboard
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem; 
                    background: linear-gradient(90deg, #FF6B35, #F7931E); 
                    border-radius: 10px; color: white;'>
            <h1 style='margin: 0; font-size: 2.5rem;'>🛡️ Admin Dashboard</h1>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem;'>Welcome back, {user_name}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Call admin dashboard
        admin_dashboard_main()
        
    else:
        # User Dashboard
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem; 
                    background: linear-gradient(90deg, #2E86AB, #A23B72); 
                    border-radius: 10px; color: white;'>
            <h1 style='margin: 0; font-size: 2.5rem;'>👤 My Dashboard</h1>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem;'>Welcome back, {user_name}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Call user dashboard
        user_dashboard_main()

if __name__ == "__main__":
    main()