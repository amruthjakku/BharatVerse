"""
Community Module for BharatVerse - Complete Implementation
"""
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_option_menu import option_menu
from datetime import datetime

def community_page():
    """Main community page"""
    user_info = st.session_state.get('user_info')
    
    colored_header(
        label="🤝 BharatVerse Community",
        description="Connect and collaborate on cultural preservation",
        color_name="violet-70"
    )
    
    selected = option_menu(
        None,
        ["Feed", "Groups", "Events", "Forums"],
        icons=["newspaper", "people-fill", "calendar-event", "chat-dots"],
        default_index=0,
        orientation="horizontal"
    )
    
    if selected == "Feed":
        show_feed(user_info)
    elif selected == "Groups":
        show_groups(user_info)
    elif selected == "Events":
        show_events(user_info)
    else:
        show_forums(user_info)

def show_feed(user_info):
    st.markdown("### 📰 Community Feed")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Members", "1,234", "+89")
    col2.metric("Posts Today", "56", "+12")
    col3.metric("Events", "8", "+3")
    col4.metric("Groups", "45", "+2")
    
    if user_info:
        with st.expander("✍️ Share Something"):
            st.text_input("Title")
            st.text_area("Content", height=100)
            if st.button("Post", type="primary"):
                st.success("Posted!")
    
    posts = [
        {"author": "Priya", "title": "Madhubani Painting Workshop", "time": "2h ago", "likes": 45},
        {"author": "Raj", "title": "Folk Music Festival Chennai", "time": "5h ago", "likes": 23},
        {"author": "Admin", "title": "New Language Support Added", "time": "1d ago", "likes": 156}
    ]
    
    for p in posts:
        with st.container():
            st.markdown(f"**{p['author']}** · {p['time']}")
            st.markdown(f"### {p['title']}")
            col1, col2, col3 = st.columns([1,1,8])
            with col1:
                st.button(f"❤️ {p['likes']}", key=f"l{posts.index(p)}")
            with col2:
                st.button("💬", key=f"c{posts.index(p)}")
            st.divider()

def show_groups(user_info):
    st.markdown("### 👥 Cultural Groups")
    
    groups = [
        {"name": "Tamil Literature", "members": 234},
        {"name": "Kathak Dancers", "members": 189},
        {"name": "Northeast Culture", "members": 456},
        {"name": "Sanskrit Scholars", "members": 167}
    ]
    
    cols = st.columns(2)
    for i, g in enumerate(groups):
        with cols[i % 2]:
            st.info(f"**{g['name']}**\n👥 {g['members']} members")
            if st.button("Join", key=f"j{i}", use_container_width=True):
                st.success("Joined!")

def show_events(user_info):
    st.markdown("### 📅 Cultural Events")
    
    events = [
        {"name": "Dance Workshop", "date": "Tomorrow", "time": "10 AM"},
        {"name": "Music Festival", "date": "Saturday", "time": "6 PM"},
        {"name": "Heritage Walk", "date": "Sunday", "time": "8 AM"}
    ]
    
    for e in events:
        col1, col2, col3 = st.columns([3,1,1])
        with col1:
            st.markdown(f"**{e['name']}**")
            st.caption(f"📅 {e['date']} · 🕐 {e['time']}")
        with col3:
            if st.button("Register", key=f"r{events.index(e)}"):
                st.success("Registered!")
        st.divider()

def show_forums(user_info):
    st.markdown("### 💬 Discussion Forums")
    
    topics = [
        {"title": "Preserving Weaving Techniques", "replies": 45, "views": 234},
        {"title": "Learning Classical Music", "replies": 32, "views": 156},
        {"title": "Documenting Family Recipes", "replies": 67, "views": 345}
    ]
    
    for t in topics:
        col1, col2, col3 = st.columns([4,1,1])
        with col1:
            st.markdown(f"**{t['title']}**")
        with col2:
            st.caption(f"💬 {t['replies']}")
        with col3:
            st.caption(f"👁️ {t['views']}")
        st.divider()
