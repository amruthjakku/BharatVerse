import streamlit as st

def collaboration_page():
    st.markdown("## 🤝 Collaboration Hub")
    st.markdown("Work together to preserve and document India's cultural heritage")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Active Projects", 
        "📋 Task Board", 
        "🔄 Review Queue", 
        "📊 Team Analytics",
        "🎯 Workflows"
    ])
    
    with tab1:
        active_projects_section()
    
    with tab2:
        task_board_section()
    
    with tab3:
        review_queue_section()
    
    with tab4:
        team_analytics_section()
    
    with tab5:
        workflows_section()

def active_projects_section():
    st.markdown("### 🚀 Active Collaborative Projects")
    
    # Always use real data - demo mode removed
    st.info("🔍 No collaborative projects available yet!")
    st.markdown("**Collaboration features will include:**")
    st.markdown("- Team-based content creation projects")
    st.markdown("- Peer review and validation workflows")
    st.markdown("- Regional cultural documentation initiatives")
    st.markdown("- Expert-guided preservation projects")
    st.markdown("- Community-driven research collaborations")
    
    st.markdown("---")
    st.markdown("#### 🚀 Start a New Project")
    
    with st.form("new_project_form"):
        st.text_input("Project Title")
        st.text_area("Project Description")
        st.selectbox("Project Type", ["Documentation", "Preservation", "Research", "Education"])
        
        if st.form_submit_button("Create Project"):
            st.success("🎉 Project creation feature coming soon!")
    
    return
    
    # Demo mode - show sample projects
    st.info("🎭 **Real Data Mode**: Showing sample collaborative projects")
    
    # Project filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.selectbox("Status", ["All", "Active", "Planning", "Review", "Completed"])
    
    with col2:
        st.selectbox("Type", ["All", "Documentation", "Preservation", "Research", "Education"])
    
    with col3:
        st.selectbox("Sort by", ["Recent", "Priority", "Progress", "Team Size"])
    
    # Get real projects from database
    # TODO: Replace with actual database query when collaboration system is implemented
    projects = []
    
    # For now, show placeholder until collaboration system is built
    if not projects:
        st.info("🤝 No collaborative projects yet!")
        st.markdown("""
        **Start the first collaborative project in your community:**
        - 📚 Document local traditions and customs
        - 🎵 Preserve traditional music and songs
        - 📸 Create visual archives of cultural events
        - 🗣️ Record oral histories and stories
        - 🎭 Document performing arts and crafts
        
        Use the "Create New Project" section below to get started!
        """)
        return
    
    # Display projects
    for project in projects:
        with st.container():
            # Project header
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                priority_colors = {"Critical": "#e74c3c", "High": "#f39c12", "Medium": "#3498db", "Low": "#95a5a6"}
                status_colors = {"Active": "#2ecc71", "Planning": "#f39c12", "Review": "#9b59b6", "Completed": "#95a5a6"}
                
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                        <h3 style='margin: 0; color: #333;'>{project['title']}</h3>
                        <span style='background: {priority_colors[project['priority']]}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 1rem;'>{project['priority']}</span>
                        <span style='background: {status_colors[project['status']]}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;'>{project['status']}</span>
                    </div>
                    <p style='color: #666; margin: 0.5rem 0;'>{project['description']}</p>
                    <div style='display: flex; gap: 1rem; margin: 1rem 0;'>
                        <span><strong>Lead:</strong> {project['lead']}</span>
                        <span><strong>Team:</strong> {project['team_size']} members</span>
                        <span><strong>Deadline:</strong> {project['deadline']}</span>
                    </div>
                    <div style='margin: 1rem 0;'>
                        <div style='background: #f1f3f4; border-radius: 10px; height: 8px; overflow: hidden;'>
                            <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: {project['progress']}%;'></div>
                        </div>
                        <small style='color: #666;'>Progress: {project['progress']}%</small>
                    </div>
                    <div style='margin: 1rem 0;'>
                        {' '.join([f"<span style='background: #e1f5fe; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem; margin-right: 0.5rem;'>{tag}</span>" for tag in project['tags']])}
                    </div>
                    <small style='color: #888;'>Last activity: {project['recent_activity']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("📋 View Details", key=f"details_{project['id']}", use_container_width=True):
                    show_project_details(project)
            
            with col3:
                if st.button("🤝 Join Project", key=f"join_{project['id']}", use_container_width=True):
                    st.success(f"Joined {project['title']}!")
    
    # Create new project
    st.markdown("---")
    st.markdown("### ➕ Start New Collaborative Project")
    
    with st.expander("Create New Project"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Project Title")
            st.text_area("Project Description")
            st.selectbox("Project Type", ["Documentation", "Preservation", "Research", "Education"])
        
        with col2:
            st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            st.date_input("Target Deadline")
            st.text_input("Tags (comma-separated)")
        
        if st.button("🚀 Create Project", type="primary"):
            st.success("Project created successfully! Team members will be notified.")

def task_board_section():
    st.markdown("### 📋 Collaborative Task Board")
    
    # Always use real data - demo mode removed
    st.info("🔍 No collaborative tasks available yet!")
    st.markdown("**Task management features will include:**")
    st.markdown("- Content creation and review tasks")
    st.markdown("- Quality assurance workflows")
    st.markdown("- Translation and localization tasks")
    st.markdown("- Expert validation assignments")
    return

def review_queue_section():
    st.markdown("### 🔄 Content Review Queue")
    
    # Always use real data - demo mode removed
    st.info("🔍 No content in review queue yet!")
    st.markdown("**Review system will include:**")
    st.markdown("- Peer review of contributed content")
    st.markdown("- Expert validation workflows")
    st.markdown("- Quality scoring and feedback")
    st.markdown("- Community moderation tools")
    return

def team_analytics_section():
    st.markdown("### 📊 Team Performance Analytics")
    
    # Always use real data - demo mode removed
    st.info("🔍 No team analytics available yet!")
    st.markdown("**Team analytics will show:**")
    st.markdown("- Collaboration activity metrics")
    st.markdown("- Team productivity insights")
    st.markdown("- Content quality trends")
    st.markdown("- Regional contribution patterns")
    return

def workflows_section():
    st.markdown("### 🎯 Automated Workflows")
    
    # Always use real data - demo mode removed
    st.info("🔍 No automated workflows available yet!")
    st.markdown("**Workflow automation will include:**")
    st.markdown("- Content validation pipelines")
    st.markdown("- Quality assurance workflows")
    st.markdown("- Automated tagging and categorization")
    st.markdown("- Notification and alert systems")
    return

def show_project_details(project):
    """Show detailed project information"""
    st.markdown(f"## Project Details: {project['title']}")
    st.markdown(f"**ID:** {project['id']}")
    st.markdown(f"**Description:** {project['description']}")
    st.markdown(f"**Lead:** {project['lead']}")
    st.markdown(f"**Team Size:** {project['team_size']} members")
    st.markdown(f"**Progress:** {project['progress']}%")
    st.markdown(f"**Priority:** {project['priority']}")
    st.markdown(f"**Status:** {project['status']}")
    st.markdown(f"**Deadline:** {project['deadline']}")
    st.markdown(f"**Type:** {project['type']}")

def show_review_interface(item):
    """Show review interface for content"""
    st.markdown(f"## Review: {item['title']}")
    st.markdown(f"**Type:** {item['type']}")
    st.markdown(f"**Contributor:** {item['contributor']}")
    st.markdown(f"**Quality Score:** {item['quality_score']}%")
    
    # Review form would go here
    st.text_area("Review Comments")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve", type="primary"):
            st.success("Content approved!")
    with col2:
        if st.button("❌ Reject"):
            st.error("Content rejected!")