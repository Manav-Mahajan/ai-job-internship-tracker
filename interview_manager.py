import streamlit as st
import database as db
import pandas as pd
from datetime import datetime

def show():
    st.title("📅 Interviews & Deadlines")
    
    tabs = st.tabs(["Upcoming Deadlines", "Interviews", "Add Interview"])
    
    with tabs[0]:
        show_deadlines()
        
    with tabs[1]:
        show_interviews()
        
    with tabs[2]:
        show_add_interview()

def show_deadlines():
    st.subheader("Upcoming Application Deadlines")
    apps_df = db.get_all_applications()
    
    if apps_df.empty:
        st.info("No applications to track deadlines for.")
        return
        
    apps_df['deadline_date'] = pd.to_datetime(apps_df['deadline'], errors='coerce')
    apps_df = apps_df.dropna(subset=['deadline_date'])
    
    if apps_df.empty:
        st.info("No deadlines set for your applications.")
        return
        
    today = pd.Timestamp.today().normalize()
    
    overdue = apps_df[(apps_df['deadline_date'] < today) & (apps_df['status'].isin(['Interested', 'Preparing to Apply']))]
    upcoming = apps_df[(apps_df['deadline_date'] >= today) & (apps_df['status'].isin(['Interested', 'Preparing to Apply']))].sort_values('deadline_date')
    
    if not overdue.empty:
        st.error(f"⚠️ You have {len(overdue)} overdue application deadlines!")
        st.dataframe(overdue[['company', 'title', 'deadline', 'status']], use_container_width=True, hide_index=True)
        
    if not upcoming.empty:
        st.success(f"🎯 You have {len(upcoming)} upcoming deadlines.")
        st.dataframe(upcoming[['company', 'title', 'deadline', 'status']], use_container_width=True, hide_index=True)
    else:
        st.write("No upcoming deadlines for applications in 'Interested' or 'Preparing to Apply' status.")

def show_interviews():
    st.subheader("Interview Schedule")
    ints_df = db.get_interviews()
    
    if ints_df.empty:
        st.info("No interviews scheduled yet.")
        return
        
    ints_df['interview_date_parsed'] = pd.to_datetime(ints_df['interview_date'], errors='coerce')
    
    ints_df = ints_df.sort_values('interview_date_parsed')
    
    display_cols = ['id', 'company', 'title', 'interview_date', 'round', 'interviewer', 'meeting_link']
    st.dataframe(ints_df[display_cols], use_container_width=True, hide_index=True)
    
    st.subheader("Delete Interview")
    int_to_delete = st.selectbox("Select Interview to Delete", ints_df['id'].tolist(), format_func=lambda x: f"{ints_df[ints_df['id']==x]['company'].values[0]} - {ints_df[ints_df['id']==x]['interview_date'].values[0]}")
    
    if st.button("Delete Interview", type="primary"):
        db.delete_interview(int_to_delete)
        st.success("Deleted successfully!")
        st.rerun()

def show_add_interview():
    st.subheader("Schedule an Interview")
    
    apps_df = db.get_all_applications()
    
    if apps_df.empty:
        st.warning("You need to add an application before scheduling an interview.")
        return
        
    app_options = apps_df['id'].tolist()
    app_format = lambda x: f"{apps_df[apps_df['id']==x]['company'].values[0]} - {apps_df[apps_df['id']==x]['title'].values[0]}"
    
    with st.form("add_interview_form"):
        application_id = st.selectbox("Select Application", app_options, format_func=app_format)
        
        col1, col2 = st.columns(2)
        
        int_date = col1.date_input("Interview Date")
        int_time = col2.time_input("Interview Time")
        
        round_name = col1.text_input("Interview Round (e.g., Technical, HR)")
        interviewer = col2.text_input("Interviewer Name(s)")
        
        meeting_link = st.text_input("Meeting Link (Zoom, Teams, etc.)")
        notes = st.text_area("Preparation Notes")
        
        submit = st.form_submit_button("Save Interview")
        
        if submit:
            dt_str = datetime.combine(int_date, int_time).strftime('%Y-%m-%d %H:%M')
            db.add_interview({
                'application_id': application_id,
                'interview_date': dt_str,
                'round': round_name,
                'interviewer': interviewer,
                'meeting_link': meeting_link,
                'notes': notes
            })
            
            current_status = apps_df[apps_df['id'] == application_id]['status'].values[0]
            if current_status not in ['Offer Received', 'Rejected', 'Withdrawn']:
                db.update_application_status(application_id, 'Interview Scheduled')
                
            st.success("Interview scheduled successfully!")
            st.rerun()
