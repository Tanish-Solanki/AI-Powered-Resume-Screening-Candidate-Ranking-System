import pdfplumber
import docx
from typing import Dict, Optional

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_resume_sections(text: str) -> Dict[str, str]:
    """
    Detect basic boundaries for sections: Skills, Education, Experience
    Returns a dictionary of raw section texts.
    """
    lines = text.split('\n')
    sections = {
        "summary": [],
        "education": [],
        "experience": [],
        "skills": []
    }
    current_section = "summary"
    
    # Common headers associated with standard resume sections
    section_mapping = {
        "education": ["education", "academic background", "academic qualifications"],
        "experience": ["experience", "employment history", "work history", "professional experience"],
        "skills": ["skills", "technical skills", "technologies", "core competencies", "competencies"]
    }
    
    for line in lines:
        clean_line = line.strip().lower()
        if not clean_line:
            continue
            
        # Detect if line is a header (mostly short lines matching keywords)
        is_header = False
        for sec, keywords in section_mapping.items():
            if any(clean_line.startswith(kw) or clean_line == kw for kw in keywords):
                if len(clean_line.split()) <= 4:  # True headers are usually short
                    current_section = sec
                    is_header = True
                    break
        
        if not is_header:
            sections[current_section].append(line)
            
    # Rejoin the lines for each section
    return {k: "\n".join(v).strip() for k, v in sections.items()}

def parse_resume(file_path: str) -> Optional[Dict]:
    """
    Given a file path (pdf, docx, txt), parse it into sections and return raw text.
    """
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif file_ext in ['doc', 'docx']:
        raw_text = extract_text_from_docx(file_path)
    elif file_ext == 'txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except Exception:
            return None
    else:
        return None
        
    sections = extract_resume_sections(raw_text)
    
    return {
        "raw_text": raw_text,
        "sections": sections
    }
