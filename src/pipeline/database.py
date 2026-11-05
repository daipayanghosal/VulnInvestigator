"""
src/pipeline/database.py
~~~~~~~~~~~~~~~~~~~~~~~~
SQLite persistence layer for VulnInvestigator.

Uses Python's built-in ``sqlite3`` module — no ORM dependency.
All writes use INSERT OR REPLACE (upsert) semantics so the pipeline
is safely re-runnable without duplicating rows.

Schema overview
---------------
- vulnerabilities  : one row per CVE with CVSS, KEV flag, risk scores.
- assets           : asset inventory mirror.
- log_events       : SIEM-style log records (simulated or real).
- investigation_results : LLM-generated investigation reports.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DDL statements
# ---------------------------------------------------------------------------

_DDL_VULNERABILITIES = """
CREATE TABLE IF NOT EXISTS vulnerabilities (
    cve_id              TEXT PRIMARY KEY,
    cvss_score          REAL,
    cvss_severity       TEXT,
    cvss_vector         TEXT,
    in_kev              INTEGER NOT NULL DEFAULT 0,
    published_date      TEXT,
    last_modified       TEXT,
    description         TEXT,
    affected_products   TEXT,
    references_         TEXT,
    vendor_project      TEXT,
    product             TEXT,
    vulnerability_name  TEXT,
    date_added_kev      TEXT,
    risk_score          REAL,
    risk_band           TEXT,
    matched_asset_id    TEXT
);
"""

_DDL_ASSETS = """
CREATE TABLE IF NOT EXISTS assets (
    asset_id        TEXT PRIMARY KEY,
    hostname        TEXT,
    ip              TEXT,
    type            TEXT,
    os              TEXT,
    software        TEXT,   -- JSON array serialised as string
    criticality     TEXT,
    exposure        TEXT,
    owner           TEXT,
    tags            TEXT,   -- JSON array serialised as string
    notes           TEXT
);
"""

_DDL_LOG_EVENTS = """
CREATE TABLE IF NOT EXISTS log_events (
    event_id        TEXT PRIMARY KEY,
    timestamp       TEXT,
    asset_id        TEXT,
    source_ip       TEXT,
    event_type      TEXT,
    technique_id    TEXT,
    description     TEXT,
    raw_log         TEXT,
    is_noise        INTEGER NOT NULL DEFAULT 0
);
"""

_DDL_INVESTIGATION_RESULTS = """
CREATE TABLE IF NOT EXISTS investigation_results (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id              TEXT,
    asset_id            TEXT,
    created_at          TEXT,
    llm_response        TEXT,
    validated_text      TEXT,
    citations_found     TEXT,   -- JSON list
    confidence_score    REAL,
    warnings            TEXT    -- JSON list
);
"""


class Database:
    """Thin SQLite wrapper providing upsert helpers for all project tables.

    Parameters
    ----------
    db_path:
        Path to the SQLite database file.  Directories are created if needed.
    """

    def __init__(self, db_path: str) -> None:
        dest = Path(db_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = str(dest)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row  # enables dict-like access
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._create_tables()
        logger.info("Database: connected to %s", self._db_path)

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------

    def _create_tables(self) -> None:
        """Create all tables if they do not already exist."""
        with self._conn:
            self._conn.execute(_DDL_VULNERABILITIES)
            self._conn.execute(_DDL_ASSETS)
            self._conn.execute(_DDL_LOG_EVENTS)
            self._conn.execute(_DDL_INVESTIGATION_RESULTS)
        logger.debug("Database: tables verified/created")

    # ------------------------------------------------------------------
    # Upsert helpers
    # ------------------------------------------------------------------

    def upsert_vulnerabilities(self, df: pd.DataFrame) -> int:
        """Upsert rows from *df* into the ``vulnerabilities`` table.

        Parameters
        ----------
        df:
            DataFrame with columns matching the vulnerabilities schema.
            Missing columns are silently ignored; unrecognised columns
            are dropped.

        Returns
        -------
        int
            Number of rows upserted.
        """
        column_map = {
            "cve_id": "cve_id",
            "cvss_v3_score": "cvss_score",
            "cvss_v3_severity": "cvss_severity",
            "cvss_v3_vector": "cvss_vector",
            "in_kev": "in_kev",
            "published_date": "published_date",
            "last_modified": "last_modified",
            "description": "description",
            "affected_products": "affected_products",
            "references": "references_",
            "vendor_project": "vendor_project",
            "product": "product",
            "vulnerability_name": "vulnerability_name",
            "date_added": "date_added_kev",
            "risk_score": "risk_score",
            "risk_band": "risk_band",
            "matched_asset_id": "matched_asset_id",
        }
        # Build a mapped copy of the DataFrame
        rows = df.rename(columns=column_map)
        valid_cols = [c for c in column_map.values() if c in rows.columns]
        rows = rows[valid_cols]

        # Coerce datetime columns to ISO strings
        for col in ("published_date", "last_modified", "date_added_kev"):
            if col in rows.columns:
                rows[col] = rows[col].astype(str)

        # Coerce in_kev to int (SQLite has no boolean type)
        if "in_kev" in rows.columns:
            rows["in_kev"] = rows["in_kev"].fillna(False).astype(int)

        placeholders = ", ".join(["?"] * len(valid_cols))
        sql = (
            f"INSERT OR REPLACE INTO vulnerabilities ({', '.join(valid_cols)}) "
            f"VALUES ({placeholders})"
        )
        with self._conn:
            self._conn.executemany(sql, rows.itertuples(index=False, name=None))
        logger.info("DB: upserted %d vulnerability rows", len(rows))
        return len(rows)

    def upsert_assets(self, assets_list: list[dict[str, Any]]) -> int:
        """Upsert asset records into the ``assets`` table.

        Parameters
        ----------
        assets_list:
            List of asset dicts as loaded from ``asset_inventory.json``.

        Returns
        -------
        int
            Number of rows upserted.
        """
        sql = """
            INSERT OR REPLACE INTO assets
                (asset_id, hostname, ip, type, os, software,
                 criticality, exposure, owner, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                a.get("asset_id", ""),
                a.get("hostname", ""),
                a.get("ip", ""),
                a.get("type", ""),
                a.get("os", ""),
                json.dumps(a.get("software", [])),
                a.get("criticality", ""),
                a.get("exposure", ""),
                a.get("owner", ""),
                json.dumps(a.get("tags", [])),
                a.get("notes", ""),
            )
            for a in assets_list
        ]
        with self._conn:
            self._conn.executemany(sql, rows)
        logger.info("DB: upserted %d asset rows", len(rows))
        return len(rows)

    def upsert_log_events(self, events_list: list[dict[str, Any]]) -> int:
        """Upsert log event records into the ``log_events`` table.

        Parameters
        ----------
        events_list:
            List of log event dicts as produced by ``LogSimulator``.

        Returns
        -------
        int
            Number of rows upserted.
        """
        sql = """
            INSERT OR REPLACE INTO log_events
                (event_id, timestamp, asset_id, source_ip,
                 event_type, technique_id, description, raw_log, is_noise)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                e.get("event_id", ""),
                e.get("timestamp", ""),
                e.get("asset_id", ""),
                e.get("source_ip", ""),
                e.get("event_type", ""),
                e.get("technique_id", ""),
                e.get("description", ""),
                e.get("raw_log", ""),
                int(e.get("is_noise", False)),
            )
            for e in events_list
        ]
        with self._conn:
            self._conn.executemany(sql, rows)
        logger.info("DB: upserted %d log event rows", len(rows))
        return len(rows)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Execute an arbitrary SELECT and return results as a list of dicts.

        Parameters
        ----------
        sql:
            SQL query string (read-only; use parameterised ``?`` placeholders).
        params:
            Positional query parameters.

        Returns
        -------
        list[dict]
        """
        cur = self._conn.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
        logger.info("Database: connection closed")

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
