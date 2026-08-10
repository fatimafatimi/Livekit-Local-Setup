import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("SF_CLIENT_ID")
client_secret = os.getenv("SF_CLIENT_SECRET")
instance_url = os.getenv("SF_INSTANCE_URL")

print("Client ID loaded:", bool(client_id))
print("Client Secret loaded:", bool(client_secret))
print("Instance URL:", instance_url)

token_url = f"{instance_url}/services/oauth2/token"

response = requests.post(
    token_url,
    data={
        "grant_type": "client_credentials",
    },
    auth=(client_id, client_secret),
)

print("Status:", response.status_code)
print("Response:", response.text)