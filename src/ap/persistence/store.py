"""Persistence layer for storing alerts."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import sqlite3
import json
from contextlib import contextmanager

from ..utils.config import settings


class AlertStore:
    """SQLite-based storage for anomaly alerts."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize alert store.
        
        Args:
            db_path: Path to SQLite database (default from config)
        """
        self.db_path = db_path or settings.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
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
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON alerts(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol ON alerts(symbol)
            """)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_alert(
        self,
        timestamp: datetime,
        symbol: str,
        anomaly_score: float,
        is_anomaly: bool,
        features: Dict[str, float],
        explanation: Dict[str, Any]
    ) -> int:
        """
        Save an alert to the database.
        
        Args:
            timestamp: Event timestamp
            symbol: Symbol
            anomaly_score: Anomaly score
            is_anomaly: Whether anomaly was detected
            features: Feature dictionary
            explanation: Explanation dictionary
        
        Returns:
            Alert ID
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO alerts 
                (timestamp, symbol, anomaly_score, is_anomaly, features, explanation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp.isoformat(),
                symbol,
                anomaly_score,
                1 if is_anomaly else 0,
                json.dumps(features),
                json.dumps(explanation),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_alerts(
        self,
        limit: int = 100,
        symbol: Optional[str] = None,
        only_anomalies: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            symbol: Optional symbol filter
            only_anomalies: If True, only return anomaly alerts
        
        Returns:
            List of alert dictionaries
        """
        with self._get_connection() as conn:
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []
            
            if only_anomalies:
                query += " AND is_anomaly = 1"
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "symbol": row["symbol"],
                    "anomaly_score": row["anomaly_score"],
                    "is_anomaly": bool(row["is_anomaly"]),
                    "features": json.loads(row["features"]),
                    "explanation": json.loads(row["explanation"]),
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    def get_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific alert by ID.
        
        Args:
            alert_id: Alert ID
        
        Returns:
            Alert dictionary or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM alerts WHERE id = ?",
                (alert_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "symbol": row["symbol"],
                "anomaly_score": row["anomaly_score"],
                "is_anomaly": bool(row["is_anomaly"]),
                "features": json.loads(row["features"]),
                "explanation": json.loads(row["explanation"]),
                "created_at": row["created_at"]
            }
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored alerts.
        
        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomalies,
                    AVG(anomaly_score) as avg_score,
                    MIN(anomaly_score) as min_score,
                    MAX(anomaly_score) as max_score
                FROM alerts
            """)
            row = cursor.fetchone()
            
            return {
                "total_alerts": row["total"],
                "anomaly_count": row["anomalies"],
                "avg_score": row["avg_score"],
                "min_score": row["min_score"],
                "max_score": row["max_score"]
            }

