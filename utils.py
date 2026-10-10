import PyPDF2

def extract_text_from_pdf(filepath):
    try:
        text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"
        
def basic_keyword_analysis(text):
    common_skills = ['python', 'java', 'javascript', 'c++', 'react', 'node', 'sql', 'aws', 'docker', 'machine learning', 'data analysis', 'html', 'css', 'git']
    text_lower = text.lower()
    
    found_skills = [skill for skill in common_skills if skill in text_lower]
    
    sections = ['education', 'experience', 'projects', 'skills']
    found_sections = [sec for sec in sections if sec in text_lower]
    missing_sections = [sec for sec in sections if sec not in text_lower]
    
    return {
        'found_skills': found_skills,
        'found_sections': found_sections,
        'missing_sections': missing_sections
    }
