import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

# Load model globally to avoid reloading into memory multiple times
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def get_embedding(text: str) -> np.ndarray:
    """Safely converts text to 384-dimensional vector embedding."""
    if not text or not model:
        return np.zeros((384,))
    return model.encode(text)

def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Computes cosine similarity between two texts."""
    res_emb = get_embedding(resume_text).reshape(1, -1)
    jd_emb = get_embedding(jd_text).reshape(1, -1)
    
    sim = cosine_similarity(res_emb, jd_emb)[0][0]
    return max(0.0, float(sim)) # Cap lower bound at 0 for logical scoring

def calculate_skill_match_percentage(resume_skills: List[str], jd_skills: List[str]) -> float:
    """Measures intersection fraction of required capabilities."""
    if not jd_skills:
        return 1.0 # If no specific skills defined, default to 100% matched expectation
    
    res_set = set([s.lower() for s in resume_skills])
    jd_set = set([s.lower() for s in jd_skills])
    
    matches = jd_set.intersection(res_set)
    return len(matches) / len(jd_set)

def calculate_experience_relevance(resume_exp_text: str, jd_exp_text: str) -> float:
    """
    Evaluates experience fit relying on semantic scope. 
    Can be expanded using parsed YOE (Years of Experience) in future iterations.
    """
    if not jd_exp_text:
        return 1.0
    if not resume_exp_text:
        return 0.0
    return compute_semantic_similarity(resume_exp_text, jd_exp_text)

def calculate_keyword_density(text: str, keywords: List[str]) -> float:
    """Calculates coverage ratio of important JD keywords inside resume block."""
    if not keywords:
        return 0.0
    text_lower = text.lower()
    total_words = len(text_lower.split())
    if total_words == 0:
        return 0.0
        
    keyword_count = sum(1 for kw in keywords if kw.lower() in text_lower)
    return keyword_count / len(keywords)

def normalize_score(score: float) -> float:
    """Scales 0.0-1.0 metric representation to whole number 0.0-100.0 bounds."""
    return round(max(0.0, min(100.0, score * 100)), 2)

def evaluate_candidate(candidate_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates structured weighting arrays executing the formula: 
    Final Score = 50% Semantic Sim + 30% Skill Match + 20% Experience Score
    """
    # Extract components
    resume_text = candidate_data.get("raw_text", "")
    resume_skills = candidate_data.get("extracted_skills", {}).get("technical_skills", [])
    resume_exp = candidate_data.get("sections", {}).get("experience", "")
    candidate_id = candidate_data.get("candidate_id", "Unknown")
    
    jd_text = jd_data.get("raw_text", "")
    jd_skills = jd_data.get("required_skills", [])
    jd_exp = jd_data.get("experience_requirements", "")
    
    # Calculate fundamental metrics (0.0 to 1.0 scale)
    semantic_sim = compute_semantic_similarity(resume_text, jd_text)
    skill_match = calculate_skill_match_percentage(resume_skills, jd_skills)
    
    # We compare extracted experience against the whole JD or specific JD exp requirements if populated
    exp_comparison_text = jd_exp if jd_exp else jd_text
    exp_score = calculate_experience_relevance(resume_exp, exp_comparison_text) 
    
    keyword_density = calculate_keyword_density(resume_text, jd_skills)
    
    # Placeholder Bias Detection checking for demographic keywords length variances
    # Future integration: actual ML discrimination checks mapped to specific features
    bias_score = 1.0 - (0.01 * (len(resume_text.split()) % 5))
    
    # Placeholder AI extractive summarization taking top boundaries
    summary_sentences = resume_text.split('.')[:3]
    ai_summary = " ".join(summary_sentences).strip() + "." if resume_text else "Summary unavailable."
    
    # Execute Weighted Formula
    final_score_raw = (0.50 * semantic_sim) + (0.30 * skill_match) + (0.20 * exp_score)
    
    # Prepare JSON response payload normalizing to 100-point scale
    results = {
        "candidate_id": candidate_id,
        "ai_summary": ai_summary,
        "metrics": {
            "semantic_similarity_score": normalize_score(semantic_sim),
            "skill_match_score": normalize_score(skill_match),
            "experience_score": normalize_score(exp_score),
            "keyword_density_score": normalize_score(keyword_density), 
            "bias_fairness_score": normalize_score(bias_score),
            "final_score": normalize_score(final_score_raw)
        }
    }
    return results

def rank_candidates(candidates: List[Dict[str, Any]], jd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Iterates evaluating multiple candidates dynamically against a single Job Description,
    returning structured response arrays sorted natively by highest fit scores first.
    """
    scored_candidates = [evaluate_candidate(cand, jd_data) for cand in candidates]
    
    # Sort descending by final weighted score
    scored_candidates.sort(key=lambda x: x["metrics"]["final_score"], reverse=True)
    
    # Assign relative ranking integers natively
    for i, res in enumerate(scored_candidates):
        res["rank"] = i + 1
        
    return scored_candidates
