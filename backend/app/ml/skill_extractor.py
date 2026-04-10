import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Dict

# Assumes model 'en_core_web_sm' is downloaded (handled in text_preprocessing)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Dictionaries / Corpora for skill matching
TECHNICAL_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "ruby", "php",
    "sql", "postgresql", "mysql", "mongodb", "oracle", "redis",
    "fastapi", "django", "flask", "spring boot", "react", "angular", "vue",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git", "linux",
    "machine learning", "deep learning", "nlp", "scikit-learn", "tensorflow", "pytorch",
    "data analysis", "pandas", "numpy", "matplotlib", "tableau", "power bi"
]

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "critical thinking",
    "adaptability", "time management", "conflict resolution", "creativity",
    "attention to detail", "project management", "agile", "scrum", "mentorship"
]

def setup_matcher(nlp_model, terms: List[str]) -> PhraseMatcher:
    matcher = PhraseMatcher(nlp_model.vocab, attr="LOWER")
    patterns = [nlp_model.make_doc(text) for text in terms]
    matcher.add("SKILLS", patterns)
    return matcher

tech_matcher = setup_matcher(nlp, TECHNICAL_SKILLS)
soft_matcher = setup_matcher(nlp, SOFT_SKILLS)

def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Scans the given raw text and isolates known entities mapped 
    to Technical and Soft Skills lists. 
    """
    doc = nlp(text)
    
    # Extract technical skills
    tech_matches = tech_matcher(doc)
    found_tech_skills = set()
    for match_id, start, end in tech_matches:
        span = doc[start:end]
        found_tech_skills.add(span.text.lower())
        
    # Extract soft skills
    soft_matches = soft_matcher(doc)
    found_soft_skills = set()
    for match_id, start, end in soft_matches:
        span = doc[start:end]
        found_soft_skills.add(span.text.lower())
        
    # Tools/Technologies overlaps with technical skills contextually
    # You could split this further utilizing specific tool corpora
    
    return {
        "technical_skills": list(found_tech_skills),
        "soft_skills": list(found_soft_skills),
        "tools_technologies": list(found_tech_skills) 
    }

def process_and_extract_entities(parsed_resume: Dict) -> Dict:
    """
    Coordinates extraction by parsing through raw text and structures.
    Returns JSON formatted structure resolving section entities.
    """
    raw_text = parsed_resume.get("raw_text", "")
    sections = parsed_resume.get("sections", {})
    
    # Extract full-scope skills across entire document to ensure nothing is missed
    skills = extract_skills(raw_text)
    
    output = {
        "detected_sections": sections,
        "extracted_skills": skills 
    }
    
    return output
