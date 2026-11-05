"""
src/pipeline/attack_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Client for the MITRE ATT&CK Enterprise knowledge base (STIX 2.1 bundle).

Downloads the full enterprise ATT&CK STIX bundle from the MITRE CTI GitHub
repository, extracts technique objects, and exposes them as a Pandas DataFrame
for downstream correlation.

ATT&CK STIX data: https://github.com/mitre/cti
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

_DEFAULT_ATTACK_URL = (
    "https://raw.githubusercontent.com/mitre/cti/master/"
    "enterprise-attack/enterprise-attack.json"
)


class ATTACKClient:
    """Downloads and parses the MITRE ATT&CK Enterprise STIX bundle.

    Parameters
    ----------
    url:
        URL of the enterprise-attack.json STIX bundle.
    timeout:
        HTTP request timeout in seconds (the bundle is ~15 MB, so allow time).
    """

    def __init__(self, url: str = _DEFAULT_ATTACK_URL, timeout: int = 120) -> None:
        self.url = url
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Core fetch
    # ------------------------------------------------------------------

    def fetch(self) -> dict[str, Any]:
        """Download the ATT&CK STIX bundle.

        Returns
        -------
        dict
            Full STIX bundle dict (top-level keys: ``type``, ``id``, ``objects``).

        Raises
        ------
        requests.HTTPError
            If the server returns a non-2xx status code.
        """
        logger.info("ATT&CK: downloading bundle from %s", self.url)
        try:
            response = self._session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("ATT&CK HTTP error: %s", exc)
            raise
        except requests.RequestException as exc:
            logger.error("ATT&CK request failed: %s", exc)
            raise

        bundle: dict[str, Any] = response.json()
        n_objects = len(bundle.get("objects", []))
        logger.info("ATT&CK: bundle downloaded, %d STIX objects", n_objects)
        return bundle

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract_techniques(self, bundle: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract ATT&CK technique objects from a STIX bundle.

        Filters for ``attack-pattern`` objects that are *not* deprecated and
        *not* sub-techniques (i.e., their external ID does not contain a dot).
        Sub-techniques (e.g., T1059.001) are included separately.

        Parameters
        ----------
        bundle:
            STIX bundle dict as returned by :meth:`fetch`.

        Returns
        -------
        list[dict]
            Each dict contains::

                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "description": "...",
                    "url": "https://attack.mitre.org/techniques/T1190",
                    "tactics": ["initial-access"],
                    "is_subtechnique": False,
                }
        """
        techniques: list[dict[str, Any]] = []

        for obj in bundle.get("objects", []):
            if obj.get("type") != "attack-pattern":
                continue
            if obj.get("x_mitre_deprecated", False):
                continue

            # Extract the ATT&CK external ID (Txxxx)
            ext_refs = obj.get("external_references", [])
            attack_ref = next(
                (r for r in ext_refs if r.get("source_name") == "mitre-attack"), None
            )
            if not attack_ref:
                continue

            technique_id: str = attack_ref.get("external_id", "")
            url: str = attack_ref.get("url", "")

            # Collect tactic phase names
            kill_chain_phases = obj.get("kill_chain_phases", [])
            tactics: list[str] = [
                p["phase_name"] for p in kill_chain_phases if p.get("kill_chain_name") == "mitre-attack"
            ]

            techniques.append(
                {
                    "id": technique_id,
                    "name": obj.get("name", ""),
                    "description": obj.get("description", ""),
                    "url": url,
                    "tactics": tactics,
                    "is_subtechnique": obj.get("x_mitre_is_subtechnique", False),
                }
            )

        logger.info("ATT&CK: extracted %d technique objects", len(techniques))
        return techniques

    # ------------------------------------------------------------------
    # DataFrame helper
    # ------------------------------------------------------------------

    def techniques_to_dataframe(self, techniques: list[dict[str, Any]]) -> pd.DataFrame:
        """Convert the extracted techniques list into a Pandas DataFrame.

        The ``tactics`` column is serialised as a pipe-separated string for
        easy storage in SQLite / Parquet.

        Parameters
        ----------
        techniques:
            List of technique dicts as returned by :meth:`extract_techniques`.

        Returns
        -------
        pd.DataFrame
            Columns: ``id``, ``name``, ``description``, ``url``, ``tactics``,
            ``is_subtechnique``.
        """
        df = pd.DataFrame(techniques)
        if not df.empty:
            # Serialise list column so the DataFrame is Parquet-safe
            df["tactics"] = df["tactics"].apply(
                lambda t: "|".join(t) if isinstance(t, list) else ""
            )
        logger.debug("ATT&CK: techniques DataFrame shape = %s", df.shape)
        return df

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_raw(self, data: dict[str, Any], path: str) -> None:
        """Persist the raw STIX bundle to a JSON file.

        Parameters
        ----------
        data:
            STIX bundle dict as returned by :meth:`fetch`.
        path:
            Destination file path (parent directories are created if needed).
        """
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        logger.info("ATT&CK: saved raw bundle → %s", dest)
