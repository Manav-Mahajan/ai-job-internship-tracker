import streamlit as st
import database as db
import pandas as pd
from datetime import datetime

STATUS_OPTIONS = [
    'Interested', 'Preparing to Apply', 'Applied', 'Assessment', 
    'Interview Scheduled', 'Offer Received', 'Rejected', 'Withdrawn'
]

def show():
    st.title("📋 Applications")
    
    tabs = st.tabs(["Applications", "List View", "Add Application"])
    
    with tabs[0]:
        show_kanban()
        
    with tabs[1]:
        show_list_view()
        
    with tabs[2]:
        show_add_application()

def show_kanban():
    st.subheader("Applications")
    apps_df = db.get_all_applications()
    
    if apps_df.empty:
        st.info("No applications yet. Add one to see it on the board!")
        return

    cols = st.columns(len(STATUS_OPTIONS))
    
    for i, status in enumerate(STATUS_OPTIONS):
        with cols[i]:
            st.markdown(f"**{status}**")
            status_apps = apps_df[apps_df['status'] == status]
            
            for _, row in status_apps.iterrows():
                with st.container():
                    st.markdown(f'''
                        <div class="kanban-card">
                            <div class="kanban-title">{row["title"]}</div>
                            <div class="kanban-company">{row["company"]}</div>
                            <div class="kanban-details">Applied: {row["applied_date"]}</div>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    new_status = st.selectbox(
                        "Move to:", 
                        STATUS_OPTIONS, 
                        index=STATUS_OPTIONS.index(status),
                        key=f"kanban_status_{row['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != status:
                        db.update_application_status(row['id'], new_status)
                        st.rerun()

def show_list_view():
    st.subheader("All Applications")
    apps_df = db.get_all_applications()
    
    if apps_df.empty:
        st.info("No applications to display.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect("Filter by Status", STATUS_OPTIONS)
    with col2:
        search_term = st.text_input("Search Company or Title")
        
    filtered_df = apps_df.copy()
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if search_term:
        filtered_df = filtered_df[
            filtered_df['company'].str.contains(search_term, case=False, na=False) |
            filtered_df['title'].str.contains(search_term, case=False, na=False)
        ]
        
    display_cols = ['id', 'company', 'title', 'type', 'status', 'applied_date', 'deadline']
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
    
    st.download_button(
        label="Download CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='applications.csv',
        mime='text/csv'
    )
    
    st.subheader("Edit or Delete Application")
    app_to_edit = st.selectbox("Select Application to Edit/Delete", filtered_df['id'].tolist(), format_func=lambda x: f"{x} - {filtered_df[filtered_df['id']==x]['company'].values[0]} ({filtered_df[filtered_df['id']==x]['title'].values[0]})" if len(filtered_df[filtered_df['id']==x])>0 else x)
    
    if app_to_edit:
        app_data = apps_df[apps_df['id'] == app_to_edit].iloc[0]
        
        with st.expander("Edit Details", expanded=False):
            with st.form(key=f"edit_form_{app_to_edit}"):
                c1, c2 = st.columns(2)
                e_company = c1.text_input("Company", value=app_data['company'])
                e_title = c2.text_input("Title", value=app_data['title'])
                
                e_type = c1.selectbox("Type", ["Job", "Internship", "Apprenticeship"], index=["Job", "Internship", "Apprenticeship"].index(app_data['type']) if app_data['type'] in ["Job", "Internship", "Apprenticeship"] else 0)
                e_status = c2.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(app_data['status']) if app_data['status'] in STATUS_OPTIONS else 0)
                
                e_applied_date = c1.date_input("Applied Date", value=pd.to_datetime(app_data['applied_date']).date() if pd.notna(app_data['applied_date']) and app_data['applied_date'] != "" else datetime.today().date())
                e_deadline = c2.date_input("Deadline", value=pd.to_datetime(app_data['deadline']).date() if pd.notna(app_data['deadline']) and app_data['deadline'] != "" else datetime.today().date())
                
                e_desc = st.text_area("Description", value=app_data['description'] if pd.notna(app_data['description']) else "")
                
                submit = st.form_submit_button("Update")
                if submit:
                    db.update_application(app_to_edit, {
                        'company': e_company, 'title': e_title, 'type': e_type, 'status': e_status,
                        'applied_date': e_applied_date.strftime('%Y-%m-%d'), 'deadline': e_deadline.strftime('%Y-%m-%d'),
                        'description': e_desc, 'location': app_data['location'], 'work_arrangement': app_data['work_arrangement'],
                        'url': app_data['url'], 'salary': app_data['salary'], 'required_skills': app_data['required_skills'],
                        'notes': app_data['notes']
                    })
                    st.success("Updated successfully!")
                    st.rerun()
                    
        if st.button("Delete Application", type="primary"):
            db.delete_application(app_to_edit)
            st.success("Deleted successfully!")
            st.rerun()

def show_add_application():
    st.subheader("Add New Application")
    
    with st.form("add_app_form"):
        col1, col2 = st.columns(2)
        
        company = col1.text_input("Company Name *")
        title = col2.text_input("Job/Internship Title *")
        
        app_type = col1.selectbox("Application Type", ["Job", "Internship", "Apprenticeship"])
        status = col2.selectbox("Status", STATUS_OPTIONS)
        
        applied_date = col1.date_input("Application Date", value=None)
        deadline = col2.date_input("Application Deadline", value=None)
        
        location = col1.text_input("Location")
        work_arrangement = col2.selectbox("Work Arrangement", ["Remote", "Hybrid", "On-site", "Unknown"])
        
        url = col1.text_input("Job/Application URL")
        salary = col2.text_input("Salary/Stipend (if known)")
        
        required_skills = st.text_input("Required Skills (comma separated)")
        description = st.text_area("Job Description")
        notes = st.text_area("Personal Notes")
        
        submitted = st.form_submit_button("Save Application")
        
        if submitted:
            if not company or not title:
                st.error("Company and Title are required fields.")
            else:
                db.add_application({
                    'company': company,
                    'title': title,
                    'type': app_type,
                    'status': status,
                    'applied_date': applied_date.strftime('%Y-%m-%d') if applied_date else "",
                    'deadline': deadline.strftime('%Y-%m-%d') if deadline else "",
                    'location': location,
                    'work_arrangement': work_arrangement,
                    'url': url,
                    'salary': salary,
                    'required_skills': required_skills,
                    'description': description,
                    'notes': notes
                })
                st.success(f"Successfully added application for {company}!")
                st.rerun()
