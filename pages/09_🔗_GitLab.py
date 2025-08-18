import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the GitLab module with fallback
try:
    from streamlit_app.gitlab_module import gitlab_page
    GITLAB_MODULE_AVAILABLE = True
except ImportError as e:
    GITLAB_MODULE_AVAILABLE = False
    gitlab_import_error = str(e)

try:
    from streamlit_app.utils.main_styling import load_custom_css
    STYLING_AVAILABLE = True
except ImportError:
    STYLING_AVAILABLE = False

def main():
    st.set_page_config(
        page_title="GitLab Integration - BharatVerse",
        page_icon="🔗",
        layout="wide"
    )
    
    # Handle OAuth callback first if present
    if 'code' in st.query_params:
        try:
            from streamlit_app.utils.auth import handle_oauth_callback
            handle_oauth_callback()
            st.stop()
        except Exception as e:
            st.error(f"OAuth callback error: {e}")
    
    # Apply enhanced styling if available
    if STYLING_AVAILABLE:
        try:
            load_custom_css()
        except Exception:
            pass
    
    # Check if GitLab module is available
    if not GITLAB_MODULE_AVAILABLE:
        st.error("🚧 GitLab Integration Temporarily Unavailable")
        st.info(f"Import error: {gitlab_import_error}")
        st.markdown("""
        ### 🔗 GitLab Integration
        
        This feature is currently being optimized for cloud deployment.
        
        **What this page normally provides:**
        - GitLab OAuth authentication
        - Repository integration
        - Collaborative features
        - Version control for cultural stories
        
        **Temporary workaround:**
        - Use the other pages for cultural documentation
        - GitLab features will be restored soon
        
        Thank you for your patience! 🙏
        """)
        return
    
    # Call the GitLab page function
    try:
        gitlab_page()
    except Exception as e:
        st.error(f"Error loading GitLab page: {e}")
        st.info("Please try refreshing the page or contact support.")

if __name__ == "__main__":
    main()