import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
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
            project_title = st.text_input("Project Title")
            project_description = st.text_area("Project Description")
            project_type = st.selectbox("Project Type", ["Documentation", "Preservation", "Research", "Education"])
            
            if st.form_submit_button("Create Project"):
                st.success("🎉 Project creation feature coming soon!")
        
        return
    
    # Demo mode - show sample projects
    st.info("🎭 **Demo Mode**: Showing sample collaborative projects")
    
    # Project filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        project_status = st.selectbox("Status", ["All", "Active", "Planning", "Review", "Completed"])
    
    with col2:
        project_type = st.selectbox("Type", ["All", "Documentation", "Preservation", "Research", "Education"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Recent", "Priority", "Progress", "Team Size"])
    
    # Active projects
    projects = [
        {
            "id": "PROJ001",
            "title": "Digital Archive of Tribal Music",
            "description": "Comprehensive documentation of tribal music from Northeast India",
            "lead": "Dr. Maya Sharma",
            "team_size": 12,
            "progress": 68,
            "priority": "High",
            "status": "Active",
            "deadline": "2024-03-15",
            "type": "Preservation",
            "tags": ["Music", "Tribal", "Northeast", "Audio"],
            "recent_activity": "2 hours ago"
        },
        {
            "id": "PROJ002", 
            "title": "Festival Calendar Documentation",
            "description": "Creating comprehensive calendar of Indian festivals with regional variations",
            "lead": "Rajesh Kumar",
            "team_size": 8,
            "progress": 45,
            "priority": "Medium",
            "status": "Active",
            "deadline": "2024-04-20",
            "type": "Documentation",
            "tags": ["Festivals", "Calendar", "Regional", "Cultural"],
            "recent_activity": "5 hours ago"
        },
        {
            "id": "PROJ003",
            "title": "Traditional Craft Techniques",
            "description": "Video documentation of traditional craft-making processes",
            "lead": "Artisan Guild",
            "team_size": 15,
            "progress": 82,
            "priority": "High",
            "status": "Review",
            "deadline": "2024-02-28",
            "type": "Documentation",
            "tags": ["Crafts", "Video", "Traditional", "Techniques"],
            "recent_activity": "1 day ago"
        },
        {
            "id": "PROJ004",
            "title": "Endangered Languages Initiative",
            "description": "Recording and preserving endangered Indian languages",
            "lead": "Language Preservation Society",
            "team_size": 20,
            "progress": 34,
            "priority": "Critical",
            "status": "Active",
            "deadline": "2024-06-30",
            "type": "Preservation",
            "tags": ["Languages", "Endangered", "Audio", "Documentation"],
            "recent_activity": "3 hours ago"
        }
    ]
    
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
            new_title = st.text_input("Project Title")
            new_description = st.text_area("Project Description")
            new_type = st.selectbox("Project Type", ["Documentation", "Preservation", "Research", "Education"])
        
        with col2:
            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            new_deadline = st.date_input("Target Deadline")
            new_tags = st.text_input("Tags (comma-separated)")
        
        if st.button("🚀 Create Project", type="primary"):
            st.success("Project created successfully! Team members will be notified.")

def task_board_section():
    st.markdown("### 📋 Collaborative Task Board")
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("🔍 No collaborative tasks available yet!")
        st.markdown("**Task management features will include:**")
        st.markdown("- Content creation and review tasks")
        st.markdown("- Quality assurance workflows")
        st.markdown("- Translation and localization tasks")
        st.markdown("- Expert validation assignments")
        return
    
    # Demo mode
    st.info("🎭 **Demo Mode**: Showing sample task board")
    
    # Task filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        task_project = st.selectbox("Project", ["All Projects", "Tribal Music Archive", "Festival Calendar", "Craft Documentation"])
    
    with col2:
        task_assignee = st.selectbox("Assignee", ["All", "My Tasks", "Unassigned", "Team Tasks"])
    
    with col3:
        task_priority = st.selectbox("Priority", ["All", "Critical", "High", "Medium", "Low"])
    
    with col4:
        task_status = st.selectbox("Status", ["All", "To Do", "In Progress", "Review", "Done"])
    
    # Kanban-style board
    col1, col2, col3, col4 = st.columns(4)
    
    # Sample tasks
    tasks = {
        "To Do": [
            {"title": "Record Bodo folk songs", "assignee": "Priya K.", "priority": "High", "project": "Tribal Music"},
            {"title": "Document Assam Bihu", "assignee": "Unassigned", "priority": "Medium", "project": "Festival Calendar"},
            {"title": "Create pottery video", "assignee": "Artisan Team", "priority": "High", "project": "Craft Documentation"}
        ],
        "In Progress": [
            {"title": "Transcribe Manipuri songs", "assignee": "Rajesh M.", "priority": "High", "project": "Tribal Music"},
            {"title": "Edit craft videos", "assignee": "Video Team", "priority": "Medium", "project": "Craft Documentation"}
        ],
        "Review": [
            {"title": "Bengali folk tale collection", "assignee": "Review Team", "priority": "Medium", "project": "Documentation"},
            {"title": "Festival photo curation", "assignee": "Meera S.", "priority": "Low", "project": "Festival Calendar"}
        ],
        "Done": [
            {"title": "Upload Rajasthani songs", "assignee": "Audio Team", "priority": "High", "project": "Tribal Music"},
            {"title": "Diwali documentation", "assignee": "Festival Team", "priority": "Medium", "project": "Festival Calendar"}
        ]
    }
    
    columns = [col1, col2, col3, col4]
    statuses = ["To Do", "In Progress", "Review", "Done"]
    status_colors = ["#f39c12", "#3498db", "#9b59b6", "#2ecc71"]
    
    for i, (status, column) in enumerate(zip(statuses, columns)):
        with column:
            st.markdown(f"""
            <div style='background: {status_colors[i]}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;'>
                <h4 style='margin: 0;'>{status} ({len(tasks[status])})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for task in tasks[status]:
                priority_colors = {"Critical": "#e74c3c", "High": "#f39c12", "Medium": "#3498db", "Low": "#95a5a6"}
                
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid {priority_colors[task['priority']]};'>
                    <h5 style='margin: 0 0 0.5rem 0; color: #333;'>{task['title']}</h5>
                    <p style='margin: 0; color: #666; font-size: 0.9rem;'><strong>Assignee:</strong> {task['assignee']}</p>
                    <p style='margin: 0; color: #666; font-size: 0.9rem;'><strong>Project:</strong> {task['project']}</p>
                    <span style='background: {priority_colors[task['priority']]}; color: white; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.8rem;'>{task['priority']}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # Add new task
    st.markdown("---")
    st.markdown("### ➕ Add New Task")
    
    with st.expander("Create New Task"):
        col1, col2 = st.columns(2)
        
        with col1:
            task_title = st.text_input("Task Title")
            task_desc = st.text_area("Task Description")
            task_project_new = st.selectbox("Assign to Project", ["Tribal Music Archive", "Festival Calendar", "Craft Documentation"])
        
        with col2:
            task_assignee_new = st.text_input("Assignee (optional)")
            task_priority_new = st.selectbox("Task Priority", ["Low", "Medium", "High", "Critical"])
            task_deadline = st.date_input("Due Date")
        
        if st.button("➕ Create Task", type="primary"):
            st.success("Task created and assigned!")

def review_queue_section():
    st.markdown("### 🔄 Content Review Queue")
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("🔍 No content in review queue yet!")
        st.markdown("**Review system will include:**")
        st.markdown("- Peer review of contributed content")
        st.markdown("- Expert validation workflows")
        st.markdown("- Quality scoring and feedback")
        st.markdown("- Community moderation tools")
        return
    
    # Demo mode
    st.info("🎭 **Demo Mode**: Showing sample review queue")
    
    # Review stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending Reviews", "23", "+5 today")
    with col2:
        st.metric("Completed Today", "12", "+3 from yesterday")
    with col3:
        st.metric("Average Review Time", "2.3 hrs", "-0.5 hrs")
    with col4:
        st.metric("Approval Rate", "94%", "+2%")
    
    # Review items
    st.markdown("#### 📝 Items Awaiting Review")
    
    review_items = [
        {
            "id": "REV001",
            "title": "Bengali Folk Song - Baul Tradition",
            "type": "Audio",
            "contributor": "Priya Sharma",
            "submitted": "2 hours ago",
            "priority": "High",
            "status": "Pending",
            "reviewer": "Unassigned",
            "quality_score": 87
        },
        {
            "id": "REV002",
            "title": "Rajasthani Wedding Customs",
            "type": "Text",
            "contributor": "Rajesh Kumar",
            "submitted": "5 hours ago",
            "priority": "Medium",
            "status": "In Review",
            "reviewer": "Dr. Maya Sharma",
            "quality_score": 92
        },
        {
            "id": "REV003",
            "title": "Kathakali Performance Photos",
            "type": "Image",
            "contributor": "Meera Nair",
            "submitted": "1 day ago",
            "priority": "Low",
            "status": "Pending",
            "reviewer": "Unassigned",
            "quality_score": 89
        }
    ]
    
    for item in review_items:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                priority_colors = {"High": "#f39c12", "Medium": "#3498db", "Low": "#95a5a6"}
                status_colors = {"Pending": "#f39c12", "In Review": "#3498db", "Approved": "#2ecc71", "Rejected": "#e74c3c"}
                
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0;'>
                    <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                        <h4 style='margin: 0; color: #333;'>{item['title']}</h4>
                        <span style='background: {priority_colors[item['priority']]}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 1rem;'>{item['priority']}</span>
                        <span style='background: {status_colors[item['status']]}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-left: 0.5rem;'>{item['status']}</span>
                    </div>
                    <div style='display: flex; gap: 1rem; margin: 0.5rem 0;'>
                        <span><strong>Type:</strong> {item['type']}</span>
                        <span><strong>Contributor:</strong> {item['contributor']}</span>
                        <span><strong>Submitted:</strong> {item['submitted']}</span>
                    </div>
                    <div style='display: flex; gap: 1rem; margin: 0.5rem 0;'>
                        <span><strong>Reviewer:</strong> {item['reviewer']}</span>
                        <span><strong>Quality Score:</strong> {item['quality_score']}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ Review", key=f"review_{item['id']}", use_container_width=True):
                    show_review_interface(item)
            
            with col3:
                if item['status'] == 'Pending':
                    if st.button("📝 Assign to Me", key=f"assign_{item['id']}", use_container_width=True):
                        st.success(f"Assigned {item['title']} for review!")
    
    # Review guidelines
    st.markdown("---")
    st.markdown("### 📋 Review Guidelines")
    
    with st.expander("Review Criteria & Guidelines"):
        st.markdown("""
        #### ✅ Content Quality Checklist:
        
        **Authenticity (25 points)**
        - Content is genuine and culturally accurate
        - Sources are credible and verifiable
        - No modern adaptations presented as traditional
        
        **Completeness (25 points)**
        - All required metadata is provided
        - Description is comprehensive and informative
        - Proper categorization and tagging
        
        **Technical Quality (25 points)**
        - Audio/video quality meets standards
        - Images are clear and well-composed
        - Text is well-written and error-free
        
        **Cultural Significance (25 points)**
        - Content has educational or preservation value
        - Represents important cultural practices
        - Contributes to diversity of the collection
        
        #### 🎯 Review Process:
        1. **Initial Assessment** - Check basic requirements
        2. **Content Evaluation** - Assess quality and authenticity
        3. **Metadata Review** - Verify completeness and accuracy
        4. **Final Decision** - Approve, request changes, or reject
        5. **Feedback** - Provide constructive comments to contributor
        """)

def team_analytics_section():
    st.markdown("### 📊 Team Performance Analytics")
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("🔍 No team analytics available yet!")
        st.markdown("**Team analytics will show:**")
        st.markdown("- Collaboration activity metrics")
        st.markdown("- Team productivity insights")
        st.markdown("- Content quality trends")
        st.markdown("- Regional contribution patterns")
        return
    
    # Demo mode
    st.info("🎭 **Demo Mode**: Showing sample team analytics")
    
    # Team overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Teams", "12", "+2 this month")
    with col2:
        st.metric("Total Contributors", "156", "+23 this week")
    with col3:
        st.metric("Avg. Team Size", "8.5", "+1.2")
    with col4:
        st.metric("Collaboration Score", "87%", "+5%")
    
    # Team performance chart
    st.markdown("#### 📈 Team Performance Trends")
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
    teams = ['Audio Team', 'Documentation Team', 'Review Team', 'Research Team']
    
    performance_data = []
    for team in teams:
        for date in dates:
            performance_data.append({
                'Date': date,
                'Team': team,
                'Contributions': np.random.randint(5, 25),
                'Quality Score': np.random.randint(75, 98)
            })
    
    df_performance = pd.DataFrame(performance_data)
    
    fig_performance = px.line(
        df_performance,
        x='Date',
        y='Contributions',
        color='Team',
        title='Team Contribution Trends'
    )
    st.plotly_chart(fig_performance, use_container_width=True)
    
    # Individual contributor stats
    st.markdown("#### 👥 Top Contributors This Month")
    
    contributors = [
        {"name": "Priya Sharma", "contributions": 45, "reviews": 23, "score": 94, "team": "Audio Team"},
        {"name": "Rajesh Kumar", "contributions": 38, "reviews": 31, "score": 91, "team": "Documentation"},
        {"name": "Dr. Maya Sharma", "contributions": 29, "reviews": 67, "score": 96, "team": "Review Team"},
        {"name": "Meera Nair", "contributions": 33, "reviews": 18, "score": 89, "team": "Research Team"},
        {"name": "Arjun Singh", "contributions": 27, "reviews": 25, "score": 87, "team": "Audio Team"}
    ]
    
    df_contributors = pd.DataFrame(contributors)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_contrib = px.bar(
            df_contributors,
            x='name',
            y='contributions',
            color='score',
            title='Contributions by Team Member',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_contrib, use_container_width=True)
    
    with col2:
        fig_reviews = px.scatter(
            df_contributors,
            x='contributions',
            y='reviews',
            size='score',
            color='team',
            title='Contributions vs Reviews',
            hover_name='name'
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
    
    # Team collaboration network
    st.markdown("#### 🕸️ Collaboration Network")
    
    st.info("Interactive collaboration network visualization would show how team members work together on projects, with node sizes representing contribution levels and edge thickness showing collaboration frequency.")

def workflows_section():
    st.markdown("### 🎯 Automated Workflows")
    
    # Check if we should use real data
    use_real_data = st.session_state.get('use_real_data', False)
    
    if use_real_data:
        st.info("🔍 No automated workflows available yet!")
        st.markdown("**Workflow automation will include:**")
        st.markdown("- Content validation pipelines")
        st.markdown("- Quality assurance workflows")
        st.markdown("- Automated tagging and categorization")
        st.markdown("- Notification and alert systems")
        return
    
    # Demo mode
    st.info("🎭 **Demo Mode**: Showing sample workflows")
    
    # Workflow templates
    st.markdown("#### 📋 Workflow Templates")
    
    workflows = [
        {
            "name": "Content Submission Workflow",
            "description": "Automated process for new content submissions",
            "steps": ["Submit → Auto-validate → Assign Reviewer → Review → Approve/Reject → Publish"],
            "active": True,
            "success_rate": "94%"
        },
        {
            "name": "Quality Assurance Workflow", 
            "description": "Multi-stage quality checking process",
            "steps": ["Initial Check → Technical Review → Cultural Validation → Final Approval"],
            "active": True,
            "success_rate": "89%"
        },
        {
            "name": "Collaborative Project Workflow",
            "description": "Project management and team coordination",
            "steps": ["Project Creation → Team Assignment → Task Distribution → Progress Tracking → Completion"],
            "active": True,
            "success_rate": "87%"
        }
    ]
    
    for workflow in workflows:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_color = "#2ecc71" if workflow['active'] else "#95a5a6"
                
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; border-left: 4px solid {status_color};'>
                    <h4 style='margin: 0 0 0.5rem 0; color: #333;'>{workflow['name']}</h4>
                    <p style='color: #666; margin: 0.5rem 0;'>{workflow['description']}</p>
                    <p style='color: #888; font-size: 0.9rem; margin: 0.5rem 0;'><strong>Steps:</strong> {workflow['steps'][0]}</p>
                    <div style='display: flex; gap: 1rem; margin-top: 1rem;'>
                        <span style='background: {status_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;'>{'Active' if workflow['active'] else 'Inactive'}</span>
                        <span style='color: #666;'><strong>Success Rate:</strong> {workflow['success_rate']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("⚙️ Configure", key=f"config_{workflow['name']}", use_container_width=True):
                    st.info(f"Configuration panel for {workflow['name']}")
    
    # Automation rules
    st.markdown("---")
    st.markdown("#### 🤖 Automation Rules")
    
    rules = [
        {"trigger": "New audio submission", "action": "Auto-assign to Audio Review Team", "active": True},
        {"trigger": "Quality score > 90%", "action": "Fast-track approval", "active": True},
        {"trigger": "Contributor reaches 50 contributions", "action": "Award Cultural Guardian badge", "active": True},
        {"trigger": "Project 80% complete", "action": "Notify stakeholders", "active": True},
        {"trigger": "Review pending > 48 hours", "action": "Escalate to senior reviewer", "active": False}
    ]
    
    for i, rule in enumerate(rules):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**Trigger:** {rule['trigger']}")
        
        with col2:
            st.markdown(f"**Action:** {rule['action']}")
        
        with col3:
            status = "🟢 Active" if rule['active'] else "🔴 Inactive"
            st.markdown(status)
    
    # Create new workflow
    st.markdown("---")
    st.markdown("#### ➕ Create Custom Workflow")
    
    with st.expander("Build New Workflow"):
        workflow_name = st.text_input("Workflow Name")
        workflow_desc = st.text_area("Description")
        
        st.markdown("**Workflow Steps:**")
        
        # Dynamic step builder
        if 'workflow_steps' not in st.session_state:
            st.session_state.workflow_steps = ["Step 1"]
        
        for i, step in enumerate(st.session_state.workflow_steps):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"Step {i+1}", key=f"step_{i}")
            with col2:
                if st.button("❌", key=f"remove_{i}") and len(st.session_state.workflow_steps) > 1:
                    st.session_state.workflow_steps.pop(i)
                    st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Step"):
                st.session_state.workflow_steps.append(f"Step {len(st.session_state.workflow_steps) + 1}")
                st.rerun()
        
        with col2:
            if st.button("💾 Save Workflow", type="primary"):
                st.success("Custom workflow created successfully!")

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