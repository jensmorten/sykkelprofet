import pandas as pd
from meteostat import hourly, config
from datetime import datetime, timedelta

# 🔓 Tillat lange historiske forespørsler
config.block_large_requests = False

# ---------------------------------------
# KONFIG
# ---------------------------------------

STATION_ID = "01257"

# ---------------------------------------
# 1. set config
# ---------------------------------------

start = datetime.now()
end = start + timedelta(weeks=1)

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


df_weather.to_csv('current_weather_forecast.csv', index=False)

print("✅ Ferdig!")
