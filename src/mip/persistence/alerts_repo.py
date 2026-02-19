"""Alerts repository - SQLite storage."""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import sqlite3

from ..config import settings


class AlertsRepository:
    """SQLite-based alert storage."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    is_anomaly INTEGER NOT NULL,
                    features TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_ts ON alerts(timestamp)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON alerts(symbol)")
            c.commit()

    # Backward-compat aliases for AlertStore
    def save_alert(self, timestamp, symbol, anomaly_score, is_anomaly, features, explanation):
        return self.save(timestamp, symbol, anomaly_score, is_anomaly, features, explanation)

    def get_recent_alerts(self, limit=100, symbol=None, only_anomalies=True):
        return self.get_recent(limit, symbol, only_anomalies)

    def get_alert(self, alert_id):
        return self.get(alert_id)

    def get_alert_stats(self):
        return self.get_stats()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save(
        self,
        timestamp: datetime,
        symbol: str,
        score: float,
        is_anomaly: bool,
        features: Dict[str, float],
        explanation: Dict[str, Any],
    ) -> int:
        with self._conn() as c:
            cur = c.execute(
                """INSERT INTO alerts (timestamp, symbol, anomaly_score, is_anomaly, features, explanation, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    timestamp.isoformat(),
                    symbol,
                    score,
                    1 if is_anomaly else 0,
                    json.dumps(features),
                    json.dumps(explanation),
                    datetime.now().isoformat(),
                ),
            )
            c.commit()
            return cur.lastrowid

    def get_recent(self, limit: int = 100, symbol: str = None, only_anomalies: bool = True) -> List[Dict]:
        with self._conn() as c:
            q = "SELECT * FROM alerts WHERE 1=1"
            params = []
            if only_anomalies:
                q += " AND is_anomaly = 1"
            if symbol:
                q += " AND symbol = ?"
                params.append(symbol)
            q += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            rows = c.execute(q, params).fetchall()
        return [
            {
                "id": r["id"],
                "timestamp": r["timestamp"],
                "symbol": r["symbol"],
                "anomaly_score": r["anomaly_score"],
                "is_anomaly": bool(r["is_anomaly"]),
                "features": json.loads(r["features"]),
                "explanation": json.loads(r["explanation"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def get(self, alert_id: int) -> Optional[Dict]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if r is None:
            return None
        return {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "symbol": r["symbol"],
            "anomaly_score": r["anomaly_score"],
            "is_anomaly": bool(r["is_anomaly"]),
            "features": json.loads(r["features"]),
            "explanation": json.loads(r["explanation"]),
            "created_at": r["created_at"],
        }

    def get_stats(self) -> Dict[str, Any]:
        with self._conn() as c:
            r = c.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomalies,
                       AVG(anomaly_score) as avg_score,
                       MIN(anomaly_score) as min_score,
                       MAX(anomaly_score) as max_score
                FROM alerts
            """).fetchone()
        return {
            "total_alerts": r["total"],
            "anomaly_count": r["anomalies"],
            "avg_score": r["avg_score"],
            "min_score": r["min_score"],
            "max_score": r["max_score"],
        }
