"""
Apply final reviewed labels to ground_truth.json and set all label statuses to VERIFIED.
Compares final labels with the original auto-suggested values and generates a diff summary.
"""
import json
from pathlib import Path
from evaluation.generate_dataset import generate_ground_truth

def main():
    gt_path = Path(__file__).parent / "ground_truth.json"
    
    # Generate original ground truth to get original auto-suggested relevance values
    original_gt, _ = generate_ground_truth()
    
    # Create lookup map of original relevance values: (job_id, candidate_id) -> relevance
    original_relevance = {}
    for eval_entry in original_gt["evaluations"]:
        job_id = eval_entry["job_id"]
        for cand in eval_entry["candidates"]:
            original_relevance[(job_id, cand["candidate_id"])] = cand["relevance"]

    # Final reviewed relevance labels from Expert Label Review report
    FINAL_REVIEWED_RELEVANCE = {
        # === JD 1: Senior Backend Python Developer ===
        ("jd_backend_python", "resume_arjun_mehta"):     3,
        ("jd_backend_python", "resume_priya_sharma"):    1,
        ("jd_backend_python", "resume_rahul_kumar"):     1,
        ("jd_backend_python", "resume_sneha_patel"):     1,
        ("jd_backend_python", "resume_vikram_singh"):    0,
        ("jd_backend_python", "resume_ananya_reddy"):    2,
        ("jd_backend_python", "resume_deepak_joshi"):    0,
        ("jd_backend_python", "resume_meera_nair"):      0,
        ("jd_backend_python", "resume_karthik_rao"):     1,
        ("jd_backend_python", "resume_sanya_gupta"):     0,

        # === JD 2: Data Scientist - NLP & Machine Learning ===
        ("jd_data_scientist", "resume_arjun_mehta"):     0,
        ("jd_data_scientist", "resume_priya_sharma"):    3,
        ("jd_data_scientist", "resume_rahul_kumar"):     0,
        ("jd_data_scientist", "resume_sneha_patel"):     0,
        ("jd_data_scientist", "resume_vikram_singh"):    0,
        ("jd_data_scientist", "resume_ananya_reddy"):    0,
        ("jd_data_scientist", "resume_deepak_joshi"):    2,
        ("jd_data_scientist", "resume_meera_nair"):      0,
        ("jd_data_scientist", "resume_karthik_rao"):     0,
        ("jd_data_scientist", "resume_sanya_gupta"):     1,

        # === JD 3: Full Stack Developer (React + Node.js) ===
        ("jd_fullstack_react", "resume_arjun_mehta"):    1,
        ("jd_fullstack_react", "resume_priya_sharma"):   0,
        ("jd_fullstack_react", "resume_rahul_kumar"):    3,
        ("jd_fullstack_react", "resume_sneha_patel"):    1,
        ("jd_fullstack_react", "resume_vikram_singh"):   0,
        ("jd_fullstack_react", "resume_ananya_reddy"):   1,
        ("jd_fullstack_react", "resume_deepak_joshi"):   0,
        ("jd_fullstack_react", "resume_meera_nair"):     3,
        ("jd_fullstack_react", "resume_karthik_rao"):    0,
        ("jd_fullstack_react", "resume_sanya_gupta"):    0,
    }

    # Load current ground_truth.json (to preserve current notes/metadata)
    with open(gt_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Dictionary of notes to preserve/update
    FINAL_NOTES = {
        # === JD 1 ===
        ("jd_backend_python", "resume_arjun_mehta"):     "CONFIRMED: Perfect match. 5yr Python/FastAPI/Django backend, all required skills, 9/9 match.",
        ("jd_backend_python", "resume_priya_sharma"):    "CHANGED 2->1: Data Scientist, not backend dev. Has Python/FastAPI/Docker but domain is ML/NLP, not API architecture.",
        ("jd_backend_python", "resume_rahul_kumar"):     "CHANGED 2->1: Full Stack dev with Node.js backend, not Python. FastAPI is secondary. Only 3yr exp (needs 4+).",
        ("jd_backend_python", "resume_sneha_patel"):     "CONFIRMED: Junior Python/Django dev with 2yr exp. Right direction but lacks Docker/K8s/Redis and seniority.",
        ("jd_backend_python", "resume_vikram_singh"):    "CONFIRMED: Marketing professional. Zero technical skills relevant to backend development.",
        ("jd_backend_python", "resume_ananya_reddy"):    "CHANGED 3->2: Backend dev with right shape (microservices/APIs/CI-CD) but primary lang is Java, Python only intermediate. No FastAPI/Django.",
        ("jd_backend_python", "resume_deepak_joshi"):    "CHANGED 1->0: ML engineer. Has Python/Git/Docker but zero backend API development experience.",
        ("jd_backend_python", "resume_meera_nair"):      "CHANGED 1->0: Pure frontend developer. No Python, no PostgreSQL, no backend experience.",
        ("jd_backend_python", "resume_karthik_rao"):     "CONFIRMED: DevOps with Docker/K8s/Jenkins/Git/PostgreSQL. Not a developer but has relevant infrastructure skills.",
        ("jd_backend_python", "resume_sanya_gupta"):     "CHANGED 1->0: Fresh grad with basic Python coursework. No backend experience for a senior role requiring 4+ years.",

        # === JD 2 ===
        ("jd_data_scientist", "resume_arjun_mehta"):     "CONFIRMED: Backend developer with zero ML/NLP/data science skills.",
        ("jd_data_scientist", "resume_priya_sharma"):    "CONFIRMED: Perfect match. 4yr NLP Data Scientist, all 11/11 required skills, publications, production ML.",
        ("jd_data_scientist", "resume_rahul_kumar"):     "CONFIRMED: Full Stack web dev with no ML/NLP background.",
        ("jd_data_scientist", "resume_sneha_patel"):     "CONFIRMED: Junior Python web dev with no ML/data science skills.",
        ("jd_data_scientist", "resume_vikram_singh"):    "CONFIRMED: Marketing professional. No technical or data science skills.",
        ("jd_data_scientist", "resume_ananya_reddy"):    "CONFIRMED: Java backend developer with no ML/NLP experience.",
        ("jd_data_scientist", "resume_deepak_joshi"):    "CHANGED 3->2: Strong ML engineer but specializes in CV, not NLP. Only 'basic text classification' as side project. 2yr exp (needs 3+).",
        ("jd_data_scientist", "resume_meera_nair"):      "CONFIRMED: Frontend developer with zero ML/NLP skills.",
        ("jd_data_scientist", "resume_karthik_rao"):     "CONFIRMED: DevOps engineer with zero ML/data science skills.",
        ("jd_data_scientist", "resume_sanya_gupta"):     "CHANGED 3->1: Has ML/NLP skills from coursework but only 3-month intern exp vs 3+ years required. Skills present but critically lacks experience.",

        # === JD 3 ===
        ("jd_fullstack_react", "resume_arjun_mehta"):    "CONFIRMED: Backend dev with PostgreSQL/Docker/Git. No JS/React/Node.js but strong backend transferable skills.",
        ("jd_fullstack_react", "resume_priya_sharma"):   "CHANGED 1->0: Data Scientist with zero JS/React/Node.js or web development experience.",
        ("jd_fullstack_react", "resume_rahul_kumar"):    "CONFIRMED: Perfect match. 3yr Full Stack React/Node.js/TypeScript developer, exact stack required.",
        ("jd_fullstack_react", "resume_sneha_patel"):    "KEPT at 1: Has JavaScript/Git, builds web apps (Django). Adjacent but no React/Node.js. Could be 0.",
        ("jd_fullstack_react", "resume_vikram_singh"):   "CONFIRMED: Marketing professional. No web development skills.",
        ("jd_fullstack_react", "resume_ananya_reddy"):   "KEPT at 1: Backend dev with PostgreSQL/Docker/Git. Relevant infra skills but no JS/React/Node.js. Could be 0.",
        ("jd_fullstack_react", "resume_deepak_joshi"):   "CHANGED 1->0: ML engineer. No JS/React/Node.js, no web development experience.",
        ("jd_fullstack_react", "resume_meera_nair"):     "CHANGED 2->3: 4yr React/TypeScript/Next.js specialist - exact frontend stack. Learning Node.js backend. Core competency is excellent match.",
        ("jd_fullstack_react", "resume_karthik_rao"):    "CHANGED 1->0: DevOps engineer. Docker/Git but no JS/React/Node.js or web app development.",
        ("jd_fullstack_react", "resume_sanya_gupta"):    "CHANGED 1->0: Fresh grad with basic JavaScript. No React/Node.js, never built a web application.",
    }

    diff_summary = []
    changes_count = 0
    
    for eval_entry in data["evaluations"]:
        job_id = eval_entry["job_id"]
        job_title = eval_entry["job_title"]
        for cand in eval_entry["candidates"]:
            cand_id = cand["candidate_id"]
            cand_name = cand["candidate_name"]
            key = (job_id, cand_id)
            
            orig_val = original_relevance[key]
            final_val = FINAL_REVIEWED_RELEVANCE[key]
            
            # Apply changes
            cand["relevance"] = final_val
            cand["label_status"] = "VERIFIED"
            
            if key in FINAL_NOTES:
                cand["notes"] = FINAL_NOTES[key]
                
            if orig_val != final_val:
                changes_count += 1
                diff_summary.append(
                    f"Job: {job_title} | Candidate: {cand_name}\n"
                    f"  Relevance: {orig_val} -> {final_val}\n"
                    f"  Notes: {cand['notes']}"
                )

    # Update metadata status
    data["_metadata"]["label_status"] = "ALL 30 labels VERIFIED after expert label review."

    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully verified all 30 labels, applying the final reviewed values.")
    print(f"Total relevance adjustments made: {changes_count}")
    print("\n--- DIFF SUMMARY OF CHANGES FROM ORIGINAL AUTO-SUGGESTED LABELS ---")
    for diff in diff_summary:
        print(diff)

if __name__ == "__main__":
    main()
