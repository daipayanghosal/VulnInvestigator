"""
scripts/pull_real_world_data.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Fetches and merges extensive real-world cybersecurity intelligence from:
1. NIST National Vulnerability Database (NVD) REST API (multiple enterprise technologies: OpenSSL, PostgreSQL, Fortinet, Kerberos, Apache)
2. CISA Known Exploited Vulnerabilities (KEV) catalogue (all 1,768+ entries)
3. MITRE ATT&CK Enterprise Matrix (855 techniques)
4. Correlates with the 12-asset simulated enterprise inventory
5. Synthesizes controlled SIEM security log scenarios for investigation
6. Updates SQLite database and evaluation metrics

Usage:
    python scripts/pull_real_world_data.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Project root on path
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from src.pipeline.nvd_client import NVDClient
from src.pipeline.kev_client import KEVClient
from src.pipeline.attack_client import ATTACKClient
from src.pipeline.normaliser import DataNormaliser
from src.pipeline.database import Database
from src.assets.inventory import AssetInventory
from src.scoring.contextual import ContextualRiskScorer
from src.scoring.baseline import CVSSBaselineScorer
from src.logs.simulator import LogSimulator
from src.evaluation.ranking_metrics import kendall_tau, rank_displacement, ndcg

load_dotenv()

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("pull_real_world_data")


def load_config() -> tuple[dict[str, Any], dict[str, Any]]:
    settings_path = _PROJECT_ROOT / "config" / "settings.yaml"
    scoring_path = _PROJECT_ROOT / "config" / "scoring.yaml"
    with settings_path.open() as fh:
        settings = yaml.safe_load(fh)
    with scoring_path.open() as fh:
        scoring = yaml.safe_load(fh)
    return settings, scoring


def main() -> None:
    console.rule("[bold cyan]VulnInvestigator — Real-World Intelligence Ingestion[/bold cyan]")

    settings, scoring = load_config()
    raw_dir = _PROJECT_ROOT / "data" / "raw"
    processed_dir = _PROJECT_ROOT / "data" / "processed"
    logs_dir = _PROJECT_ROOT / "data" / "logs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    db_path = processed_dir / "vulninvestigator.db"
    assets_file = _PROJECT_ROOT / "data" / "assets" / "asset_inventory.json"

    # -----------------------------------------------------------------------
    # 1. Load or fetch KEV & ATT&CK
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 1 — Loading CISA KEV and MITRE ATT&CK…[/bold]")
    kev_path = raw_dir / "kev_raw.json"
    if kev_path.exists():
        with kev_path.open(encoding="utf-8") as fh:
            raw_kev = json.load(fh)
        console.print(f"  [green]✓ Loaded {len(raw_kev)} CISA KEV entries from cache[/green]")
    else:
        kev_client = KEVClient()
        raw_kev = kev_client.fetch()
        kev_client.save_raw(raw_kev, str(kev_path))
        console.print(f"  [green]✓ Downloaded {len(raw_kev)} CISA KEV entries[/green]")

    attack_path = raw_dir / "attack_raw.json"
    attack_client = ATTACKClient()
    if attack_path.exists():
        with attack_path.open(encoding="utf-8") as fh:
            attack_bundle = json.load(fh)
    else:
        attack_bundle = attack_client.fetch()
        attack_client.save_raw(attack_bundle, str(attack_path))
    techniques = attack_client.extract_techniques(attack_bundle)
    console.print(f"  [green]✓ Loaded {len(techniques)} MITRE ATT&CK techniques[/green]")

    # -----------------------------------------------------------------------
    # 2. Ingest NVD CVEs across multiple technologies
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 2 — Ingesting Real-World NVD CVEs…[/bold]")
    nvd_client = NVDClient(delay=1.0)
    existing_cves: dict[str, dict] = {}

    # Load existing Apache CVEs if present
    nvd_raw_path = raw_dir / "nvd_raw.json"
    if nvd_raw_path.exists():
        with nvd_raw_path.open(encoding="utf-8") as fh:
            cached_nvd = json.load(fh)
        for c in cached_nvd:
            cve_id = c.get("cve", {}).get("id")
            if cve_id:
                existing_cves[cve_id] = c
        console.print(f"  [green]✓ Loaded {len(existing_cves)} existing CVEs from disk[/green]")

    # Target technologies matching organizational assets
    target_keywords = ["OpenSSL", "PostgreSQL", "Fortinet", "Kerberos"]
    for kw in target_keywords:
        console.print(f"  Fetching NVD records for: [bold yellow]{kw}[/bold yellow]…")
        try:
            kw_cves = nvd_client.fetch_cves(keyword=kw, results_per_page=1000)
            added = 0
            for c in kw_cves:
                cve_id = c.get("cve", {}).get("id")
                if cve_id and cve_id not in existing_cves:
                    existing_cves[cve_id] = c
                    added += 1
            console.print(f"    ✓ Fetched {len(kw_cves)} CVEs ({added} new unique)")
        except Exception as exc:
            console.print(f"    [red]⚠ Warning: fetch for {kw} failed: {exc}[/red]")

    all_raw_cves = list(existing_cves.values())
    nvd_client.save_raw(all_raw_cves, str(nvd_raw_path))
    console.print(f"  [bold green]✓ Total unique NVD CVE pool: {len(all_raw_cves)}[/bold green]")

    # -----------------------------------------------------------------------
    # 3. Normalise and Merge
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 3 — Normalising and Merging Datasets…[/bold]")
    normaliser = DataNormaliser()
    nvd_df = normaliser.normalise_nvd(all_raw_cves)
    kev_df = normaliser.normalise_kev(raw_kev)
    merged_df = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)

    # Enrich: Ensure all 1,768 CISA KEV entries are represented in the dataset
    existing_cve_ids = set(merged_df["cve_id"].str.upper())
    kev_records_to_add = []
    for entry in raw_kev:
        cve_id = entry.get("cveID", "").upper()
        if cve_id and cve_id not in existing_cve_ids:
            kev_records_to_add.append({
                "cve_id": cve_id,
                "description": entry.get("shortDescription", "Actively exploited vulnerability listed in CISA KEV catalogue."),
                "cvss_v3_score": 8.8,  # Default high severity for known exploited flaws
                "cvss_v3_severity": "HIGH",
                "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "published_date": entry.get("dateAdded"),
                "last_modified": entry.get("dateAdded"),
                "affected_products": f"{entry.get('vendorProject', '')} {entry.get('product', '')}".strip(),
                "references": entry.get("requiredAction", ""),
                "vendor_project": entry.get("vendorProject", ""),
                "product": entry.get("product", ""),
                "vulnerability_name": entry.get("vulnerabilityName", ""),
                "date_added": entry.get("dateAdded"),
                "short_description": entry.get("shortDescription", ""),
                "required_action": entry.get("requiredAction", ""),
                "due_date": entry.get("dueDate", ""),
                "in_kev": True,
            })

    if kev_records_to_add:
        kev_additional_df = pd.DataFrame(kev_records_to_add)
        merged_df = pd.concat([merged_df, kev_additional_df], ignore_index=True)
        console.print(f"  [green]✓ Ingested {len(kev_records_to_add)} additional KEV entries from CISA catalogue[/green]")

    console.print(
        f"  [bold green]✓ Merged Dataset: {len(merged_df)} total vulnerabilities, "
        f"{merged_df['in_kev'].sum()} verified in CISA KEV[/bold green]"
    )

    # -----------------------------------------------------------------------
    # 4. Asset Contextual Scoring
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 4 — Applying Contextual Risk Scoring…[/bold]")
    inventory = AssetInventory()
    assets = inventory.load(str(assets_file)) if assets_file.exists() else []

    scorer = ContextualRiskScorer(
        weights_config=scoring.get("weights"),
        asset_config=scoring.get("asset_criticality"),
        exposure_config=scoring.get("exposure"),
        bands_config=scoring.get("bands"),
    )
    scored_df = scorer.score_dataframe(merged_df, assets)
    console.print(f"  [green]✓ Scored {len(scored_df)} vulnerabilities against {len(assets)} enterprise assets[/green]")

    # -----------------------------------------------------------------------
    # 5. Synthesize Security Log Scenarios for Threat Hunting
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 5 — Generating Security Log Scenarios for Threat Hunting…[/bold]")
    simulator = LogSimulator(seed=42)
    top_critical_vulns = scored_df[scored_df["risk_band"] == "Critical"].head(10)
    all_simulated_logs: list[dict[str, Any]] = []

    technique_map = {
        "apache": "T1190",
        "openssl": "T1190",
        "vpn": "T1078",
        "fortinet": "T1190",
        "kerberos": "T1078",
        "active directory": "T1078",
        "bash": "T1059",
    }

    for _, row in top_critical_vulns.iterrows():
        cve_id = row["cve_id"]
        asset_id = str(row.get("matched_asset_id", "SRV-WEB-001"))
        prod_desc = (str(row.get("affected_products", "")) + " " + str(row.get("description", ""))).lower()
        tech = "T1190"
        for k, v in technique_map.items():
            if k in prod_desc:
                tech = v
                break
        events = simulator.generate_scenario(technique_id=tech, asset_id=asset_id, n_events=6, inject_noise=True)
        for ev in events:
            ev["cve_id"] = cve_id
            all_simulated_logs.append(ev)

    logs_file = logs_dir / "security_logs.jsonl"
    with logs_file.open("w", encoding="utf-8") as fh:
        for ev in all_simulated_logs:
            fh.write(json.dumps(ev, default=str) + "\n")
    console.print(f"  [green]✓ Generated {len(all_simulated_logs)} security log events across top CVEs → {logs_file}[/green]")

    # -----------------------------------------------------------------------
    # 6. Database Upsert
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 6 — Persisting to SQLite Database…[/bold]")
    with Database(str(db_path)) as db:
        n_vulns = db.upsert_vulnerabilities(scored_df)
        n_assets = db.upsert_assets(assets)
        n_logs = db.upsert_log_events(all_simulated_logs)
    console.print(f"  [bold green]✓ DB Updated: {n_vulns} vulns, {n_assets} assets, {n_logs} log events → {db_path}[/bold green]")

    # -----------------------------------------------------------------------
    # 7. Re-run Evaluation Metrics
    # -----------------------------------------------------------------------
    console.print("\n[bold]Step 7 — Computing Baseline vs Contextual Evaluation…[/bold]")
    baseline_scorer = CVSSBaselineScorer()
    ranked_baseline = baseline_scorer.score(scored_df)

    cvss_order = ranked_baseline["cve_id"].tolist()
    context_order = scored_df.sort_values("risk_score", ascending=False)["cve_id"].tolist()

    tau = kendall_tau(cvss_order, context_order)
    relevance = dict(zip(scored_df["cve_id"], scored_df["risk_score"]))
    ndcg_score = ndcg(cvss_order, relevance, k=10)
    disp_df = rank_displacement(cvss_order, context_order)

    eval_results = {
        "total_cves": len(scored_df),
        "total_in_kev": int(scored_df["in_kev"].sum()),
        "kendall_tau": round(tau, 4),
        "ndcg_at_10": round(ndcg_score, 4),
        "cvss_top_5": cvss_order[:5],
        "contextual_top_5": context_order[:5],
        "top_displacement": disp_df.head(15).to_dict(orient="records"),
    }

    eval_path = processed_dir / "evaluation_results.json"
    with eval_path.open("w", encoding="utf-8") as fh:
        json.dump(eval_results, fh, indent=2)

    console.rule("[bold green]Intelligence Update Complete[/bold green]")
    table = Table(title="Vulnerability Summary by Risk Band", header_style="bold magenta")
    table.add_column("Risk Band", style="cyan")
    table.add_column("Total Count", justify="right")
    table.add_column("In CISA KEV (Active Exploitation)", justify="right")
    table.add_column("Top CVSS", justify="right")

    for band in ["Critical", "High", "Medium", "Low"]:
        sub = scored_df[scored_df["risk_band"] == band]
        in_kev_cnt = sub["in_kev"].sum() if not sub.empty else 0
        top_c = sub["cvss_v3_score"].max() if not sub.empty else 0.0
        table.add_row(band, str(len(sub)), str(in_kev_cnt), f"{top_c:.1f}")

    console.print(table)
    console.print(f"\n[bold]Kendall's Rank Correlation (τ):[/bold] [green]{tau:.4f}[/green]")
    console.print(f"[bold]nDCG@10 (Baseline vs Contextual):[/bold] [green]{ndcg_score:.4f}[/green]")
    console.print(f"\n[green]✓ Evaluation saved → {eval_path}[/green]")


if __name__ == "__main__":
    main()
