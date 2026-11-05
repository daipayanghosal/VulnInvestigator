"""
tests/test_evaluation.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Pytest tests for ranking metric functions:
- kendall_tau
- rank_displacement
- ndcg

Edge cases covered:
- Identical rankings
- Fully reversed rankings
- Partial overlap between rankings
- Single-item lists
- Empty lists
"""

from __future__ import annotations

import pytest

from src.evaluation.ranking_metrics import kendall_tau, rank_displacement, ndcg


# ---------------------------------------------------------------------------
# kendall_tau tests
# ---------------------------------------------------------------------------

class TestKendallTau:

    def test_identical_rankings_returns_one(self) -> None:
        ranking = ["A", "B", "C", "D", "E"]
        result = kendall_tau(ranking, ranking)
        assert abs(result - 1.0) < 1e-9, f"Expected 1.0, got {result}"

    def test_reversed_rankings_returns_minus_one(self) -> None:
        ranking_a = ["A", "B", "C", "D"]
        ranking_b = ["D", "C", "B", "A"]
        result = kendall_tau(ranking_a, ranking_b)
        assert abs(result - (-1.0)) < 1e-9, f"Expected -1.0, got {result}"

    def test_partial_overlap(self) -> None:
        ranking_a = ["A", "B", "C", "D"]
        ranking_b = ["A", "C", "D", "E"]  # E not in a, B not in b
        result = kendall_tau(ranking_a, ranking_b)
        # Only A, C, D are common — A before C before D in both → τ = 1.0
        assert abs(result - 1.0) < 1e-9

    def test_empty_lists(self) -> None:
        assert kendall_tau([], []) == 0.0

    def test_single_item(self) -> None:
        assert kendall_tau(["A"], ["A"]) == 0.0  # < 2 common items → 0.0

    def test_two_items_concordant(self) -> None:
        result = kendall_tau(["A", "B"], ["A", "B"])
        assert abs(result - 1.0) < 1e-9

    def test_two_items_discordant(self) -> None:
        result = kendall_tau(["A", "B"], ["B", "A"])
        assert abs(result - (-1.0)) < 1e-9

    def test_known_value(self) -> None:
        # Manually verified: τ for this pair = 1/3
        ranking_a = ["A", "B", "C"]
        ranking_b = ["A", "C", "B"]
        result = kendall_tau(ranking_a, ranking_b)
        # Pairs: (A,B) concordant, (A,C) concordant, (B,C) discordant
        # τ = (2-1)/sqrt(3*3) = 1/3
        assert abs(result - (1 / 3)) < 1e-6, f"Expected ~0.333, got {result}"


# ---------------------------------------------------------------------------
# rank_displacement tests
# ---------------------------------------------------------------------------

class TestRankDisplacement:

    def test_identical_rankings_zero_displacement(self) -> None:
        ranking = ["A", "B", "C", "D"]
        df = rank_displacement(ranking, ranking)
        assert (df["displacement"] == 0).all()

    def test_reversed_maximum_displacement(self) -> None:
        ranking_a = ["A", "B", "C"]
        ranking_b = ["C", "B", "A"]
        df = rank_displacement(ranking_a, ranking_b)
        # A: rank_a=1, rank_b=3 → displacement=−2
        a_row = df[df["item"] == "A"].iloc[0]
        assert a_row["displacement"] == -2

    def test_all_items_in_result(self) -> None:
        ranking_a = ["A", "B", "C"]
        ranking_b = ["A", "B", "C"]
        df = rank_displacement(ranking_a, ranking_b)
        assert set(df["item"].tolist()) == {"A", "B", "C"}

    def test_sorted_by_absolute_displacement(self) -> None:
        ranking_a = ["A", "B", "C", "D"]
        ranking_b = ["D", "A", "B", "C"]
        df = rank_displacement(ranking_a, ranking_b)
        abs_disps = df["displacement"].abs().tolist()
        assert abs_disps == sorted(abs_disps, reverse=True)

    def test_partial_overlap_items_included(self) -> None:
        # Only common items should appear
        ranking_a = ["A", "B", "C"]
        ranking_b = ["B", "C", "D"]  # A not in b, D not in a
        df = rank_displacement(ranking_a, ranking_b)
        items = set(df["item"].tolist())
        assert "A" not in items  # A is only in ranking_a
        assert "D" not in items  # D is only in ranking_b
        assert "B" in items and "C" in items


# ---------------------------------------------------------------------------
# ndcg tests
# ---------------------------------------------------------------------------

class TestNDCG:

    def test_perfect_ranking_returns_one(self) -> None:
        ranked = ["A", "B", "C"]
        rel = {"A": 3, "B": 2, "C": 1}
        result = ndcg(ranked, rel, k=3)
        assert abs(result - 1.0) < 1e-9

    def test_reversed_ranking_less_than_one(self) -> None:
        ranked = ["C", "B", "A"]
        rel = {"A": 3, "B": 2, "C": 1}
        result = ndcg(ranked, rel, k=3)
        assert result < 1.0

    def test_all_zero_relevance_returns_zero(self) -> None:
        ranked = ["A", "B", "C"]
        rel = {"A": 0, "B": 0, "C": 0}
        result = ndcg(ranked, rel, k=3)
        assert result == 0.0

    def test_k_cutoff_respected(self) -> None:
        ranked = ["C", "B", "A"]
        rel = {"A": 3, "B": 2, "C": 1}
        result_k1 = ndcg(ranked, rel, k=1)
        # At k=1 we only see "C" (rel=1); ideal is "A" (rel=3)
        assert result_k1 < 1.0

    def test_missing_items_in_relevance(self) -> None:
        # Items not in rel_scores get 0 relevance
        ranked = ["A", "B", "C", "D"]
        rel = {"A": 3, "B": 2}
        result = ndcg(ranked, rel, k=4)
        assert 0.0 <= result <= 1.0

    def test_empty_ranked_list(self) -> None:
        result = ndcg([], {"A": 3}, k=5)
        assert result == 0.0

    def test_single_item_perfect(self) -> None:
        result = ndcg(["A"], {"A": 1}, k=1)
        assert abs(result - 1.0) < 1e-9

    def test_ndcg_range(self) -> None:
        """nDCG must always be in [0, 1]."""
        import random
        items = list("ABCDEFGHIJ")
        rel = {item: random.randint(0, 5) for item in items}
        ranked = items[:]
        random.shuffle(ranked)
        result = ndcg(ranked, rel, k=5)
        assert 0.0 <= result <= 1.0
