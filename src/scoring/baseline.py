"""
src/scoring/baseline.py
~~~~~~~~~~~~~~~~~~~~~~~
CVSS-only baseline scorer.

Ranks vulnerabilities purely by their CVSS v3 base score (descending).
This baseline is used as the comparison point for the contextual risk scorer —
the two rankings are later compared with Kendall's τ.
"""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class CVSSBaselineScorer:
    """Ranks vulnerabilities by CVSS v3 base score only.

    Parameters
    ----------
    vuln_df:
        Normalised vulnerability DataFrame.  Must contain ``cve_id`` and
        ``cvss_v3_score`` columns (produced by ``DataNormaliser.normalise_nvd``).

    Usage
    -----
    >>> scorer = CVSSBaselineScorer(vuln_df)
    >>> ranked = scorer.score(vuln_df)
    >>> top10 = scorer.get_top_n(10)
    """

    def __init__(self, vuln_df: pd.DataFrame | None = None) -> None:
        self._ranked_df: pd.DataFrame = pd.DataFrame()
        if vuln_df is not None:
            self.score(vuln_df)

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score(self, vuln_df: pd.DataFrame) -> pd.DataFrame:
        """Sort *vuln_df* by CVSS v3 score descending and add a rank column.

        CVEs with no CVSS score (NaN) are sorted to the bottom.

        Parameters
        ----------
        vuln_df:
            Input vulnerability DataFrame.  Must contain ``cve_id`` and
            ``cvss_v3_score`` columns.

        Returns
        -------
        pd.DataFrame
            Copy of *vuln_df* sorted descending by ``cvss_v3_score`` with an
            additional ``rank_cvss`` column (1 = highest score).
        """
        if vuln_df.empty:
            logger.warning("CVSSBaselineScorer.score: received empty DataFrame")
            self._ranked_df = vuln_df.copy()
            return self._ranked_df

        required = {"cve_id", "cvss_v3_score"}
        missing = required - set(vuln_df.columns)
        if missing:
            raise ValueError(f"CVSSBaselineScorer: DataFrame missing columns: {missing}")

        ranked = vuln_df.copy()
        # Drop any existing/duplicated rank_cvss column cleanly
        clean_cols = [c for c in ranked.columns if c != "rank_cvss"]
        ranked = ranked.loc[:, clean_cols]
        ranked["cvss_v3_score"] = pd.to_numeric(ranked["cvss_v3_score"], errors="coerce")
        ranked = ranked.sort_values("cvss_v3_score", ascending=False, na_position="last")
        ranked = ranked.reset_index(drop=True)
        ranked["rank_cvss"] = list(range(1, len(ranked) + 1))
        # Re-order so rank_cvss is the leading column
        ordered_cols = ["rank_cvss"] + [c for c in ranked.columns if c != "rank_cvss"]
        ranked = ranked[ordered_cols]

        self._ranked_df = ranked
        logger.info(
            "CVSSBaselineScorer: ranked %d CVEs; top score = %.1f",
            len(ranked),
            ranked["cvss_v3_score"].iloc[0] if not ranked.empty else float("nan"),
        )
        return ranked

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def get_top_n(self, n: int) -> pd.DataFrame:
        """Return the top *n* CVEs by CVSS score.

        Parameters
        ----------
        n:
            Number of top-ranked CVEs to return.

        Returns
        -------
        pd.DataFrame

        Raises
        ------
        RuntimeError
            If :meth:`score` has not been called yet.
        """
        if self._ranked_df.empty:
            raise RuntimeError(
                "CVSSBaselineScorer: call score() before get_top_n()"
            )
        return self._ranked_df.head(n).copy()
