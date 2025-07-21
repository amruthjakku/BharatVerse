"""
Database Admin Panel for BharatVerse
View and manage user data, contributions, and analytics
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import utilities
from streamlit_app.utils.auth import get_auth_manager, require_auth
from streamlit_app.utils.user_manager import UserManager
from streamlit_app.utils.database import get_db_connection, get_database_stats
from streamlit_app.utils.main_styling import load_custom_css

# Safe database imports
try:
    from utils.supabase_db import get_database_manager
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    get_database_manager = None

def check_admin_access():
    """Check if current user has admin access"""
    auth = get_auth_manager()
    if not auth.is_authenticated():
        st.error("🔒 Please login to access the Database Admin panel")
        st.stop()
    
    user_info = auth.get_current_user()
    if not user_info:
        st.error("❌ Unable to verify user information")
        st.stop()
    
    # For now, allow any authenticated user to view database
    # In production, you'd check for admin role
    return user_info

def show_sqlite_users():
    """Display users from SQLite database"""
    st.subheader("📱 Local SQLite Users")
    
    try:
        user_manager = UserManager()
        
        # Get SQLite connection
        import sqlite3
        conn = sqlite3.connect(user_manager.db_path)
        conn.row_factory = sqlite3.Row
        
        # Query users
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, email, full_name, gitlab_id, 
                   created_at, last_login, login_count, role
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        if users:
            # Convert to DataFrame for better display
            users_data = []
            for user in users:
                users_data.append({
                    'ID': user['id'],
                    'Username': user['username'],
                    'Email': user['email'],
                    'Full Name': user['full_name'],
                    'GitLab ID': user['gitlab_id'],
                    'Role': user['role'] or 'user',
                    'Login Count': user['login_count'] or 0,
                    'Created': user['created_at'],
                    'Last Login': user['last_login']
                })
            
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                admin_count = len([u for u in users_data if u['Role'] == 'admin'])
                st.metric("Admins", admin_count)
            with col3:
                recent_users = len([u for u in users_data if u['Created'] and 
                                  datetime.fromisoformat(u['Created']) > datetime.now() - timedelta(days=7)])
                st.metric("New (7 days)", recent_users)
            with col4:
                active_users = len([u for u in users_data if u['Last Login']])
                st.metric("Ever Logged In", active_users)
                
        else:
            st.info("No users found in SQLite database")
            
    except Exception as e:
        st.error(f"Error accessing SQLite database: {e}")

def show_supabase_users():
    """Display users from Supabase/PostgreSQL database"""
    st.subheader("☁️ Supabase/PostgreSQL Users")
    
    if not SUPABASE_AVAILABLE:
        st.warning("⚠️ Supabase connection not available")
        return
    
    try:
        db_manager = get_database_manager()
        
        # Query users from PostgreSQL
        query = """
            SELECT id, username, email, full_name, region, 
                   preferred_language, created_at, updated_at
            FROM users 
            ORDER BY created_at DESC
            LIMIT 100
        """
        
        users = db_manager.execute_query(query)
        
        if users:
            # Convert to DataFrame
            df = pd.DataFrame(users)
            st.dataframe(df, use_container_width=True)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(users))
            with col2:
                recent_users = len([u for u in users if u.get('created_at') and 
                                  u['created_at'] > datetime.now() - timedelta(days=7)])
                st.metric("New (7 days)", recent_users)
            with col3:
                regions = [u.get('region') for u in users if u.get('region')]
                unique_regions = len(set(regions))
                st.metric("Regions", unique_regions)
                
        else:
            st.info("No users found in Supabase database")
            
    except Exception as e:
        st.error(f"Error accessing Supabase database: {e}")
        st.code(str(e))

def show_contributions_data():
    """Display contributions data"""
    st.subheader("📊 Contributions Data")
    
    try:
        # SQLite contributions
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get contributions by type
        cursor.execute("""
            SELECT contribution_type, COUNT(*) as count,
                   MIN(created_at) as first_contribution,
                   MAX(created_at) as latest_contribution
            FROM contributions 
            GROUP BY contribution_type
            ORDER BY count DESC
        """)
        
        contrib_stats = cursor.fetchall()
        conn.close()
        
        if contrib_stats:
            contrib_data = []
            for stat in contrib_stats:
                contrib_data.append({
                    'Type': stat[0],
                    'Count': stat[1],
                    'First': stat[2],
                    'Latest': stat[3]
                })
            
            df = pd.DataFrame(contrib_data)
            st.dataframe(df, use_container_width=True)
            
            # Show total contributions
            total_contributions = sum([c['Count'] for c in contrib_data])
            st.metric("Total Contributions", total_contributions)
            
        else:
            st.info("No contributions found")
            
    except Exception as e:
        st.error(f"Error accessing contributions data: {e}")

def show_database_health():
    """Show database health and statistics"""
    st.subheader("🏥 Database Health")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### SQLite Status")
        try:
            stats = get_database_stats()
            st.json(stats)
            st.success("✅ SQLite database accessible")
        except Exception as e:
            st.error(f"❌ SQLite error: {e}")
    
    with col2:
        st.markdown("### Supabase Status")
        if SUPABASE_AVAILABLE:
            try:
                db_manager = get_database_manager()
                # Test connection
                result = db_manager.execute_query("SELECT 1 as test")
                if result:
                    st.success("✅ Supabase database accessible")
                else:
                    st.warning("⚠️ Supabase connection issue")
            except Exception as e:
                st.error(f"❌ Supabase error: {e}")
        else:
            st.warning("⚠️ Supabase not configured")

def show_user_search():
    """Search and filter users"""
    st.subheader("🔍 User Search")
    
    search_term = st.text_input("Search users (username, email, or name):")
    
    if search_term:
        try:
            user_manager = UserManager()
            import sqlite3
            conn = sqlite3.connect(user_manager.db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, full_name, gitlab_id, 
                       created_at, last_login, role
                FROM users 
                WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
                ORDER BY created_at DESC
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            users = cursor.fetchall()
            conn.close()
            
            if users:
                for user in users:
                    with st.expander(f"👤 {user['username']} ({user['email']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Full Name:** {user['full_name'] or 'Not set'}")
                            st.write(f"**Role:** {user['role'] or 'user'}")
                            st.write(f"**GitLab ID:** {user['gitlab_id'] or 'Not linked'}")
                        with col2:
                            st.write(f"**Created:** {user['created_at']}")
                            st.write(f"**Last Login:** {user['last_login'] or 'Never'}")
                            st.write(f"**User ID:** {user['id']}")
            else:
                st.info(f"No users found matching '{search_term}'")
                
        except Exception as e:
            st.error(f"Search error: {e}")

def main():
    st.set_page_config(
        page_title="Database Admin - BharatVerse",
        page_icon="🗄️",
        layout="wide"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Check admin access
    user_info = check_admin_access()
    
    st.title("🗄️ Database Administration Panel")
    st.markdown(f"**Logged in as:** {user_info.get('name', 'Unknown')} ({user_info.get('email', 'No email')})")
    
    # Sidebar navigation
    st.sidebar.title("📋 Admin Menu")
    
    menu_option = st.sidebar.selectbox(
        "Choose section:",
        [
            "👥 User Overview",
            "🔍 User Search", 
            "📊 Contributions",
            "🏥 Database Health",
            "⚙️ Database Tools"
        ]
    )
    
    if menu_option == "👥 User Overview":
        st.markdown("## User Database Overview")
        
        # Show users from both databases
        show_sqlite_users()
        st.markdown("---")
        show_supabase_users()
        
    elif menu_option == "🔍 User Search":
        show_user_search()
        
    elif menu_option == "📊 Contributions":
        show_contributions_data()
        
    elif menu_option == "🏥 Database Health":
        show_database_health()
        
    elif menu_option == "⚙️ Database Tools":
        st.subheader("🛠️ Database Management Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Database Stats"):
                st.rerun()
            
            if st.button("📥 Export User Data"):
                try:
                    user_manager = UserManager()
                    import sqlite3
                    conn = sqlite3.connect(user_manager.db_path)
                    
                    df = pd.read_sql_query("""
                        SELECT username, email, full_name, created_at, last_login, role
                        FROM users ORDER BY created_at DESC
                    """, conn)
                    
                    conn.close()
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv,
                        file_name=f"bharatverse_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"Export error: {e}")
        
        with col2:
            st.info("🔒 **Security Note:** This admin panel shows user data for management purposes. Ensure proper access controls in production.")

if __name__ == "__main__":
    main()