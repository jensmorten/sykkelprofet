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

# -----------------------------
# Bysykkelturer
# -----------------------------
fig.add_trace(
    go.Bar(
        x=df["ds"],
        y=df["yhat"],
        name="Predikert turer",
        opacity=0.9,
    )
)

# -----------------------------
# Temperatur
# -----------------------------
fig.add_trace(
    go.Scatter(
        x=df["ds"],
        y=df["temp"],
        mode="lines",
        name="Temperatur (°C)",
        yaxis="y2",
        line=dict(dash="dot", color="orange"),
    )
)

# -----------------------------
# Nedbør
# -----------------------------
fig.add_trace(
    go.Bar(
        x=df["ds"],
        y=df["rain"],
        name="Nedbør (mm)",
        yaxis="y2",
        opacity=0.4,
    )
)

fig.update_layout(
    height=500,
    hovermode="x unified",
    xaxis_title="Tid",
    yaxis=dict(
        title="Bysykkelturer",
    ),
    yaxis2=dict(
        title="Temperatur / Nedbør",
        overlaying="y",
        side="right",
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