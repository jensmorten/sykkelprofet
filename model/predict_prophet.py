import json
from prophet.serialize import model_from_json
import pandas as pd
import numpy as np

with open('prophet_model.json', 'r') as fin:
    m = model_from_json(json.load(fin))

pred = pd.read_csv("https://raw.githubusercontent.com/jensmorten/sykkelprofet/refs/heads/main/model_current_weather_forecast.csv", parse_dates=["ds"])
pred = pred.sort_values("ds")


