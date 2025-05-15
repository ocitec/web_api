import requests
from app.config import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET


# client_id = "YOUR_API_KEY"
# client_secret = "YOUR_API_SECRET"

def get_access_token():
    url = "https://test.travel.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }

    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json().get("access_token")

def get_exchange_rate(from_currency, to_currency, amount=1):
    token = get_access_token()
    url = f"https://test.travel.api.amadeus.com/v1/reference-data/locations/currency-conversion?from={from_currency}&to={to_currency}&amount={amount}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data")
        print("Exchange Rate:", data)
        return data
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}")
        print(f"Response: {err.response.json()}")

