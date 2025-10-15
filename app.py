import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from database import TaskDatabase
from llm_handler import LLMTaskPlanner

# Page configuration
st.set_page_config(
    page_title="Smart Task Planner",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and LLM handler
@st.cache_resource
def init_resources():
    db = TaskDatabase()
    llm = LLMTaskPlanner()
    return db, llm

db, llm = init_resources()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .task-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .priority-high {
        border-left: 4px solid #ff4444;
    }
    .priority-medium {
        border-left: 4px solid #ffaa00;
    }
    .priority-low {
        border-left: 4px solid #44ff44;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🚀 Smart Task Planner")
    st.markdown("*AI-Powered by Hugging Face*")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["📝 Create New Plan", "📚 View Projects", "📊 Analytics"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("### About")
    st.info("AI-powered task planner using Hugging Face LLMs to break down goals into actionable steps with timelines and dependencies.")
    
    st.markdown("### Features")
    st.markdown("""
    - 🤖 AI Task Generation  
    - 📊 Progress Tracking  
    - 🎯 Priority Management  
    - 📈 Analytics Dashboard  
    - 💾 Persistent Storage  
    """)

# Main content
if page == "📝 Create New Plan":
    st.markdown('<h1 class="main-header">📋 Create New Task Plan</h1>', unsafe_allow_html=True)
    
    st.markdown("Enter your goal and let AI create a detailed task breakdown with timelines and dependencies.")
    
    with st.form("goal_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            goal = st.text_area(
                "What's your goal?",
                placeholder="Example: Launch a product in 2 weeks, Build a mobile app, Complete research paper...",
                height=120,
                help="Be specific about what you want to achieve"
            )
        
        with col2:
            deadline = st.date_input(
                "Target deadline",
                value=datetime.now() + timedelta(days=14),
                min_value=datetime.now(),
                help="When do you want to complete this goal?"
            )
            
            context = st.text_area(
                "Additional context (optional)",
                placeholder="Team size, budget, constraints, resources available...",
                height=60
            )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            submitted = st.form_submit_button("🚀 Generate Task Plan", use_container_width=True, type="primary")
    
    if submitted and goal:
        with st.spinner("🤖 AI is analyzing your goal and creating a detailed task plan... This may take 20-30 seconds."):
            deadline_str = deadline.strftime("%Y-%m-%d")
            full_goal = f"{goal}\n\nContext: {context}" if context else goal
            
            result = llm.generate_task_plan(full_goal, deadline_str)
            
            if "error" in result:
                st.warning(f"⚠️ {result['error']}")
                st.info("Using fallback task generation...")
            
            project_id = db.save_project(goal, deadline_str)
            db.save_tasks(project_id, result['tasks'])
            
            st.success("✅ Task plan generated successfully!")
            
            # Summary
            st.markdown("## 📊 Your Task Breakdown")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tasks", len(result['tasks']))
            with col2:
                st.metric("Estimated Time", result.get('estimated_total_time', 'N/A'))
            with col3:
                high_priority = len([t for t in result['tasks'] if t.get('priority') == 'high'])
                st.metric("High Priority", high_priority)
            with col4:
                st.metric("Project ID", f"#{project_id}")
            
            # Task list
            st.markdown("### 📝 Task List")
            for idx, task in enumerate(result['tasks'], 1):
                priority_class = f"priority-{task.get('priority', 'medium')}"
                
                with st.container():
                    st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(f"**{idx}. {task['name']}**")
                        st.caption(task.get('description', ''))
                        if task.get('category'):
                            st.markdown(f"🏷️ *{task['category']}*")
                    
                    with col2:
                        st.markdown(f"⏱️ **Duration:** {task.get('duration', 'N/A')}")
                        st.markdown(f"🎯 **Priority:** {task.get('priority', 'medium').upper()}")
                        st.markdown(f"📅 {task.get('start_date', 'TBD')} → {task.get('end_date', 'TBD')}")
                    
                    if task.get('dependencies'):
                        st.markdown(f"**⛓️ Dependencies:** {', '.join(task['dependencies'])}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if result.get('critical_path'):
                    st.markdown("### 🎯 Critical Path")
                    st.info(" → ".join(result['critical_path']))
                
                if result.get('recommendations'):
                    st.markdown("### 💡 Recommendations")
                    for rec in result['recommendations']:
                        st.markdown(f"- {rec}")
            
            with col2:
                if result.get('risk_factors'):
                    st.markdown("### ⚠️ Risk Factors")
                    for risk in result['risk_factors']:
                        st.warning(f"⚠️ {risk}")
                
                st.markdown("### 🔗 Quick Actions")
                st.markdown(f"- View this project in **View Projects** tab")
                st.markdown(f"- Project ID: **{project_id}**")
                st.markdown(f"- Tasks created: **{len(result['tasks'])}**")

elif page == "📚 View Projects":
    st.markdown('<h1 class="main-header">📚 Your Projects</h1>', unsafe_allow_html=True)
    
    projects_df = db.get_all_projects()
    
    if projects_df.empty:
        st.info("📭 No projects yet. Create your first task plan!")
        if st.button("➕ Create New Project", type="primary"):
            st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 Search projects", placeholder="Search by goal...")
        with col2:
            status_filter = st.selectbox("Status", ["All", "active", "completed"])
        with col3:
            st.metric("Total Projects", len(projects_df))
        
        filtered_df = projects_df
        if search:
            filtered_df = filtered_df[filtered_df['goal'].str.contains(search, case=False, na=False)]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        for _, project in filtered_df.iterrows():
            with st.expander(f"📋 {project['goal']} (ID: {project['id']})", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Goal:** {project['goal']}")
                    st.caption(f"Created: {project['created_at']}")
                
                with col2:
                    st.markdown(f"**Deadline:** {project['deadline']}")
                    st.markdown(f"**Status:** {project['status']}")
                
                with col3:
                    if st.button("🗑️ Delete Project", key=f"del_{project['id']}"):
                        db.delete_project(project['id'])
                        st.success("Project deleted!")
                        st.rerun()
                
                tasks_df = db.get_project_tasks(project['id'])
                
                if not tasks_df.empty:
                    st.markdown("#### 📋 Tasks")
                    for _, task in tasks_df.iterrows():
                        priority_class = f"priority-{task['priority']}"
                        st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**{task['task_name']}**")
                            st.caption(task['description'])
                        with col2:
                            st.markdown(f"⏱️ {task['estimated_duration']}")
                            st.markdown(f"🎯 {task['priority'].capitalize()}")
                            st.markdown(f"📅 {task['start_date']} → {task['end_date']}")
                        with col3:
                            new_status = st.selectbox(
                                "Status",
                                ["pending", "in_progress", "completed", "blocked"],
                                index=["pending", "in_progress", "completed", "blocked"].index(task['status']),
                                key=f"status_{task['id']}"
                            )
                            if new_status != task['status']:
                                db.update_task_status(task['id'], new_status)
                                st.success("✅ Status updated!")
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    total_tasks = len(tasks_df)
                    completed = len(tasks_df[tasks_df['status'] == 'completed'])
                    in_progress = len(tasks_df[tasks_df['status'] == 'in_progress'])
                    progress = completed / total_tasks if total_tasks > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Completed", f"{completed}/{total_tasks}")
                    col2.metric("In Progress", in_progress)
                    col3.metric("Progress", f"{progress*100:.0f}%")
                    st.progress(progress)

elif page == "📊 Analytics":
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    projects_df = db.get_all_projects()
    
    if projects_df.empty:
        st.info("📭 No data yet. Create some projects to see analytics!")
    else:
        st.markdown("### 📈 Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        total_projects = len(projects_df)
        active_projects = len(projects_df[projects_df['status'] == 'active'])
        
        all_tasks = []
        for project_id in projects_df['id']:
            tasks = db.get_project_tasks(project_id)
            all_tasks.append(tasks)
        
        if all_tasks:
            all_tasks_df = pd.concat(all_tasks, ignore_index=True)
            total_tasks = len(all_tasks_df)
            completed_tasks = len(all_tasks_df[all_tasks_df['status'] == 'completed'])
        else:
            total_tasks = 0
            completed_tasks = 0
        
        col1.metric("Total Projects", total_projects)
        col2.metric("Active Projects", active_projects)
        col3.metric("Total Tasks", total_tasks)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks else 0
        col4.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        st.divider()
        
        if total_tasks > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Task Status Distribution")
                status_counts = all_tasks_df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, title="Tasks by Status")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🎯 Priority Distribution")
                priority_counts = all_tasks_df['priority'].value_counts()
                fig = px.bar(
                    x=priority_counts.index, y=priority_counts.values,
                    title="Tasks by Priority", labels={'x': 'Priority', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📅 Project Timelines")
            projects_df['deadline'] = pd.to_datetime(projects_df['deadline'])
            projects_df['created_at'] = pd.to_datetime(projects_df['created_at'])
            
            fig = go.Figure()
            for _, project in projects_df.iterrows():
                fig.add_trace(go.Scatter(
                    x=[project['created_at'], project['deadline']],
                    y=[project['goal'], project['goal']],
                    mode='lines+markers',
                    name=project['goal'][:30] + '...' if len(project['goal']) > 30 else project['goal'],
                    line=dict(width=10)
                ))
            fig.update_layout(title="Project Timelines", xaxis_title="Date", yaxis_title="Project", height=400)
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Smart Task Planner | Powered by Hugging Face 🤗 | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
) 
