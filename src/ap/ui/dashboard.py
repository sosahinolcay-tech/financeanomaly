"""Streamlit dashboard for viewing anomaly alerts and explanations."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any, Optional

from ..utils.config import settings

# Page config
st.set_page_config(
    page_title="Anomaly Detection Dashboard",
    page_icon="📊",
    layout="wide"
)

# API base URL
API_BASE_URL = f"http://localhost:{settings.API_PORT}"


@st.cache_data(ttl=5)  # Cache for 5 seconds
def fetch_alerts(limit: int = 100, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch alerts from API."""
    try:
        params = {"limit": limit, "only_anomalies": True}
        if symbol:
            params["symbol"] = symbol
        response = requests.get(f"{API_BASE_URL}/alerts/recent", params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get("alerts", [])
        return []
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return []


@st.cache_data(ttl=10)
def fetch_metrics() -> Dict[str, Any]:
    """Fetch metrics from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return {}


def plot_price_chart(alert: Dict[str, Any]) -> go.Figure:
    """Create a price chart for an alert (simplified)."""
    fig = go.Figure()
    
    # Extract price from features if available
    features = alert.get("features", {})
    
    # Create a simple line chart
    # In a real implementation, you'd fetch historical price data
    timestamp = datetime.fromisoformat(alert["timestamp"])
    times = [timestamp - timedelta(seconds=i) for i in range(60, 0, -1)]
    prices = [100.0 + (i * 0.1) for i in range(60)]  # Placeholder
    
    fig.add_trace(go.Scatter(
        x=times,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color='blue')
    ))
    
    # Highlight anomaly point
    fig.add_trace(go.Scatter(
        x=[timestamp],
        y=[prices[-1]],
        mode='markers',
        name='Anomaly',
        marker=dict(size=15, color='red', symbol='x')
    ))
    
    fig.update_layout(
        title="Price Chart (60s window)",
        xaxis_title="Time",
        yaxis_title="Price",
        height=300
    )
    
    return fig


def main():
    """Main dashboard function."""
    st.title("📊 Real-time Financial Anomaly Detection Dashboard")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    symbol_filter = st.sidebar.text_input("Symbol Filter (optional)", "")
    limit = st.sidebar.slider("Number of alerts", 10, 500, 100)
    
    # Fetch data
    alerts = fetch_alerts(limit=limit, symbol=symbol_filter if symbol_filter else None)
    metrics = fetch_metrics()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alerts", metrics.get("total_alerts", 0))
    with col2:
        st.metric("Anomalies Detected", metrics.get("anomaly_count", 0))
    with col3:
        avg_score = metrics.get("avg_score", 0)
        st.metric("Avg Anomaly Score", f"{avg_score:.3f}" if avg_score else "N/A")
    with col4:
        st.metric("Alerts Shown", len(alerts))
    
    if not alerts:
        st.info("No alerts found. Make sure the pipeline is running and generating alerts.")
        return
    
    # Alerts table
    st.header("Recent Anomaly Alerts")
    
    # Prepare data for table
    table_data = []
    for alert in alerts:
        table_data.append({
            "ID": alert["id"],
            "Timestamp": alert["timestamp"],
            "Symbol": alert["symbol"],
            "Score": f"{alert['anomaly_score']:.3f}",
            "Reason": alert.get("explanation", {}).get("reason", "N/A")
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    # Alert details
    if alerts:
        st.header("Alert Details")
        selected_idx = st.selectbox(
            "Select an alert to view details",
            range(len(alerts)),
            format_func=lambda i: f"Alert {alerts[i]['id']} - {alerts[i]['symbol']} - {alerts[i]['timestamp']}"
        )
        
        selected_alert = alerts[selected_idx]
        
        # Display alert info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Alert Information")
            st.write(f"**ID:** {selected_alert['id']}")
            st.write(f"**Timestamp:** {selected_alert['timestamp']}")
            st.write(f"**Symbol:** {selected_alert['symbol']}")
            st.write(f"**Anomaly Score:** {selected_alert['anomaly_score']:.4f}")
            st.write(f"**Is Anomaly:** {'Yes' if selected_alert['is_anomaly'] else 'No'}")
        
        with col2:
            st.subheader("Explanation")
            explanation = selected_alert.get("explanation", {})
            st.write(f"**Reason:** {explanation.get('reason', 'N/A')}")
            
            # Top features
            top_features = explanation.get("top_features", [])
            if top_features:
                st.write("**Top Contributing Features:**")
                for feat in top_features:
                    st.write(f"- {feat['feature']}: {feat.get('value', 0):.4f} "
                           f"(contribution: {feat.get('contribution', 0):.4f})")
        
        # Price chart
        st.subheader("Price Context")
        fig = plot_price_chart(selected_alert)
        st.plotly_chart(fig, use_container_width=True)
        
        # Features table
        st.subheader("All Features")
        features_df = pd.DataFrame([
            {"Feature": k, "Value": v}
            for k, v in selected_alert.get("features", {}).items()
        ])
        st.dataframe(features_df, use_container_width=True)


if __name__ == "__main__":
    main()

