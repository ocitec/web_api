import requests
import os


AMADEUS_CLIENT_ID = "QUFhcFnUFOjBtusxWUd6rAX4xIiLFv7R"
AMADEUS_CLIENT_SECRET = "JW8rEvSznu31jgTE"
AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"

payload = {
    "grant_type": "client_credentials",
    "client_id": AMADEUS_CLIENT_ID,
    "client_secret": AMADEUS_CLIENT_SECRET
}


response = requests.post(url=AUTH_URL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
print(f"Response Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

if response.status_code == 200:
    print("✅ Authentication Successful:", response.json())
else:
    print("❌ Authentication Failed:", response.json())
