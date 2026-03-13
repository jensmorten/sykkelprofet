import json
from prophet.serialize import model_from_json
import functions as f
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("modell og data for prediksjon...")
with open('prophet_model.json', 'r') as fin:
    m = model_from_json(json.load(fin))

pred = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model/current_weather_forecast.csv", parse_dates=["ds"])
pred = pred.sort_values("ds")

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
    "yhat": forecast["yhat"],
    "temperatur (C)" : pred['air_temperature'],
    "effektiv_temperatur (C)": pred['feels_like'],
    "nedbør (mm)" : pred['precipitation_amount'],
    "vind (m/s)" : pred['wind_speed']
})


predictions["yhat"] = np.expm1(predictions["yhat"])  # exp(yhat) - 1
predictions["yhat"] = predictions["yhat"].clip(lower=0)
predictions["yhat"] = predictions["yhat"].round().astype(int)

print(predictions)

predictions.to_csv(f"predictions.csv", index=False, sep=',')

###same dates from last year
history = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/data/bysykkel_history2018-2025.csv", parse_dates=["ds"])

start=predictions['ds'].min().date()+ timedelta(weeks=-52)
end = predictions['ds'].max().date()+ timedelta(weeks=-52)

#print(start)
#print(end)

history = history[history['ds'].dt.date >start]
history = history[history['ds'].dt.date <end]


history["feels_like"] = f.compute_feels_like(
    history["air_temperature"].values,
    history["wind_speed"].values
)

history = pd.DataFrame({
    "ds": history["ds"],
    "y": history["y"],
    "effektiv_temperatur (C)": history['feels_like'],
    "nedbør (mm)" : history['precipitation_amount'],
    "vind (m/s)" : history['wind_speed']
})

#print(history)
