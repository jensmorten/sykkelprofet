import json
from prophet.serialize import model_from_json
import functions as f
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("modell og data for prediksjon...")
#with open('prophet_model.json', 'r') as fin:
with open('https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/prophet_model.json', 'r') as fin:
    m = model_from_json(json.load(fin))

pred = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/current_weather_forecast.csv", parse_dates=["ds"])
#pred=pd.read_csv("current_weather_forecast.csv", parse_dates=["ds"])
pred["ds"] = pred["ds"].dt.tz_localize(None)

pred = pred.sort_values("ds")

#print(pred)
print("ferdig!")


weather_cols = [
    "air_temperature",
    "wind_speed",
    "precipitation_amount"
]

pred[weather_cols] = (
    pred[weather_cols]
    .ffill()
    .bfill()
)

pred['month']=pred['ds'].dt.month

pred['sept_ind'] = (pred['month']==9).astype(int)

pred["feels_like"] = f.compute_feels_like(
    pred["air_temperature"].values,
    pred["wind_speed"].values
)

regressors = [ 
    "precipitation_amount",
    "air_temperature",
    "wind_speed",
    "feels_like",
    "sept_ind"
]

future = pred[["ds"] + regressors].copy()

forecast = m.predict(future)

predictions = pd.DataFrame({
    "ds": pred["ds"],

    # prediksjon
    "yhat": forecast["yhat"],
    "yhat_log": forecast["yhat"],

    # komponentar
    "trend": forecast["trend"],
    "weekly": forecast.get("weekly", 0),
    "daily": forecast.get("daily", 0),
    "yearly": forecast.get("yearly", 0),

    # vær
    "temperatur (C)" : pred['air_temperature'],
    "effektiv_temperatur (C)": pred['feels_like'],
    "nedbør (mm)" : pred['precipitation_amount'],
    "vind (m/s)" : pred['wind_speed']
})

predictions["seasonality"] = (
    predictions["weekly"]
    + predictions["daily"]
    + predictions["yearly"]
)

# transform yhat til faktisk nivå
predictions["yhat"] = np.expm1(predictions["yhat"])
predictions["yhat"] = predictions["yhat"].clip(lower=0)
predictions["yhat"] = predictions["yhat"].round().astype(int)

# baseline (trend)
predictions["effect_trend"] = np.expm1(predictions["trend"])

# trend + sesong
trend_plus_season = predictions["trend"] + predictions["seasonality"]

# sesong-effekt (delta frå trend)
predictions["effect_seasonality"] = (
    np.expm1(trend_plus_season)
    - np.expm1(predictions["trend"])
)

# vær-effekt (delta frå trend + sesong)
predictions["effect_weather"] = (
    np.expm1(predictions["yhat_log"])
    - np.expm1(trend_plus_season)
)

predictions["effect_trend"] = predictions["effect_trend"].round().astype(int)
predictions["effect_seasonality"] = predictions["effect_seasonality"].round().astype(int)
predictions["effect_weather"] = predictions["effect_weather"].round().astype(int)

# la vær bli restledd (slik at det alltid stemmer)
predictions["effect_weather"] = (
    predictions["yhat"]
    - predictions["effect_trend"]
    - predictions["effect_seasonality"]
)


print(predictions)

predictions.to_csv(f"predictions.csv", index=False, sep=',')