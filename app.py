import streamlit as st
import os
import database as db

st.set_page_config(
    page_title="AI Job & Internship Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("styles.css")

db.init_db()

if not os.path.exists('uploads'):
    os.makedirs('uploads')

import dashboard
import application_manager
import interview_manager
import skills_tracker
import resume_analyzer
import job_matcher

def main():
    st.sidebar.title("💼 AI Job Tracker")
    st.sidebar.markdown("Manage your career journey.")
    
    pages = {
        "Dashboard": dashboard.show,
        "Applications": application_manager.show,
        "Interviews & Deadlines": interview_manager.show,
        "Skills Gap Tracker": skills_tracker.show,
        "Resume Analyzer": resume_analyzer.show,
        "Job Description Matcher": job_matcher.show,
    }
    
    st.sidebar.markdown("---")
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Welcome to your AI Job & Internship Tracker! "
        "Keep your data updated to get the most out of the metrics and reminders."
    )
    
    pages[selection]()

if __name__ == "__main__":
    main()
