"""
scripts/run_evaluation.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Entry-point script for the VulnInvestigator evaluation pipeline.

Steps
-----
1. Load vulnerability data from SQLite database
2. Run CVSS baseline scorer
3. Run contextual risk scorer (reload from DB)
4. Compute Kendall's τ and rank displacement
5. Print Rich comparison table
6. Save results to data/processed/evaluation_results.json

Usage
-----
    python scripts/run_evaluation.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root on path
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pandas as pd
import yaml  # type: ignore
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------
from src.pipeline.database import Database
from src.scoring.baseline import CVSSBaselineScorer
from src.scoring.contextual import ContextualRiskScorer
from src.evaluation.ranking_metrics import kendall_tau, rank_displacement, ndcg
from src.evaluation.grounding_metrics import generate_evaluation_report
from src.evaluation.pipeline_runner import run_evaluation_pipeline

load_dotenv()

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("run_evaluation")


def load_config(settings_path: Path, scoring_path: Path) -> tuple[dict, dict]:
    with settings_path.open() as fh:
        settings = yaml.safe_load(fh)
    with scoring_path.open() as fh:
        scoring = yaml.safe_load(fh)
    return settings, scoring


def main() -> None:
    """Run the evaluation pipeline and save results."""
    console.rule("[bold blue]VulnInvestigator Evaluation[/bold blue]")

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------
    settings_path = _PROJECT_ROOT / "config" / "settings.yaml"
    scoring_path = _PROJECT_ROOT / "config" / "scoring.yaml"
    settings, scoring = load_config(settings_path, scoring_path)
    db_path = _PROJECT_ROOT / settings["data"]["db_path"]
    output_path = _PROJECT_ROOT / "data" / "processed" / "evaluation_results.json"

    # ------------------------------------------------------------------
    # 1. Load vulnerability data from DB
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 1/4 — Loading vulnerability data from DB…[/bold]")
    if not db_path.exists():
        console.print(
            f"[red]Database not found: {db_path}\n"
            "Run 'python scripts/run_pipeline.py' first.[/red]"
        )
        sys.exit(1)

    with Database(str(db_path)) as db:
        rows = db.query(
            "SELECT cve_id, cvss_score, cvss_severity, in_kev, risk_score, risk_band "
            "FROM vulnerabilities ORDER BY cve_id"
        )

    if not rows:
        console.print("[yellow]No vulnerability rows found in DB. Run the pipeline first.[/yellow]")
        sys.exit(0)

    df = pd.DataFrame(rows)
    df = df.rename(columns={"cvss_score": "cvss_v3_score", "cvss_severity": "cvss_v3_severity"})
    console.print(f"  [green]✓ Loaded {len(df)} CVEs from database[/green]")

    # ------------------------------------------------------------------
    # 2. CVSS baseline scoring
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 2/4 — CVSS baseline ranking…[/bold]")
    baseline_scorer = CVSSBaselineScorer()
    baseline_df = baseline_scorer.score(df)
    ranking_cvss: list[str] = baseline_df["cve_id"].tolist()
    console.print(f"  [green]✓ CVSS top-5: {ranking_cvss[:5]}[/green]")

    # ------------------------------------------------------------------
    # 3. Contextual ranking (from DB risk_score)
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 3/4 — Contextual risk ranking…[/bold]")
    if "risk_score" in df.columns and df["risk_score"].notna().any():
        contextual_df = df.sort_values("risk_score", ascending=False, na_position="last").reset_index(drop=True)
        ranking_contextual: list[str] = contextual_df["cve_id"].tolist()
        console.print(f"  [green]✓ Contextual top-5: {ranking_contextual[:5]}[/green]")
    else:
        console.print("  [yellow]No contextual scores in DB — re-scoring now…[/yellow]")
        scorer = ContextualRiskScorer(
            weights_config=scoring.get("weights"),
            asset_config=scoring.get("asset_criticality"),
            exposure_config=scoring.get("exposure"),
            bands_config=scoring.get("bands"),
        )
        scored = scorer.score_dataframe(df, [])
        ranking_contextual = scored["cve_id"].tolist()

    # ------------------------------------------------------------------
    # 4. Metrics
    # ------------------------------------------------------------------
    console.print("\n[bold]Step 4/4 — Computing evaluation metrics…[/bold]")

    tau = kendall_tau(ranking_cvss, ranking_contextual)
    disp_df = rank_displacement(ranking_cvss, ranking_contextual)

    # nDCG: use risk_score as ground-truth relevance if available
    if "risk_score" in df.columns:
        relevance = dict(zip(df["cve_id"].tolist(), df["risk_score"].fillna(0).tolist()))
        ndcg_at_10 = ndcg(ranking_cvss, relevance, k=10)
        ndcg_at_20 = ndcg(ranking_cvss, relevance, k=20)
    else:
        ndcg_at_10 = ndcg_at_20 = None

    console.print(f"  Kendall's τ: [bold]{tau:.4f}[/bold]")
    if ndcg_at_10 is not None:
        console.print(f"  nDCG@10 (CVSS vs contextual relevance): [bold]{ndcg_at_10:.4f}[/bold]")

    # ------------------------------------------------------------------
    # Rich comparison table
    # ------------------------------------------------------------------
    table = Table(title="Top-20 Rank Displacement (CVSS vs Contextual)", show_header=True)
    table.add_column("CVE ID")
    table.add_column("CVSS Rank", justify="right")
    table.add_column("Contextual Rank", justify="right")
    table.add_column("Displacement", justify="right")

    for _, row in disp_df.head(20).iterrows():
        disp = int(row["displacement"])
        colour = "green" if disp > 0 else "red" if disp < 0 else "white"
        table.add_row(
            str(row["item"]),
            str(int(row["rank_a"])),
            str(int(row["rank_b"])),
            f"[{colour}]{disp:+d}[/{colour}]",
        )

    console.print(table)

    # ------------------------------------------------------------------
    # Save results (using unified pipeline runner for complete metrics)
    # ------------------------------------------------------------------
    console.print("\n[bold]Finalizing grounding benchmarks & stress tests…[/bold]")
    results = run_evaluation_pipeline(vuln_df=df, db_path=db_path, output_path=output_path)

    console.print(f"\n[green]✓ Evaluation results saved → {output_path}[/green]")
    console.rule("[bold green]Evaluation Complete[/bold green]")


if __name__ == "__main__":
    main()
