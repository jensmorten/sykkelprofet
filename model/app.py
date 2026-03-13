import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Prognose for bysykkelbruk i Trondheim", layout="wide")

st.title("🚲 Prognose for bysykkelbruk i Trondheim")

# -----------------------------
# LES DATA
# -----------------------------

df = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/predictions.csv")

df["ds"] = pd.to_datetime(df["ds"])

df = df.rename(columns={
    "temperatur (C)": "temp",
    "effektiv_temperatur (C)": "feels_like",
    "nedbør (mm)": "rain",
    "vind (m/s)": "wind"
})

# -----------------------------
# HOVEDPLOT
# -----------------------------

fig = go.Figure()

# sykkelbruk
fig.add_trace(
    go.Scatter(
        x=df["ds"],
        y=df["yhat"],
        mode="lines+markers",
        name="Predikert turer",
        line=dict(width=3)
    )
)

# temperatur
fig.add_trace(
    go.Scatter(
        x=df["ds"],
        y=df["temp"],
        mode="lines",
        name="Temperatur",
        yaxis="y2",
        line=dict(dash="dot")
    )
)

# nedbør
fig.add_trace(
    go.Bar(
        x=df["ds"],
        y=df["rain"],
        name="Nedbør",
        opacity=0.3,
        yaxis="y3"
    )
)

fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis_title="Tid",
    yaxis=dict(
        title="Bysykkelturer"
    ),
    yaxis2=dict(
        title="Temperatur (°C)",
        overlaying="y",
        side="right"
    ),
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# NØKKELTALL
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Maks forventet bruk",
        int(df["yhat"].max())
    )

with col2:
    st.metric(
        "Gjennomsnitt temperatur",
        f"{df['temp'].mean():.1f} °C"
    )

with col3:
    st.metric(
        "Total nedbør",
        f"{df['rain'].sum():.1f} mm"
    )

# -----------------------------
# TABELL
# -----------------------------

with st.expander("Se rådata"):
    st.dataframe(df)