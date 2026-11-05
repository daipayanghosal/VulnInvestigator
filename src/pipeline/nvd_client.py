"""
src/pipeline/nvd_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Client for the NIST National Vulnerability Database (NVD) REST API v2.

Handles:
- Single-page and paginated CVE fetches
- API-key-based rate limiting (6 s without key, 0.6 s with key)
- Date-range filtering for recent CVEs
- Raw JSON persistence

NVD API docs: https://nvd.nist.gov/developers/vulnerabilities
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


class NVDClient:
    """Wraps the NVD CVE 2.0 REST API.

    Parameters
    ----------
    api_key:
        Optional NVD API key.  With a key the rate limit is ~50 req/30 s;
        without it ~5 req/30 s.
    delay:
        Minimum seconds to wait between successive API calls.  Defaults to
        6 s (safe without a key).  Pass 0.6 when you have a key.
    base_url:
        NVD endpoint base URL.
    """

    _DEFAULT_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    _DEFAULT_DELAY = 6  # seconds (unauthenticated rate-limit safe value)

    def __init__(
        self,
        api_key: str | None = None,
        delay: float = _DEFAULT_DELAY,
        base_url: str = _DEFAULT_BASE_URL,
    ) -> None:
        self.api_key = api_key
        self.delay = delay
        self.base_url = base_url

        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        if api_key:
            self._session.headers["apiKey"] = api_key
            logger.info("NVDClient: authenticated session (key ending ...%s)", api_key[-4:])
        else:
            logger.info("NVDClient: unauthenticated session — delay=%.1f s", delay)

    # ------------------------------------------------------------------
    # Core fetch
    # ------------------------------------------------------------------

    def fetch_cves(
        self,
        keyword: str | None = None,
        pub_start_date: str | None = None,
        pub_end_date: str | None = None,
        start_index: int = 0,
        results_per_page: int = 2000,
    ) -> list[dict[str, Any]]:
        """Fetch CVEs from the NVD API with optional filters, handling pagination.

        Parameters
        ----------
        keyword:
            Free-text keyword filter (passed as ``keywordSearch``).
        pub_start_date:
            ISO-8601 start date for ``pubStartDate`` filter, e.g. ``"2024-01-01T00:00:00.000"``.
        pub_end_date:
            ISO-8601 end date for ``pubEndDate`` filter.
        start_index:
            Zero-based index of the first CVE to fetch.
        results_per_page:
            Number of results per API page (max 2000 per NVD docs).

        Returns
        -------
        list[dict]
            Flat list of raw NVD CVE item dicts (each containing a ``cve`` key).
        """
        params: dict[str, Any] = {
            "startIndex": start_index,
            "resultsPerPage": results_per_page,
        }
        if keyword:
            params["keywordSearch"] = keyword
        if pub_start_date:
            params["pubStartDate"] = pub_start_date
        if pub_end_date:
            params["pubEndDate"] = pub_end_date

        all_cves: list[dict[str, Any]] = []
        current_index = start_index

        while True:
            params["startIndex"] = current_index
            logger.debug("NVD fetch: startIndex=%d params=%s", current_index, params)

            try:
                response = self._session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
            except requests.HTTPError as exc:
                logger.error("NVD HTTP error: %s", exc)
                raise
            except requests.RequestException as exc:
                logger.error("NVD request failed: %s", exc)
                raise

            payload = response.json()
            total_results: int = payload.get("totalResults", 0)
            vulnerabilities: list[dict] = payload.get("vulnerabilities", [])

            all_cves.extend(vulnerabilities)
            logger.info(
                "NVD: fetched %d/%d CVEs (page startIndex=%d)",
                len(all_cves),
                total_results,
                current_index,
            )

            current_index += len(vulnerabilities)
            if current_index >= total_results or not vulnerabilities:
                break  # all pages consumed

            logger.debug("NVD: sleeping %.1f s before next page…", self.delay)
            time.sleep(self.delay)

        logger.info("NVD: total CVEs retrieved = %d", len(all_cves))
        return all_cves

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def fetch_all_recent(self, days_back: int = 90) -> list[dict[str, Any]]:
        """Fetch all CVEs published within the last *days_back* calendar days.

        NVD imposes a maximum 120-day window per request; this method splits
        larger ranges into 119-day chunks automatically.

        Parameters
        ----------
        days_back:
            Number of past days to query.

        Returns
        -------
        list[dict]
            Combined list of raw NVD CVE item dicts.
        """
        now = datetime.now(tz=timezone.utc)
        all_cves: list[dict[str, Any]] = []

        # NVD max window is 120 days; chunk into 119-day windows to be safe
        chunk_days = 119
        remaining = days_back
        end_dt = now

        while remaining > 0:
            window = min(remaining, chunk_days)
            start_dt = end_dt - timedelta(days=window)

            start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000")
            end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000")

            logger.info("NVD: querying %s → %s", start_str, end_str)
            chunk = self.fetch_cves(pub_start_date=start_str, pub_end_date=end_str)
            all_cves.extend(chunk)

            end_dt = start_dt - timedelta(seconds=1)
            remaining -= window

            if remaining > 0:
                time.sleep(self.delay)

        return all_cves

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_raw(self, cves: list[dict[str, Any]], path: str) -> None:
        """Persist raw CVE list to a JSON file.

        Parameters
        ----------
        cves:
            List of raw NVD CVE dicts as returned by :meth:`fetch_cves`.
        path:
            Destination file path (parent directories are created if needed).
        """
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(cves, fh, indent=2)
        logger.info("NVD: saved %d raw CVEs → %s", len(cves), dest)
