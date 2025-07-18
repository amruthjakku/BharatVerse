import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the user profile module
from streamlit_app.user_profile import user_profile_main
from streamlit_app.utils.enhanced_styling import apply_enhanced_styling

def main():
    st.set_page_config(
        page_title="My Profile - BharatVerse",
        page_icon="👤",
        layout="wide"
    )
    
    # Apply enhanced styling
    apply_enhanced_styling()
    
    # Call the user profile main function
    user_profile_main()

if __name__ == "__main__":
    main()