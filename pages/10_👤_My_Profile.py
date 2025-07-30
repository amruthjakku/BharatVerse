import streamlit as st
import sys
from pathlib import Path
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the user profile module
from streamlit_app.user_profile import user_profile_main
from streamlit_app.utils.main_styling import load_custom_css

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title="My Profile - BharatVerse",
        page_icon="👤",
        layout="wide"
    )
    
    # Log application start
    logger.info("Launching the My Profile page of BharatVerse.")

    # Apply enhanced styling
    load_custom_css()

    # Display welcome message
    st.markdown("## 👋 Welcome to your BharatVerse Profile")
    st.markdown("Here you can view and manage your cultural journey, contributions, and preferences.")

    # Call the user profile main function
    user_profile_main()

    # Log successful load
    logger.info("User profile loaded successfully.")

if __name__ == "__main__":
    main()
