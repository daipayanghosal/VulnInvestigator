"""
scripts/run_pipeline.py
~~~~~~~~~~~~~~~~~~~~~~~
Entry-point script for the VulnInvestigator data pipeline.

Steps
-----
1. Load configuration (config/settings.yaml + .env)
2. Fetch NVD CVEs (recent 90 days)
3. Fetch CISA KEV catalogue
4. Fetch MITRE ATT&CK enterprise bundle
5. Normalise and merge vulnerability datasets
6. Load asset inventory
7. Apply contextual risk scoring
8. Persist to SQLite database
9. Print summary statistics via Rich

Usage
-----
    python scripts/run_pipeline.py

    # Fetch a specific keyword instead of recent CVEs:
    python scripts/run_pipeline.py --keyword "Apache" --days 30
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure project root on path
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Third-party imports (must be installed)
# ---------------------------------------------------------------------------
import yaml  # type: ignore
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from src.pipeline.nvd_client import NVDClient
from src.pipeline.kev_client import KEVClient
from src.pipeline.attack_client import ATTACKClient
from src.pipeline.normaliser import DataNormaliser
from src.pipeline.database import Database
from src.assets.inventory import AssetInventory
from src.scoring.contextual import ContextualRiskScorer

load_dotenv()

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("run_pipeline")


def load_config(settings_path: Path, scoring_path: Path) -> tuple[dict, dict]:
    """Load settings.yaml and scoring.yaml."""
    with settings_path.open() as fh:
        settings = yaml.safe_load(fh)
    with scoring_path.open() as fh:
        scoring = yaml.safe_load(fh)
    return settings, scoring


def main(keyword: str | None = None, days: int = 90) -> None:
    """Run the full VulnInvestigator data pipeline."""
    console.rule("[bold blue]VulnInvestigator Pipeline[/bold blue]")

    # ------------------------------------------------------------------
    # 1. Config
    # ------------------------------------------------------------------
    settings_path = _PROJECT_ROOT / "config" / "settings.yaml"
    scoring_path = _PROJECT_ROOT / "config" / "scoring.yaml"

    if not settings_path.exists():
        console.print(f"[red]Config not found: {settings_path}[/red]")
        sys.exit(1)

    settings, scoring = load_config(settings_path, scoring_path)
    pipeline_cfg = settings.get("pipeline", {})
    data_cfg = settings.get("data", {})
    llm_cfg = settings.get("llm", {})

    raw_dir = _PROJECT_ROOT / data_cfg.get("raw_dir", "data/raw")
    db_path = _PROJECT_ROOT / data_cfg.get("db_path", "data/processed/vulninvestigator.db")
    assets_file = _PROJECT_ROOT / data_cfg.get("assets_file", "data/assets/asset_inventory.json")
    raw_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]✓ Config loaded[/green] | DB: {db_path}")

    # ------------------------------------------------------------------
    # 2. Fetch NVD
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 1/6 — Fetching NVD CVEs…[/bold]")
    nvd_client = NVDClient(
        delay=pipeline_cfg.get("request_delay_seconds", 6),
        base_url=pipeline_cfg.get("nvd_base_url", NVDClient._DEFAULT_BASE_URL),
    )

    if keyword:
        console.print(f"  Keyword search: '{keyword}'")
        raw_cves = nvd_client.fetch_cves(keyword=keyword)
    else:
        console.print(f"  Fetching last {days} days of CVEs…")
        raw_cves = nvd_client.fetch_all_recent(days_back=days)

    nvd_raw_path = raw_dir / "nvd_raw.json"
    nvd_client.save_raw(raw_cves, str(nvd_raw_path))
    console.print(f"  [green]✓ {len(raw_cves)} CVEs fetched → {nvd_raw_path}[/green]")

    # ------------------------------------------------------------------
    # 3. Fetch KEV
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 2/6 — Fetching CISA KEV catalogue…[/bold]")
    kev_client = KEVClient(url=pipeline_cfg.get("kev_url", KEVClient.__init__.__defaults__[0] if hasattr(KEVClient.__init__, '__defaults__') and KEVClient.__init__.__defaults__ else ""))  # type: ignore
    # Fallback to default
    kev_client = KEVClient()
    raw_kev = kev_client.fetch()
    kev_raw_path = raw_dir / "kev_raw.json"
    kev_client.save_raw(raw_kev, str(kev_raw_path))
    console.print(f"  [green]✓ {len(raw_kev)} KEV entries → {kev_raw_path}[/green]")

    # ------------------------------------------------------------------
    # 4. Fetch ATT&CK
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 3/6 — Fetching MITRE ATT&CK bundle…[/bold]")
    attack_client = ATTACKClient(url=pipeline_cfg.get("attack_url", ATTACKClient.__init__.__defaults__[0] if hasattr(ATTACKClient.__init__, '__defaults__') and ATTACKClient.__init__.__defaults__ else ""))  # type: ignore
    attack_client = ATTACKClient()
    attack_bundle = attack_client.fetch()
    attack_raw_path = raw_dir / "attack_raw.json"
    attack_client.save_raw(attack_bundle, str(attack_raw_path))
    techniques = attack_client.extract_techniques(attack_bundle)
    console.print(f"  [green]✓ {len(techniques)} ATT&CK techniques extracted[/green]")

    # ------------------------------------------------------------------
    # 5. Normalise and merge
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 4/6 — Normalising and merging datasets…[/bold]")
    normaliser = DataNormaliser()
    nvd_df = normaliser.normalise_nvd(raw_cves)
    kev_df = normaliser.normalise_kev(raw_kev)
    merged_df = normaliser.merge_vulnerability_dataset(nvd_df, kev_df)
    console.print(
        f"  [green]✓ Merged dataset: {len(merged_df)} CVEs, "
        f"{merged_df['in_kev'].sum()} in KEV[/green]"
    )

    # ------------------------------------------------------------------
    # 6. Asset inventory
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 5/6 — Loading asset inventory…[/bold]")
    inventory = AssetInventory()
    if assets_file.exists():
        assets = inventory.load(str(assets_file))
        console.print(f"  [green]✓ {len(assets)} assets loaded[/green]")
    else:
        assets = []
        console.print(f"  [yellow]⚠ Asset file not found: {assets_file}[/yellow]")

    # ------------------------------------------------------------------
    # 7. Contextual scoring
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 6/6 — Applying contextual risk scoring…[/bold]")
    scorer = ContextualRiskScorer(
        weights_config=scoring.get("weights"),
        asset_config=scoring.get("asset_criticality"),
        exposure_config=scoring.get("exposure"),
        bands_config=scoring.get("bands"),
    )
    scored_df = scorer.score_dataframe(merged_df, assets)
    console.print(f"  [green]✓ Scoring complete[/green]")

    # ------------------------------------------------------------------
    # 8. Persist to DB
    # ------------------------------------------------------------------
    console.print("\n[bold]Persisting to database…[/bold]")
    with Database(str(db_path)) as db:
        n_vulns = db.upsert_vulnerabilities(scored_df)
        n_assets = db.upsert_assets(assets)
    console.print(f"  [green]✓ {n_vulns} vulnerabilities, {n_assets} assets saved → {db_path}[/green]")

    # ------------------------------------------------------------------
    # 9. Summary
    # ------------------------------------------------------------------
    console.rule("[bold green]Pipeline Complete[/bold green]")

    table = Table(title="Vulnerability Summary by Risk Band", show_header=True)
    table.add_column("Risk Band", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("In KEV", justify="right")
    table.add_column("Top CVSS", justify="right")

    if "risk_band" in scored_df.columns:
        for band in ["Critical", "High", "Medium", "Low"]:
            band_df = scored_df[scored_df["risk_band"] == band]
            in_kev_count = int(band_df["in_kev"].sum()) if "in_kev" in band_df.columns else 0
            top_cvss = f"{band_df['cvss_v3_score'].max():.1f}" if not band_df.empty else "—"
            table.add_row(band, str(len(band_df)), str(in_kev_count), top_cvss)

    console.print(table)
    console.print(f"\n[dim]Raw data → {raw_dir}[/dim]")
    console.print(f"[dim]Database → {db_path}[/dim]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the VulnInvestigator data pipeline.")
    parser.add_argument("--keyword", default=None, help="Keyword search instead of date-range fetch")
    parser.add_argument("--days", type=int, default=90, help="Days back for recent CVE fetch (default: 90)")
    args = parser.parse_args()
    main(keyword=args.keyword, days=args.days)
