import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the text module
from streamlit_app.text_module import text_page
from streamlit_app.utils.enhanced_styling import apply_enhanced_styling

def main():
    st.set_page_config(
        page_title="Text Stories - BharatVerse",
        page_icon="📝",
        layout="wide"
    )
    
    # Apply enhanced styling
    apply_enhanced_styling()
    
    # Call the text page function
    text_page()

if __name__ == "__main__":
    main()