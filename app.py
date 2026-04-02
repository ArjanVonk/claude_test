import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Elia Imbalance Prices", layout="wide")
st.title("Belgian Imbalance Prices — Elia")


def generate_test_data() -> pd.DataFrame:
    now = datetime.utcnow().replace(second=0, microsecond=0)
    # Round down to nearest quarter
    now = now - timedelta(minutes=now.minute % 15)
    periods = 96  # 24h of 15-min quarters
    timestamps = [now - timedelta(minutes=15 * i) for i in range(periods - 1, -1, -1)]

    rng = np.random.default_rng(42)
    nrv = rng.normal(0, 150, periods)  # Net Regulation Volume (MW)
    alpha = 80 + rng.uniform(-10, 10, periods)  # Alpha price (€/MWh)
    mip = alpha + rng.normal(0, 5, periods)   # Marginal Incremental Price
    mdp = alpha - rng.normal(0, 5, periods)   # Marginal Decremental Price

    return pd.DataFrame({
        "datetime": timestamps,
        "nrv_mw": nrv.round(1),
        "alpha_eur_mwh": alpha.round(2),
        "mip_eur_mwh": mip.round(2),
        "mdp_eur_mwh": mdp.round(2),
    })


df = generate_test_data()

# ── KPIs ──────────────────────────────────────────────────────────────────────
latest = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Alpha (€/MWh)", f"{latest['alpha_eur_mwh']:.2f}")
col2.metric("MIP (€/MWh)", f"{latest['mip_eur_mwh']:.2f}")
col3.metric("MDP (€/MWh)", f"{latest['mdp_eur_mwh']:.2f}")
col4.metric("NRV (MW)", f"{latest['nrv_mw']:.1f}")

st.caption(f"Last quarter: {latest['datetime'].strftime('%Y-%m-%d %H:%M')} UTC  •  Test data")

# ── Imbalance prices chart ────────────────────────────────────────────────────
fig_prices = go.Figure()
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["alpha_eur_mwh"], name="Alpha", line=dict(color="#1f77b4", width=2)))
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["mip_eur_mwh"], name="MIP", line=dict(color="#2ca02c", width=1, dash="dot")))
fig_prices.add_trace(go.Scatter(x=df["datetime"], y=df["mdp_eur_mwh"], name="MDP", line=dict(color="#d62728", width=1, dash="dot")))
fig_prices.update_layout(title="Imbalance Prices (last 24h)", yaxis_title="€/MWh", xaxis_title="", hovermode="x unified", height=350)
st.plotly_chart(fig_prices, use_container_width=True)

# ── NRV chart ─────────────────────────────────────────────────────────────────
fig_nrv = go.Figure()
fig_nrv.add_bar(
    x=df["datetime"],
    y=df["nrv_mw"],
    marker_color=["#d62728" if v < 0 else "#2ca02c" for v in df["nrv_mw"]],
    name="NRV",
)
fig_nrv.update_layout(title="Net Regulation Volume (last 24h)", yaxis_title="MW", xaxis_title="", height=280)
st.plotly_chart(fig_nrv, use_container_width=True)

# ── Raw data ──────────────────────────────────────────────────────────────────
with st.expander("Raw data"):
    st.dataframe(df.sort_values("datetime", ascending=False).reset_index(drop=True), use_container_width=True)
