"""
Legacy app.py - Redirects to new multipage structure
This file is kept for backward compatibility
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="BharatVerse - Redirecting...",
        page_icon="🇮🇳",
        layout="wide"
    )
    
    st.markdown("## 🔄 Redirecting to New Multipage Structure")
    st.markdown("BharatVerse has been updated with a new multipage navigation structure.")
    st.markdown("Please use the main **Home.py** file to run the application:")
    
    st.code("streamlit run Home.py", language="bash")
    
    st.markdown("### 📁 New Page Structure:")
    st.markdown("""
    - **Home.py** - Main landing page
    - **pages/01_🎤_Audio_Capture.py** - Audio recording and upload
    - **pages/02_📝_Text_Stories.py** - Text story documentation
    - **pages/03_📸_Visual_Heritage.py** - Image and visual content
    - **pages/04_🔍_Discover.py** - Search and discovery
    - **pages/05_📊_Analytics.py** - Analytics and insights
    - **pages/06_🤝_Community.py** - Community hub
    - **pages/07_🤖_AI_Insights.py** - AI-powered insights
    - **pages/08_👥_Collaboration.py** - Collaboration tools
    - **pages/09_🦊_GitLab.py** - GitLab integration
    - **pages/10_👤_My_Profile.py** - User profile
    - **pages/11_📚_Browse_Contributions.py** - Browse all content
    - **pages/12_ℹ️_About.py** - About BharatVerse
    """)
    
    st.info("💡 The new structure provides better navigation and improved user experience!")

if __name__ == "__main__":
    main()