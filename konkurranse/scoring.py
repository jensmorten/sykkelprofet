import pandas as pd
from sklearn.metrics import root_mean_squared_error

# Last fasit
y_true = pd.read_csv("test_target_secret.csv", parse_dates=["ds"])

# Last innsending
y_pred = pd.read_csv("submission.csv", parse_dates=["ds"])

# Merge på ds
df = y_true.merge(y_pred, on="ds")

rmse = root_mean_squared_error(df["y"], df["yhat"])

print(f"RMSE: {rmse:.2f}")
