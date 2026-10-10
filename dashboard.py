import streamlit as st
import database as db
import pandas as pd
import plotly.express as px
from datetime import datetime

def show():
    st.title("📊 Dashboard")
    
    apps_df = db.get_all_applications()
    ints_df = db.get_interviews()
    
    if apps_df.empty:
        st.info("👋 Welcome! You haven't added any applications yet. Head over to **Applications** to add your first one!")
        return
        
    total_apps = len(apps_df)
    in_progress_statuses = ['Interested', 'Preparing to Apply', 'Applied', 'Assessment', 'Interview Scheduled']
    in_progress = len(apps_df[apps_df['status'].isin(in_progress_statuses)])
    interviews_scheduled = len(apps_df[apps_df['status'] == 'Interview Scheduled'])
    offers = len(apps_df[apps_df['status'] == 'Offer Received'])
    rejected = len(apps_df[apps_df['status'] == 'Rejected'])
    
    apps_df['deadline_date'] = pd.to_datetime(apps_df['deadline'], errors='coerce')
    upcoming_deadlines = apps_df[(apps_df['deadline_date'] >= pd.Timestamp.today()) & 
                                 (apps_df['status'].isin(['Interested', 'Preparing to Apply']))].sort_values('deadline_date')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{total_apps}</div>
                <div class="metric-label">Total Applications</div>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{in_progress}</div>
                <div class="metric-label">In Progress</div>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{interviews_scheduled}</div>
                <div class="metric-label">Interviews Scheduled</div>
            </div>
        ''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''
            <div class="metric-card">
                <div class="metric-value">{offers}</div>
                <div class="metric-label">Offers Received</div>
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown("---")
    
    col_charts1, col_charts2 = st.columns(2)
    
    with col_charts1:
        st.subheader("Application Status Distribution")
        status_counts = apps_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Plasma)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_charts2:
        st.subheader("Applications by Month")
        apps_df['month_year'] = pd.to_datetime(apps_df['applied_date']).dt.to_period('M').astype(str)
        monthly_counts = apps_df.groupby('month_year').size().reset_index(name='Count')
        if not monthly_counts.empty and monthly_counts['month_year'].iloc[0] != 'NaT':
            fig2 = px.bar(monthly_counts, x='month_year', y='Count', text='Count',
                          color_discrete_sequence=['#3b82f6'])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
                               xaxis_title="Month", yaxis_title="Applications")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.write("Not enough data to display monthly trends.")

    st.markdown("---")
    
    col_recent, col_deadline = st.columns(2)
    
    with col_recent:
        st.subheader("Recent Activity")
        recent_apps = apps_df.sort_values(by='created_at', ascending=False).head(5)
        for _, row in recent_apps.iterrows():
            st.markdown(f"**{row['company']}** - {row['title']} ({row['status']})")
            
    with col_deadline:
        st.subheader("Upcoming Deadlines")
        if not upcoming_deadlines.empty:
            for _, row in upcoming_deadlines.head(5).iterrows():
                st.warning(f"**{row['company']}** - {row['title']} due on {row['deadline']}")
        else:
            st.success("No upcoming deadlines!")
