import streamlit as st
import database as db
import utils

def show():
    st.title("🤝 Job Description Matcher")
    
    resumes_df = db.get_resumes()
    
    if resumes_df.empty:
        st.warning("Please upload a resume in the Resume Analyzer first.")
        return
        
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Select Resume")
        resume_options = {row['id']: row['filename'] for _, row in resumes_df.iterrows()}
        selected_id = st.selectbox("Choose a saved resume", list(resume_options.keys()), format_func=lambda x: resume_options[x])
        
    with col2:
        st.subheader("2. Job Description")
        job_desc = st.text_area("Paste the job description here", height=200)
        
    if st.button("Analyze Match", type="primary"):
        if not job_desc.strip():
            st.error("Please paste a job description.")
            return
            
        filepath = resumes_df[resumes_df['id'] == selected_id]['filepath'].values[0]
        resume_text = utils.extract_text_from_pdf(filepath)
        
        if "Error extracting text" in resume_text:
            st.error(resume_text)
            return
            
        with st.spinner("Matching resume to job description..."):
            resume_lower = resume_text.lower()
            job_lower = job_desc.lower()
            
            common_tech = ['python', 'java', 'javascript', 'c++', 'react', 'node', 'sql', 'aws', 'docker', 'machine learning', 'data analysis', 'html', 'css', 'git', 'agile', 'scrum', 'kubernetes', 'azure', 'linux']
            
            job_skills = [skill for skill in common_tech if skill in job_lower]
            resume_skills = [skill for skill in common_tech if skill in resume_lower]
            
            matched_skills = set(job_skills).intersection(set(resume_skills))
            missing_skills = set(job_skills) - set(resume_skills)
            
            st.markdown("### 📊 Match Results")
            st.info("Note: This is an approximate text-based keyword match, not a definitive prediction of hiring success.")
            
            match_percentage = 0
            if job_skills:
                match_percentage = int((len(matched_skills) / len(job_skills)) * 100)
                
            st.progress(match_percentage / 100.0)
            st.write(f"**Approximate Match Score: {match_percentage}%**")
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### ✅ Matching Skills")
                if matched_skills:
                    for skill in matched_skills:
                        st.success(skill.capitalize())
                else:
                    st.write("No matching common skills found.")
                    
            with c2:
                st.markdown("#### ❌ Missing Skills (Consider Learning/Adding)")
                if missing_skills:
                    for skill in missing_skills:
                        st.warning(skill.capitalize())
                else:
                    st.write("No obvious missing skills found.")
                    
            st.markdown("---")
            st.markdown("#### 💡 Next Steps")
            st.write("1. Add the missing skills to your **Skills Gap Tracker**.")
            st.write("2. If you actually possess these missing skills, update your resume to explicitly mention them.")
            st.write("3. Tailor your bullet points to reflect the phrasing used in the job description.")
