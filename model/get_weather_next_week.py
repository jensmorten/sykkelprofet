import pandas as pd
from meteostat import hourly, config
from datetime import datetime, timedelta

# ---------------------------------------
# KONFIG
# ---------------------------------------

config.block_large_requests = False
STATION_ID = "01257"

start = datetime.now()
end = start + timedelta(days=7)

print(f"Tidsrom: {start} → {end}")

# ---------------------------------------
# HENT DATA
# ---------------------------------------

print("Henter værdata fra Meteostat…")

df = hourly(STATION_ID, start, end).fetch()

if df.empty:
    raise RuntimeError("Ingen værdata returnert fra Meteostat")

# ---------------------------------------
# RYDD
# ---------------------------------------

df = df.rename(columns={
    "temp": "air_temperature",
    "prcp": "precipitation_amount",
    "wspd": "wind_speed"
})

df = df[[
    "air_temperature",
    "wind_speed",
    "precipitation_amount"
]]

# ---------------------------------------
# RESAMPLE TIL 3 TIMER
# ---------------------------------------

df = df.resample("3h").agg({
    "air_temperature": "mean",
    "wind_speed": "mean",
    "precipitation_amount": "sum"
})

# interpoler manglande verdiar
df["air_temperature"] = df["air_temperature"].interpolate()
df["wind_speed"] = df["wind_speed"].interpolate()

# fordel nedbør dersom 6-timars data
df["precipitation_amount"] = df["precipitation_amount"].fillna(0)

# ---------------------------------------
# FORMAT
# ---------------------------------------

df = df.reset_index().rename(columns={"time": "ds"})

df.to_csv("current_weather_forecast.csv", index=False)

print("✅ Ferdig!")