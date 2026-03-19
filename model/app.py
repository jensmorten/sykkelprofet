import streamlit as st
import pandas as pd
import plotly.graph_objects as go


st.set_page_config(page_title="Prognose for bysykkelbruk i Trondheim", layout="wide")

st.title("🚲 Prognose for bysykkelbruk i Trondheim")

# -----------------------------
# LES DATA
# -----------------------------

df = pd.read_csv(
    "https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/predictions.csv", parse_dates=["ds"]
)

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

start_pred=df["ds"].min().strftime("%d.%m.%y %H:%M")
end_pred=df["ds"].max().strftime("%d.%m.%y %H:%M")

st.markdown(f"""
Prediksjonsmodellen er basert på <a href="https://facebook.github.io/prophet/">Prophet</a>  
og er trent på historiske data fra **{start_train} til {end_train}**.  

Prediksjonen er oppdatert **{start_pred}**  
og inneholder prognoser fram til **{end_pred}**.
""", unsafe_allow_html=True)


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
        name="I fjor (samme ukedag)",
        marker=dict(color="steelblue", opacity=0.4),
        opacity=0.3,
    )
)

# Predikert bruk
fig.add_trace(
    go.Bar(
        x=df["label"],
        y=df["yhat"],
        name="Predikert",
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
        name="Varsla Temperatur (°C)",
        yaxis="y2",
        line=dict(dash="dot", color="orange"),
    )
)

# Nedbør
fig.add_trace(
    go.Bar(
        x=df["label"],
        y=df["rain"],
        name="Varsla Nedbør (mm)",
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
        title="Temperatur / Nedbør",
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
    st.markdown("#### 🔍 Forklaring av prognose")
    selected_label = st.selectbox(
    "Velg tidspunkt",
    df["label"]
    )

    row = df[df["label"] == selected_label].iloc[0]

    st.markdown(f"""
    **Trend**: {row["effect_trend"]:+}  
    **+ Sesong**: {row["effect_seasonality"]:+}  
    **+ Vær**: {row["effect_weather"]:+}  
    **= Totalt**: {row["yhat"]}
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





# -----------------------------
# NØKKELTALL
# -----------------------------

#col1, col2, col3 = st.columns(3)

#with col1:
#st.metric(
#        "Maks forventet bruk",
#        int(df["yhat"].max())
#    )

#with col2:
#    st.metric(
#        "Varsla gjennomsnitt-temperatur",
#        f"{df['temp'].mean():.1f} °C"
#    )

#with col3:
#    st.metric(
#        "Varsla total nedbør",
#        f"{df['rain'].sum():.1f} mm"
#    )

# -----------------------------
# TABELL
# -----------------------------

#with st.expander("Se rådata"):
#    st.dataframe(df)