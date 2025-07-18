"""
Community-specific styling for BharatVerse
"""

import streamlit as st

def apply_community_styling():
    """Apply community-specific CSS styling"""
    st.markdown("""
    <style>
    /* Community Chat Styling */
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #ff6b35;
    }
    
    .chat-message {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .chat-message.own {
        background-color: #e3f2fd;
        margin-left: 20px;
    }
    
    .chat-sender {
        font-weight: bold;
        color: #ff6b35;
        font-size: 0.9em;
    }
    
    .chat-time {
        color: #666;
        font-size: 0.8em;
        font-style: italic;
    }
    
    .chat-content {
        margin: 5px 0;
        line-height: 1.4;
    }
    
    /* Group Card Styling */
    .group-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .group-card h3 {
        margin-top: 0;
        color: white;
    }
    
    .group-card .description {
        opacity: 0.9;
        margin: 10px 0;
    }
    
    .group-card .stats {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 15px;
    }
    
    /* Discussion Thread Styling */
    .discussion-topic {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #fafafa;
    }
    
    .discussion-topic.pinned {
        border-color: #ff6b35;
        background-color: #fff3e0;
    }
    
    .discussion-reply {
        border-left: 3px solid #ff6b35;
        padding-left: 15px;
        margin: 10px 0;
        background-color: white;
        border-radius: 0 8px 8px 0;
    }
    
    /* Challenge Card Styling */
    .challenge-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .challenge-card h3 {
        color: white;
        margin-top: 0;
    }
    
    .challenge-timer {
        background-color: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 5px 15px;
        display: inline-block;
        font-weight: bold;
    }
    
    /* Leaderboard Styling */
    .leaderboard-podium {
        text-align: center;
        padding: 20px;
        margin: 10px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .leaderboard-podium.first {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        transform: scale(1.05);
    }
    
    .leaderboard-podium.second {
        background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
    }
    
    .leaderboard-podium.third {
        background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
    }
    
    /* Profile Card Styling */
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .profile-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    
    .profile-stat {
        text-align: center;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
    }
    
    .profile-stat .number {
        font-size: 2em;
        font-weight: bold;
        display: block;
    }
    
    .profile-stat .label {
        font-size: 0.9em;
        opacity: 0.8;
    }
    
    /* Badge Styling */
    .badge {
        display: inline-block;
        background-color: #ff6b35;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
        font-weight: bold;
    }
    
    .badge.gold {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        color: #333;
    }
    
    .badge.silver {
        background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
        color: #333;
    }
    
    .badge.bronze {
        background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
        color: white;
    }
    
    /* Activity Feed Styling */
    .activity-item {
        border-left: 4px solid #ff6b35;
        padding: 10px 15px;
        margin: 8px 0;
        background-color: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    
    .activity-time {
        color: #666;
        font-size: 0.8em;
        float: right;
    }
    
    /* Reaction Buttons */
    .reaction-button {
        background: none;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .reaction-button:hover {
        background-color: #f0f0f0;
        transform: scale(1.1);
    }
    
    /* Community Stats */
    .community-stat {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .community-stat .number {
        font-size: 2.5em;
        font-weight: bold;
        display: block;
        margin-bottom: 5px;
    }
    
    .community-stat .label {
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    .community-stat .delta {
        font-size: 0.9em;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .group-card, .challenge-card, .profile-card {
            margin: 10px 5px;
            padding: 15px;
        }
        
        .profile-stats {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .community-stat .number {
            font-size: 2em;
        }
    }
    
    /* Animation for new messages */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .new-message {
        animation: slideIn 0.3s ease-out;
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #ff6b35;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def render_chat_message(message, current_user_id, is_new=False):
    """Render a chat message with proper styling"""
    is_own = message.get('sender_id') == current_user_id
    css_class = "chat-message own new-message" if is_own and is_new else "chat-message new-message" if is_new else "chat-message own" if is_own else "chat-message"
    
    return f"""
    <div class="{css_class}">
        <div class="chat-sender">{message.get('sender_name', 'Unknown')}</div>
        <div class="chat-content">{message['content']}</div>
        <div class="chat-time">{message['created_at'].strftime('%H:%M')}</div>
    </div>
    """

def render_group_card(group, is_member=False):
    """Render a group card with proper styling"""
    button_text = "Leave" if is_member else "Join"
    button_color = "#dc3545" if is_member else "#28a745"
    
    return f"""
    <div class="group-card">
        <h3>{group['name']}</h3>
        <div class="description">{group['description']}</div>
        <div class="stats">
            <span>👥 {group['actual_member_count']} members</span>
            <span>{group['group_type'].title()} • {group['group_category']}</span>
        </div>
    </div>
    """

def render_challenge_card(challenge):
    """Render a challenge card with proper styling"""
    days_left = (challenge['end_date'] - challenge['created_at']).days
    
    return f"""
    <div class="challenge-card">
        <h3>🏆 {challenge['title']}</h3>
        <div class="challenge-timer">⏰ {days_left} days left</div>
        <p>{challenge['description']}</p>
        <div class="stats">
            <span>👥 {challenge['actual_participant_count']} participants</span>
            <span>🎯 {challenge['challenge_type'].title()}</span>
        </div>
    </div>
    """

def render_profile_stats(profile):
    """Render profile statistics with proper styling"""
    return f"""
    <div class="profile-card">
        <h2>👤 {profile['username']}</h2>
        <div class="profile-stats">
            <div class="profile-stat">
                <span class="number">{profile.get('community_points', 0)}</span>
                <span class="label">Points</span>
            </div>
            <div class="profile-stat">
                <span class="number">{profile.get('contribution_count', 0)}</span>
                <span class="label">Contributions</span>
            </div>
            <div class="profile-stat">
                <span class="number">{profile.get('groups_joined', 0)}</span>
                <span class="label">Groups</span>
            </div>
            <div class="profile-stat">
                <span class="number">{profile.get('challenges_participated', 0)}</span>
                <span class="label">Challenges</span>
            </div>
        </div>
    </div>
    """