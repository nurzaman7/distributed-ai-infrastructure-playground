from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
import httpx

API_BASE = st.sidebar.text_input("API Base URL", "http://localhost:8080")

st.set_page_config(page_title="Future AI Systems Dashboard", layout="wide")
st.title("Future AI Systems: Observability Dashboard")


def fetch(path: str):
    with httpx.Client(timeout=4.0) as client:
        res = client.get(f"{API_BASE.rstrip('/')}{path}")
        res.raise_for_status()
        return res.json()


try:
    q = fetch("/metrics/queue")
    a = fetch("/analytics")
    d = fetch("/distributed/metrics")
    p3 = fetch("/phase3/metrics")
    traces = fetch("/traces?limit=1000")
except Exception as exc:
    st.error(f"API unavailable: {exc}")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Queue Depth", q["queue_depth"])
c2.metric("Written", q["written_total"])
c3.metric("Dropped", q["dropped_total"])
c4.metric("Error Rate", f"{a['error_rate']*100:.2f}%")
c5.metric("Throughput RPS", a.get("throughput_rps", 0))

st.subheader("Latency Percentiles")
st.write(a["latency"])

st.subheader("Distributed + Phase3 Metrics")
mc1, mc2, mc3 = st.columns(3)
mc1.json(d)
mc2.json(p3)
mc3.json(q)

if traces:
    df = pd.DataFrame(traces)
    st.subheader("Recent Traces")
    st.dataframe(df, use_container_width=True)

    if "latency_ms" in df.columns:
        fig = px.histogram(df, x="latency_ms", nbins=40, title="Latency Distribution")
        st.plotly_chart(fig, use_container_width=True)

    if "status" in df.columns:
        fig2 = px.histogram(df, x="status", title="Status Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # Advanced heatmap: throughput vs latency by quant mode (or provider fallback)
    dim = "quant_mode" if "quant_mode" in df.columns else ("provider" if "provider" in df.columns else None)
    if dim:
        dfx = df.copy()
        dfx["latency_bucket"] = (pd.to_numeric(dfx.get("latency_ms", 0), errors="coerce").fillna(0) // 50) * 50
        agg = dfx.groupby([dim, "latency_bucket"], dropna=False).size().reset_index(name="count")
        h = px.density_heatmap(agg, x="latency_bucket", y=dim, z="count", color_continuous_scale="Viridis", title="Throughput vs Latency Heatmap")
        st.plotly_chart(h, use_container_width=True)
