import pandas as pd

# Les original testsett
df_test = pd.read_csv("bysykkel_test.csv", parse_dates=["ds"])

df_target = df_test[["ds", "y"]]
df_target.to_csv("test_target_secret.csv", index=False)

# Fjern y
df_public = df_test.drop(columns=["y"])

df_public.to_csv("test_compete.csv", index=False)

print("✅ Laget test_features.csv (uten y)")
