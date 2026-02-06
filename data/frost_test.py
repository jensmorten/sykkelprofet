import requests, os
from dotenv import load_dotenv

load_dotenv()

r = requests.get(
    "https://frost.met.no/sources/v0.jsonld",
    auth=(os.getenv("FROST_CLIENT_ID"), "")
)

print(r.status_code)
print(r.json()["data"][0]["id"])