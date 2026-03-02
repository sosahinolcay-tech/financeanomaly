"""Feature snapshot repository for drift and similarity analysis."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import json
import sqlite3

from ..config import settings


class FeatureRepository:
    """Persist per-symbol feature snapshots."""

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
                CREATE TABLE IF NOT EXISTS feature_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    features TEXT NOT NULL
                )
                """
            )
            c.execute("CREATE INDEX IF NOT EXISTS idx_fs_ts ON feature_snapshots(timestamp)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_fs_symbol ON feature_snapshots(symbol)")
            c.commit()

    def save(self, timestamp: datetime, symbol: str, features: Dict[str, float]) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO feature_snapshots (timestamp, symbol, features) VALUES (?, ?, ?)",
                (timestamp.isoformat(), symbol, json.dumps(features)),
            )
            c.commit()
            return int(cur.lastrowid)

    def get_recent(self, limit: int = 100, symbol: Optional[str] = None) -> List[Dict]:
        with self._conn() as c:
            q = "SELECT * FROM feature_snapshots WHERE 1=1"
            params = []
            if symbol:
                q += " AND symbol = ?"
                params.append(symbol)
            q += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            rows = c.execute(q, params).fetchall()
        return [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "symbol": row["symbol"],
                "features": json.loads(row["features"]),
            }
            for row in rows
        ]
