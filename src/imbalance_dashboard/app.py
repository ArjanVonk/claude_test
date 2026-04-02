import os

import plotly.graph_objects as go
import streamlit as st

from imbalance_dashboard.offline import OfflineDataLoader

st.set_page_config(page_title="Elia Imbalance Prices", layout="wide")
st.title("Belgian Imbalance Prices — Elia")

if os.environ.get("DATABASE_URL"):
    from imbalance_dashboard.db import PostgresDataLoader

    loader = PostgresDataLoader()
    df = loader.load()
    if df.empty:
        # Seed the database with offline data on first run
        from imbalance_dashboard.offline import OfflineDataLoader as _Offline

        df = _Offline().load()
        loader.save(df)
    data_source = "PostgreSQL"
else:
    df = OfflineDataLoader().load()
    data_source = "Offline (test data)"

# ── KPIs ──────────────────────────────────────────────────────────────────────
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Alpha (€/MWh)", f"{latest['alpha_eur_mwh']:.2f}")
col2.metric("MIP (€/MWh)", f"{latest['mip_eur_mwh']:.2f}")
col3.metric("MDP (€/MWh)", f"{latest['mdp_eur_mwh']:.2f}")
col4.metric("NRV (MW)", f"{latest['nrv_mw']:.1f}")

st.caption(f"Last quarter: {latest['datetime'].strftime('%Y-%m-%d %H:%M')} UTC  •  {data_source}")

# ── Imbalance prices chart ────────────────────────────────────────────────────
fig_prices = go.Figure()
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["alpha_eur_mwh"], name="Alpha", line=dict(color="#1f77b4", width=2)))
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["mip_eur_mwh"], name="MIP", line=dict(color="#2ca02c", width=1, dash="dot")))
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["mdp_eur_mwh"], name="MDP", line=dict(color="#d62728", width=1, dash="dot")))
fig_prices.update_layout(title="Imbalance Prices (last 24h)", yaxis_title="€/MWh", hovermode="x unified", height=350)
st.plotly_chart(fig_prices, use_container_width=True)

# ── NRV chart ─────────────────────────────────────────────────────────────────
fig_nrv = go.Figure()
fig_nrv.add_bar(
    x=df["datetime"],
    y=df["nrv_mw"],
    marker_color=["#d62728" if v < 0 else "#2ca02c" for v in df["nrv_mw"]],
    name="NRV",
)
fig_nrv.update_layout(title="Net Regulation Volume (last 24h)", yaxis_title="MW", height=280)
st.plotly_chart(fig_nrv, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("Raw data"):
    st.dataframe(df.sort_values("datetime", ascending=False).reset_index(drop=True), use_container_width=True)
