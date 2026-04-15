import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests


st.set_page_config(page_title="Prognose for bysykkelbruk i Trondheim", layout="wide")

st.title("🚲 Prognose for bysykkelbruk i Trondheim")

# -----------------------------
# LES DATA
# -----------------------------

api_url = "https://api.github.com/repos/jensmorten/sykkelprofet/commits/main"

try:
    response = requests.get(api_url, timeout=5)
    response.raise_for_status()
    commit = response.json()["sha"]

    url = f"https://raw.githubusercontent.com/jensmorten/sykkelprofet/{commit}/model/predictions.csv"

except Exception:
    # fallback til main (kan vere litt cache, men funkar alltid)
    url = "https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/predictions.csv"

df = pd.read_csv(url, parse_dates=["ds"])

df_hist = pd.read_csv(
    "https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/data/bysykkel_history2018-2025.csv",
    parse_dates=["ds"]
)

df["ds"] = pd.to_datetime(df["ds"])

df = df.rename(columns={
    "temperatur (C)": "temp",
    "effektiv_temperatur (C)": "feels_like",
    "nedbør (mm)": "rain",
    "vind (m/s)": "wind"
})

####
start_train=df_hist["ds"].min().strftime("%d.%m.%y")
end_train=df_hist["ds"].max().strftime("%d.%m.%y")
count_trips=df_hist["y"].sum()

start_pred=df["ds"].min().strftime("%d.%m.%y %H:%M")
end_pred=df["ds"].max().strftime("%d.%m.%y %H:%M")

st.markdown(f"""
Prediksjonsmodellen er trent på historiske data fra {start_train} til {end_train}, totalt {count_trips} bysykkel-turer.  Prediksjonen er oppdatert {start_pred}  og inneholder prognoser fram til {end_pred}.""")


# -----------------------------
# FEATURE ENGINEERING (MATCH "SAMME DAG I FJOR")
# -----------------------------
#df["label"] = df["ds"].dt.strftime("%a %H")
df["label"] = df["ds"].dt.strftime("%d.%m.%y %H:%M")

df["week"] = df["ds"].dt.isocalendar().week.astype(int)
df["weekday"] = df["ds"].dt.weekday
df["hour"] = df["ds"].dt.hour

df_hist["week"] = df_hist["ds"].dt.isocalendar().week.astype(int)
df_hist["weekday"] = df_hist["ds"].dt.weekday
df_hist["hour"] = df_hist["ds"].dt.hour
df_hist["year"] = df_hist["ds"].dt.year

# Finn siste år i historikk
last_year = df_hist["year"].max()

df_last_year = df_hist[df_hist["year"] == last_year]

# 🔥 HER er nøkkelen: bruk "y"
df = df.merge(
    df_last_year[["week", "weekday", "hour", "y"]],
    on=["week", "weekday", "hour"],
    how="left"
)

df = df.rename(columns={"y": "last_year"})

# -----------------------------
# PLOTT
# -----------------------------

fig = go.Figure()

# I fjor (samme dagstype)
fig.add_trace(
    go.Bar(
        x=df["label"],
        y=df["last_year"],
        name="Antall turer i fjor",
        marker=dict(color="steelblue", opacity=0.4),
        opacity=0.3,
    )
)

# Predikert bruk
fig.add_trace(
    go.Bar(
        x=df["label"],
        y=df["yhat"],
        name="Predikert antall turer i år",
        marker=dict(color="steelblue"),
        opacity=0.9,
    )
)


# Temperatur
fig.add_trace(
    go.Scatter(
        x=df["label"],
        y=df["temp"],
        mode="lines",
        name="Varsla temperatur (°C)",
        yaxis="y2",
        line=dict(dash="dot", color="orange"),
    )
)

# Nedbør
fig.add_trace(
    go.Bar(
        x=df["label"],
        y=df["rain"],
        name="Varsla nedbør (mm)",
        yaxis="y2",
        opacity=0.3,
    )
)

# Layout tweaks (🔥 viktig for tett visning)
fig.update_layout(
    barmode="overlay",
    bargap=0.05,
    bargroupgap=0.0,
    height=500,
    hovermode="x unified",
    xaxis_title="Tid",
    yaxis=dict(title="Bysykkelturer"),
    yaxis2=dict(
        title="Temperatur / nedbør",
        overlaying="y",
        side="right",
    ),
)

# Fjern “tidsgap” → tettare stolper
#fig.update_xaxes(type="category")
fig.update_xaxes(tickangle=-30)

#st.plotly_chart(fig, width="stretch")


col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig, width="stretch")

with col2:
    st.markdown("##### Forklaring av prognose")
    selected_label = st.selectbox(
    "Velg tidspunkt",
    df["label"]
    )

    row = df[df["label"] == selected_label].iloc[0]

    st.markdown(f"""
    **Generell Trend-effekt**: {row["effect_trend"]:+}  
    **+ Sesong-effekt (tidspunkt, ukedag, måned, år)**: {row["effect_seasonality"]:+}  
    **+ Vær-effekt**: {row["effect_weather"]:+}  
    **= Gir totalt predikert antall turer for 3 timer etter {selected_label}**: {row["yhat"]}  
    **Sammenligna med samme periode i fjor**: {int(row["last_year"]) if pd.notna(row["last_year"]) else "Ingen data"}
    """)

    fig2 = go.Figure(go.Waterfall(
    x=["Trend", "Sesong", "Vær", "Totalt"],
    y=[
        row["effect_trend"],
        row["effect_seasonality"],
        row["effect_weather"],
        row["yhat"]
    ],
    measure=["relative", "relative", "relative", "total"]
    ))

    #st.plotly_chart(fig2, width="content")
    #fig2.update_layout(
    #title="Kva driv prognosen?",
    #height=250
    #)


st.markdown("---")

st.markdown("""
**Om modellen**  
Prognosen er laget med <a href="https://facebook.github.io/prophet/">Prophet</a> og kombinerer historiske mønstre i bysykkelbruk med værdata (temperatur, nedbør og vind).  
Modellen estimerer hvordan trend, sesong og vær påvirker etterspørselen time for time. Data er henta fra https://trondheimbysykkel.no/apne-data/historisk og berika med vær-data fra <a href="https://meteostat.net/en/">Meteostat</a>. 
Værvarsel fram i tid er henta fra <a href="https://api.met.no/weatherapi/">Meteorologisk institutt</a>. 

**Kildekode og metode**  
Se GitHub for detaljer om datagrunnlag, modell og implementasjon: https://github.com/jensmorten/sykkelprofet 
            
""",
unsafe_allow_html=True) 