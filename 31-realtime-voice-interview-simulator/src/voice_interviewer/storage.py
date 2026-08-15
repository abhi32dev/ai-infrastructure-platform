from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

from .models import Event, InterviewSession, SessionSummary


class SQLiteSessionStore:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.RLock()
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS sessions(
          id TEXT PRIMARY KEY, state TEXT NOT NULL, document TEXT NOT NULL,
          created_at REAL NOT NULL, updated_at REAL NOT NULL, expires_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events(
          session_id TEXT NOT NULL, sequence INTEGER NOT NULL, event_type TEXT NOT NULL,
          payload TEXT NOT NULL, created_at REAL NOT NULL,
          PRIMARY KEY(session_id, sequence), FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS summaries(
          session_id TEXT PRIMARY KEY, document TEXT NOT NULL, created_at REAL NOT NULL,
          FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );
        """)
        self.connection.commit()

    def save(self, session: InterviewSession, retention_days: int = 30) -> None:
        if retention_days < 1 or retention_days > 365:
            raise ValueError("retention_days must be between 1 and 365")
        now = time.time()
        document = session.model_dump_json()
        with self._lock:
            self.connection.execute(
                """INSERT INTO sessions VALUES(?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET state=excluded.state, document=excluded.document,
                   updated_at=excluded.updated_at, expires_at=excluded.expires_at""",
                (session.id, session.state.value, document, session.created_at.timestamp(), now, now + retention_days * 86400),
            )
            self.connection.commit()

    def get(self, session_id: str) -> InterviewSession:
        with self._lock:
            row = self.connection.execute("SELECT document FROM sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            raise ValueError(f"unknown session: {session_id}")
        return InterviewSession.model_validate_json(row["document"])

    def append_event(self, event: Event) -> None:
        with self._lock:
            self.connection.execute(
                "INSERT INTO events VALUES(?,?,?,?,?)",
                (event.session_id, event.sequence, event.event_type, json.dumps(event.payload, sort_keys=True), event.created_at.timestamp()),
            )
            self.connection.commit()

    def events(self, session_id: str) -> list[Event]:
        with self._lock:
            rows = self.connection.execute("SELECT * FROM events WHERE session_id=? ORDER BY sequence", (session_id,)).fetchall()
        return [Event(session_id=row["session_id"], sequence=row["sequence"], event_type=row["event_type"], payload=json.loads(row["payload"]), created_at=row["created_at"]) for row in rows]

    def save_summary(self, summary: SessionSummary) -> None:
        with self._lock:
            self.connection.execute("INSERT OR REPLACE INTO summaries VALUES(?,?,?)", (summary.session_id, summary.model_dump_json(), time.time()))
            self.connection.commit()

    def purge_expired(self, now: float | None = None) -> int:
        current = time.time() if now is None else now
        with self._lock:
            cursor = self.connection.execute("DELETE FROM sessions WHERE expires_at<=?", (current,))
            self.connection.commit()
            return cursor.rowcount

    def delete(self, session_id: str) -> bool:
        with self._lock:
            cursor = self.connection.execute("DELETE FROM sessions WHERE id=?", (session_id,))
            self.connection.commit()
            return cursor.rowcount > 0

    def close(self) -> None:
        self.connection.close()
