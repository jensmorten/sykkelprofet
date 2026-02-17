import pandas as pd

# Les original testsett
df_test = pd.read_csv("bysykkel_test.csv", parse_dates=["ds"])
print(df_test.count())

df_target = df_test[["ds", "y"]].copy()
print(df_target.count())
df_target.to_csv("test_target_secret.csv", index=False)

# Fjern y
df_public = df_test.drop(columns=["y"])
print(df_public.count())
df_public.to_csv("test_compete.csv", index=False)

print("✅ Laget test_compete.csv (uten y)")
