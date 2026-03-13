
import pandas as pd
import numpy as np
from prophet import Prophet
import json
import functions as f
from prophet.serialize import model_to_json

print("Leser data ...")
train = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/data/bysykkel_history2018-2025.csv", parse_dates=["ds"])
train = train.sort_values("ds")
print("ferdig!")

weather_cols = [
    "air_temperature",
    "wind_speed",
    "precipitation_amount"
]

train[weather_cols] = (
    train[weather_cols]
    .ffill()
    .bfill()
)


train['sept_ind'] = (train['month']==9).astype(int)

train["feels_like"] = f.compute_feels_like(
    train["air_temperature"].values,
    train["wind_speed"].values
)

regressors = [ 
    "precipitation_amount",
    "feels_like",
    "sept_ind"
]

train["y_original"] = train["y"].copy()
train["y"] = np.log1p(train["y"])  # log(1 + y) to handle y=0

# --------------------------------------------------
# 4. DEFINER PROPHET
# --------------------------------------------------

m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=True,
    seasonality_mode="additive"
)

m.add_country_holidays(country_name='NO')


for r in regressors:
    m.add_regressor(r)


print("Trener modell ...")
m.fit(train[["ds", "y"] + regressors])

with open('prophet_model.json', 'w') as fout:
    json.dump(model_to_json(m), fout)

