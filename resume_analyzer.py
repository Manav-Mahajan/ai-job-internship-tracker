import streamlit as st
import database as db
import os
import utils

def show():
    st.title("📄 Resume Analyzer")
    
    tabs = st.tabs(["Upload Resume", "Saved Resumes", "Analyze"])
    
    with tabs[0]:
        show_upload()
        
    with tabs[1]:
        show_saved_resumes()
        
    with tabs[2]:
        show_analyze()

def show_upload():
    st.subheader("Upload a New Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Save Resume"):
            filepath = os.path.join("uploads", uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            db.add_resume(uploaded_file.name, filepath)
            st.success(f"Successfully saved {uploaded_file.name}!")

def show_saved_resumes():
    st.subheader("Your Resumes")
    resumes_df = db.get_resumes()
    
    if resumes_df.empty:
        st.info("No resumes uploaded yet.")
        return
        
    for _, row in resumes_df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{row['filename']}** (Uploaded: {row['uploaded_at'][:10]})")
        with col2:
            if os.path.exists(row['filepath']):
                with open(row['filepath'], "rb") as f:
                    st.download_button("Download", f, file_name=row['filename'], key=f"dl_{row['id']}")
            else:
                st.error("File missing")
        with col3:
            if st.button("Delete", key=f"del_{row['id']}", type="primary"):
                db.delete_resume(row['id'], row['filepath'])
                st.rerun()

def show_analyze():
    st.subheader("Analyze a Resume")
    resumes_df = db.get_resumes()
    
    if resumes_df.empty:
        st.warning("Upload a resume first to analyze it.")
        return
        
    resume_options = {row['id']: row['filename'] for _, row in resumes_df.iterrows()}
    selected_id = st.selectbox("Select Resume to Analyze", list(resume_options.keys()), format_func=lambda x: resume_options[x])
    
    if st.button("Run Analysis"):
        filepath = resumes_df[resumes_df['id'] == selected_id]['filepath'].values[0]
        
        if not os.path.exists(filepath):
            st.error("File not found on disk.")
            return
            
        with st.spinner("Analyzing resume..."):
            text = utils.extract_text_from_pdf(filepath)
            
            if "Error extracting text" in text:
                st.error(text)
                return
                
            analysis = utils.basic_keyword_analysis(text)
            
            st.markdown("### 📊 Analysis Results")
            st.info("Note: This is a basic rule-based analysis. A fully configured AI API would provide deeper insights.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Detected Sections")
                for sec in analysis['found_sections']:
                    st.success(sec.capitalize())
                    
                st.markdown("#### ❌ Missing Sections (Consider adding)")
                for sec in analysis['missing_sections']:
                    st.error(sec.capitalize())
                    
            with col2:
                st.markdown("#### 🛠️ Detected Technical Skills")
                if analysis['found_skills']:
                    st.write(", ".join([s.capitalize() for s in analysis['found_skills']]))
                else:
                    st.write("No common technical skills detected.")
                    
            st.markdown("#### 📝 Extracted Text Preview")
            with st.expander("View Text"):
                st.text(text[:1000] + "...\n\n(Truncated for preview)")
