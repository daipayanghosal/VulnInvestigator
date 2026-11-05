# Data Dictionary — VulnInvestigator

This document defines the schemas for all primary data structures used in the VulnInvestigator pipeline.

---

## 1. `vulnerabilities` Table (SQLite)

Stored in `data/processed/vulninvestigator.db`.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `cve_id` | TEXT (PK) | No | CVE identifier, e.g. `CVE-2024-12345` |
| `cvss_score` | REAL | Yes | CVSS v3 base score (0.0 – 10.0); NULL if no CVSS v3 |
| `cvss_severity` | TEXT | Yes | Severity label: `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `NONE` |
| `cvss_vector` | TEXT | Yes | CVSS v3 vector string, e.g. `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/…` |
| `in_kev` | INTEGER | No | 1 if listed in CISA KEV catalogue, 0 otherwise |
| `published_date` | TEXT | Yes | ISO 8601 publication date from NVD |
| `last_modified` | TEXT | Yes | ISO 8601 last-modified date from NVD |
| `description` | TEXT | Yes | English description from NVD |
| `affected_products` | TEXT | Yes | Semicolon-separated CPE match criteria strings |
| `references_` | TEXT | Yes | Semicolon-separated reference URLs |
| `vendor_project` | TEXT | Yes | Vendor/project (from KEV); NULL if not in KEV |
| `product` | TEXT | Yes | Product name (from KEV); NULL if not in KEV |
| `vulnerability_name` | TEXT | Yes | Descriptive name (from KEV); NULL if not in KEV |
| `date_added_kev` | TEXT | Yes | Date added to KEV (ISO 8601); NULL if not in KEV |
| `risk_score` | REAL | Yes | Contextual risk score (0.0 – 1.0); NULL until scored |
| `risk_band` | TEXT | Yes | `Critical` / `High` / `Medium` / `Low`; NULL until scored |
| `matched_asset_id` | TEXT | Yes | Asset ID matched during contextual scoring; empty string if none |

---

## 2. `assets` Table / `asset_inventory.json`

Stored in `data/assets/asset_inventory.json` and mirrored in SQLite `assets` table.

### JSON Structure

```json
{
  "organisation": "string",
  "last_updated": "YYYY-MM-DD",
  "assets": [ <asset_object>, ... ]
}
```

### Asset Object

| Field | Type | Description |
|---|---|---|
| `asset_id` | string | Unique identifier, e.g. `SRV-WEB-001` |
| `hostname` | string | DNS hostname of the asset |
| `ip` | string | Primary IP address |
| `type` | string | `server` / `workstation` / `laptop` / `industrial-controller` |
| `os` | string | Operating system and version |
| `software` | array[string] | Installed software with versions, e.g. `["Apache HTTP Server 2.4.58"]` |
| `criticality` | string | `critical` / `high` / `medium` / `low` |
| `exposure` | string | `internet_facing` / `dmz` / `internal` / `restricted` / `air_gapped` |
| `owner` | string | Owning team or department |
| `tags` | array[string] | Descriptive tags for filtering |
| `notes` | string | Free-text notes |

---

## 3. Log Events (JSONL)

Stored in `data/logs/*.jsonl`. One JSON object per line.

| Field | Type | Description |
|---|---|---|
| `event_id` | string (UUID4) | Unique event identifier |
| `timestamp` | string (ISO 8601) | Event timestamp with timezone |
| `asset_id` | string | Asset identifier from inventory |
| `source_ip` | string | Source IP address of event originator |
| `event_type` | string | High-level event category (e.g. `web_exploit_attempt`) |
| `technique_id` | string | ATT&CK technique ID (e.g. `T1190`), or `""` for noise |
| `description` | string | Human-readable event description |
| `raw_log` | string | Simulated raw log line in key=value format |
| `is_noise` | boolean | `true` if the event is unrelated background noise |

---

## 4. ATT&CK Techniques DataFrame

Produced by `ATTACKClient.techniques_to_dataframe()`.

| Column | Type | Description |
|---|---|---|
| `id` | string | ATT&CK technique ID, e.g. `T1190` |
| `name` | string | Technique name |
| `description` | string | Full STIX description (may be very long) |
| `url` | string | ATT&CK website URL |
| `tactics` | string | Pipe-separated tactic phase names, e.g. `initial-access\|execution` |
| `is_subtechnique` | boolean | True for sub-techniques (e.g. T1059.001) |

---

## 5. Investigation Scenario Dict

Produced by `ThreatCorrelator.build_investigation_scenario()`.

```python
{
    "cve_id": "CVE-2024-12345",          # str: CVE identifier
    "asset": {                            # dict: full asset object from inventory
        "asset_id": "SRV-WEB-001",
        "hostname": "web-proxy-01",
        # ... all asset fields
    },
    "matched_techniques": [               # list[dict]: correlated ATT&CK techniques
        {
            "id": "T1190",
            "name": "Exploit Public-Facing Application",
            "description": "...",
            "tactics": "initial-access",
        }
    ],
    "relevant_logs": [                    # list[dict]: matching log event dicts
        {
            "event_id": "...",
            "technique_id": "T1190",
            "is_noise": False,
            # ... all log event fields
        }
    ],
    "evidence_summary": "str: plain-text summary of the scenario"
}
```

---

## 6. GenAI Output Dict

Produced by `OutputValidator.validate()`.

```python
{
    "validated_text": "str: full LLM response text",
    "citations_found": ["CVE-2024-12345", "T1190", "9.8"],  # list[str]
    "unsupported_claims": [                                   # list[str]
        "sentence that could not be linked to evidence"
    ],
    "confidence_score": 0.823,   # float in [0.0, 1.0]
    "warnings": [                # list[str]: human-readable validation notes
        "Hedged language detected in 2 passage(s).",
        "Model self-flagged 1 unsupported claim(s) with [UNSUPPORTED]."
    ]
}
```

---

## 7. Evaluation Results JSON

Saved to `data/processed/evaluation_results.json` by `scripts/run_evaluation.py`.

```python
{
    "kendall_tau": 0.712,              # float: agreement between CVSS and contextual rankings
    "ndcg_at_10": 0.834,              # float: nDCG@10 of CVSS ranking vs contextual relevance
    "ndcg_at_20": 0.819,              # float: nDCG@20
    "rank_displacement": [            # list[dict]: per-CVE rank change
        {"item": "CVE-2024-X", "rank_a": 1, "rank_b": 5, "displacement": -4}
    ],
    "total_cves": 1248,
    "grounding_metrics": {
        "total_responses": 50,
        "evidence_citation_rate": 0.84,
        "claim_support_rate": 0.76,
        "hallucination_rate": 0.08,
        "mean_confidence_score": 0.731,
        "responses_with_warnings": 12
    }
}
```
