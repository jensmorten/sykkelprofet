"""
Henter værprognose fra MET Locationforecast
Aggregerer til 3-timers intervall
Lagrer kompatibelt med Prophet-regressorer
"""

import requests
import pandas as pd

# --------------------------------------------------
# KONFIG
# --------------------------------------------------

LAT = 63.4305   # Trondheim
LON = 10.3951

OUTPUT_FILE = "weather_forecast_3h.csv"

# --------------------------------------------------
# 1. HENT DATA FRA MET
# --------------------------------------------------

print("Henter værprognose fra MET …")

url = (
    "https://api.met.no/weatherapi/locationforecast/2.0/complete"
    f"?lat={LAT}&lon={LON}"
)

headers = {
    "User-Agent": "sykkelprofet/1.0 (jens.nilsen@example.com)"
}

r = requests.get(url, headers=headers)
r.raise_for_status()

data = r.json()

# --------------------------------------------------
# 2. PARSE TIME-SERIE
# --------------------------------------------------

rows = []

for entry in data["properties"]["timeseries"]:
    time = entry["time"]
    details = entry["data"]["instant"]["details"]

    air_temp = details.get("air_temperature")
    wind_speed = details.get("wind_speed")

    # Nedbør ligger ofte i next_1_hours
    precipitation = None
    next_1h = entry["data"].get("next_1_hours")
    if next_1h:
        precipitation = next_1h["details"].get("precipitation_amount")

    rows.append({
        "ds": pd.to_datetime(time),
        "air_temperature": air_temp,
        "wind_speed": wind_speed,
        "precipitation_amount": precipitation
    })

df = pd.DataFrame(rows)

# --------------------------------------------------
# 3. AGGREGER TIL 3 TIMER
# --------------------------------------------------

df["ds"] = df["ds"].dt.floor("3h")

df_3h = (
    df
    .groupby("ds")
    .agg({
        "air_temperature": "mean",
        "wind_speed": "mean",
        "precipitation_amount": "sum"
    })
    .reset_index()
)

# --------------------------------------------------
# 4. LAGRE
# --------------------------------------------------

df_3h.to_csv(OUTPUT_FILE, index=False)

print("✅ Ferdig!")
print(f"Lagret som {OUTPUT_FILE}")
print(f"Rader: {len(df_3h)}")
