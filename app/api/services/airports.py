import requests
from pymongo import MongoClient
from app.config import AMADEUS_CLIENT_ID, API_AIRPORTS_URL

def fetch_airports_from_api():
    headers = {"Authorization": f"Bearer {AMADEUS_CLIENT_ID}"}
    response = requests.get(API_AIRPORTS_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Sync API data with DB
def update_airports():
    new_airports = fetch_airports_from_api()
    
    if new_airports:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["travel_db"]
        airports_collection = db["airports"]
        
        for airport in new_airports:
            airports_collection.update_one(
                {"iata_code": airport["iataCode"]},
                {"$set": {
                    "name": airport["name"],
                    "city": airport["address"]["cityName"],
                    "country": airport["address"]["countryName"]
                }},
                upsert=True  # Insert if not exists
            )

# Schedule this function as a cron job or FastAPI background task
# update_airports()