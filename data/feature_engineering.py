import pandas as pd

INPUT_FILE = "trondheimbysykkel_alle_aar.csv"
OUTPUT_FILE = "bysykkel_prophet_features_3h.csv"

print("Leser rådata …")

df = pd.read_csv(
    INPUT_FILE,
    usecols=["started_at"]
)

# ---- Robust datetime-parsing ----
df["started_at"] = pd.to_datetime(
    df["started_at"],
    utc=True,          # tolker +00:00 korrekt
    errors="coerce"    # evt. skit -> NaT
)

# Fjern rader som ikkje kunne parses (bør vere svært få / ingen)
df = df.dropna(subset=["started_at"])

# Prophet vil ha naive timestamps
df["started_at"] = df["started_at"].dt.tz_convert(None)

# ---- 3-timers avrunding ----
df["ds"] = df["started_at"].dt.floor("3h")

# ---- Aggreger antall turer ----
df_agg = (
    df.groupby("ds")
      .size()
      .reset_index(name="y")
)

# ---- Tidsfeatures ----
df_agg["hour"] = df_agg["ds"].dt.hour
df_agg["weekday"] = df_agg["ds"].dt.weekday
df_agg["is_weekend"] = df_agg["weekday"].isin([5, 6]).astype(int)
df_agg["weekofyear"] = df_agg["ds"].dt.isocalendar().week.astype(int)
df_agg["month"] = df_agg["ds"].dt.month
df_agg["year"] = df_agg["ds"].dt.year
df_agg["is_winter"] = df_agg["month"].isin([11, 12, 1, 2, 3]).astype(int)

df_agg = df_agg.sort_values("ds")
df_agg.to_csv(OUTPUT_FILE, index=False)

print("✅ Ferdig!")
print(f"Rader: {len(df_agg):,}")
print(f"Lagret som: {OUTPUT_FILE}")
