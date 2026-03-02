"""Event repository using SQLite for replay/audit."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import sqlite3

from ..config import settings


class EventsRepository:
    """Persist raw market events for replay/debugging."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    size REAL NOT NULL,
                    side TEXT NOT NULL
                )
                """
            )
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_symbol ON events(symbol)")
            c.commit()

    def save(self, timestamp: datetime, symbol: str, price: float, size: float, side: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO events (timestamp, symbol, price, size, side) VALUES (?, ?, ?, ?, ?)",
                (timestamp.isoformat(), symbol, float(price), float(size), side),
            )
            c.commit()
            return int(cur.lastrowid)

    def get_recent(self, limit: int = 100, symbol: Optional[str] = None) -> List[Dict]:
        with self._conn() as c:
            q = "SELECT * FROM events WHERE 1=1"
            params = []
            if symbol:
                q += " AND symbol = ?"
                params.append(symbol)
            q += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            rows = c.execute(q, params).fetchall()
        return [dict(row) for row in rows]
