import streamlit as st
import database as db
import pandas as pd
import plotly.express as px

def show():
    st.title("🎯 Personal Skills Gap Tracker")
    
    tabs = st.tabs(["My Skills", "Add Skill", "Analysis"])
    
    with tabs[0]:
        show_skills_list()
        
    with tabs[1]:
        show_add_skill()
        
    with tabs[2]:
        show_analysis()

def show_skills_list():
    st.subheader("Manage Skills")
    skills_df = db.get_skills()
    
    if skills_df.empty:
        st.info("No skills added yet. Add skills you know or want to learn!")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧠 Skills I Know")
        known = skills_df[skills_df['category'] == 'Already Know']
        if not known.empty:
            st.dataframe(known[['id', 'name']], hide_index=True, use_container_width=True)
        else:
            st.write("No skills in this category.")
            
    with col2:
        st.markdown("### 📚 Skills to Learn")
        to_learn = skills_df[skills_df['category'] == 'Want to Learn']
        if not to_learn.empty:
            for _, row in to_learn.iterrows():
                with st.container():
                    c1, c2, c3 = st.columns([3, 2, 2])
                    c1.write(f"**{row['name']}**")
                    c2.write(f"Priority: {row['priority']}")
                    
                    new_status = c3.selectbox(
                        "Status", 
                        ["Not Started", "In Progress", "Completed"],
                        index=["Not Started", "In Progress", "Completed"].index(row['status']) if row['status'] in ["Not Started", "In Progress", "Completed"] else 0,
                        key=f"skill_status_{row['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != row['status']:
                        db.update_skill_status(row['id'], new_status)
                        st.rerun()
        else:
            st.write("No skills in this category.")
            
    st.markdown("---")
    st.subheader("Delete Skill")
    skill_to_delete = st.selectbox("Select Skill to Delete", skills_df['id'].tolist(), format_func=lambda x: f"{skills_df[skills_df['id']==x]['name'].values[0]} ({skills_df[skills_df['id']==x]['category'].values[0]})")
    
    if st.button("Delete Skill", type="primary"):
        db.delete_skill(skill_to_delete)
        st.success("Deleted successfully!")
        st.rerun()

def show_add_skill():
    st.subheader("Add a New Skill")
    
    with st.form("add_skill_form"):
        name = st.text_input("Skill Name (e.g., Python, React, AWS)")
        category = st.radio("Category", ["Already Know", "Want to Learn"])
        
        priority = st.selectbox("Learning Priority", ["Low", "Medium", "High"])
        target_date = st.date_input("Target Completion Date (Optional)", value=None)
        
        status = "Completed" if category == "Already Know" else "Not Started"
        
        submit = st.form_submit_button("Add Skill")
        if submit:
            if not name:
                st.error("Skill name is required.")
            else:
                db.add_skill({
                    'name': name,
                    'category': category,
                    'priority': priority,
                    'target_date': target_date.strftime('%Y-%m-%d') if target_date else "",
                    'status': status
                })
                st.success(f"Added {name} to your skills tracker!")
                st.rerun()

def show_analysis():
    st.subheader("Skills Analysis")
    skills_df = db.get_skills()
    
    if skills_df.empty:
        st.info("Add some skills to see analysis.")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        cat_counts = skills_df['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig1 = px.pie(cat_counts, values='Count', names='Category', title='Skills Breakdown')
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        to_learn = skills_df[skills_df['category'] == 'Want to Learn']
        if not to_learn.empty:
            status_counts = to_learn['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig2 = px.bar(status_counts, x='Status', y='Count', title='Learning Progress',
                          color='Status', color_discrete_map={
                              'Not Started': '#ef4444',
                              'In Progress': '#f59e0b',
                              'Completed': '#10b981'
                          })
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Add some skills to learn to see progress tracking.")
