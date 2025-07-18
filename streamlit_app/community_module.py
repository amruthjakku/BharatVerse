import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def community_page():
    st.markdown("## 🤝 Community Hub")
    st.markdown("Connect with fellow cultural enthusiasts and contributors")
    
    # Import the utility function
    from streamlit_app.utils.mock_data_handler import get_community_data
    
    # Get community data
    community_data = get_community_data()
    
    # Community stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Members", community_data["members"], "+127 this month" if community_data["members"] > 0 else "Real data not available")
    with col2:
        st.metric("Cultural Experts", community_data["experts"], "+8 this week" if community_data["experts"] > 0 else "Real data not available")
    with col3:
        st.metric("Verified Contributors", community_data["contributors"], "+23 this month" if community_data["contributors"] > 0 else "Real data not available")
    with col4:
        st.metric("Community Projects", community_data["projects"], "+3 active" if community_data["projects"] > 0 else "Real data not available")
    
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
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("🏆 Real leaderboard data would be displayed here when available from the API")
        return
    
    # Time period selector
    period = st.selectbox("Time Period", ["This Week", "This Month", "All Time"], key="leaderboard_period")
    
    # Generate sample leaderboard data
    contributors = [
        {"rank": 1, "name": "Priya Sharma", "location": "Mumbai, Maharashtra", "contributions": 156, "points": 2340, "badge": "🥇", "specialty": "Folk Songs"},
        {"rank": 2, "name": "Rajesh Kumar", "location": "Kolkata, West Bengal", "contributions": 142, "points": 2180, "badge": "🥈", "specialty": "Stories & Legends"},
        {"rank": 3, "name": "Meera Nair", "location": "Kochi, Kerala", "contributions": 128, "points": 1950, "badge": "🥉", "specialty": "Classical Arts"},
        {"rank": 4, "name": "Arjun Singh", "location": "Jaipur, Rajasthan", "contributions": 115, "points": 1820, "badge": "🏅", "specialty": "Traditional Crafts"},
        {"rank": 5, "name": "Lakshmi Reddy", "location": "Hyderabad, Telangana", "contributions": 98, "points": 1650, "badge": "🏅", "specialty": "Recipes & Food"},
        {"rank": 6, "name": "Amit Patel", "location": "Ahmedabad, Gujarat", "contributions": 87, "points": 1420, "badge": "🏅", "specialty": "Festival Traditions"},
        {"rank": 7, "name": "Sunita Das", "location": "Bhubaneswar, Odisha", "contributions": 76, "points": 1280, "badge": "🏅", "specialty": "Dance & Music"},
        {"rank": 8, "name": "Vikram Joshi", "location": "Pune, Maharashtra", "contributions": 69, "points": 1150, "badge": "🏅", "specialty": "Historical Content"},
    ]
    
    # Display leaderboard
    for contributor in contributors:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1.5, 1, 1])
            
            with col1:
                st.markdown(f"### {contributor['badge']}")
            
            with col2:
                st.markdown(f"**{contributor['name']}**")
                st.markdown(f"📍 {contributor['location']}")
                st.markdown(f"🎯 {contributor['specialty']}")
            
            with col3:
                st.metric("Contributions", contributor['contributions'])
            
            with col4:
                st.metric("Points", contributor['points'])
            
            with col5:
                if st.button(f"View Profile", key=f"profile_{contributor['rank']}"):
                    show_contributor_profile(contributor)
            
            st.markdown("---")
    
    # Achievement badges
    st.markdown("### 🎖️ Achievement Badges")
    
    badges = [
        {"name": "Cultural Guardian", "description": "Contributed 100+ items", "icon": "🛡️", "rarity": "Epic"},
        {"name": "Language Keeper", "description": "Content in 5+ languages", "icon": "🗣️", "rarity": "Rare"},
        {"name": "Story Teller", "description": "Shared 50+ stories", "icon": "📚", "rarity": "Common"},
        {"name": "Music Maestro", "description": "Audio contributions expert", "icon": "🎵", "rarity": "Rare"},
        {"name": "Festival Expert", "description": "Festival content specialist", "icon": "🎉", "rarity": "Uncommon"},
        {"name": "Recipe Master", "description": "Traditional food expert", "icon": "👨‍🍳", "rarity": "Uncommon"}
    ]
    
    cols = st.columns(3)
    for i, badge in enumerate(badges):
        with cols[i % 3]:
            rarity_colors = {
                "Common": "#95a5a6",
                "Uncommon": "#3498db", 
                "Rare": "#9b59b6",
                "Epic": "#f39c12",
                "Legendary": "#e74c3c"
            }
            
            st.markdown(f"""
            <div style='background: {rarity_colors[badge["rarity"]]}; padding: 1rem; border-radius: 8px; color: white; text-align: center; margin-bottom: 1rem;'>
                <h2>{badge['icon']}</h2>
                <h4>{badge['name']}</h4>
                <p>{badge['description']}</p>
                <small>{badge['rarity']}</small>
            </div>
            """, unsafe_allow_html=True)

def contributors_section():
    st.markdown("### 👥 Community Contributors")
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("👥 Real contributors data would be displayed here when available from the API")
        return
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_contributor = st.text_input("🔍 Search contributors", placeholder="Name or location")
    
    with col2:
        filter_specialty = st.selectbox("Filter by Specialty", 
            ["All", "Folk Songs", "Stories", "Recipes", "Arts", "Crafts", "Dance", "Music"])
    
    with col3:
        filter_location = st.selectbox("Filter by Region",
            ["All", "North India", "South India", "East India", "West India", "Northeast"])
    
    # Contributors grid
    contributors_data = [
        {
            "name": "Dr. Kamala Devi",
            "title": "Cultural Anthropologist",
            "location": "Chennai, Tamil Nadu",
            "specialty": "Classical Arts",
            "contributions": 89,
            "joined": "2023-03-15",
            "verified": True,
            "avatar": "👩‍🎓"
        },
        {
            "name": "Ravi Shankar",
            "title": "Folk Music Researcher", 
            "location": "Varanasi, Uttar Pradesh",
            "specialty": "Folk Songs",
            "contributions": 156,
            "joined": "2023-01-20",
            "verified": True,
            "avatar": "👨‍🎤"
        },
        {
            "name": "Anita Desai",
            "title": "Food Heritage Expert",
            "location": "Delhi",
            "specialty": "Traditional Recipes",
            "contributions": 67,
            "joined": "2023-06-10",
            "verified": False,
            "avatar": "👩‍🍳"
        },
        {
            "name": "Suresh Babu",
            "title": "Storyteller",
            "location": "Mysore, Karnataka",
            "specialty": "Folk Tales",
            "contributions": 134,
            "joined": "2023-02-28",
            "verified": True,
            "avatar": "👨‍🏫"
        }
    ]
    
    cols = st.columns(2)
    for i, contributor in enumerate(contributors_data):
        with cols[i % 2]:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: #f0f2f6; padding: 1rem; border-radius: 50%; text-align: center; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center;'>
                        <h1>{contributor['avatar']}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    verified_badge = "✅" if contributor['verified'] else ""
                    st.markdown(f"**{contributor['name']}** {verified_badge}")
                    st.markdown(f"*{contributor['title']}*")
                    st.markdown(f"📍 {contributor['location']}")
                    st.markdown(f"🎯 {contributor['specialty']}")
                    st.markdown(f"📊 {contributor['contributions']} contributions")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👁️ View Profile", key=f"view_contrib_{i}"):
                        st.success(f"Viewing {contributor['name']}'s profile")
                with col2:
                    if st.button("💬 Message", key=f"msg_contrib_{i}"):
                        st.success(f"Message sent to {contributor['name']}")
                
                st.markdown("---")

def challenges_section():
    st.markdown("### 🎯 Community Challenges")
    
    # Active challenges
    st.markdown("#### 🔥 Active Challenges")
    
    challenges = [
        {
            "title": "Festival Season Documentation",
            "description": "Document unique festival traditions from your region during the upcoming festival season",
            "reward": "500 points + Festival Expert badge",
            "deadline": "2024-03-15",
            "participants": 45,
            "difficulty": "Medium",
            "type": "Seasonal"
        },
        {
            "title": "Endangered Languages Project",
            "description": "Record and transcribe content in endangered or less-documented Indian languages",
            "reward": "1000 points + Language Guardian badge",
            "deadline": "2024-04-30",
            "participants": 23,
            "difficulty": "Hard",
            "type": "Preservation"
        },
        {
            "title": "Recipe Revival Challenge",
            "description": "Share traditional recipes that are at risk of being forgotten",
            "reward": "300 points + Recipe Master badge",
            "deadline": "2024-02-28",
            "participants": 67,
            "difficulty": "Easy",
            "type": "Food Heritage"
        }
    ]
    
    for challenge in challenges:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                difficulty_colors = {"Easy": "#2ecc71", "Medium": "#f39c12", "Hard": "#e74c3c"}
                
                st.markdown(f"### {challenge['title']}")
                st.markdown(f"**Type:** {challenge['type']} | **Difficulty:** <span style='color: {difficulty_colors[challenge['difficulty']]}'>{challenge['difficulty']}</span>", unsafe_allow_html=True)
                st.markdown(challenge['description'])
                st.markdown(f"**Reward:** {challenge['reward']}")
                st.markdown(f"**Deadline:** {challenge['deadline']} | **Participants:** {challenge['participants']}")
            
            with col2:
                if st.button("Join Challenge", key=f"join_{challenge['title']}", use_container_width=True):
                    st.success(f"Joined {challenge['title']}!")
                
                if st.button("View Details", key=f"details_{challenge['title']}", use_container_width=True):
                    st.info("Challenge details opened")
            
            st.markdown("---")
    
    # Challenge leaderboard
    st.markdown("#### 🏆 Challenge Leaderboard")
    
    challenge_leaders = [
        {"name": "Priya K.", "challenges_won": 8, "total_points": 3200},
        {"name": "Rajesh M.", "challenges_won": 6, "total_points": 2800},
        {"name": "Meera S.", "challenges_won": 5, "total_points": 2400},
        {"name": "Arjun P.", "challenges_won": 4, "total_points": 1900}
    ]
    
    for i, leader in enumerate(challenge_leaders, 1):
        col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
        
        with col1:
            st.markdown(f"**#{i}**")
        with col2:
            st.markdown(f"**{leader['name']}**")
        with col3:
            st.markdown(f"🏆 {leader['challenges_won']} wins")
        with col4:
            st.markdown(f"⭐ {leader['total_points']} pts")

def discussions_section():
    st.markdown("### 💬 Community Discussions")
    
    # Discussion categories
    categories = st.tabs(["🔥 Popular", "❓ Q&A", "💡 Ideas", "📢 Announcements"])
    
    with categories[0]:  # Popular
        discussions = [
            {
                "title": "Best practices for recording folk songs",
                "author": "MusicLover23",
                "replies": 34,
                "views": 567,
                "last_activity": "2 hours ago",
                "category": "Audio",
                "pinned": True
            },
            {
                "title": "How to preserve family recipes for future generations?",
                "author": "GrandmaRecipes",
                "replies": 28,
                "views": 445,
                "last_activity": "5 hours ago",
                "category": "Food",
                "pinned": False
            },
            {
                "title": "Regional variations in wedding customs",
                "author": "CultureExplorer",
                "replies": 52,
                "views": 789,
                "last_activity": "1 day ago",
                "category": "Traditions",
                "pinned": False
            }
        ]
        
        for discussion in discussions:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    pin_icon = "📌 " if discussion['pinned'] else ""
                    st.markdown(f"### {pin_icon}{discussion['title']}")
                    st.markdown(f"By **{discussion['author']}** in *{discussion['category']}*")
                    st.markdown(f"💬 {discussion['replies']} replies | 👁️ {discussion['views']} views | ⏰ {discussion['last_activity']}")
                
                with col2:
                    if st.button("Join Discussion", key=f"join_disc_{discussion['title']}", use_container_width=True):
                        st.success("Joined discussion!")
                
                st.markdown("---")
    
    with categories[1]:  # Q&A
        st.markdown("#### ❓ Ask the Community")
        
        question = st.text_area("What would you like to know?", placeholder="Ask about cultural practices, traditions, or anything related to Indian heritage...")
        
        if st.button("Post Question", type="primary"):
            st.success("Your question has been posted!")
        
        st.markdown("#### Recent Questions")
        
        questions = [
            {"q": "What's the significance of rangoli patterns?", "answers": 12, "author": "CuriousLearner"},
            {"q": "How to identify authentic classical ragas?", "answers": 8, "author": "MusicStudent"},
            {"q": "Regional differences in Diwali celebrations?", "answers": 15, "author": "FestivalFan"}
        ]
        
        for q in questions:
            st.markdown(f"**Q:** {q['q']}")
            st.markdown(f"By {q['author']} | {q['answers']} answers")
            st.markdown("---")

def projects_section():
    st.markdown("### 🚀 Community Projects")
    
    # Featured projects
    projects = [
        {
            "title": "Digital Archive of Tribal Songs",
            "description": "Collaborative effort to document and preserve tribal music from Northeast India",
            "lead": "Dr. Maya Sharma",
            "contributors": 23,
            "progress": 65,
            "status": "Active",
            "category": "Preservation"
        },
        {
            "title": "Interactive Festival Calendar",
            "description": "Creating a comprehensive calendar of Indian festivals with regional variations",
            "lead": "Rajesh Kumar",
            "contributors": 45,
            "progress": 80,
            "status": "Active", 
            "category": "Documentation"
        },
        {
            "title": "Traditional Craft Techniques",
            "description": "Video documentation of traditional craft-making processes",
            "lead": "Artisan Guild",
            "contributors": 18,
            "progress": 40,
            "status": "Recruiting",
            "category": "Arts & Crafts"
        }
    ]
    
    for project in projects:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_colors = {"Active": "#2ecc71", "Recruiting": "#f39c12", "Completed": "#95a5a6"}
                
                st.markdown(f"### {project['title']}")
                st.markdown(f"**Category:** {project['category']} | **Status:** <span style='color: {status_colors[project['status']]}'>{project['status']}</span>", unsafe_allow_html=True)
                st.markdown(project['description'])
                st.markdown(f"**Project Lead:** {project['lead']}")
                st.markdown(f"**Contributors:** {project['contributors']} | **Progress:** {project['progress']}%")
                
                # Progress bar
                st.progress(project['progress'] / 100)
            
            with col2:
                if st.button("Join Project", key=f"join_proj_{project['title']}", use_container_width=True):
                    st.success(f"Joined {project['title']}!")
                
                if st.button("View Details", key=f"proj_details_{project['title']}", use_container_width=True):
                    st.info("Project details opened")
            
            st.markdown("---")
    
    # Start new project
    st.markdown("### ➕ Start a New Project")
    
    with st.expander("Propose a Community Project"):
        project_title = st.text_input("Project Title")
        project_desc = st.text_area("Project Description")
        project_category = st.selectbox("Category", ["Preservation", "Documentation", "Arts & Crafts", "Music", "Food", "Stories", "Other"])
        
        if st.button("Submit Proposal", type="primary"):
            st.success("Project proposal submitted for community review!")

def show_contributor_profile(contributor):
    """Show detailed contributor profile"""
    st.markdown(f"## Profile: {contributor['name']}")
    st.markdown(f"**Specialty:** {contributor['specialty']}")
    st.markdown(f"**Location:** {contributor['location']}")
    st.markdown(f"**Contributions:** {contributor['contributions']}")
    st.markdown(f"**Points:** {contributor['points']}")