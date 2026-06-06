"""
Unit tests for IR evaluation metrics.

Each test uses hand-computed expected values to verify correctness.
Run with:
    cd backend
    python -m pytest evaluation/test_metrics.py -v
"""

import pytest
import math
from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    average_precision,
    mean_average_precision,
    dcg_at_k,
    ndcg_at_k,
    mean_reciprocal_rank,
    compute_all_metrics_for_query,
    compute_aggregate_metrics,
)


# ============================================================================
# Precision@K Tests
# ============================================================================

class TestPrecisionAtK:
    def test_all_relevant(self):
        """All top-K results are relevant → Precision@K = 1.0"""
        ranked = ["a", "b", "c", "d"]
        relevant = {"a", "b", "c", "d"}
        assert precision_at_k(ranked, relevant, k=3) == 1.0

    def test_none_relevant(self):
        """No top-K results are relevant → Precision@K = 0.0"""
        ranked = ["a", "b", "c", "d"]
        relevant = {"x", "y", "z"}
        assert precision_at_k(ranked, relevant, k=3) == 0.0

    def test_partial_relevant(self):
        """2 of top-3 are relevant → Precision@3 = 2/3"""
        ranked = ["a", "b", "c", "d"]
        relevant = {"a", "c"}
        result = precision_at_k(ranked, relevant, k=3)
        assert abs(result - 2 / 3) < 1e-6

    def test_k_equals_one(self):
        """Precision@1 is 1.0 if first result is relevant."""
        ranked = ["a", "b", "c"]
        relevant = {"a"}
        assert precision_at_k(ranked, relevant, k=1) == 1.0

    def test_k_exceeds_list(self):
        """K larger than ranking list — only evaluate available items."""
        ranked = ["a", "b"]
        relevant = {"a", "b"}
        # K=5 but only 2 items: 2/5 = 0.4
        assert abs(precision_at_k(ranked, relevant, k=5) - 0.4) < 1e-6

    def test_k_zero(self):
        """K=0 should return 0.0."""
        assert precision_at_k(["a", "b"], {"a"}, k=0) == 0.0

    def test_empty_ranking(self):
        """Empty ranking list."""
        assert precision_at_k([], {"a", "b"}, k=3) == 0.0


# ============================================================================
# Recall@K Tests
# ============================================================================

class TestRecallAtK:
    def test_all_found(self):
        """All relevant items in top-K → Recall@K = 1.0"""
        ranked = ["a", "b", "c", "d"]
        relevant = {"a", "b"}
        assert recall_at_k(ranked, relevant, k=3) == 1.0

    def test_none_found(self):
        """No relevant items in top-K → Recall@K = 0.0"""
        ranked = ["x", "y", "z"]
        relevant = {"a", "b"}
        assert recall_at_k(ranked, relevant, k=3) == 0.0

    def test_partial_found(self):
        """1 of 3 relevant found in top-2 → Recall@2 = 1/3"""
        ranked = ["a", "x", "b", "c"]
        relevant = {"a", "b", "c"}
        result = recall_at_k(ranked, relevant, k=2)
        assert abs(result - 1 / 3) < 1e-6

    def test_no_relevant_items(self):
        """No relevant items at all → Recall = 0.0."""
        assert recall_at_k(["a", "b"], set(), k=3) == 0.0


# ============================================================================
# Average Precision Tests
# ============================================================================

class TestAveragePrecision:
    def test_perfect_ranking(self):
        """All relevant items ranked first → AP = 1.0"""
        ranked = ["a", "b", "c", "d"]
        relevant = {"a", "b"}
        assert average_precision(ranked, relevant) == 1.0

    def test_worst_ranking(self):
        """Relevant items ranked last."""
        ranked = ["x", "y", "a", "b"]
        relevant = {"a", "b"}
        # AP = (1/2) * (1/3 + 2/4) = (1/2) * (0.3333 + 0.5) = 0.4167
        result = average_precision(ranked, relevant)
        assert abs(result - (1 / 2) * (1 / 3 + 2 / 4)) < 1e-4

    def test_mixed_ranking(self):
        """Hand-computed: relevant at positions 1 and 3."""
        ranked = ["a", "x", "b", "y"]
        relevant = {"a", "b"}
        # AP = (1/2) * (1/1 + 2/3) = (1/2) * (1.6667) = 0.8333
        result = average_precision(ranked, relevant)
        assert abs(result - (1 / 2) * (1 + 2 / 3)) < 1e-4

    def test_no_relevant(self):
        """No relevant items → AP = 0.0"""
        assert average_precision(["a", "b", "c"], set()) == 0.0

    def test_single_relevant_first(self):
        """Single relevant item at rank 1 → AP = 1.0"""
        assert average_precision(["a", "b", "c"], {"a"}) == 1.0

    def test_single_relevant_last(self):
        """Single relevant item at rank 3 → AP = 1/3"""
        result = average_precision(["x", "y", "a"], {"a"})
        assert abs(result - 1 / 3) < 1e-6


# ============================================================================
# MAP Tests
# ============================================================================

class TestMAP:
    def test_two_queries(self):
        """MAP over two queries."""
        results = [
            (["a", "x", "b"], {"a", "b"}),  # AP = (1/2)*(1/1 + 2/3) = 0.8333
            (["x", "y", "z"], {"y"}),         # AP = 1/2 = 0.5
        ]
        expected = (0.8333 + 0.5) / 2
        result = mean_average_precision(results)
        assert abs(result - expected) < 1e-3

    def test_empty_queries(self):
        """No queries → MAP = 0.0"""
        assert mean_average_precision([]) == 0.0


# ============================================================================
# DCG Tests
# ============================================================================

class TestDCG:
    def test_basic_dcg(self):
        """Hand-computed DCG@3 for relevances [3, 2, 0]."""
        # DCG = (2^3-1)/log2(2) + (2^2-1)/log2(3) + (2^0-1)/log2(4)
        # DCG = 7/1 + 3/1.585 + 0/2 = 7.0 + 1.893 + 0.0 = 8.893
        result = dcg_at_k([3, 2, 0, 1], k=3)
        expected = 7.0 / math.log2(2) + 3.0 / math.log2(3) + 0.0 / math.log2(4)
        assert abs(result - expected) < 1e-3

    def test_single_item(self):
        """DCG@1 = (2^rel - 1) / log2(2) = (2^3 - 1) / 1 = 7.0"""
        result = dcg_at_k([3], k=1)
        assert abs(result - 7.0) < 1e-6

    def test_all_zeros(self):
        """All-zero relevances → DCG = 0.0"""
        assert dcg_at_k([0, 0, 0], k=3) == 0.0

    def test_k_zero(self):
        """K=0 → DCG = 0.0"""
        assert dcg_at_k([3, 2, 1], k=0) == 0.0


# ============================================================================
# NDCG Tests
# ============================================================================

class TestNDCG:
    def test_perfect_ranking(self):
        """Perfect ranking (already in ideal order) → NDCG = 1.0"""
        # Already sorted descending
        result = ndcg_at_k([3, 2, 1, 0], k=4)
        assert abs(result - 1.0) < 1e-6

    def test_worst_ranking(self):
        """Reversed ranking → NDCG < 1.0"""
        # Worst order for this set
        result = ndcg_at_k([0, 1, 2, 3], k=4)
        assert result < 1.0
        assert result > 0.0

    def test_all_same_relevance(self):
        """All same relevance → NDCG = 1.0 (any order is ideal)"""
        result = ndcg_at_k([2, 2, 2], k=3)
        assert abs(result - 1.0) < 1e-6

    def test_all_zero_relevance(self):
        """All zero → NDCG = 0.0 (IDCG is 0)"""
        result = ndcg_at_k([0, 0, 0], k=3)
        assert result == 0.0

    def test_ndcg_at_k_smaller_than_list(self):
        """NDCG@2 with 4 items — only first 2 matter."""
        # relevances = [3, 0, 2, 1], k=2
        # DCG@2 = (2^3-1)/log2(2) + (2^0-1)/log2(3) = 7/1 + 0/1.585 = 7.0
        # Ideal@2 from [3,2,1,0] = (2^3-1)/log2(2) + (2^2-1)/log2(3) = 7+1.893 = 8.893
        # NDCG = 7.0 / 8.893 ≈ 0.7871
        result = ndcg_at_k([3, 0, 2, 1], k=2)
        ideal_dcg = 7.0 / math.log2(2) + 3.0 / math.log2(3)
        actual_dcg = 7.0 / math.log2(2) + 0.0 / math.log2(3)
        expected = actual_dcg / ideal_dcg
        assert abs(result - expected) < 1e-3


# ============================================================================
# MRR Tests
# ============================================================================

class TestMRR:
    def test_first_relevant_at_rank_1(self):
        """First relevant at rank 1 for all queries → MRR = 1.0"""
        results = [
            (["a", "b", "c"], {"a"}),
            (["x", "y", "z"], {"x"}),
        ]
        assert mean_reciprocal_rank(results) == 1.0

    def test_mixed_ranks(self):
        """First relevant at rank 2 and rank 1 → MRR = (0.5 + 1.0) / 2 = 0.75"""
        results = [
            (["x", "a", "b"], {"a", "b"}),   # RR = 1/2
            (["a", "b", "c"], {"a"}),          # RR = 1/1
        ]
        result = mean_reciprocal_rank(results)
        assert abs(result - 0.75) < 1e-6

    def test_no_relevant(self):
        """No relevant items found in any query → RR = 0 for those queries."""
        results = [
            (["a", "b", "c"], {"x", "y"}),  # RR = 0
        ]
        assert mean_reciprocal_rank(results) == 0.0

    def test_empty_queries(self):
        """No queries → MRR = 0.0"""
        assert mean_reciprocal_rank([]) == 0.0


# ============================================================================
# Integration: compute_all_metrics_for_query
# ============================================================================

class TestComputeAllMetrics:
    def test_basic_integration(self):
        """Smoke test: all metrics computed without error."""
        ranked_ids = ["a", "b", "c", "d", "e"]
        relevance_map = {"a": 3, "b": 0, "c": 2, "d": 1, "e": 0}

        result = compute_all_metrics_for_query(ranked_ids, relevance_map, k_values=[3, 5])

        assert "average_precision" in result
        assert "num_relevant" in result
        assert result["num_relevant"] == 3  # a(3), c(2), d(1) are relevant
        assert 3 in result["per_k"]
        assert 5 in result["per_k"]
        assert "precision_at_k" in result["per_k"][3]
        assert "recall_at_k" in result["per_k"][3]
        assert "ndcg_at_k" in result["per_k"][3]

    def test_values_correct(self):
        """Verify computed values match hand-calculated expectations."""
        ranked_ids = ["a", "b", "c"]
        relevance_map = {"a": 3, "b": 0, "c": 2}

        result = compute_all_metrics_for_query(ranked_ids, relevance_map, k_values=[3])

        # Precision@3: 2 relevant out of 3 = 0.6667
        assert abs(result["per_k"][3]["precision_at_k"] - 2 / 3) < 1e-3

        # Recall@3: 2 of 2 relevant found = 1.0
        assert result["per_k"][3]["recall_at_k"] == 1.0


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    def test_single_candidate(self):
        """Single candidate in ranking."""
        ranked = ["a"]
        relevant = {"a"}
        assert precision_at_k(ranked, relevant, k=1) == 1.0
        assert recall_at_k(ranked, relevant, k=1) == 1.0
        assert average_precision(ranked, relevant) == 1.0

    def test_large_k_small_list(self):
        """K much larger than list size."""
        ranked = ["a", "b"]
        relevant = {"a"}
        # Precision@100 = 1/100 = 0.01
        assert abs(precision_at_k(ranked, relevant, k=100) - 0.01) < 1e-6
        # Recall@100 = 1/1 = 1.0
        assert recall_at_k(ranked, relevant, k=100) == 1.0

    def test_all_irrelevant_candidates(self):
        """No candidates are relevant at all."""
        ranked = ["a", "b", "c"]
        relevance_map = {"a": 0, "b": 0, "c": 0}
        result = compute_all_metrics_for_query(ranked, relevance_map, k_values=[3])
        assert result["num_relevant"] == 0
        assert result["average_precision"] == 0.0
        assert result["per_k"][3]["precision_at_k"] == 0.0
        assert result["per_k"][3]["ndcg_at_k"] == 0.0
