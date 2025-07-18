import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
import uuid
from typing import Dict, List, Optional

# Import community service
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.database import DatabaseManager
from core.community_service import CommunityService
from streamlit_app.utils.demo_auth import demo_auth
from streamlit_app.utils.community_styling import apply_community_styling

# Use demo auth for community features
auth = demo_auth

def get_current_user():
    """Get current user for community features"""
    if auth.is_authenticated():
        user_info = auth.get_current_user()
        db_user = auth.get_current_db_user()
        
        if user_info and db_user:
            return {
                'id': db_user['id'],
                'username': user_info.get('username', db_user.get('username')),
                'email': user_info.get('email', db_user.get('email')),
                'name': user_info.get('name', db_user.get('full_name'))
            }
    return None

# Initialize services
@st.cache_resource
def get_community_service():
    try:
        db_manager = DatabaseManager()
        return CommunityService(db_manager)
    except Exception as e:
        st.error(f"Failed to initialize community service: {e}")
        return None

def community_page():
    # Apply community styling
    apply_community_styling()
    
    # Show user info in sidebar
    auth.show_user_info()
    
    st.markdown("## 🤝 Community Hub")
    st.markdown("Connect with fellow cultural enthusiasts and contributors")
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        st.markdown("### 🔐 Authentication Required")
        st.info("Please log in to access community features and start connecting with fellow cultural enthusiasts!")
        auth.show_login_form()
        return
    
    community_service = get_community_service()
    if not community_service:
        st.error("Community service is not available")
        return
    
    # Get community stats
    try:
        all_groups = community_service.get_all_groups()
        active_challenges = community_service.get_active_challenges()
        leaderboard = community_service.get_community_leaderboard(10)
        
        # Community stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = sum(group.get('actual_member_count', 0) for group in all_groups)
            st.metric("Active Members", total_members, f"+{len(all_groups)} groups")
        with col2:
            verified_count = len([user for user in leaderboard if user.get('badges')])
            st.metric("Cultural Experts", verified_count, "Verified contributors")
        with col3:
            total_contributions = sum(user.get('contribution_count', 0) for user in leaderboard)
            st.metric("Total Contributions", total_contributions, "Across all users")
        with col4:
            st.metric("Active Challenges", len(active_challenges), "Join now!")
        
    except Exception as e:
        st.error(f"Failed to load community stats: {e}")
        return
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Groups", 
        "💬 Chat", 
        "🗣️ Discussions", 
        "🎯 Challenges", 
        "🏆 Leaderboard", 
        "👤 Profile"
    ])
    
    with tab1:
        groups_section(community_service, current_user)
    
    with tab2:
        chat_section(community_service, current_user)
    
    with tab3:
        discussions_section(community_service, current_user)
    
    with tab4:
        challenges_section(community_service, current_user)
    
    with tab5:
        leaderboard_section(community_service)
    
    with tab6:
        profile_section(community_service, current_user)

def groups_section(community_service, current_user):
    """Community Groups Section"""
    st.markdown("### 🏠 Community Groups")
    
    # Group type filter
    group_type_filter = st.selectbox(
        "Filter by type:",
        ["All", "Regional", "Language", "Interest"],
        key="group_type_filter"
    )
    
    try:
        # Get groups based on filter
        if group_type_filter == "All":
            groups = community_service.get_all_groups()
        else:
            groups = community_service.get_all_groups(group_type_filter.lower())
        
        # Get user's groups
        user_groups = community_service.get_user_groups(current_user['id'])
        user_group_ids = {group['id'] for group in user_groups}
        
        # Display groups by category
        if groups:
            # Group by type for better organization
            groups_by_type = {}
            for group in groups:
                group_type = group['group_type'].title()
                if group_type not in groups_by_type:
                    groups_by_type[group_type] = []
                groups_by_type[group_type].append(group)
            
            for group_type, type_groups in groups_by_type.items():
                if group_type_filter == "All" or group_type_filter == group_type:
                    st.markdown(f"#### {group_type} Groups")
                    
                    cols = st.columns(2)
                    for i, group in enumerate(type_groups):
                        with cols[i % 2]:
                            with st.container():
                                st.markdown(f"**{group['name']}**")
                                st.markdown(f"*{group['description']}*")
                                st.markdown(f"👥 {group['actual_member_count']} members")
                                
                                # Join/Leave button
                                if group['id'] in user_group_ids:
                                    if st.button(f"Leave", key=f"leave_{group['id']}"):
                                        if community_service.leave_group(current_user['id'], group['id']):
                                            st.success(f"Left {group['name']}")
                                            st.rerun()
                                        else:
                                            st.error("Failed to leave group")
                                else:
                                    if st.button(f"Join", key=f"join_{group['id']}", type="primary"):
                                        if community_service.join_group(current_user['id'], group['id']):
                                            st.success(f"Joined {group['name']}")
                                            st.rerun()
                                        else:
                                            st.error("Failed to join group")
                                
                                st.markdown("---")
        else:
            st.info("No groups found for the selected filter.")
            
    except Exception as e:
        st.error(f"Failed to load groups: {e}")

def chat_section(community_service, current_user):
    """Real-time Chat Section"""
    st.markdown("### 💬 Group Chat")
    
    try:
        # Get user's groups for chat selection
        user_groups = community_service.get_user_groups(current_user['id'])
        
        if not user_groups:
            st.info("Join a group to start chatting!")
            return
        
        # Group selection
        group_options = {group['name']: group['id'] for group in user_groups}
        selected_group_name = st.selectbox("Select a group to chat:", list(group_options.keys()))
        selected_group_id = group_options[selected_group_name]
        
        # Chat interface
        st.markdown(f"#### Chat: {selected_group_name}")
        
        # Message input
        with st.form("chat_form", clear_on_submit=True):
            message_input = st.text_area("Type your message:", height=100, key="chat_message")
            col1, col2 = st.columns([1, 4])
            with col1:
                send_button = st.form_submit_button("Send", type="primary")
            
            if send_button and message_input.strip():
                try:
                    community_service.send_chat_message(
                        selected_group_id, 
                        current_user['id'], 
                        message_input.strip()
                    )
                    st.success("Message sent!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to send message: {e}")
        
        # Display messages
        st.markdown("#### Recent Messages")
        try:
            messages = community_service.get_chat_messages(selected_group_id, limit=20)
            
            if messages:
                for message in messages:
                    with st.container():
                        col1, col2 = st.columns([1, 6])
                        with col1:
                            st.markdown(f"**{message.get('sender_name', 'Unknown')}**")
                            st.markdown(f"*{message['created_at'].strftime('%H:%M')}*")
                        with col2:
                            st.markdown(message['content'])
                            
                            # Reaction buttons
                            reaction_cols = st.columns(5)
                            reactions = ['👍', '❤️', '😊', '🎉', '👏']
                            for i, reaction in enumerate(reactions):
                                with reaction_cols[i]:
                                    if st.button(reaction, key=f"react_{message['id']}_{reaction}"):
                                        community_service.add_message_reaction(
                                            message['id'], current_user['id'], reaction
                                        )
                                        st.rerun()
                        st.markdown("---")
            else:
                st.info("No messages yet. Be the first to start the conversation!")
                
        except Exception as e:
            st.error(f"Failed to load messages: {e}")
            
    except Exception as e:
        st.error(f"Failed to load chat: {e}")

def discussions_section(community_service, current_user):
    """Discussion Forums Section"""
    st.markdown("### 🗣️ Discussion Forums")
    
    try:
        # Get user's groups
        user_groups = community_service.get_user_groups(current_user['id'])
        
        if not user_groups:
            st.info("Join a group to participate in discussions!")
            return
        
        # Group selection for discussions
        group_options = {group['name']: group['id'] for group in user_groups}
        selected_group_name = st.selectbox("Select a group:", list(group_options.keys()), key="discussion_group")
        selected_group_id = group_options[selected_group_name]
        
        # Create new topic
        with st.expander("Start a New Discussion"):
            with st.form("new_topic_form"):
                topic_title = st.text_input("Topic Title")
                topic_description = st.text_area("Description")
                topic_category = st.selectbox("Category", ["general", "help", "showcase", "question"])
                
                if st.form_submit_button("Create Topic", type="primary"):
                    if topic_title.strip() and topic_description.strip():
                        try:
                            community_service.create_discussion_topic(
                                selected_group_id, current_user['id'], 
                                topic_title.strip(), topic_description.strip(), topic_category
                            )
                            st.success("Discussion topic created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create topic: {e}")
                    else:
                        st.error("Please fill in all fields")
        
        # Display discussion topics
        st.markdown("#### Discussion Topics")
        try:
            topics = community_service.get_discussion_topics(selected_group_id)
            
            if topics:
                for topic in topics:
                    with st.expander(f"{'📌 ' if topic['is_pinned'] else ''}{topic['title']} ({topic['actual_reply_count']} replies)"):
                        st.markdown(f"**Category:** {topic['category'].title()}")
                        st.markdown(f"**Created by:** {topic.get('creator_name', 'Unknown')}")
                        st.markdown(f"**Created:** {topic['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.markdown("---")
                        st.markdown(topic['description'])
                        
                        # Replies section
                        st.markdown("#### Replies")
                        replies = community_service.get_discussion_replies(topic['id'])
                        
                        for reply in replies:
                            with st.container():
                                col1, col2 = st.columns([1, 5])
                                with col1:
                                    st.markdown(f"**{reply.get('author_name', 'Unknown')}**")
                                    st.markdown(f"*{reply['created_at'].strftime('%Y-%m-%d %H:%M')}*")
                                with col2:
                                    st.markdown(reply['content'])
                                st.markdown("---")
                        
                        # Add reply
                        with st.form(f"reply_form_{topic['id']}"):
                            reply_content = st.text_area("Your reply:", key=f"reply_{topic['id']}")
                            if st.form_submit_button("Reply"):
                                if reply_content.strip():
                                    try:
                                        community_service.add_discussion_reply(
                                            topic['id'], current_user['id'], reply_content.strip()
                                        )
                                        st.success("Reply added!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to add reply: {e}")
            else:
                st.info("No discussion topics yet. Start the first one!")
                
        except Exception as e:
            st.error(f"Failed to load discussions: {e}")
            
    except Exception as e:
        st.error(f"Failed to load discussion section: {e}")

def challenges_section(community_service, current_user):
    """Community Challenges Section"""
    st.markdown("### 🎯 Community Challenges")
    
    try:
        challenges = community_service.get_active_challenges()
        
        if challenges:
            for challenge in challenges:
                with st.expander(f"🏆 {challenge['title']} - {challenge['actual_participant_count']} participants"):
                    st.markdown(f"**Type:** {challenge['challenge_type'].title()}")
                    st.markdown(f"**Created by:** {challenge.get('creator_name', 'System')}")
                    
                    # Challenge dates
                    end_date = challenge['end_date']
                    days_left = (end_date - datetime.now(end_date.tzinfo)).days
                    st.markdown(f"**Days left:** {days_left}")
                    
                    st.markdown("---")
                    st.markdown(challenge['description'])
                    
                    # Requirements and rewards
                    if challenge['requirements']:
                        st.markdown("**Requirements:**")
                        requirements = challenge['requirements']
                        for key, value in requirements.items():
                            st.markdown(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    if challenge['rewards']:
                        st.markdown("**Rewards:**")
                        rewards = challenge['rewards']
                        for key, value in rewards.items():
                            st.markdown(f"- {key.replace('_', ' ').title()}: {value}")
                    
                    # Participation button
                    if st.button(f"View Leaderboard", key=f"leaderboard_{challenge['id']}"):
                        leaderboard = community_service.get_challenge_leaderboard(challenge['id'])
                        if leaderboard:
                            st.markdown("#### Challenge Leaderboard")
                            for i, participant in enumerate(leaderboard[:10], 1):
                                st.markdown(f"{i}. **{participant['username']}** - {participant['points_earned']} points")
                        else:
                            st.info("No participants yet!")
        else:
            st.info("No active challenges at the moment. Check back soon!")
            
    except Exception as e:
        st.error(f"Failed to load challenges: {e}")

def leaderboard_section(community_service):
    """Community Leaderboard Section"""
    st.markdown("### 🏆 Community Leaderboard")
    
    try:
        leaderboard = community_service.get_community_leaderboard(20)
        
        if leaderboard:
            # Top 3 special display
            if len(leaderboard) >= 3:
                st.markdown("#### 🥇 Top Contributors")
                cols = st.columns(3)
                
                for i, user in enumerate(leaderboard[:3]):
                    with cols[i]:
                        medal = ["🥇", "🥈", "🥉"][i]
                        st.markdown(f"### {medal} {user['username']}")
                        st.markdown(f"**Points:** {user.get('community_points', 0)}")
                        st.markdown(f"**Contributions:** {user.get('contribution_count', 0)}")
                        st.markdown(f"**Location:** {user.get('location', 'Unknown')}")
                        if user.get('badges'):
                            st.markdown(f"**Badges:** {', '.join(user['badges'])}")
            
            # Full leaderboard table
            st.markdown("#### Full Leaderboard")
            leaderboard_data = []
            for i, user in enumerate(leaderboard, 1):
                leaderboard_data.append({
                    "Rank": i,
                    "Username": user['username'],
                    "Points": user.get('community_points', 0),
                    "Contributions": user.get('contribution_count', 0),
                    "Groups": user.get('groups_joined', 0),
                    "Challenges Won": user.get('challenges_won', 0),
                    "Location": user.get('location', 'Unknown')
                })
            
            df = pd.DataFrame(leaderboard_data)
            st.dataframe(df, use_container_width=True)
            
        else:
            st.info("No contributors yet. Be the first to start contributing!")
            
    except Exception as e:
        st.error(f"Failed to load leaderboard: {e}")

def profile_section(community_service, current_user):
    """User Profile Section"""
    st.markdown("### 👤 Your Profile")
    
    try:
        # Get user profile
        profile = community_service.get_user_profile(current_user['id'])
        
        if profile:
            # Display current profile
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("#### Current Profile")
                st.markdown(f"**Username:** {profile['username']}")
                st.markdown(f"**Email:** {profile['email']}")
                st.markdown(f"**Points:** {profile.get('community_points', 0)}")
                st.markdown(f"**Contributions:** {profile.get('contribution_count', 0)}")
                
                if profile.get('badges'):
                    st.markdown(f"**Badges:** {', '.join(profile['badges'])}")
            
            with col2:
                st.markdown("#### Update Profile")
                with st.form("profile_form"):
                    bio = st.text_area("Bio", value=profile.get('bio', ''))
                    location = st.text_input("Location", value=profile.get('location', ''))
                    
                    # Languages spoken
                    languages_input = st.text_input(
                        "Languages Spoken (comma-separated)", 
                        value=', '.join(profile.get('languages_spoken', []))
                    )
                    
                    # Cultural interests
                    interests_input = st.text_input(
                        "Cultural Interests (comma-separated)",
                        value=', '.join(profile.get('cultural_interests', []))
                    )
                    
                    if st.form_submit_button("Update Profile", type="primary"):
                        try:
                            profile_data = {
                                'bio': bio,
                                'location': location,
                                'languages_spoken': [lang.strip() for lang in languages_input.split(',') if lang.strip()],
                                'cultural_interests': [interest.strip() for interest in interests_input.split(',') if interest.strip()]
                            }
                            
                            community_service.update_user_profile(current_user['id'], profile_data)
                            st.success("Profile updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update profile: {e}")
            
            # Activity feed
            st.markdown("#### Your Recent Activity")
            try:
                activities = community_service.get_user_activity_feed(current_user['id'], 10)
                
                if activities:
                    for activity in activities:
                        activity_type = activity['activity_type'].replace('_', ' ').title()
                        created_at = activity['created_at'].strftime('%Y-%m-%d %H:%M')
                        st.markdown(f"- **{activity_type}** - {created_at}")
                else:
                    st.info("No recent activity. Start engaging with the community!")
                    
            except Exception as e:
                st.error(f"Failed to load activity feed: {e}")
        else:
            st.error("Failed to load profile")
            
    except Exception as e:
        st.error(f"Failed to load profile section: {e}")