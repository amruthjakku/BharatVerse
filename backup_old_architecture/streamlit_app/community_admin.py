import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import uuid

def get_postgres_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "bharatverse"),
            user=os.getenv("POSTGRES_USER", "bharatverse_user"),
            password=os.getenv("POSTGRES_PASSWORD", "secretpassword")
        )
        return conn
    except Exception as e:
        st.error(f"Failed to connect to PostgreSQL: {e}")
        return None

def community_admin_page():
    """Community Administration Interface"""
    st.markdown("## 🛠️ Community Administration")
    st.markdown("Manage community groups, challenges, and settings")
    
    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Manage Groups", 
        "🎯 Manage Challenges", 
        "👥 User Management",
        "📊 Analytics"
    ])
    
    with tab1:
        manage_groups_section()
    
    with tab2:
        manage_challenges_section()
    
    with tab3:
        user_management_section()
    
    with tab4:
        analytics_section()

def manage_groups_section():
    """Manage Community Groups"""
    st.markdown("### 🏠 Community Groups Management")
    
    # Add new group
    with st.expander("➕ Add New Community Group"):
        with st.form("add_group_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                group_name = st.text_input("Group Name*")
                group_type = st.selectbox("Group Type*", ["language", "regional", "interest"])
                group_category = st.text_input("Category*", help="e.g., Bengali, North India, Festivals")
            
            with col2:
                description = st.text_area("Description*")
                is_public = st.checkbox("Public Group", value=True)
                image_url = st.text_input("Image URL (optional)")
            
            if st.form_submit_button("Create Group", type="primary"):
                if group_name and group_type and group_category and description:
                    if create_community_group(group_name, description, group_type, group_category, is_public, image_url):
                        st.success(f"Community group '{group_name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create community group")
                else:
                    st.error("Please fill in all required fields")
    
    # Display existing groups
    st.markdown("### Existing Community Groups")
    groups = get_all_community_groups()
    
    if groups:
        for group in groups:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{group['name']}**")
                    st.markdown(f"*{group['description']}*")
                    st.markdown(f"Type: {group['group_type'].title()} | Category: {group['group_category']} | Members: {group['member_count']}")
                    st.markdown(f"Created: {group['created_at'].strftime('%Y-%m-%d')}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_group_{group['id']}"):
                        st.session_state[f"edit_group_{group['id']}"] = True
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_group_{group['id']}"):
                        if delete_community_group(group['id']):
                            st.success(f"Group '{group['name']}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete group")
                
                # Edit form
                if st.session_state.get(f"edit_group_{group['id']}", False):
                    with st.form(f"edit_group_form_{group['id']}"):
                        st.markdown(f"**Editing: {group['name']}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Name", value=group['name'])
                            new_type = st.selectbox("Type", ["language", "regional", "interest"], 
                                                  index=["language", "regional", "interest"].index(group['group_type']))
                            new_category = st.text_input("Category", value=group['group_category'])
                        
                        with col2:
                            new_description = st.text_area("Description", value=group['description'])
                            new_is_public = st.checkbox("Public", value=group['is_public'])
                            new_image_url = st.text_input("Image URL", value=group['image_url'] or "")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                if update_community_group(group['id'], new_name, new_description, new_type, 
                                                        new_category, new_is_public, new_image_url):
                                    st.success("Group updated successfully!")
                                    st.session_state[f"edit_group_{group['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update group")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_group_{group['id']}"] = False
                                st.rerun()
                
                st.markdown("---")
    else:
        st.info("No community groups found.")

def manage_challenges_section():
    """Manage Community Challenges"""
    st.markdown("### 🎯 Community Challenges Management")
    
    # Add new challenge
    with st.expander("➕ Add New Challenge"):
        with st.form("add_challenge_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                challenge_title = st.text_input("Challenge Title*")
                challenge_type = st.selectbox("Challenge Type*", ["preservation", "documentation", "creative"])
                start_date = st.date_input("Start Date", value=datetime.now().date())
                end_date = st.date_input("End Date", value=(datetime.now() + timedelta(days=30)).date())
            
            with col2:
                description = st.text_area("Description*")
                is_active = st.checkbox("Active", value=True)
                points_reward = st.number_input("Points Reward", min_value=0, value=50)
                badge_name = st.text_input("Badge Name", placeholder="e.g., Recipe Keeper")
            
            requirements = st.text_area("Requirements (JSON format)", 
                                      value='{"min_description": 100, "required_fields": []}',
                                      help="JSON format for challenge requirements")
            
            if st.form_submit_button("Create Challenge", type="primary"):
                if challenge_title and challenge_type and description:
                    try:
                        import json
                        req_json = json.loads(requirements) if requirements else {}
                        rewards_json = {"points": points_reward, "badge": badge_name} if badge_name else {"points": points_reward}
                        
                        if create_community_challenge(challenge_title, description, challenge_type, 
                                                    req_json, rewards_json, start_date, end_date, is_active):
                            st.success(f"Challenge '{challenge_title}' created successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to create challenge")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format in requirements")
                else:
                    st.error("Please fill in all required fields")
    
    # Display existing challenges
    st.markdown("### Existing Challenges")
    challenges = get_all_community_challenges()
    
    if challenges:
        for challenge in challenges:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_icon = "🟢" if challenge['is_active'] else "🔴"
                    st.markdown(f"**{status_icon} {challenge['title']}**")
                    st.markdown(f"*{challenge['description'][:100]}...*")
                    st.markdown(f"Type: {challenge['challenge_type'].title()} | Participants: {challenge['participant_count']}")
                    if challenge['start_date'] and challenge['end_date']:
                        st.markdown(f"Duration: {challenge['start_date'].strftime('%Y-%m-%d')} to {challenge['end_date'].strftime('%Y-%m-%d')}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_challenge_{challenge['id']}"):
                        st.session_state[f"edit_challenge_{challenge['id']}"] = True
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_challenge_{challenge['id']}"):
                        if delete_community_challenge(challenge['id']):
                            st.success(f"Challenge '{challenge['title']}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete challenge")
                
                # Edit form (similar to groups)
                if st.session_state.get(f"edit_challenge_{challenge['id']}", False):
                    with st.form(f"edit_challenge_form_{challenge['id']}"):
                        st.markdown(f"**Editing: {challenge['title']}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_title = st.text_input("Title", value=challenge['title'])
                            new_type = st.selectbox("Type", ["preservation", "documentation", "creative"],
                                                  index=["preservation", "documentation", "creative"].index(challenge['challenge_type']))
                            new_is_active = st.checkbox("Active", value=challenge['is_active'])
                        
                        with col2:
                            new_description = st.text_area("Description", value=challenge['description'])
                            new_start_date = st.date_input("Start Date", value=challenge['start_date'].date() if challenge['start_date'] else datetime.now().date())
                            new_end_date = st.date_input("End Date", value=challenge['end_date'].date() if challenge['end_date'] else datetime.now().date())
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                if update_community_challenge(challenge['id'], new_title, new_description, new_type,
                                                            new_start_date, new_end_date, new_is_active):
                                    st.success("Challenge updated successfully!")
                                    st.session_state[f"edit_challenge_{challenge['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to update challenge")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_challenge_{challenge['id']}"] = False
                                st.rerun()
                
                st.markdown("---")
    else:
        st.info("No challenges found.")

def user_management_section():
    """User Management"""
    st.markdown("### 👥 User Management")
    
    # Get user statistics
    users = get_all_users()
    
    if users:
        st.markdown(f"**Total Users:** {len(users)}")
        
        # Display users in a table
        df = pd.DataFrame(users)
        if not df.empty:
            st.dataframe(df[['username', 'email', 'full_name', 'created_at']], use_container_width=True)
        
        # User details
        st.markdown("### User Details")
        for user in users[:10]:  # Show first 10 users
            with st.expander(f"👤 {user['username']} ({user['email']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Full Name:** {user['full_name'] or 'Not provided'}")
                    st.markdown(f"**Email:** {user['email']}")
                    st.markdown(f"**Created:** {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    # Get user's group memberships
                    memberships = get_user_group_memberships(user['id'])
                    if memberships:
                        st.markdown("**Group Memberships:**")
                        for membership in memberships:
                            st.markdown(f"- {membership['group_name']} ({membership['role']})")
                    else:
                        st.markdown("**No group memberships**")
    else:
        st.info("No users found.")

def analytics_section():
    """Analytics Dashboard"""
    st.markdown("### 📊 Community Analytics")
    
    # Get analytics data
    analytics = get_community_analytics()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Groups", analytics['total_groups'])
    with col2:
        st.metric("Active Challenges", analytics['active_challenges'])
    with col3:
        st.metric("Total Users", analytics['total_users'])
    with col4:
        st.metric("Total Memberships", analytics['total_memberships'])
    
    # Charts
    if analytics['groups_by_type']:
        st.markdown("### Groups by Type")
        df_groups = pd.DataFrame(list(analytics['groups_by_type'].items()), columns=['Type', 'Count'])
        st.bar_chart(df_groups.set_index('Type'))
    
    if analytics['challenges_by_type']:
        st.markdown("### Challenges by Type")
        df_challenges = pd.DataFrame(list(analytics['challenges_by_type'].items()), columns=['Type', 'Count'])
        st.bar_chart(df_challenges.set_index('Type'))

# Database functions
def create_community_group(name, description, group_type, group_category, is_public, image_url):
    """Create a new community group"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO community_groups (name, description, group_type, group_category, is_public, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, description, group_type, group_category, is_public, image_url or None))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error creating group: {e}")
        return False

def get_all_community_groups():
    """Get all community groups"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return []
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT g.*, COUNT(gm.user_id) as member_count
                FROM community_groups g
                LEFT JOIN group_memberships gm ON g.id = gm.group_id
                GROUP BY g.id
                ORDER BY g.created_at DESC
            """)
            groups = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return groups
    except Exception as e:
        st.error(f"Error fetching groups: {e}")
        return []

def update_community_group(group_id, name, description, group_type, group_category, is_public, image_url):
    """Update a community group"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE community_groups 
                SET name = %s, description = %s, group_type = %s, group_category = %s, 
                    is_public = %s, image_url = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (name, description, group_type, group_category, is_public, image_url or None, group_id))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating group: {e}")
        return False

def delete_community_group(group_id):
    """Delete a community group"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            # Delete related data first
            cursor.execute("DELETE FROM group_memberships WHERE group_id = %s", (group_id,))
            cursor.execute("DELETE FROM discussion_topics WHERE group_id = %s", (group_id,))
            cursor.execute("DELETE FROM chat_messages WHERE group_id = %s", (group_id,))
            cursor.execute("DELETE FROM community_groups WHERE id = %s", (group_id,))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting group: {e}")
        return False

def create_community_challenge(title, description, challenge_type, requirements, rewards, start_date, end_date, is_active):
    """Create a new community challenge"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO community_challenges 
                (title, description, challenge_type, requirements, rewards, start_date, end_date, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, challenge_type, 
                  psycopg2.extras.Json(requirements), psycopg2.extras.Json(rewards),
                  start_date, end_date, is_active))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error creating challenge: {e}")
        return False

def get_all_community_challenges():
    """Get all community challenges"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return []
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT c.*, COUNT(cp.user_id) as participant_count
                FROM community_challenges c
                LEFT JOIN challenge_participations cp ON c.id = cp.challenge_id
                GROUP BY c.id
                ORDER BY c.created_at DESC
            """)
            challenges = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return challenges
    except Exception as e:
        st.error(f"Error fetching challenges: {e}")
        return []

def update_community_challenge(challenge_id, title, description, challenge_type, start_date, end_date, is_active):
    """Update a community challenge"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE community_challenges 
                SET title = %s, description = %s, challenge_type = %s, 
                    start_date = %s, end_date = %s, is_active = %s
                WHERE id = %s
            """, (title, description, challenge_type, start_date, end_date, is_active, challenge_id))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating challenge: {e}")
        return False

def delete_community_challenge(challenge_id):
    """Delete a community challenge"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return False
        
        with conn.cursor() as cursor:
            # Delete related data first
            cursor.execute("DELETE FROM challenge_participations WHERE challenge_id = %s", (challenge_id,))
            cursor.execute("DELETE FROM community_challenges WHERE id = %s", (challenge_id,))
            
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting challenge: {e}")
        return False

def get_all_users():
    """Get all users"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return []
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            users = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return users
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def get_user_group_memberships(user_id):
    """Get user's group memberships"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return []
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT gm.role, g.name as group_name, gm.joined_at
                FROM group_memberships gm
                JOIN community_groups g ON gm.group_id = g.id
                WHERE gm.user_id = %s
                ORDER BY gm.joined_at DESC
            """, (user_id,))
            memberships = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return memberships
    except Exception as e:
        st.error(f"Error fetching memberships: {e}")
        return []

def get_community_analytics():
    """Get community analytics"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return {}
        
        analytics = {}
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Total groups
            cursor.execute("SELECT COUNT(*) as count FROM community_groups")
            analytics['total_groups'] = cursor.fetchone()['count']
            
            # Active challenges
            cursor.execute("SELECT COUNT(*) as count FROM community_challenges WHERE is_active = true")
            analytics['active_challenges'] = cursor.fetchone()['count']
            
            # Total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            analytics['total_users'] = cursor.fetchone()['count']
            
            # Total memberships
            cursor.execute("SELECT COUNT(*) as count FROM group_memberships")
            analytics['total_memberships'] = cursor.fetchone()['count']
            
            # Groups by type
            cursor.execute("SELECT group_type, COUNT(*) as count FROM community_groups GROUP BY group_type")
            analytics['groups_by_type'] = {row['group_type']: row['count'] for row in cursor.fetchall()}
            
            # Challenges by type
            cursor.execute("SELECT challenge_type, COUNT(*) as count FROM community_challenges GROUP BY challenge_type")
            analytics['challenges_by_type'] = {row['challenge_type']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        return analytics
    except Exception as e:
        st.error(f"Error fetching analytics: {e}")
        return {}

if __name__ == "__main__":
    community_admin_page()