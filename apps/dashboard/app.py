"""Streamlit dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any, Optional

from mip.config import settings

st.set_page_config(page_title="Market Intelligence Dashboard", page_icon="📊", layout="wide")

API_BASE = f"http://localhost:{settings.API_PORT}"


@st.cache_data(ttl=5)
def fetch_alerts(limit: int = 100, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        params = {"limit": limit, "only_anomalies": True}
        if symbol:
            params["symbol"] = symbol
        r = requests.get(f"{API_BASE}/alerts/recent", params=params, timeout=5)
        return r.json().get("alerts", []) if r.status_code == 200 else []
    except Exception as e:
        st.error(str(e))
        return []


@st.cache_data(ttl=10)
def fetch_metrics() -> Dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}/metrics", timeout=5)
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        st.error(str(e))
        return {}


def main():
    st.title("📊 Market Intelligence Dashboard")
    st.sidebar.header("Filters")
    symbol = st.sidebar.text_input("Symbol (optional)", "")
    limit = st.sidebar.slider("Alerts", 10, 500, 100)

    alerts = fetch_alerts(limit=limit, symbol=symbol if symbol else None)
    metrics = fetch_metrics()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Alerts", metrics.get("total_alerts", 0))
    with c2:
        st.metric("Anomalies", metrics.get("anomaly_count", 0))
    with c3:
        avg = metrics.get("avg_score", 0)
        st.metric("Avg Score", f"{avg:.3f}" if avg else "N/A")
    with c4:
        st.metric("Shown", len(alerts))

    if not alerts:
        st.info("No alerts. Run the pipeline first.")
        return

    df = pd.DataFrame([
        {"ID": a["id"], "Timestamp": a["timestamp"], "Symbol": a["symbol"], "Score": f"{a['anomaly_score']:.3f}", "Reason": a.get("explanation", {}).get("reason", "N/A")}
        for a in alerts
    ])
    st.dataframe(df, use_container_width=True)

    st.header("Alert Details")
    idx = st.selectbox("Select alert", range(len(alerts)), format_func=lambda i: f"{alerts[i]['id']} - {alerts[i]['symbol']}")
    a = alerts[idx]
    col1, col2 = st.columns(2)
    with col1:
        st.write("**ID:**", a["id"], "**Symbol:**", a["symbol"], "**Score:**", a["anomaly_score"])
    with col2:
        st.write("**Reason:**", a.get("explanation", {}).get("reason", "N/A"))
    st.dataframe(pd.DataFrame([{"Feature": k, "Value": v} for k, v in a.get("features", {}).items()]))


if __name__ == "__main__":
    main()
