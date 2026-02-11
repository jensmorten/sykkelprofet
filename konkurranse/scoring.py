import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import root_mean_squared_error

# --------------------------------------------------
# FILNAVN
# --------------------------------------------------

TARGET_FILE = "test_target_secret.csv"
SUBMISSION_FILE = "submission_testing.csv"

# PNG lagres med samme navn som submission
OUTPUT_PLOT = SUBMISSION_FILE.replace(".csv", "_score.png")

# --------------------------------------------------
# 1. LES DATA
# --------------------------------------------------

y_true = pd.read_csv(TARGET_FILE, parse_dates=["ds"])
y_pred = pd.read_csv(SUBMISSION_FILE, parse_dates=["ds"])

df = y_true.merge(y_pred, on="ds")

# --------------------------------------------------
# 2. BEREGN RMSE
# --------------------------------------------------

rmse = root_mean_squared_error(df["y"], df["yhat"])

print(f"RMSE: {rmse:.2f}")

# --------------------------------------------------
# 3. PLOTT
# --------------------------------------------------

plt.figure(figsize=(12, 5))

plt.plot(df["ds"], df["y"], label="Faktisk", linewidth=2)
plt.plot(df["ds"], df["yhat"], label="Predikert", linewidth=2)

plt.title(f"Faktisk vs Predikert\nRMSE: {rmse:.2f}")
plt.xlabel("Dato")
plt.ylabel("Antall turer")
plt.legend()
plt.tight_layout()

# Lagre figur
plt.savefig(OUTPUT_PLOT, dpi=300)
plt.close()

print(f"📊 Plot lagret som {OUTPUT_PLOT}")
