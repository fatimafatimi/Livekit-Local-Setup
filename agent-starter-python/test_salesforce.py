import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("SF_CLIENT_ID")
client_secret = os.getenv("SF_CLIENT_SECRET")
refresh_token = os.getenv("SF_REFRESH_TOKEN")

print("CLIENT:", (client_id or "")[:15])
print("REFRESH:", (refresh_token or "")[:15])
print("REFRESH LENGTH:", len(refresh_token or ""))

response = requests.post(
    "https://login.salesforce.com/services/oauth2/token",
    data={
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    },
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
