"""
End-to-End Evaluation Runner for Resume Ranking System.

This script:
1. Loads ground-truth relevance labels from ground_truth.json
2. Runs the ranking engine on each (JD, candidates) pair
3. Compares system rankings against human labels
4. Computes Precision@K, Recall@K, MAP, NDCG@K, MRR
5. Outputs results as a formatted table + exportable JSON + README snippet

Usage:
    cd backend
    python -m evaluation.run_evaluation
    python -m evaluation.run_evaluation --ground-truth path/to/custom_labels.json
    python -m evaluation.run_evaluation --k-values 3 5 10 15
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path so we can import from app.ml
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.metrics import (
    compute_all_metrics_for_query,
    compute_aggregate_metrics,
    precision_at_k,
    recall_at_k,
    average_precision,
    mean_average_precision,
    ndcg_at_k,
    mean_reciprocal_rank,
)


def load_ground_truth(filepath: str) -> Dict[str, Any]:
    """Load and validate ground-truth labels from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    evaluations = data.get("evaluations", [])
    if not evaluations:
        print("ERROR: No evaluations found in ground_truth.json")
        print("Please fill in the template with your actual data.")
        sys.exit(1)

    # Validate: check for unfilled entries (relevance == -1)
    unfilled_count = 0
    unverified_count = 0
    for eval_entry in evaluations:
        for cand in eval_entry.get("candidates", []):
            if cand.get("relevance", -1) == -1:
                unfilled_count += 1
            if cand.get("label_status", "") == "REVIEW_REQUIRED":
                unverified_count += 1

    if unfilled_count > 0:
        print(f"WARNING: {unfilled_count} candidate(s) have relevance = -1 (unfilled).")
        print("These will be treated as relevance = 0 (not relevant).")
        print("For accurate evaluation, please assign proper relevance grades.\n")

    if unverified_count > 0:
        print(f"NOTE: {unverified_count} label(s) are marked REVIEW_REQUIRED (auto-suggested).")
        print("Results are based on suggested labels. For publication-quality metrics,")
        print("review and change label_status to 'VERIFIED' in ground_truth.json.\n")

    return data


def run_ranking_for_evaluation(eval_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run the ranking engine on one evaluation entry.

    Constructs the data structures expected by ranking_engine.rank_candidates()
    from the ground truth format.
    """
    from app.ml.ranking_engine import rank_candidates
    from app.ml.skill_extractor import extract_skills

    jd_data = {
        "raw_text": eval_entry["job_description_text"],
        "required_skills": eval_entry.get("required_skills", []),
        "experience_requirements": eval_entry.get("experience_requirements", ""),
    }

    candidates = []
    for cand in eval_entry["candidates"]:
        resume_text = cand.get("resume_text", "")

        # Extract skills from resume text using the same pipeline
        skills = extract_skills(resume_text)

        candidate_data = {
            "candidate_id": cand["candidate_id"],
            "raw_text": resume_text,
            "extracted_skills": skills,
            "sections": {
                "experience": resume_text  # Use full text as experience proxy
            },
        }
        candidates.append(candidate_data)

    # Run the actual ranking engine
    ranked_results = rank_candidates(candidates, jd_data)
    return ranked_results


def evaluate_single_query(
    eval_entry: Dict[str, Any],
    ranked_results: List[Dict[str, Any]],
    k_values: List[int],
) -> Dict[str, Any]:
    """Evaluate ranking results for a single job description."""

    # Build relevance map from ground truth
    relevance_map = {}
    for cand in eval_entry["candidates"]:
        rel = cand.get("relevance", -1)
        relevance_map[cand["candidate_id"]] = max(0, rel)  # Treat -1 as 0

    # Extract system ranking order
    ranked_ids = [r["candidate_id"] for r in ranked_results]

    # Compute metrics
    metrics = compute_all_metrics_for_query(ranked_ids, relevance_map, k_values)

    # Build candidate name lookup from ground truth
    name_map = {c["candidate_id"]: c.get("candidate_name", c["candidate_id"])
                for c in eval_entry["candidates"]}

    # Add detailed ranking comparison
    ranking_detail = []
    for rank_pos, result in enumerate(ranked_results):
        cid = result["candidate_id"]
        ranking_detail.append({
            "rank": rank_pos + 1,
            "candidate_id": cid,
            "candidate_name": name_map.get(cid, cid),
            "system_score": result["metrics"]["final_score"],
            "human_relevance": relevance_map.get(cid, 0),
            "is_relevant_binary": relevance_map.get(cid, 0) >= 1,
        })

    return {
        "job_id": eval_entry["job_id"],
        "job_title": eval_entry.get("job_title", ""),
        "metrics": metrics,
        "ranking_detail": ranking_detail,
    }


def print_results(
    per_query_results: List[Dict[str, Any]],
    aggregate: Dict[str, Any],
    k_values: List[int],
) -> None:
    """Print formatted evaluation results to console."""

    print("\n" + "=" * 80)
    print("   RESUME RANKING EVALUATION RESULTS")
    print("=" * 80)
    print(f"   Evaluated {aggregate['num_queries']} job description(s)")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Per-query results
    for qr in per_query_results:
        print(f"\n{'─' * 70}")
        print(f"  Job: {qr['job_title']} ({qr['job_id']})")
        print(f"  Relevant candidates: {qr['metrics']['num_relevant']} / {qr['metrics']['num_candidates']}")
        print(f"  Average Precision: {qr['metrics']['average_precision']:.4f}")
        print(f"{'─' * 70}")

        # Ranking detail
        print(f"\n  {'Rank':<6} {'Candidate':<22} {'System Score':<15} {'Human Label':<14} {'Relevant?'}")
        print(f"  {'─'*6} {'─'*22} {'─'*15} {'─'*14} {'─'*10}")
        for rd in qr["ranking_detail"]:
            rel_marker = "  YES" if rd["is_relevant_binary"] else "  NO"
            grade_labels = {0: "Not Relevant", 1: "Marginal", 2: "Relevant", 3: "Highly Rel."}
            human_label = grade_labels.get(rd["human_relevance"], str(rd["human_relevance"]))
            display_name = rd.get("candidate_name", rd["candidate_id"])
            print(
                f"  {rd['rank']:<6} {display_name:<22} "
                f"{rd['system_score']:<15.2f} {human_label:<14} {rel_marker}"
            )

        # Per-K metrics table
        print(f"\n  {'Metric':<22}", end="")
        for k in k_values:
            print(f"{'K=' + str(k):<12}", end="")
        print()
        print(f"  {'─'*22}", end="")
        for _ in k_values:
            print(f"{'─'*12}", end="")
        print()

        for metric_name, metric_key in [
            ("Precision@K", "precision_at_k"),
            ("Recall@K", "recall_at_k"),
            ("NDCG@K", "ndcg_at_k"),
        ]:
            print(f"  {metric_name:<22}", end="")
            for k in k_values:
                if k in qr["metrics"]["per_k"]:
                    val = qr["metrics"]["per_k"][k][metric_key]
                    print(f"{val:<12.4f}", end="")
                else:
                    print(f"{'N/A':<12}", end="")
            print()

    # Aggregate results
    print(f"\n{'=' * 80}")
    print("   AGGREGATE RESULTS (Averaged Across All Job Descriptions)")
    print(f"{'=' * 80}\n")

    print(f"  MAP  (Mean Average Precision):  {aggregate['MAP']:.4f}")
    print(f"  MRR  (Mean Reciprocal Rank):    {aggregate['MRR']:.4f}\n")

    print(f"  {'Metric':<28}", end="")
    for k in k_values:
        print(f"{'K=' + str(k):<12}", end="")
    print()
    print(f"  {'─'*28}", end="")
    for _ in k_values:
        print(f"{'─'*12}", end="")
    print()

    for metric_name, metric_key in [
        ("Mean Precision@K", "mean_precision_at_k"),
        ("Mean Recall@K", "mean_recall_at_k"),
        ("Mean NDCG@K", "mean_ndcg_at_k"),
    ]:
        print(f"  {metric_name:<28}", end="")
        for k in k_values:
            if k in aggregate["per_k"]:
                val = aggregate["per_k"][k][metric_key]
                print(f"{val:<12.4f}", end="")
            else:
                print(f"{'N/A':<12}", end="")
        print()

    print()


def generate_readme_snippet(
    aggregate: Dict[str, Any],
    k_values: List[int],
    output_path: str,
) -> None:
    """Generate a markdown table suitable for pasting into README.md."""

    lines = [
        "## Evaluation Results",
        "",
        "Ranking quality evaluated using industry-standard Information Retrieval metrics.",
        f"Evaluated across **{aggregate['num_queries']}** job description(s) with human-labeled relevance judgments.",
        "",
        "| Metric | " + " | ".join(f"K={k}" for k in k_values) + " |",
        "|--------|" + "|".join("------" for _ in k_values) + "|",
    ]

    for metric_name, metric_key in [
        ("Precision@K", "mean_precision_at_k"),
        ("Recall@K", "mean_recall_at_k"),
        ("NDCG@K", "mean_ndcg_at_k"),
    ]:
        row = f"| {metric_name} |"
        for k in k_values:
            val = aggregate["per_k"].get(k, {}).get(metric_key, 0.0)
            row += f" {val:.4f} |"
        lines.append(row)

    lines.extend([
        "",
        f"| **MAP** (Mean Average Precision) | {aggregate['MAP']:.4f} | — | — |",
        f"| **MRR** (Mean Reciprocal Rank) | {aggregate['MRR']:.4f} | — | — |",
        "",
        "*Metrics computed from human-labeled ground truth using standard IR evaluation methodology.*",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.*",
    ])

    snippet = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(snippet)

    print(f"  README snippet saved to: {output_path}")


def export_results_json(
    per_query_results: List[Dict[str, Any]],
    aggregate: Dict[str, Any],
    output_path: str,
) -> None:
    """Export full evaluation results as JSON."""
    export = {
        "generated_at": datetime.now().isoformat(),
        "aggregate_metrics": aggregate,
        "per_query_results": per_query_results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)

    print(f"  Full results JSON saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Resume Ranking System with IR metrics"
    )
    parser.add_argument(
        "--ground-truth",
        default=str(Path(__file__).parent / "ground_truth.json"),
        help="Path to ground truth JSON file (default: evaluation/ground_truth.json)",
    )
    parser.add_argument(
        "--k-values",
        nargs="+",
        type=int,
        default=[3, 5, 10],
        help="K values to compute metrics at (default: 3 5 10)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).parent),
        help="Directory to write output files (default: evaluation/)",
    )

    args = parser.parse_args()
    k_values = sorted(args.k_values)

    print("Loading ground truth labels...")
    gt_data = load_ground_truth(args.ground_truth)

    per_query_results = []
    all_queries_for_map = []  # (ranked_ids, relevant_ids) tuples

    for eval_entry in gt_data["evaluations"]:
        job_id = eval_entry["job_id"]
        print(f"Ranking candidates for: {eval_entry.get('job_title', job_id)}...")

        # Run the actual ranking engine
        ranked_results = run_ranking_for_evaluation(eval_entry)

        # Evaluate against ground truth
        query_result = evaluate_single_query(eval_entry, ranked_results, k_values)
        per_query_results.append(query_result)

        # Collect for MAP/MRR computation
        ranked_ids = [r["candidate_id"] for r in ranked_results]
        relevance_map = {}
        for cand in eval_entry["candidates"]:
            relevance_map[cand["candidate_id"]] = max(0, cand.get("relevance", 0))
        relevant_ids = {cid for cid, rel in relevance_map.items() if rel >= 1}
        all_queries_for_map.append((ranked_ids, relevant_ids))

    # Compute aggregate metrics
    aggregate = compute_aggregate_metrics(
        [qr["metrics"] for qr in per_query_results],
        all_queries_for_map,
        k_values,
    )

    # Print formatted results
    print_results(per_query_results, aggregate, k_values)

    # Export files
    print("Exporting results...\n")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    export_results_json(
        per_query_results, aggregate,
        str(output_dir / "evaluation_results.json"),
    )
    generate_readme_snippet(
        aggregate, k_values,
        str(output_dir / "README_metrics_snippet.md"),
    )

    print("\nDone! Copy the contents of README_metrics_snippet.md into your README.md")


if __name__ == "__main__":
    main()
