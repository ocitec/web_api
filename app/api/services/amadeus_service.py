from fastapi import HTTPException
import os
import requests
import re
import time
import httpx
from datetime import datetime, timedelta
from app.config import AMADEUS_BASE_URL, AMADEUS_AUTH_URL, AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET
from app.api.db.collections import amadeus_flight_offers, amadeus_flight_pricing, amadeus_flight_bookings
from app.api.services.helper import get_current_date, coy_profile

# Fetch exchange rate (USD → NGN)
USD_TO_NGN = 1500 # Get live amadeus rate

class AmadeusEnterpriseAPI:
    def __init__(self):
        self.auth_url = AMADEUS_AUTH_URL
        self.base_url = AMADEUS_BASE_URL
        self.access_token = None
        self.token_expires_at = 0

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

        response = requests.post(self.auth_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expires_at = time.time() + token_data["expires_in"]
            return self.access_token
        else:
            raise Exception(f"Failed to authenticate: {response.json()}")


    async def find_flight_in_db(self, search_params: dict):
        existing_offer = await amadeus_flight_offers.find_one({"search_params": search_params})

        if existing_offer:
            return existing_offer
        return None


    async def find_flight_pricing_in_db(self, search_params: dict):
        flight_offer_id = search_params.get("flightOfferId")

        query = {"flight_pricing.data.type": "flight-offers-pricing"}

        if flight_offer_id:
            query["flight_pricing.data.flightOffers"] = {
                "$elemMatch": {"id": flight_offer_id}
            }

        existing_pricing = await amadeus_flight_pricing.find_one(query)

        return existing_pricing if existing_pricing else None



    async def make_search_request(self, method: str, endpoint: str, data: dict):
        try:
            cached_offers = await self.find_flight_in_db(data)
            if cached_offers:
                
                cached_offers["flight_offers"]["inserted_id"] = cached_offers["_id"]
                return self.format_flight_search_data(cached_offers["flight_offers"])

            token = self.get_access_token() 
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.request(method, url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                
                amadeus_data = response.json()

                flight_offer_data = {
                    "search_params": data,
                    "flight_offers": amadeus_data,
                    "created_at": datetime.utcnow()
                }
                insert_result = await amadeus_flight_offers.insert_one(flight_offer_data)

                amadeus_data["inserted_id"] = insert_result.inserted_id

                return self.format_flight_search_data(amadeus_data)                  
                 
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Request failed: {response.json()}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in make_search_request: {str(e)}")


    def convert_duration(self, duration):
        
        match = re.match(r'PT(\d+H)?(\d+M)?', duration)
        hours = match.group(1)[:-1] if match.group(1) else "0"
        minutes = match.group(2)[:-1] if match.group(2) else "0"
        return f"{hours}h {minutes}m"

    def convert_usd_to_ngn(self, usd_amount):
        
        return round(float(usd_amount) * USD_TO_NGN, 2)

    def apply_markup(self, price, markup_percentage=5):
        
        return round(float(price) * (1 + markup_percentage / 100), 2)

    def calculate_layover(self, prev_arrival_time, next_departure_time):
        
        arrival_time = datetime.strptime(prev_arrival_time, "%Y-%m-%dT%H:%M:%S")
        departure_time = datetime.strptime(next_departure_time, "%Y-%m-%dT%H:%M:%S")
        
        layover_duration = departure_time - arrival_time
        hours, remainder = divmod(layover_duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{int(hours)}h {int(minutes)}m"

    def flight_rule(self, refundable=False):
        if refundable == True:
            return "Fare Rule for refundable"
        else:
            return "Fare Rule for nonrefundable"

    def get_fare_details(self, flight_offer, segment_id):
        for traveler in flight_offer.get("travelerPricings", []):
            for segment in traveler.get("fareDetailsBySegment", []):
                if segment["segmentId"] == segment_id:
                    return {
                        "class": segment["class"],
                        "cabin": segment["cabin"],
                        "baggage": segment.get("includedCheckedBags", {}).get("quantity", "Unknown"),
                        "fare_basis": segment.get("fareBasis", "Unknown"),
                        "is_refundable": "Yes" if "REFUNDABLE" in segment.get("fareBasis", "").upper() else "No"
                    }
        return {"class": "Unknown", "cabin": "Unknown", "baggage": "No baggage info", "fare_basis": "Unknown", "is_refundable": "Unknown"}

    def format_flight_search_data(self, response_data):
        
        formatted_results = []
        dictionaries = response_data.get("dictionaries", {})
        _id = response_data.get("inserted_id", {})

        for offer in response_data.get("data", []):
            formatted_offer = {
                "type": offer["type"],
                "id": offer["id"],
                "source": offer["source"],
                "instantTicketingRequired": offer["instantTicketingRequired"],
                "one_way": offer["oneWay"],
                "is_up_sell_offer": offer["isUpsellOffer"],
                "last_ticketing_date": offer["lastTicketingDate"],
                "last_ticketing_time": offer["lastTicketingDateTime"],
                "available_seats": offer["numberOfBookableSeats"],
                "price": {
                    "currency": "NGN", 
                    "grand_total": self.convert_usd_to_ngn(self.apply_markup(offer["price"]["grandTotal"])),
                    "base_price": self.convert_usd_to_ngn(self.apply_markup(offer["price"]["base"])),
                },
                "pricing_options": {
                    "fare_type": [
                        offer["pricingOptions"]["fareType"]
                    ],
                    "included_checked_BagOnly": offer["pricingOptions"]["includedCheckedBagsOnly"]
                },
                "validating_airline": offer["validatingAirlineCodes"],
                "itineraries": []
            }

            for itinerary in offer["itineraries"]:
                formatted_itinerary = {
                    "duration": self.convert_duration(itinerary["duration"]),
                    "segments": []
                }

                prev_arrival_time = None 

                for segment in itinerary["segments"]:
                    departure_airport_code = segment["departure"]["iataCode"]
                    arrival_airport_code = segment["arrival"]["iataCode"]
                    airline_code = segment["carrierCode"]


                    fare_details = self.get_fare_details(offer, segment["id"])

                    formatted_segment = {
                        "departure": {
                            "airport": {
                                "code": departure_airport_code,
                                "name": dictionaries["locations"].get(departure_airport_code, {}).get("countryCode", "Unknown Airport")
                            },
                            "terminal": segment["departure"].get("terminal", "N/A"),
                            "time": segment["departure"]["at"]
                        },
                        "arrival": {
                            "airport": {
                                "code": arrival_airport_code,
                                "name": dictionaries["locations"].get(arrival_airport_code, {}).get("countryCode", "Unknown Airport")
                            },
                            "terminal": segment["arrival"].get("terminal", "N/A"),
                            "time": segment["arrival"]["at"]
                        },
                        "flight_number": f"{airline_code}{segment['number']}",
                        "airline": {
                            "code": airline_code,
                            "name": dictionaries["carriers"].get(airline_code, "Unknown Airline"),
                            "logo": f"https://www.gstatic.com/flights/airline_logos/70px/{airline_code}.png"
                        },
                        "aircraft": dictionaries["aircraft"].get(segment["aircraft"]["code"], "Unknown Aircraft"),
                        "operating_airline": segment.get("operating", {}).get("carrierCode", ""),
                        "stops": segment["numberOfStops"],
                        "segment_class": fare_details.get("class", "Unknown"),
                        "travel_class": fare_details.get("cabin", "Unknown"),
                        "baggage": fare_details.get("baggage", "No baggage info"),
                        "fare_basis": fare_details.get("fare_basis", "Unknown"),
                        "is_refundable": fare_details.get("is_refundable", "Unknown")
                    }

                    if prev_arrival_time:
                        layover_duration = self.calculate_layover(prev_arrival_time, segment["departure"]["at"])
                        formatted_segment["layover_duration"] = layover_duration

                    prev_arrival_time = segment["arrival"]["at"]  

                    formatted_itinerary["segments"].append(formatted_segment)

                formatted_offer["itineraries"].append(formatted_itinerary)

            formatted_results.append(formatted_offer)

        formatted_results.append(dictionaries)

        formatted_results.append({"data_id": str(_id)})

        return formatted_results

    def format_flight_pricing_data(self, response_data):
        
        formatted_pricing = []
        dictionaries = response_data.get("dictionaries", {})
        _id = response_data.get("inserted_id", {})

        for offer in response_data.get("data", {}).get("flightOffers", []):
            formatted_offer = {
                "flight_id": offer["id"],
                "source": offer["source"],
                "instant_Ticketing_Required": offer["instantTicketingRequired"],
                "last_ticketing_date": offer["lastTicketingDate"],
                "price": {
                    "currency": "NGN",
                    "total": self.convert_usd_to_ngn(self.apply_markup(offer["price"]["grandTotal"])),
                    "base": self.convert_usd_to_ngn(self.apply_markup(offer["price"]["base"]))
                },
                "validating_airline": offer["validatingAirlineCodes"],
                "traveler_pricing": []
            }

            for traveler in offer["travelerPricings"]:
                traveler_details = {
                    "traveler_id": traveler["travelerId"],
                    "fare_option": traveler["fareOption"],
                    "traveler_type": traveler["travelerType"],
                    "total_price": self.convert_usd_to_ngn(self.apply_markup(traveler["price"]["total"])),
                    "segments": []
                }

                for segment in traveler["fareDetailsBySegment"]:
                    segment_details = {
                        "segment_id": segment["segmentId"],
                        "cabin": segment["cabin"],
                        "class": segment["class"],
                        "fare_basis": segment["fareBasis"],
                        "baggage": segment.get("includedCheckedBags", {}).get("quantity", "Unknown"),
                        "is_refundable": "Yes" if "REFUNDABLE" in segment.get("fareBasis", "").upper() else "No"
                    }
                    traveler_details["segments"].append(segment_details)

                formatted_offer["traveler_pricing"].append(traveler_details)

            formatted_pricing.append(formatted_offer)

        formatted_pricing.append(dictionaries)

        formatted_pricing.append({"data_id": str(_id)})

        return formatted_pricing

    def selection_rule(self, adults, children, infants):
        
        if infants > adults:
            return False
        if adults < 1:
            return False
        return True

    def flight_travelers(self, travelers, passengers, passengers_type):
        
        for _ in range(passengers):
            travelers.append({
                "id": str(len(travelers) + 1),
                "travelerType": passengers_type, 
                # "fareOptions": ["STANDARD"]
            })
        return travelers

    def maxFlightOffers(self):
        
        return 5

    def excludedCarrierCodes(self):
        pass

    def convert_currency(self, amount, from_currency, to_currency):
        if not amount:
            return None
        return round(currency_rates.convert(from_currency, to_currency, amount), 2)


    async def search_flights(self, origin_destinations, adults=1, children=0, infants=0, cabin="ECONOMY",
                        flexible_dates=False, date_range=3, preferred_carriers: list = None, min_price: float = None, 
                        max_price: float = None, currency: str = "USD"
    ):
        
        if not self.selection_rule(adults, children, infants):
            raise HTTPException(status_code=400, detail="Invalid passenger selection. Each infant must have an adult.")


        travelers = []

        travelers = self.flight_travelers(travelers, adults, "ADULT")
        travelers = self.flight_travelers(travelers, children, "CHILD") if children > 0 else travelers
        travelers = self.flight_travelers(travelers, infants, "INFANT") if infants > 0 else travelers

        # Construct search criteria
        search_criteria = {
            "maxFlightOffers": self.maxFlightOffers(),
            "flightFilters": {
                "cabinRestrictions": [
                    {
                        "cabin": cabin,
                        "coverage": "MOST_SEGMENTS",
                        "originDestinationIds": ["1"]
                    }
                ],
                "carrierRestrictions": {
                    "excludedCarrierCodes": self.excludedCarrierCodes()
                }
            }
        }

        if preferred_carriers:
            search_criteria["flightFilters"]["carrierRestrictions"]["includedCarrierCodes"] = preferred_carriers

        if min_price or max_price:
            price_filter = {}
            
            if currency != "USD":
                min_price = self.convert_currency(min_price, currency, "USD") if min_price else None
                max_price = self.convert_currency(max_price, currency, "USD") if max_price else None

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
        
        return await self.make_search_request("POST", "/v2/shopping/flight-offers", payload)



    async def get_flight_pricing(self, flight_offer):
        cached_pricing = await self.find_flight_pricing_in_db(flight_offer)
        if cached_pricing:
            cached_pricing["flight_pricing"]["inserted_id"] = cached_pricing["_id"]
            return self.format_flight_pricing_data(cached_pricing["flight_pricing"])

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

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:

                amadeus_data = response.json()

                flight_pricing_data = {
                    "flight_pricing": amadeus_data,
                    "created_at": datetime.utcnow()
                }

                insert_result = await amadeus_flight_pricing.insert_one(flight_pricing_data)

                amadeus_data["inserted_id"] = insert_result.inserted_id

                return self.format_flight_pricing_data(amadeus_data)

            else:
                raise HTTPException(status_code=response.status_code, detail=f"Request failed: {response.json()}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in get_flight_pricing: {str(e)}")


    async def book_flight_order(self, flight_offer: dict, travelers: list):
        
        try:
            
            if "data" not in flight_offer or "flightOffers" not in flight_offer["data"]:
                raise HTTPException(status_code=400, detail="Invalid flight offer format.")

            # get coy information
            coy = await coy_profile()


            payload = {
                "data": {
                    "type": "flight-order",
                    "flightOffers": flight_offer["data"]["flightOffers"], 
                    "travelers": travelers, 
                    "remark": {
                        "general": [
                            {
                                "subType": "OCI",
                                "text": f"ONLINE BOOKING FROM {coy.get("coy_name", "OCI")}" 
                            }
                        ]
                    },
                    "ticketingAgreement": {
                        "option": "DELAY_TO_CANCEL",
                        "delay": "2D" 
                    },
                    
                      "contacts": [
                        {
                          "addresseeName": {
                            "firstName": f"{coy.get("contact_firstname", "Busayo")}",
                            "lastName": f"{coy.get("contact_lastname", "Afolabi")}",
                          },
                          "companyName": "OCI",
                          "purpose": "STANDARD",
                          "phones": [
                            {
                              "deviceType": "LANDLINE",
                              "countryCallingCode": f"{coy.get("country_code", "234")}",
                              "number": f"{coy.get("agency_phone_number", "")}"
                            },
                            {
                              "deviceType": "MOBILE",
                              "countryCallingCode": f"{coy.get("country_code", "234")}",
                              "number": f"{coy.get("agency_phone_number", "234")}",
                            }
                          ],
                          "emailAddress": f"{coy.get("agency_email", "info@ocitravels.com")}",
                          "address": {
                            "lines": [
                              f"{coy.get("address_1", "Lekki Phase 1")}"
                            ],
                            "postalCode": f"{coy.get("postal_code", "100001")}",
                            "cityName": f"{coy.get("city", "Lagos")}",
                            "countryCode": f"{coy.get("countryIataCode", "NG")}"
                          }
                        }
                      ]                  

                }
            }


            token = self.get_access_token()
            url = f"{self.base_url}/v1/booking/flight-orders"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60)

            # Handle response
            if response.status_code == 201:
                booking_data = response.json()

                # source
                booking_data['source'] = "Amadeus"
                booking_data['date'] = get_current_date()

                # add info
                payment_info = {
                    "status": "pending",
                    "payment_reference_id": None,
                    "payment_id": None,
                    "payment_date": None
                }

                booking_data["payment"] = payment_info
                booking_data["status"] = "booked"

                # save booking data
                insert_result = await amadeus_flight_bookings.insert_one(booking_data)

                return self.format_flight_booking(booking_data)  # Format booking response
            else:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to book flight: {response.json()}")

        except HTTPException:
            raise  
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error booking flight: {str(e)}")


    def format_flight_booking(self, response_data):
        
        booking_data = response_data.get("data", {})
        payment_data = response_data.get("payment", {})
        status = response_data.get("status")

        formatted_booking = {
            "booking_reference": booking_data.get("id"),
            "status": status,
            "date": response_data.get("date"),
            "associated_records": booking_data.get("associatedRecords", []),
            "flight_offers": [],
            "travelers": []
        }

        for offer in booking_data.get("flightOffers", []):
            formatted_booking["flight_offers"].append({
                "flight_id": offer["id"],
                "source": offer["source"],
                "validating_airline": offer["validatingAirlineCodes"]
            })

        for traveler in booking_data.get("travelers", []):
            formatted_booking["travelers"].append({
                "traveler_id": traveler["id"],
                "name": f"{traveler['name']['firstName']} {traveler['name']['lastName']}",
                "date_of_birth": traveler["dateOfBirth"],
                "gender": traveler["gender"],
                "email": traveler["contact"]["emailAddress"],
                "phone": f"{traveler['contact']['phones'][0]['countryCallingCode']}{traveler['contact']['phones'][0]['number']}" if "phones" in traveler["contact"] and traveler["contact"]["phones"] else "N/A",
                "documents": traveler.get("documents", [])
            })

        payment_details = {
            "payment_id" : payment_data['payment_id'],
            "payment_status" : payment_data['status'],
            "payment_reference_id" : payment_data['payment_reference_id']
        }
        
        formatted_booking['payment'] = payment_details

        return formatted_booking

        
    
# Create an instance of the API
amadeus_api = AmadeusEnterpriseAPI()
