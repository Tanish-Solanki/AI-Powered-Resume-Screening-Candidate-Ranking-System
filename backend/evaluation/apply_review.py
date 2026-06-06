"""
Apply reviewed labels to ground_truth.json.
Updates relevance grades and label_status based on expert review.
"""
import json
from pathlib import Path

gt_path = Path(__file__).parent / "ground_truth.json"

with open(gt_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Reviewed labels: (job_id, candidate_id) -> (relevance, status, notes)
REVIEWED = {
    # === JD 1: Senior Backend Python Developer ===
    ("jd_backend_python", "resume_arjun_mehta"):     (3, "VERIFIED",  "CONFIRMED: Perfect match. 5yr Python/FastAPI/Django backend, all required skills, 9/9 match."),
    ("jd_backend_python", "resume_priya_sharma"):    (1, "VERIFIED",  "CHANGED 2->1: Data Scientist, not backend dev. Has Python/FastAPI/Docker but domain is ML/NLP, not API architecture."),
    ("jd_backend_python", "resume_rahul_kumar"):     (1, "VERIFIED",  "CHANGED 2->1: Full Stack dev with Node.js backend, not Python. FastAPI is secondary. Only 3yr exp (needs 4+)."),
    ("jd_backend_python", "resume_sneha_patel"):     (1, "VERIFIED",  "CONFIRMED: Junior Python/Django dev with 2yr exp. Right direction but lacks Docker/K8s/Redis and seniority."),
    ("jd_backend_python", "resume_vikram_singh"):    (0, "VERIFIED",  "CONFIRMED: Marketing professional. Zero technical skills relevant to backend development."),
    ("jd_backend_python", "resume_ananya_reddy"):    (2, "VERIFIED",  "CHANGED 3->2: Backend dev with right shape (microservices/APIs/CI-CD) but primary lang is Java, Python only intermediate. No FastAPI/Django."),
    ("jd_backend_python", "resume_deepak_joshi"):    (0, "VERIFIED",  "CHANGED 1->0: ML engineer. Has Python/Git/Docker but zero backend API development experience."),
    ("jd_backend_python", "resume_meera_nair"):      (0, "VERIFIED",  "CHANGED 1->0: Pure frontend developer. No Python, no PostgreSQL, no backend experience."),
    ("jd_backend_python", "resume_karthik_rao"):     (1, "VERIFIED",  "CONFIRMED: DevOps with Docker/K8s/Jenkins/Git/PostgreSQL. Not a developer but has relevant infrastructure skills."),
    ("jd_backend_python", "resume_sanya_gupta"):     (0, "VERIFIED",  "CHANGED 1->0: Fresh grad with basic Python coursework. No backend experience for a senior role requiring 4+ years."),

    # === JD 2: Data Scientist - NLP & Machine Learning ===
    ("jd_data_scientist", "resume_arjun_mehta"):     (0, "VERIFIED",  "CONFIRMED: Backend developer with zero ML/NLP/data science skills."),
    ("jd_data_scientist", "resume_priya_sharma"):    (3, "VERIFIED",  "CONFIRMED: Perfect match. 4yr NLP Data Scientist, all 11/11 required skills, publications, production ML."),
    ("jd_data_scientist", "resume_rahul_kumar"):     (0, "VERIFIED",  "CONFIRMED: Full Stack web dev with no ML/NLP background."),
    ("jd_data_scientist", "resume_sneha_patel"):     (0, "VERIFIED",  "CONFIRMED: Junior Python web dev with no ML/data science skills."),
    ("jd_data_scientist", "resume_vikram_singh"):    (0, "VERIFIED",  "CONFIRMED: Marketing professional. No technical or data science skills."),
    ("jd_data_scientist", "resume_ananya_reddy"):    (0, "VERIFIED",  "CONFIRMED: Java backend developer with no ML/NLP experience."),
    ("jd_data_scientist", "resume_deepak_joshi"):    (2, "VERIFIED",  "CHANGED 3->2: Strong ML engineer but specializes in CV, not NLP. Only 'basic text classification' as side project. 2yr exp (needs 3+)."),
    ("jd_data_scientist", "resume_meera_nair"):      (0, "VERIFIED",  "CONFIRMED: Frontend developer with zero ML/NLP skills."),
    ("jd_data_scientist", "resume_karthik_rao"):     (0, "VERIFIED",  "CONFIRMED: DevOps engineer with zero ML/data science skills."),
    ("jd_data_scientist", "resume_sanya_gupta"):     (1, "LOW_CONFIDENCE", "CHANGED 3->1: Has ML/NLP skills from coursework but only 3-month intern exp vs 3+ years required. Skills present but critically lacks experience."),

    # === JD 3: Full Stack Developer (React + Node.js) ===
    ("jd_fullstack_react", "resume_arjun_mehta"):    (1, "VERIFIED",  "CONFIRMED: Backend dev with PostgreSQL/Docker/Git. No JS/React/Node.js but strong backend transferable skills."),
    ("jd_fullstack_react", "resume_priya_sharma"):   (0, "VERIFIED",  "CHANGED 1->0: Data Scientist with zero JS/React/Node.js or web development experience."),
    ("jd_fullstack_react", "resume_rahul_kumar"):    (3, "VERIFIED",  "CONFIRMED: Perfect match. 3yr Full Stack React/Node.js/TypeScript developer, exact stack required."),
    ("jd_fullstack_react", "resume_sneha_patel"):    (1, "LOW_CONFIDENCE", "KEPT at 1: Has JavaScript/Git, builds web apps (Django). Adjacent but no React/Node.js. Could be 0."),
    ("jd_fullstack_react", "resume_vikram_singh"):   (0, "VERIFIED",  "CONFIRMED: Marketing professional. No web development skills."),
    ("jd_fullstack_react", "resume_ananya_reddy"):   (1, "LOW_CONFIDENCE", "KEPT at 1: Backend dev with PostgreSQL/Docker/Git. Relevant infra skills but no JS/React/Node.js. Could be 0."),
    ("jd_fullstack_react", "resume_deepak_joshi"):   (0, "VERIFIED",  "CHANGED 1->0: ML engineer. No JS/React/Node.js, no web development experience."),
    ("jd_fullstack_react", "resume_meera_nair"):     (3, "LOW_CONFIDENCE", "CHANGED 2->3: 4yr React/TypeScript/Next.js specialist - exact frontend stack. Learning Node.js backend. Core competency is excellent match."),
    ("jd_fullstack_react", "resume_karthik_rao"):    (0, "VERIFIED",  "CHANGED 1->0: DevOps engineer. Docker/Git but no JS/React/Node.js or web app development."),
    ("jd_fullstack_react", "resume_sanya_gupta"):    (0, "VERIFIED",  "CHANGED 1->0: Fresh grad with basic JavaScript. No React/Node.js, never built a web application."),
}

# Apply reviews
changes_made = 0
for eval_entry in data["evaluations"]:
    job_id = eval_entry["job_id"]
    for cand in eval_entry["candidates"]:
        key = (job_id, cand["candidate_id"])
        if key in REVIEWED:
            new_rel, new_status, new_notes = REVIEWED[key]
            old_rel = cand["relevance"]
            if old_rel != new_rel:
                changes_made += 1
            cand["relevance"] = new_rel
            cand["label_status"] = new_status
            cand["notes"] = new_notes

# Update metadata
data["_metadata"]["label_status"] = f"REVIEWED: 26 VERIFIED, 4 LOW_CONFIDENCE. {changes_made} labels changed from auto-suggestion."

with open(gt_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated {len(REVIEWED)} labels ({changes_made} changed from auto-suggestion)")
print(f"  VERIFIED: {sum(1 for _, s, _ in REVIEWED.values() if s == 'VERIFIED')}")
print(f"  LOW_CONFIDENCE: {sum(1 for _, s, _ in REVIEWED.values() if s == 'LOW_CONFIDENCE')}")
