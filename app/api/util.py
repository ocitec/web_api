import re
from datetime import datetime
from app.api.db.collections import amadeus_flight_offers, amadeus_flight_pricing, airports_collection

class FlightUtil:
	
	def excludedCarrierCodes(self):
	    pass # list of excluded carrier

	
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


	async def aita_code_det(self, aita_code):
		det = await airports_collection.find_one({"iata_code": aita_code})

		if det:
		    det["_id"] = str(det["_id"])

		    return det

		return None


	def get_fare_details(self, flight_offer, segment_id):
		for traveler in flight_offer.get("travelerPricings", []):
		    for segment in traveler.get("fareDetailsBySegment", []):
		        if segment["segmentId"] == segment_id:
		            return {
		                "class": segment["class"],
		                "cabin": segment["cabin"],
		                "baggage": segment.get("includedCheckedBags", {}).get("quantity", 0),
		                "cabin_baggage": segment.get("includedCabinBags", {}).get("quantity", 0),
		                "fare_basis": segment.get("fareBasis", "Unknown"),
		                "is_refundable": "Yes" if "REFUNDABLE" in segment.get("fareBasis", "").upper() else "No"
		            }
		return {"class": "Unknown", "cabin": "Unknown", "baggage": "No baggage info", "fare_basis": "Unknown", "is_refundable": "Unknown"}


	def convert_date_to_time(self, value):
		# convert 2025-04-09T11:45:00 to HH:MM
		datetime_obj = datetime.fromisoformat(value)
		return datetime_obj.strftime("%H:%M")


	def convert_date(self, value):
		# convert 2025-04-09T11:45:00 to Aug 12, 2025
		datetime_obj = datetime.fromisoformat(value)
		return datetime_obj.strftime("%b %d, %Y")


	def convert_duration(self, duration):	    
		match = re.match(r'PT(\d+H)?(\d+M)?', duration)
		hours = match.group(1)[:-1] if match.group(1) else "0"
		minutes = match.group(2)[:-1] if match.group(2) else "0"

		return f"{hours}h {minutes}m"


	def calculate_layover(self, prev_arrival_time: str, next_departure_time: str) -> str:
		try:
		    arrival_time = datetime.strptime(prev_arrival_time, "%Y-%m-%dT%H:%M:%S")
		    departure_time = datetime.strptime(next_departure_time, "%Y-%m-%dT%H:%M:%S")
		    
		    if departure_time <= arrival_time:
		        return "0h 0m"

		    layover_duration = departure_time - arrival_time
		    total_minutes = int(layover_duration.total_seconds() // 60)
		    hours, minutes = divmod(total_minutes, 60)

		    return f"{hours}h {minutes}m"
		except (ValueError, TypeError):
		    return "Invalid time format"


	def get_airline_name(self, aita_code):
		return "carrier_data"



flightutils = FlightUtil()