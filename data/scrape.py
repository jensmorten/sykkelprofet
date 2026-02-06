import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

BASE_URL = "https://trondheimbysykkel.no/apne-data/historisk"
DOWNLOAD_DIR = "trondheimbysykkel_csv"
MERGED_FILE = "trondheimbysykkel_alle_aar.csv"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

print("Henter oversikt over historiske data …")
resp = requests.get(BASE_URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

# Finn alle CSV-lenker
csv_links = [
    a["href"] for a in soup.find_all("a", href=True)
    if "CSV" in a.text
]

print(f"Fant {len(csv_links)} CSV-lenker")

downloaded_files = []

for i, csv_url in enumerate(csv_links, start=1):

    # Gjør relative lenker absolutte
    if csv_url.startswith("//"):
        csv_url = "https:" + csv_url
    elif csv_url.startswith("/"):
        csv_url = "https://trondheimbysykkel.no" + csv_url

    # URL-format:
    # https://data.urbansharing.com/.../trips/v1/2026/06.csv
    parts = csv_url.rstrip(".csv").split("/")
    year = parts[-2]
    month = parts[-1]

    filename = f"trips_{year}_{month}.csv"
    path = os.path.join(DOWNLOAD_DIR, filename)

    print(f"[{i}/{len(csv_links)}] Prøver {filename}")

    r = requests.get(csv_url)

    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        downloaded_files.append(path)
        print("  ✔ Lastet ned")
    elif r.status_code == 404:
        print("  ⏭ Ingen data denne måneden (stengt sesong)")
    else:
        print(f"  ⚠ Uventet status {r.status_code}")

# ---- Slå sammen alle CSV-er ----

print("\nSlår sammen CSV-filer …")

dfs = []
for file in downloaded_files:
    df = pd.read_csv(file)
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)
df_all.to_csv(MERGED_FILE, index=False)

print(f"🎉 Ferdig! Samlet datasett lagret som: {MERGED_FILE}")
print(f"Totalt antall rader: {len(df_all):,}")
