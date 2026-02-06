"""
Legg historisk vær på bysykkeldata (3-timers oppløsning)
"""

import pandas as pd
from meteostat import hourly, config

# 🔓 Tillat lange historiske forespørsler
config.block_large_requests = False

# ---------------------------------------
# KONFIG
# ---------------------------------------

INPUT_FILE = "bysykkel_prophet_features_3h.csv"
OUTPUT_FILE = "bysykkel_prophet_features_3h_weather_hois.csv"

# Fast Meteostat-stasjon: Trondheim – Voll
#STATION_ID = "01415"
STATION_ID = "01257"

# ---------------------------------------
# 1. LES BYSYKKELDATA
# ---------------------------------------

print("Leser bysykkeldata …")
df_bike = pd.read_csv(INPUT_FILE, parse_dates=["ds"])

start = df_bike["ds"].min()
end = df_bike["ds"].max()

print(f"Tidsrom: {start.date()} → {end.date()}")

# ---------------------------------------
# 2. HENT VÆRDATA (TIMEVIS)
# ---------------------------------------

print("Henter værdata fra Meteostat …")

ts = hourly(STATION_ID, start, end)   # TimeSeries
df_weather = ts.fetch()               # DataFrame

if df_weather is None or df_weather.empty:
    raise RuntimeError("Ingen værdata returnert fra Meteostat")

df_weather = df_weather.reset_index()

# ---------------------------------------
# 3. RYDD & AGGREGER
# ---------------------------------------

df_weather = df_weather.rename(columns={
    "time": "ds",
    "temp": "air_temperature",
    "prcp": "precipitation_amount",
    "wspd": "wind_speed"
})

df_weather["ds"] = df_weather["ds"].dt.floor("3h")

df_weather = (
    df_weather
    .groupby("ds")
    .agg({
        "air_temperature": "mean",
        "wind_speed": "mean",
        "precipitation_amount": "sum"
    })
    .reset_index()
)

# ---------------------------------------
# 4. MERGE
# ---------------------------------------

df_final = df_bike.merge(df_weather, on="ds", how="left")

# ---------------------------------------
# 5. LAGRE
# ---------------------------------------

df_final.to_csv(OUTPUT_FILE, index=False)

print("✅ Ferdig!")
print(f"Lagret som: {OUTPUT_FILE}")
print(f"Rader: {len(df_final):,}")
