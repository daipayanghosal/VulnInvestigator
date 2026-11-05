"""
src/correlation/correlator.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Maps CVEs to MITRE ATT&CK techniques using keyword-based heuristics, and
correlates those techniques with log events to build investigation scenarios.

The correlation is intentionally lightweight — keyword matching against
technique descriptions and log event tags — to keep the system self-contained
without requiring an NLP model at runtime.  LLM-enriched correlation can be
applied downstream in the GenAI module.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword hints: technique ID → list of product/technology strings that
# commonly indicate the technique is applicable.  Extend as needed.
# ---------------------------------------------------------------------------
_TECHNIQUE_KEYWORDS: dict[str, list[str]] = {
    "T1190": ["apache", "nginx", "iis", "weblogic", "jboss", "spring", "log4j",
              "struts", "php", "wordpress", "drupal", "openssl", "tomcat"],
    "T1078": ["active directory", "ldap", "kerberos", "oauth", "saml", "vpn",
              "ssh", "rdp", "okta", "azure ad"],
    "T1059": ["powershell", "bash", "cmd", "python", "perl", "ruby", "javascript",
              "vbscript", "wscript", "cscript"],
    "T1486": ["ransomware", "encrypted", "shadow copy", "backup", "vss"],
    "T1021": ["rdp", "ssh", "smb", "winrm", "vnc", "telnet", "psexec"],
    "T1055": ["dll", "injection", "process hollowing", "shellcode"],
    "T1083": ["directory traversal", "path traversal", "lfi", "file inclusion"],
    "T1110": ["brute force", "password spray", "credential stuffing", "hydra"],
    "T1566": ["phishing", "spear phishing", "attachment", "malicious link"],
    "T1071": ["http", "https", "dns", "ftp", "smtp", "command and control"],
}


class ThreatCorrelator:
    """Correlates CVEs and log events with MITRE ATT&CK techniques.

    Parameters
    ----------
    attack_df:
        ATT&CK techniques DataFrame (from ``ATTACKClient.techniques_to_dataframe``).
        Must contain columns: ``id``, ``name``, ``description``, ``tactics``.
    log_events:
        List of log event dicts (from ``LogSimulator.generate_scenario`` or DB).
    """

    def __init__(
        self, attack_df: pd.DataFrame, log_events: list[dict[str, Any]]
    ) -> None:
        self.attack_df = attack_df
        self.log_events = log_events
        logger.info(
            "ThreatCorrelator: %d ATT&CK techniques, %d log events",
            len(attack_df),
            len(log_events),
        )

    # ------------------------------------------------------------------
    # CVE → Techniques
    # ------------------------------------------------------------------

    def map_cve_to_techniques(
        self, cve_id: str, affected_products: str
    ) -> list[dict[str, Any]]:
        """Find ATT&CK techniques likely applicable to a CVE.

        Uses two-pass keyword matching:

        1. Product/vendor keywords from ``affected_products`` against the
           curated ``_TECHNIQUE_KEYWORDS`` hint table.
        2. Fallback: keyword scan of ATT&CK technique *descriptions* for terms
           present in the CVE's affected products string.

        Parameters
        ----------
        cve_id:
            CVE identifier (used only for logging).
        affected_products:
            Semicolon-separated CPE / product names from the NVD record.

        Returns
        -------
        list[dict]
            List of matched technique dicts: ``{id, name, description, tactics}``.
        """
        products_lower = affected_products.lower()
        matched_ids: set[str] = set()

        # Pass 1 — curated keyword hints
        for tech_id, keywords in _TECHNIQUE_KEYWORDS.items():
            if any(kw in products_lower for kw in keywords):
                matched_ids.add(tech_id)

        # Pass 2 — full-text scan of ATT&CK descriptions
        if not self.attack_df.empty:
            product_tokens = {
                tok.strip()
                for tok in products_lower.replace(";", " ").split()
                if len(tok.strip()) > 3
            }
            for _, row in self.attack_df.iterrows():
                desc_lower = str(row.get("description", "")).lower()
                if any(tok in desc_lower for tok in product_tokens):
                    matched_ids.add(str(row["id"]))

        # Resolve IDs to full technique dicts
        results: list[dict[str, Any]] = []
        for tech_id in matched_ids:
            match = self.attack_df[self.attack_df["id"] == tech_id]
            if not match.empty:
                r = match.iloc[0]
                results.append(
                    {
                        "id": r["id"],
                        "name": r.get("name", ""),
                        "description": str(r.get("description", ""))[:500],
                        "tactics": r.get("tactics", ""),
                    }
                )
            else:
                # Technique exists in hint table but not in loaded ATT&CK dump
                results.append({"id": tech_id, "name": "", "description": "", "tactics": ""})

        logger.info(
            "ThreatCorrelator: CVE %s → %d matched techniques", cve_id, len(results)
        )
        return results

    # ------------------------------------------------------------------
    # Technique → Logs
    # ------------------------------------------------------------------

    def map_logs_to_technique(self, technique_id: str) -> list[dict[str, Any]]:
        """Return log events whose ``technique_id`` field matches *technique_id*.

        Parameters
        ----------
        technique_id:
            ATT&CK technique ID, e.g. ``"T1190"``.

        Returns
        -------
        list[dict]
            Matching log event dicts.
        """
        matches = [
            ev for ev in self.log_events if ev.get("technique_id") == technique_id
        ]
        logger.debug(
            "ThreatCorrelator: technique %s → %d matching log events",
            technique_id,
            len(matches),
        )
        return matches

    # ------------------------------------------------------------------
    # Investigation scenario builder
    # ------------------------------------------------------------------

    def build_investigation_scenario(
        self, cve_id: str, asset: dict[str, Any]
    ) -> dict[str, Any]:
        """Assemble a full investigation scenario for a CVE on a given asset.

        Combines:
        - CVE metadata from the asset context
        - Matched ATT&CK techniques
        - Relevant log events (non-noise, then noise if present)
        - A human-readable evidence summary

        Parameters
        ----------
        cve_id:
            CVE identifier.
        asset:
            Asset dict from ``AssetInventory``.

        Returns
        -------
        dict
            Keys: ``cve_id``, ``asset``, ``matched_techniques``,
            ``relevant_logs``, ``evidence_summary``.
        """
        affected_products = " ".join(asset.get("software", []))
        matched_techniques = self.map_cve_to_techniques(cve_id, affected_products)

        relevant_logs: list[dict[str, Any]] = []
        for tech in matched_techniques:
            logs = self.map_logs_to_technique(tech["id"])
            relevant_logs.extend(logs)

        # Deduplicate by event_id
        seen: set[str] = set()
        deduped_logs: list[dict[str, Any]] = []
        for ev in relevant_logs:
            eid = ev.get("event_id", "")
            if eid not in seen:
                seen.add(eid)
                deduped_logs.append(ev)

        # Build a plain-text evidence summary
        tech_names = ", ".join(t["name"] or t["id"] for t in matched_techniques) or "none"
        log_count = len([ev for ev in deduped_logs if not ev.get("is_noise", False)])
        noise_count = len(deduped_logs) - log_count

        evidence_summary = (
            f"CVE {cve_id} is relevant to asset '{asset.get('hostname', '')}' "
            f"({asset.get('asset_id', '')}) running {', '.join(asset.get('software', [])[:2])}. "
            f"Correlated techniques: {tech_names}. "
            f"Log events found: {log_count} signal event(s), {noise_count} noise event(s)."
        )

        scenario: dict[str, Any] = {
            "cve_id": cve_id,
            "asset": asset,
            "matched_techniques": matched_techniques,
            "relevant_logs": deduped_logs,
            "evidence_summary": evidence_summary,
        }
        logger.info(
            "ThreatCorrelator: scenario built for %s / %s — %d techniques, %d logs",
            cve_id,
            asset.get("asset_id", ""),
            len(matched_techniques),
            len(deduped_logs),
        )
        return scenario
