"""FastAPI server for anomaly alerts API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..persistence.store import AlertStore
from ..utils.config import settings

app = FastAPI(title="Anomaly Detection API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize alert store
alert_store = AlertStore()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Anomaly Detection API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/alerts/recent")
async def get_recent_alerts(
    limit: int = 100,
    symbol: Optional[str] = None,
    only_anomalies: bool = True
):
    """
    Get recent alerts.
    
    Args:
        limit: Maximum number of alerts to return
        symbol: Optional symbol filter
        only_anomalies: If True, only return anomaly alerts
    
    Returns:
        List of alerts
    """
    alerts = alert_store.get_recent_alerts(
        limit=limit,
        symbol=symbol,
        only_anomalies=only_anomalies
    )
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: int):
    """
    Get a specific alert by ID.
    
    Args:
        alert_id: Alert ID
    
    Returns:
        Alert details
    """
    alert = alert_store.get_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@app.get("/metrics")
async def get_metrics():
    """
    Get alert statistics and metrics.
    
    Returns:
        Dictionary with statistics
    """
    stats = alert_store.get_alert_stats()
    return stats


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

