"""SQLite persistence layer.

Justification for SQLite (per brief): zero-operations single-file database,
SQL-queryable, ships with Python, trivially resettable in tests. For an MVP
whose write pattern is "batch insert once, read many", a client/server
database would add ops burden without benefit.

Schema:
    logs      - raw ingested interactions (append-only)
    reminders - generated reminders (regenerated wholesale per pipeline run)
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import LogEntry, Reminder

_SCHEMA = """
CREATE TABLE IF NOT EXISTS logs (
    row_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL,
    timestamp    TEXT NOT NULL,
    agent        TEXT NOT NULL DEFAULT '',
    user_request TEXT NOT NULL DEFAULT '',
    agent_action TEXT NOT NULL DEFAULT '',
    result       TEXT NOT NULL DEFAULT '',
    error        TEXT NOT NULL DEFAULT '',
    metadata     TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_logs_session ON logs(session_id);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id       TEXT PRIMARY KEY,
    description       TEXT NOT NULL,
    trigger_context   TEXT NOT NULL,          -- JSON list of tokens
    recommended_action TEXT NOT NULL,
    evidence_log_ids  TEXT NOT NULL,          -- JSON list of ints
    confidence        REAL NOT NULL,
    frequency         INTEGER NOT NULL,
    created_at        TEXT NOT NULL,
    source_pattern_id TEXT NOT NULL
);
"""


class Store:
    """Thread-safe store: the HTTP API serves requests from worker threads,
    so the connection allows cross-thread use and every operation is
    serialized under a re-entrant lock."""

    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self._lock:
            self.conn.executescript(_SCHEMA)

    # -- logs --------------------------------------------------------------

    def insert_log(self, e: LogEntry) -> int:
        with self._lock:
            cur = self.conn.execute(
                "INSERT INTO logs(session_id,timestamp,agent,user_request,"
                "agent_action,result,error,metadata) VALUES(?,?,?,?,?,?,?,?)",
                (e.session_id, e.timestamp, e.agent, e.user_request,
                 e.agent_action, e.result, e.error, json.dumps(e.metadata)))
            self.conn.commit()
            return cur.lastrowid

    def all_logs(self) -> List[LogEntry]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT * FROM logs ORDER BY row_id").fetchall()
        return [self._row_to_log(r) for r in rows]

    @staticmethod
    def _row_to_log(r: sqlite3.Row) -> LogEntry:
        return LogEntry(
            session_id=r["session_id"], timestamp=r["timestamp"],
            agent=r["agent"], user_request=r["user_request"],
            agent_action=r["agent_action"], result=r["result"],
            error=r["error"], metadata=json.loads(r["metadata"]),
            row_id=r["row_id"])

    # -- reminders ---------------------------------------------------------

    def replace_reminders(self, reminders: Iterable[Reminder]) -> None:
        """Reminders are derived data: regenerate atomically."""
        with self._lock, self.conn:
            self.conn.execute("DELETE FROM reminders")
            for r in reminders:
                self.conn.execute(
                    "INSERT INTO reminders VALUES(?,?,?,?,?,?,?,?,?)",
                    (r.reminder_id, r.description,
                     json.dumps(r.trigger_context), r.recommended_action,
                     json.dumps(r.evidence_log_ids), r.confidence,
                     r.frequency, r.created_at, r.source_pattern_id))

    def all_reminders(self) -> List[Reminder]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT * FROM reminders ORDER BY frequency DESC").fetchall()
        return [self._row_to_reminder(r) for r in rows]

    def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        with self._lock:
            r = self.conn.execute("SELECT * FROM reminders WHERE reminder_id=?",
                                  (reminder_id,)).fetchone()
        return self._row_to_reminder(r) if r else None

    @staticmethod
    def _row_to_reminder(r: sqlite3.Row) -> Reminder:
        return Reminder(
            reminder_id=r["reminder_id"], description=r["description"],
            trigger_context=json.loads(r["trigger_context"]),
            recommended_action=r["recommended_action"],
            evidence_log_ids=json.loads(r["evidence_log_ids"]),
            confidence=r["confidence"], frequency=r["frequency"],
            created_at=r["created_at"],
            source_pattern_id=r["source_pattern_id"])

    # -- utils -------------------------------------------------------------

    def count(self, table: str) -> int:
        assert table in ("logs", "reminders")
        with self._lock:
            return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def close(self):
        self.conn.close()
