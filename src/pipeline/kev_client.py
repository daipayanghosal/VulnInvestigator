"""
src/pipeline/kev_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Client for the CISA Known Exploited Vulnerabilities (KEV) catalogue.

CISA publishes the KEV list as a single JSON file at a stable URL.
This module downloads that file, exposes it as a list of dicts, and
provides a helper that returns the set of CVE IDs for fast membership tests.

KEV catalogue docs: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

_DEFAULT_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
)


class KEVClient:
    """Downloads and parses the CISA Known Exploited Vulnerabilities catalogue.

    Parameters
    ----------
    url:
        URL of the KEV JSON feed.  Defaults to the official CISA endpoint.
    timeout:
        HTTP request timeout in seconds.
    """

    def __init__(self, url: str = _DEFAULT_KEV_URL, timeout: int = 30) -> None:
        self.url = url
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Core fetch
    # ------------------------------------------------------------------

    def fetch(self) -> list[dict[str, Any]]:
        """Download the CISA KEV catalogue and return the list of vulnerability records.

        Returns
        -------
        list[dict]
            Each dict represents one KEV entry, e.g.::

                {
                    "cveID": "CVE-2021-44228",
                    "vendorProject": "Apache",
                    "product": "Log4j2",
                    "vulnerabilityName": "Apache Log4j2 Remote Code Execution Vulnerability",
                    "dateAdded": "2021-12-10",
                    "shortDescription": "...",
                    "requiredAction": "...",
                    "dueDate": "2021-12-24",
                    "knownRansomwareCampaignUse": "Known",
                    "notes": "..."
                }

        Raises
        ------
        requests.HTTPError
            If the server returns a non-2xx status code.
        """
        logger.info("KEV: downloading catalogue from %s", self.url)
        try:
            response = self._session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("KEV HTTP error: %s", exc)
            raise
        except requests.RequestException as exc:
            logger.error("KEV request failed: %s", exc)
            raise

        payload: dict[str, Any] = response.json()
        vulnerabilities: list[dict[str, Any]] = payload.get("vulnerabilities", [])
        logger.info("KEV: downloaded %d entries", len(vulnerabilities))
        return vulnerabilities

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_cve_set(self, kev_data: list[dict[str, Any]]) -> set[str]:
        """Return the set of CVE IDs present in the KEV catalogue.

        Parameters
        ----------
        kev_data:
            List of KEV dicts as returned by :meth:`fetch`.

        Returns
        -------
        set[str]
            Upper-cased CVE IDs, e.g. ``{"CVE-2021-44228", "CVE-2022-26134", ...}``.
        """
        cve_set = {entry.get("cveID", "").upper() for entry in kev_data if entry.get("cveID")}
        logger.debug("KEV: CVE set size = %d", len(cve_set))
        return cve_set

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_raw(self, data: list[dict[str, Any]], path: str) -> None:
        """Persist raw KEV records to a JSON file.

        Parameters
        ----------
        data:
            KEV vulnerability list as returned by :meth:`fetch`.
        path:
            Destination file path (parent directories are created if needed).
        """
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        logger.info("KEV: saved %d records → %s", len(data), dest)
