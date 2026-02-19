"""FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from mip.persistence.alerts_repo import AlertsRepository
from mip.config import settings

app = FastAPI(title="Market Intelligence Platform API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alerts_repo = AlertsRepository()


@app.get("/")
async def root():
    return {"service": "Market Intelligence Platform API", "version": "0.2.0", "status": "running"}


@app.get("/alerts/recent")
async def get_recent_alerts(limit: int = 100, symbol: Optional[str] = None, only_anomalies: bool = True):
    alerts = alerts_repo.get_recent_alerts(limit=limit, symbol=symbol, only_anomalies=only_anomalies)
    return {"alerts": alerts, "count": len(alerts)}


@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: int):
    alert = alerts_repo.get_alert(alert_id)
    if alert is None:
        raise HTTPException(404, "Alert not found")
    return alert


@app.get("/metrics")
async def get_metrics():
    return alerts_repo.get_alert_stats()


@app.get("/health")
async def health():
    return {"status": "healthy"}
