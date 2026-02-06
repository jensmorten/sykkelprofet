import pandas as pd 
df = pd.read_csv("bysykkel_prophet_features_3h.csv", parse_dates=["ds"])
df.head()
df.tail()
print(df.describe())