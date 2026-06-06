"""
Information Retrieval Evaluation Metrics for Resume Ranking.

This module implements standard IR ranking metrics from scratch.
Each function includes the mathematical formula in its docstring
for inclusion in academic reports (e.g., Amazon ML Summer School).

Metrics implemented:
    - Precision@K
    - Recall@K
    - Average Precision (AP) & Mean Average Precision (MAP)
    - DCG@K & NDCG@K (Normalized Discounted Cumulative Gain)
    - MRR (Mean Reciprocal Rank)

References:
    - Manning, Raghavan & Schütze, "Introduction to Information Retrieval", Ch. 8
    - Järvelin & Kekäläinen, "Cumulated Gain-Based Evaluation of IR Techniques", ACM TOIS 2002
"""

import numpy as np
from typing import List, Set, Dict, Any, Tuple


# ============================================================================
# Binary Relevance Metrics
# ============================================================================

def precision_at_k(ranked_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Precision@K — fraction of top-K results that are relevant.

    Formula:
        Precision@K = |{relevant documents in top-K}| / K

    Args:
        ranked_ids: Ordered list of candidate IDs as ranked by the system
                    (index 0 = rank 1, i.e., highest-scored candidate).
        relevant_ids: Set of candidate IDs that are truly relevant
                      (from human ground-truth labels).
        k: Number of top results to evaluate.

    Returns:
        Precision score in [0.0, 1.0].

    Example:
        >>> precision_at_k(["a", "b", "c", "d"], {"a", "c", "e"}, k=3)
        0.6667  # 2 relevant out of top-3
    """
    if k <= 0:
        return 0.0
    top_k = ranked_ids[:k]
    relevant_in_top_k = sum(1 for cid in top_k if cid in relevant_ids)
    return relevant_in_top_k / k


def recall_at_k(ranked_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """
    Recall@K — fraction of all relevant items that appear in the top-K.

    Formula:
        Recall@K = |{relevant documents in top-K}| / |{all relevant documents}|

    Args:
        ranked_ids: Ordered list of candidate IDs as ranked by the system.
        relevant_ids: Set of all truly relevant candidate IDs.
        k: Number of top results to evaluate.

    Returns:
        Recall score in [0.0, 1.0]. Returns 0.0 if there are no relevant items.

    Example:
        >>> recall_at_k(["a", "b", "c", "d"], {"a", "c", "e"}, k=3)
        0.6667  # 2 of 3 relevant found in top-3
    """
    if k <= 0 or len(relevant_ids) == 0:
        return 0.0
    top_k = ranked_ids[:k]
    relevant_in_top_k = sum(1 for cid in top_k if cid in relevant_ids)
    return relevant_in_top_k / len(relevant_ids)


def average_precision(ranked_ids: List[str], relevant_ids: Set[str]) -> float:
    """
    Average Precision (AP) — average of Precision@K at each relevant position.

    Formula:
        AP = (1 / |relevant|) × Σ_{k=1}^{n} [rel(k) × Precision@k]

    Where rel(k) = 1 if the item at rank k is relevant, 0 otherwise.

    This rewards systems that place relevant items earlier in the ranking.

    Args:
        ranked_ids: Ordered list of candidate IDs as ranked by the system.
        relevant_ids: Set of all truly relevant candidate IDs.

    Returns:
        AP score in [0.0, 1.0]. Returns 0.0 if there are no relevant items.

    Example:
        >>> average_precision(["a", "b", "c", "d"], {"a", "c"})
        0.8333  # (1/2) * (1/1 + 2/3) = (1/2) * (1.667) = 0.8333
    """
    if len(relevant_ids) == 0:
        return 0.0

    cumulative_precision = 0.0
    relevant_count = 0

    for i, cid in enumerate(ranked_ids):
        if cid in relevant_ids:
            relevant_count += 1
            precision_at_i = relevant_count / (i + 1)
            cumulative_precision += precision_at_i

    return cumulative_precision / len(relevant_ids)


def mean_average_precision(all_queries_results: List[Tuple[List[str], Set[str]]]) -> float:
    """
    Mean Average Precision (MAP) — mean of AP across multiple queries.

    Formula:
        MAP = (1 / |Q|) × Σ_{q=1}^{|Q|} AP(q)

    Where Q is the set of all queries (job descriptions).

    Args:
        all_queries_results: List of tuples, each containing:
            - ranked_ids: system ranking for one query
            - relevant_ids: ground truth relevant set for that query

    Returns:
        MAP score in [0.0, 1.0]. Returns 0.0 if no queries provided.

    Example:
        >>> results = [
        ...     (["a", "b", "c"], {"a", "c"}),      # AP = 0.8333
        ...     (["x", "y", "z"], {"y"}),            # AP = 0.5
        ... ]
        >>> mean_average_precision(results)
        0.6667  # (0.8333 + 0.5) / 2
    """
    if len(all_queries_results) == 0:
        return 0.0

    ap_scores = [
        average_precision(ranked, relevant)
        for ranked, relevant in all_queries_results
    ]
    return np.mean(ap_scores).item()


# ============================================================================
# Graded Relevance Metrics
# ============================================================================

def dcg_at_k(relevances: List[float], k: int) -> float:
    """
    Discounted Cumulative Gain at K — measures ranking quality with graded relevance.

    Formula:
        DCG@K = Σ_{i=1}^{K} (2^{rel_i} - 1) / log₂(i + 1)

    The logarithmic discount penalizes relevant items that appear at lower ranks.

    Args:
        relevances: List of relevance scores in the order of system ranking.
                    (index 0 = rank 1). Higher values = more relevant.
        k: Number of top results to evaluate.

    Returns:
        DCG score (non-negative float, unbounded above).

    Example:
        >>> dcg_at_k([3, 2, 0, 1], k=3)
        # (2^3-1)/log2(2) + (2^2-1)/log2(3) + (2^0-1)/log2(4) = 7/1 + 3/1.585 + 0/2 = 8.893
    """
    if k <= 0:
        return 0.0

    relevances_at_k = relevances[:k]
    dcg = 0.0

    for i, rel in enumerate(relevances_at_k):
        # Position is 1-indexed, so discount = log2(i + 2) since i is 0-indexed
        discount = np.log2(i + 2)
        gain = (2 ** rel - 1) / discount
        dcg += gain

    return dcg


def ndcg_at_k(relevances: List[float], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain at K.

    Formula:
        NDCG@K = DCG@K / IDCG@K

    Where IDCG@K is the DCG@K of the ideal (perfect) ranking — i.e., the
    relevance scores sorted in descending order.

    NDCG normalizes DCG to [0, 1], making it comparable across queries
    with different numbers of relevant documents.

    Args:
        relevances: List of relevance scores in the order of system ranking.
        k: Number of top results to evaluate.

    Returns:
        NDCG score in [0.0, 1.0]. Returns 0.0 if ideal DCG is 0.

    Example:
        >>> ndcg_at_k([3, 2, 0, 1], k=4)
        # System DCG / Ideal DCG where ideal order = [3, 2, 1, 0]
    """
    if k <= 0:
        return 0.0

    actual_dcg = dcg_at_k(relevances, k)

    # Ideal ranking: sort relevances descending
    ideal_relevances = sorted(relevances, reverse=True)
    ideal_dcg = dcg_at_k(ideal_relevances, k)

    if ideal_dcg == 0.0:
        return 0.0

    return actual_dcg / ideal_dcg


def mean_reciprocal_rank(all_queries_results: List[Tuple[List[str], Set[str]]]) -> float:
    """
    Mean Reciprocal Rank (MRR) — average of 1/rank of the first relevant result.

    Formula:
        MRR = (1 / |Q|) × Σ_{q=1}^{|Q|} (1 / rank_q)

    Where rank_q is the position of the first relevant document for query q.

    MRR measures how quickly the system surfaces a relevant candidate.

    Args:
        all_queries_results: List of tuples, each containing:
            - ranked_ids: system ranking for one query
            - relevant_ids: ground truth relevant set for that query

    Returns:
        MRR score in [0.0, 1.0]. Returns 0.0 if no queries provided.

    Example:
        >>> results = [
        ...     (["a", "b", "c"], {"b", "c"}),  # first relevant at rank 2 → RR = 0.5
        ...     (["x", "y", "z"], {"x"}),        # first relevant at rank 1 → RR = 1.0
        ... ]
        >>> mean_reciprocal_rank(results)
        0.75  # (0.5 + 1.0) / 2
    """
    if len(all_queries_results) == 0:
        return 0.0

    reciprocal_ranks = []

    for ranked_ids, relevant_ids in all_queries_results:
        rr = 0.0
        for i, cid in enumerate(ranked_ids):
            if cid in relevant_ids:
                rr = 1.0 / (i + 1)
                break
        reciprocal_ranks.append(rr)

    return np.mean(reciprocal_ranks).item()


# ============================================================================
# Convenience: Compute All Metrics at Once
# ============================================================================

def compute_all_metrics_for_query(
    ranked_ids: List[str],
    relevance_map: Dict[str, int],
    k_values: List[int] = [3, 5, 10]
) -> Dict[str, Any]:
    """
    Compute all metrics for a single query (job description).

    Args:
        ranked_ids: Ordered list of candidate IDs as produced by the ranking system.
        relevance_map: Dict mapping candidate_id → relevance grade (0, 1, 2, 3).
                       For binary metrics, relevance >= 1 is treated as relevant.
        k_values: List of K values to compute metrics at.

    Returns:
        Dictionary with all metric values organized by K.
    """
    # Binary relevant set (relevance >= 1)
    relevant_ids = {cid for cid, rel in relevance_map.items() if rel >= 1}

    # Graded relevance list in system ranking order
    graded_relevances = [relevance_map.get(cid, 0) for cid in ranked_ids]

    results = {
        "average_precision": round(average_precision(ranked_ids, relevant_ids), 4),
        "num_relevant": len(relevant_ids),
        "num_candidates": len(ranked_ids),
        "per_k": {}
    }

    for k in k_values:
        results["per_k"][k] = {
            "precision_at_k": round(precision_at_k(ranked_ids, relevant_ids, k), 4),
            "recall_at_k": round(recall_at_k(ranked_ids, relevant_ids, k), 4),
            "ndcg_at_k": round(ndcg_at_k(graded_relevances, k), 4),
        }

    return results


def compute_aggregate_metrics(
    all_query_metrics: List[Dict[str, Any]],
    all_queries_results: List[Tuple[List[str], Set[str]]],
    k_values: List[int] = [3, 5, 10]
) -> Dict[str, Any]:
    """
    Aggregate metrics across all queries (job descriptions).

    Args:
        all_query_metrics: List of per-query metric dicts from compute_all_metrics_for_query.
        all_queries_results: List of (ranked_ids, relevant_ids) tuples for MAP/MRR.
        k_values: K values used during per-query computation.

    Returns:
        Dictionary with aggregated (averaged) metrics.
    """
    aggregate = {
        "num_queries": len(all_query_metrics),
        "MAP": round(mean_average_precision(all_queries_results), 4),
        "MRR": round(mean_reciprocal_rank(all_queries_results), 4),
        "per_k": {}
    }

    for k in k_values:
        p_at_k_values = [qm["per_k"][k]["precision_at_k"] for qm in all_query_metrics if k in qm["per_k"]]
        r_at_k_values = [qm["per_k"][k]["recall_at_k"] for qm in all_query_metrics if k in qm["per_k"]]
        ndcg_values = [qm["per_k"][k]["ndcg_at_k"] for qm in all_query_metrics if k in qm["per_k"]]

        aggregate["per_k"][k] = {
            "mean_precision_at_k": round(np.mean(p_at_k_values).item(), 4) if p_at_k_values else 0.0,
            "mean_recall_at_k": round(np.mean(r_at_k_values).item(), 4) if r_at_k_values else 0.0,
            "mean_ndcg_at_k": round(np.mean(ndcg_values).item(), 4) if ndcg_values else 0.0,
        }

    return aggregate
