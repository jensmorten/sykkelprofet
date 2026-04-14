import pandas as pd
import requests
from datetime import datetime
import pytz

# ---------------------------------------
# KONFIG
# ---------------------------------------

LAT = 63.4305   # Trondheim
LON = 10.3951

URL = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={LAT}&lon={LON}"

HEADERS = {
    "User-Agent": "sykkelprofet/1.0 github.com/jensmorten"
}

print("Henter værdata fra met.no…")

# ---------------------------------------
# HENT DATA
# ---------------------------------------

response = requests.get(URL, headers=HEADERS)

if response.status_code != 200:
    raise RuntimeError(f"Feil fra met.no API: {response.status_code}")

data = response.json()

timeseries = data["properties"]["timeseries"]

# ---------------------------------------
# PARSE
# ---------------------------------------

rows = []

for entry in timeseries:
    time = entry["time"]

    details = entry["data"]["instant"]["details"]

    air_temp = details.get("air_temperature")
    wind_speed = details.get("wind_speed")

    # nedbør ligg i next_1_hours eller next_6_hours
    precipitation = 0

    if "next_1_hours" in entry["data"]:
        precipitation = entry["data"]["next_1_hours"]["details"].get(
            "precipitation_amount", 0
        )
    elif "next_6_hours" in entry["data"]:
        precipitation = entry["data"]["next_6_hours"]["details"].get(
            "precipitation_amount", 0
        )

    rows.append({
        "ds": pd.to_datetime(time),
        "air_temperature": air_temp,
        "wind_speed": wind_speed,
        "precipitation_amount": precipitation
    })

df = pd.DataFrame(rows)

# ---------------------------------------
# RYDD
# ---------------------------------------

df = df.set_index("ds").sort_index()

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

df["precipitation_amount"] = df["precipitation_amount"].fillna(0)

# ---------------------------------------
# BEGRENS TIL NESTE 7 DAGAR (valgfritt)
# ---------------------------------------

now = pd.Timestamp.now(tz=pytz.UTC)
df = df[df.index >= now]
df = df[df.index <= now + pd.Timedelta(days=7)]

# ---------------------------------------
# FORMAT
# ---------------------------------------

df = df.reset_index()

df.to_csv("model/current_weather_forecast.csv", index=False)

print(df)

print("✅ Ferdig!")