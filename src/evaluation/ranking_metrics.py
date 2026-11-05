"""
src/evaluation/ranking_metrics.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ranking quality metrics: Kendall's τ, rank displacement, and nDCG.

All implementations use NumPy directly — no scikit-learn dependency — so
the evaluation module remains lightweight and dependency-minimal.

References
----------
- Kendall (1938) "A New Measure of Rank Correlation", Biometrika.
- Järvelin & Kekäläinen (2002) "Cumulated gain-based evaluation of IR techniques", ACM TOIS.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Kendall's τ
# ---------------------------------------------------------------------------

def kendall_tau(ranking_a: list, ranking_b: list) -> float:
    """Compute Kendall's τ-b between two ranked lists of items.

    Both lists must contain the same items (order determines rank).
    Items present in one list but not the other are silently ignored
    (only the intersection is used).

    Parameters
    ----------
    ranking_a:
        Ordered list of items — position 0 = rank 1 (highest).
    ranking_b:
        Ordered list of items — position 0 = rank 1 (highest).

    Returns
    -------
    float
        Kendall's τ-b in the range [−1.0, 1.0].
        Returns 0.0 if fewer than 2 common items exist.

    Examples
    --------
    >>> kendall_tau(["A", "B", "C"], ["A", "B", "C"])
    1.0
    >>> kendall_tau(["A", "B", "C"], ["C", "B", "A"])
    -1.0
    """
    # Build rank mappings (1-indexed)
    rank_a: dict[object, int] = {item: i + 1 for i, item in enumerate(ranking_a)}
    rank_b: dict[object, int] = {item: i + 1 for i, item in enumerate(ranking_b)}

    # Intersection only
    common = [item for item in ranking_a if item in rank_b]
    n = len(common)
    if n < 2:
        return 0.0

    ranks_a = np.array([rank_a[item] for item in common], dtype=float)
    ranks_b = np.array([rank_b[item] for item in common], dtype=float)

    concordant = 0
    discordant = 0
    ties_a = 0
    ties_b = 0

    for i in range(n):
        for j in range(i + 1, n):
            diff_a = ranks_a[i] - ranks_a[j]
            diff_b = ranks_b[i] - ranks_b[j]
            product = diff_a * diff_b
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
            else:
                if diff_a == 0:
                    ties_a += 1
                if diff_b == 0:
                    ties_b += 1

    n_pairs = n * (n - 1) / 2
    denominator = math.sqrt(
        (n_pairs - ties_a) * (n_pairs - ties_b)
    )
    if denominator == 0:
        return 0.0

    tau = (concordant - discordant) / denominator
    return float(tau)


# ---------------------------------------------------------------------------
# Rank displacement
# ---------------------------------------------------------------------------

def rank_displacement(ranking_a: list, ranking_b: list) -> pd.DataFrame:
    """Compute per-item rank change between two rankings.

    Parameters
    ----------
    ranking_a:
        Reference ranking (e.g. CVSS baseline).
    ranking_b:
        Alternative ranking (e.g. contextual risk).

    Returns
    -------
    pd.DataFrame
        Columns: ``item``, ``rank_a``, ``rank_b``, ``displacement``
        (rank_a − rank_b; positive means item moved up in ranking_b).
        Sorted by absolute displacement descending.
    """
    rank_a: dict[object, int] = {item: i + 1 for i, item in enumerate(ranking_a)}
    rank_b: dict[object, int] = {item: i + 1 for i, item in enumerate(ranking_b)}

    all_items = list(dict.fromkeys(ranking_a + ranking_b))  # preserve order, deduplicate
    records = []
    for item in all_items:
        ra = rank_a.get(item, None)
        rb = rank_b.get(item, None)
        if ra is not None and rb is not None:
            records.append(
                {"item": item, "rank_a": ra, "rank_b": rb, "displacement": ra - rb}
            )

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("displacement", key=lambda s: s.abs(), ascending=False)
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# nDCG
# ---------------------------------------------------------------------------

def ndcg(ranked_list: list, relevance_scores: dict, k: int = 10) -> float:
    """Compute Normalised Discounted Cumulative Gain (nDCG@k).

    Parameters
    ----------
    ranked_list:
        Ordered list of items as returned by the ranker (position 0 = rank 1).
    relevance_scores:
        Dict mapping item → ground-truth relevance score (non-negative float).
        Items not in the dict are assigned relevance 0.
    k:
        Cutoff depth.

    Returns
    -------
    float
        nDCG@k in [0.0, 1.0].  Returns 0.0 if the ideal DCG is 0.

    Examples
    --------
    >>> ndcg(["A", "B", "C"], {"A": 3, "B": 2, "C": 1}, k=3)
    1.0
    >>> ndcg(["C", "B", "A"], {"A": 3, "B": 2, "C": 1}, k=3)
    # value < 1.0 (worst ordering)
    """
    ranked_top_k = ranked_list[:k]

    def dcg(items: list) -> float:
        total = 0.0
        for i, item in enumerate(items):
            rel = relevance_scores.get(item, 0.0)
            total += rel / math.log2(i + 2)  # log2(rank+1), rank is 1-indexed
        return total

    actual_dcg = dcg(ranked_top_k)
    # Ideal DCG: sort by relevance descending, take top-k
    ideal_items = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)[:k]
    ideal_dcg = dcg(ideal_items)

    if ideal_dcg == 0.0:
        return 0.0
    return actual_dcg / ideal_dcg
