import httpx
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from app.api.db.collections import amadeus_flight_bookings
from app.api.services.amadeus_service import AmadeusEnterpriseAPI
from app.api.services.helper import coy_profile
from app.api.services.email_service import email_service

class FlightBookingService(AmadeusEnterpriseAPI):
    
    def __init__(self):
        super().__init__()
    
    async def book_flight_order(self, flight_offer: dict, travelers: list):
        """Handles the flight booking process, ensuring updated flight segment details before booking."""
    
        try:
            # Validate flight offer format
            if not flight_offer.get("data") or "flightOffers" not in flight_offer["data"]:
                raise HTTPException(status_code=400, detail="Invalid flight offer format.")

            # Fetch latest flight details before proceeding
            latest_flight_offer = await self.get_latest_flight_details(flight_offer)

            # Ensure segment times are still valid
            if not self.validate_segments(flight_offer["data"]["flightOffers"], latest_flight_offer["data"]["flightOffers"]):
                raise HTTPException(status_code=400, detail="Itinerary schedule change detected. Flight segments have been updated.")

            # Get company profile
            coy = await coy_profile()

            # Construct booking payload
            payload = self.construct_payload(latest_flight_offer, travelers, coy)

            # Make request to Amadeus API
            response = await self.send_booking_request(payload)

            # Process the response and save booking data
            return await self.handle_booking_response(response)

        except HTTPException as e:
            raise e  # Re-raise FastAPI exceptions for proper HTTP response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error booking flight: {str(e)}")


    async def get_latest_flight_details(self, flight_offer: dict):
        """Fetches the latest flight details to ensure segment times are still valid."""
        token = self.get_access_token()
        url = f"{self.base_url}/v1/shopping/flight-offers/pricing"  # Amadeus flight-offers-pricing API
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json={"data": flight_offer["data"]}, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch the latest flight details. Try again.")


    def validate_segments(self, original_segments: list, latest_segments: list) -> bool:
        """Validates that flight segment times match the latest availability."""
        if len(original_segments) != len(latest_segments):
            return False  # Segment count mismatch
        
        for orig, latest in zip(original_segments, latest_segments):
            if orig.get("departureDateTime") != latest.get("departureDateTime") or \
               orig.get("arrivalDateTime") != latest.get("arrivalDateTime"):
                return False  # Segment time mismatch detected

        return True


    def construct_payload(self, flight_offer: dict, travelers: list, coy: dict) -> dict:
        """Constructs the flight booking payload."""
        return {
            "data": {
                "type": "flight-order",
                "flightOffers": flight_offer["data"]["flightOffers"],
                "travelers": travelers,
                "remark": {
                    "general": [
                        {
                            "subType": "OCI",
                            "text": f"ONLINE BOOKING FROM {coy.get('coy_name', 'OCI')}"
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
                            "firstName": coy.get("contact_firstname", "Busayo"),
                            "lastName": coy.get("contact_lastname", "Afolabi"),
                        },
                        "companyName": "OCI",
                        "purpose": "STANDARD",
                        "phones": [
                            {
                                "deviceType": "LANDLINE",
                                "countryCallingCode": coy.get("country_code", "234"),
                                "number": coy.get("agency_phone_number", ""),
                            },
                            {
                                "deviceType": "MOBILE",
                                "countryCallingCode": coy.get("country_code", "234"),
                                "number": coy.get("agency_phone_number", "234"),
                            }
                        ],
                        "emailAddress": coy.get("agency_email", "info@ocitravels.com"),
                        "address": {
                            "lines": [coy.get("address_1", "Lekki Phase 1")],
                            "postalCode": coy.get("postal_code", "100001"),
                            "cityName": coy.get("city", "Lagos"),
                            "countryCode": coy.get("countryIataCode", "NG"),
                        }
                    }
                ]
            }
        }


    async def send_booking_request(self, payload: dict):
        """Sends the flight booking request to Amadeus API."""
        token = self.get_access_token()
        url = f"{self.base_url}/v1/booking/flight-orders"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60) as client:
            return await client.post(url, json=payload, headers=headers)


    async def handle_booking_response(self, response):
        """Processes the booking response, saves it in the database, and returns the formatted result."""

        if response.status_code == 201:
            booking_data = response.json()
            booking_data.update({
                "source": "Amadeus",
                "date": datetime.utcnow().isoformat(),
                "payment": {
                    "status": "pending",
                    "payment_reference_id": None,
                    "payment_id": None,
                    "payment_date": None
                },
                "status": "Booked"
            })

            # Save booking data
            insert_result = await amadeus_flight_bookings.insert_one(booking_data)
            booking_data["bookingId"] = str(insert_result.inserted_id)

            await self.handle_email(str(insert_result.inserted_id))

            return await self.format_flight_booking(booking_data)
        
        # Handle error response
        response_data = response.json()
        raise HTTPException(status_code=response.status_code, detail=f"Failed to book flight: {response_data}")


    async def handle_email(self, booking_id):
        # fetch booking record
        bookingDetails = await amadeus_flight_bookings.find_one({"_id": ObjectId(booking_id)})
        
        # send email notification 
        c = await email_service.send_email(bookingDetails)
        return c



