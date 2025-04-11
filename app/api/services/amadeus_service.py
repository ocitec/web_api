from fastapi import HTTPException
import os
import requests
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import time
import httpx
from datetime import datetime, timedelta
from app.config import AMADEUS_BASE_URL, AMADEUS_AUTH_URL, AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET
from app.api.db.collections import amadeus_flight_offers, amadeus_flight_pricing, amadeus_flight_bookings, airports_collection
from app.api.util import flightutils
from app.api.formatter import formatter
from app.api.pricing import pricing
from app.api.services.flightRules import flightrules
from app.api.services.helper import get_current_date, coy_profile, convertDateTime, iataCarrier, airportName, calculate_total_time


# Create a session
session = requests.Session()

# Define retry strategy
retry = Retry(
    total=5, 
    backoff_factor=1, 
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=frozenset({'GET', 'HEAD', 'POST'}) 
)

# Mount the adapter to retry on failed requests
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


class AmadeusEnterpriseAPI:
    def __init__(self):
        self.auth_url = AMADEUS_AUTH_URL
        self.base_url = AMADEUS_BASE_URL
        self.access_token = None
        self.token_expires_at = 0
        self.maxFlightOffers = 5

    
    def get_access_token(self):
        current_time = time.time() 

        if self.access_token and current_time < self.token_expires_at:
            return self.access_token  

        payload = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = session.post(self.auth_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data["expires_in"]
            return self.access_token
        else:
            raise Exception(f"Failed to authenticate: {response.json()}")


    def selection_rule(self, adults, children, infants):
        return adults >= 1 and infants <= adults

    
    async def make_search_request(self, endpoint: str, payload: dict):
        try:
            cached_offers = await flightutils.find_flight_in_db(payload)
            if cached_offers:
                
                cached_offers["flight_offers"]["inserted_id"] = cached_offers["_id"]
                data = formatter.format_flight_search_data(cached_offers["flight_offers"])

                return {
                    "status_code": 200,
                    "data": data
                }

            token = self.get_access_token() 
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = session.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                
                amadeus_data = response.json()

                flight_offer_data = {
                    "search_params": payload,
                    "flight_offers": amadeus_data,
                    "created_at": datetime.utcnow()
                }

                insert_result = await amadeus_flight_offers.insert_one(flight_offer_data)

                amadeus_data["inserted_id"] = insert_result.inserted_id

                data = formatter.format_flight_search_data(amadeus_data)                  

                return {
                    "status_code": 200,
                    "data": data
                }
                 
            else:
                return {
                    "status_code": response.status_code,
                    "message": f"Request failed: {response.json()}"
                }

        except Exception as e:
            return {
                "status_code": 500,
                "message": f"Error in make_search_request: {str(e)}"
            }


    
    def flight_travelers(self, travelers, passengers, passengers_type):
        for _ in range(passengers):
            if passengers_type == "INFANT":
                # Get the list of all existing adults
                adult_travelers = [t for t in travelers if t["travelerType"] == "ADULT"]
                
                if not adult_travelers:
                    return{
                        "status_code": 500,
                        "message": "At least one adult is required for an infant traveler."
                    }                    
                
                # Associate each infant with the next available adult
                associated_adult = adult_travelers[len(travelers) % len(adult_travelers)]
                
                travelers.append({
                    "id": str(len(travelers) + 1),
                    "travelerType": "HELD_INFANT",
                    "associatedAdultId": associated_adult["id"],
                    "age": 1,  # Default age, adjust as needed
                    "fareOptions": ["STANDARD"]
                })
            else:
                travelers.append({
                    "id": str(len(travelers) + 1),
                    "travelerType": passengers_type,
                    "fareOptions": ["STANDARD"]
                })
        
        return travelers


    async def search_flights(self, origin_destinations, adults=1, children=0, infants=0, cabin="ECONOMY",
                        flexible_dates=False, date_range=3, preferred_carriers: list = None, min_price: float = None, 
                        max_price: float = None, currency: str = "USD"
    ):
        
        if not self.selection_rule(adults, children, infants):
            return {
                "status_code": 400,
                "message": "Invalid passenger selection. Each infant must have an adult."
            }


        travelers = []

        travelers = self.flight_travelers(travelers, adults, "ADULT")
        travelers = self.flight_travelers(travelers, children, "CHILD") if children > 0 else travelers
        travelers = self.flight_travelers(travelers, infants, "INFANT") if infants > 0 else travelers

        # Construct search criteria
        search_criteria = {
            "maxFlightOffers": self.maxFlightOffers,
            "flightFilters": {
                "cabinRestrictions": [
                    {
                        "cabin": cabin,
                        "coverage": "MOST_SEGMENTS",
                        "originDestinationIds": ["1"]
                    }
                ],
                "carrierRestrictions": {
                    "excludedCarrierCodes": flightutils.excludedCarrierCodes()
                }
            }
        }

        # if preferred carriers selected
        if preferred_carriers:
            search_criteria["flightFilters"]["carrierRestrictions"]["includedCarrierCodes"] = preferred_carriers

        # if mininum or maximum price is selected 
        if min_price or max_price:
            price_filter = {}
            
            if currency != "USD":
                min_price = pricing.convert_currency(min_price, currency, "USD") if min_price else None
                max_price = pricing.convert_currency(max_price, currency, "USD") if max_price else None

            if min_price:
                price_filter["minPrice"] = f"{min_price:.2f}"
            if max_price:
                price_filter["maxPrice"] = f"{max_price:.2f}"
            
            search_criteria["flightFilters"]["price"] = price_filter


        if flexible_dates:
            for od in origin_destinations:
                od["departureDateTimeRange"]["dateWindow"] = {
                    "plusMinusDays": date_range
                }

        payload = {
            "currencyCode": "USD",
            "originDestinations": origin_destinations,
            "travelers": travelers,
            "sources": ["GDS"],
            "searchCriteria": search_criteria
        }
        
        return await self.make_search_request("/v2/shopping/flight-offers", payload)



    async def get_flight_pricing(self, flight_offer):
        
        payload = {
            "data": {
                "type": "flight-offers-pricing",
                "flightOffers": [flight_offer]
            }
        }

        try:
            
            token = self.get_access_token() 
            url = f"{self.base_url}/v1/shopping/flight-offers/pricing"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = session.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:

                amadeus_data = response.json()

                flight_pricing_data = {
                    "flight_pricing": amadeus_data,
                    "created_at": datetime.utcnow()
                }

                insert_result = await amadeus_flight_pricing.insert_one(flight_pricing_data)

                amadeus_data["inserted_id"] = insert_result.inserted_id

                data = await formatter.format_flight_pricing_data(amadeus_data)

                return {
                    "status_code": 200,
                    "data": data
                }

            else:
                return {
                    "status_code": response.status_code,
                    "message": f"Request failed: {response.json()}"
                }


        except Exception as e:
            return {
                "status_code": 500,
                "message": f"Error in get_flight_pricing: {str(e)}"
            }


    
    async def flight_issue(self, orderData):
        if orderData:
            # check if bookig ID exist in DB
            bookingId = orderData["order_id"]

            isExist = await amadeus_flight_bookings.find_one({ "data.id": bookingId})

            if isExist:
                isExist["_id"] = str(isExist["_id"])
                token = self.get_access_token() 

                payload = {
                    "data": {
                        "formOfPayments": [
                            orderData["formOfPayment"]
                        ]
                    }
                }

                url = f"{self.base_url}/v1/booking/flight-orders/{bookingId}/issuance"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                response = session.post(url, json=payload, headers=headers)

                if response.status_code in [200, 201]:

                    amadeus_data = response.json()

                    return {
                        "status": 200,
                        "message": amadeus_data
                    }
                else:
                    return {
                        "status_code": response.status_code,
                        "message": f"Request failed: {response.json()}"
                    }                    

            else:
                return {
                    "status": 404,
                    "message": "Booking Id not found."
                }

        else:
            return False

# Create an instance of the API
amadeus_api = AmadeusEnterpriseAPI()
