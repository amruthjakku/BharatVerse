import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def community_page():
    st.markdown("## 🤝 Community Hub")
    st.markdown("Connect with fellow cultural enthusiasts and contributors")
    
    # Always use real data - demo mode removed
    st.info("🤝 Community data will be displayed here when users start joining the platform")
    
    # Community stats - real data placeholders
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Members", "0", "Join to be the first!")
    with col2:
        st.metric("Cultural Experts", "0", "Become an expert!")
    with col3:
        st.metric("Verified Contributors", "0", "Start contributing!")
    with col4:
        st.metric("Community Projects", "0", "Create the first project!")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Leaderboard", 
        "👥 Contributors", 
        "🎯 Challenges", 
        "💬 Discussions", 
        "🚀 Projects"
    ])
    
    with tab1:
        leaderboard_section()
    
    with tab2:
        contributors_section()
    
    with tab3:
        challenges_section()
    
    with tab4:
        discussions_section()
    
    with tab5:
        projects_section()

def leaderboard_section():
    st.markdown("### 🏆 Top Contributors")
    
    # Always use real data - demo mode removed
    st.info("🏆 Real leaderboard data will be displayed when contributors start using the platform")
    st.markdown("**Start contributing to see your name on the leaderboard!**")
    st.markdown("- Upload audio content")
    st.markdown("- Share text stories")
    st.markdown("- Add cultural images")
    st.markdown("- Engage with the community")
    
    # Achievement badges
    st.markdown("### 🎖️ Achievement Badges")
    st.info("🎖️ Achievement badges will be displayed here when you start earning them through contributions!")
    st.markdown("**Available badges to earn:**")
    st.markdown("- 🛡️ **Cultural Guardian**: Contribute 100+ items")
    st.markdown("- 🗣️ **Language Keeper**: Content in 5+ languages") 
    st.markdown("- 📚 **Story Teller**: Share 50+ stories")
    st.markdown("- 🎵 **Music Maestro**: Audio contributions expert")
    st.markdown("- 🎉 **Festival Expert**: Festival content specialist")
    st.markdown("- 👨‍🍳 **Recipe Master**: Traditional food expert")

def contributors_section():
    st.markdown("### 👥 Community Contributors")
    
    # Always use real data - demo mode removed
    st.info("👥 Real contributors data will be displayed when users start joining the platform")
    st.markdown("**Join the community to see contributor profiles!**")
    return

def challenges_section():
    st.markdown("### 🎯 Community Challenges")
    
    # Always use real data - demo mode removed
    st.info("🎯 Community challenges will appear here when they are created!")
    st.markdown("**Challenge types that will be available:**")
    st.markdown("- 🎭 **Festival Season Documentation**: Document unique festival traditions")
    st.markdown("- 🗣️ **Endangered Languages Project**: Record content in rare languages")
    st.markdown("- 🍽️ **Recipe Revival Challenge**: Share traditional recipes")
    st.markdown("- 🎵 **Music Preservation**: Record folk songs and classical music")
    st.markdown("- 🎨 **Arts & Crafts Documentation**: Document traditional techniques")
    
    st.markdown("---")
    st.markdown("#### 🏆 Challenge Leaderboard")
    st.info("🏆 Challenge leaderboard will show top performers when challenges are active!")

def discussions_section():
    st.markdown("### 💬 Community Discussions")
    
    # Discussion categories
    categories = st.tabs(["🔥 Popular", "❓ Q&A", "💡 Ideas", "📢 Announcements"])
    
    with categories[0]:  # Popular
        st.info("💬 Popular discussions will appear here when community members start engaging!")
        st.markdown("**Discussion topics will include:**")
        st.markdown("- Best practices for recording folk songs")
        st.markdown("- How to preserve family recipes")
        st.markdown("- Regional variations in traditions")
        st.markdown("- Cultural documentation techniques")
    
    with categories[1]:  # Q&A
        st.markdown("#### ❓ Ask the Community")
        
        question = st.text_area("What would you like to know?", placeholder="Ask about cultural practices, traditions, or anything related to Indian heritage...")
        
        if st.button("Post Question", type="primary"):
            st.success("Your question will be posted when the community feature is active!")
        
        st.markdown("#### Recent Questions")
        st.info("❓ Recent questions from community members will appear here!")
    
    with categories[2]:  # Ideas
        st.info("💡 Community ideas and suggestions will be displayed here!")
        
    with categories[3]:  # Announcements
        st.info("📢 Important community announcements will be posted here!")

def projects_section():
    st.markdown("### 🚀 Community Projects")
    
    # Always use real data - demo mode removed
    st.info("🚀 Community projects will appear here when they are created!")
    st.markdown("**Project types that will be available:**")
    st.markdown("- 🎵 **Digital Archive of Tribal Songs**: Preserve tribal music")
    st.markdown("- 📅 **Interactive Festival Calendar**: Document festivals")
    st.markdown("- 🎨 **Traditional Craft Techniques**: Video documentation")
    st.markdown("- 📚 **Story Collection Projects**: Preserve oral traditions")
    st.markdown("- 🍽️ **Recipe Documentation**: Traditional food heritage")
    
    # Start new project
    st.markdown("### ➕ Start a New Project")
    
    with st.expander("Propose a Community Project"):
        project_title = st.text_input("Project Title")
        project_desc = st.text_area("Project Description")
        project_category = st.selectbox("Category", ["Preservation", "Documentation", "Arts & Crafts", "Music", "Food", "Stories", "Other"])
        
        if st.button("Submit Proposal", type="primary"):
            st.success("Project proposal will be submitted when the community feature is active!")

def show_contributor_profile(contributor):
    """Show detailed contributor profile"""
    st.markdown(f"## Profile: {contributor['name']}")
    st.markdown(f"**Specialty:** {contributor['specialty']}")
    st.markdown(f"**Location:** {contributor['location']}")
    st.markdown(f"**Contributions:** {contributor['contributions']}")
    st.markdown(f"**Points:** {contributor['points']}")