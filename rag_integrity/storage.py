"""SQLite-backed history of check and regression runs, used for trend
tracking and reporting."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional

from .exceptions import StorageError

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    question TEXT,
    passed INTEGER,
    score REAL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_kind_created ON runs (kind, created_at);
"""


class Storage:
    """Thin wrapper around a SQLite database storing check/regression history."""

    def __init__(self, db_path: str = "rag_integrity.db"):
        self.db_path = db_path
        try:
            with self._connect() as conn:
                conn.executescript(SCHEMA)
        except sqlite3.Error as exc:
            raise StorageError(f"Failed to initialize storage at {db_path}: {exc}") from exc

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def record_check(self, question: str, passed: bool, score: float, details: Any) -> int:
        details_json = json.dumps(details)
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO runs (kind, question, passed, score, details_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("check", question, 1 if passed else 0, score, details_json, datetime.utcnow().isoformat()),
            )
            return cur.lastrowid

    def record_regression(self, report: Any) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO runs (kind, question, passed, score, details_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    "regression",
                    None,
                    1 if report.failed == 0 else 0,
                    round(report.pass_rate * 100, 2),
                    json.dumps(report.to_dict()),
                    datetime.utcnow().isoformat(),
                ),
            )
            return cur.lastrowid

    def history(self, kind: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            if kind:
                rows = conn.execute(
                    "SELECT * FROM runs WHERE kind = ? ORDER BY created_at DESC LIMIT ?", (kind, limit)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def pass_rate_trend(self, kind: str = "regression", limit: int = 20) -> Optional[float]:
        rows = self.history(kind=kind, limit=limit)
        scored = [r["score"] for r in rows if r["score"] is not None]
        if not scored:
            return None
        return round(sum(scored) / len(scored), 2)
