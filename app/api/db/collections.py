from app.database import database
import pymongo

airports_collection = database["airports"]
carrier_collection = database["carriers"]
amadeus_flight_offers = database["amadeus_flight_offers"]
amadeus_flight_pricing = database["amadeus_flight_pricing"]
amadeus_flight_bookings = database["amadeus_flight_bookings"]
about_collection = database["about_us"]
destinations_collection = database["destinations"]
flight_bookings_collection = database["flight_bookings"]
flight_deals_collection = database["flight_deals"]
tour_reservations_collection = database["tour_reservations"]
tour_packages_collection = database["tour_packages"]
visa_collection = database["visa"]

agencymgt_collection = database["agencymgt"]
currency_collection = database["currency"]
payment_collection = database["payment"]


async def create_ttl_index():
    """
    Creates TTL indexes for `amadeus_flight_offers` and `amadeus_flight_pricing` collections.
    - `amadeus_flight_offers`: Expires after 1 hour (3600 seconds)
    - `amadeus_flight_pricing`: Expires after 15 minutes (900 seconds)
    """

    try:
        await amadeus_flight_offers.create_index(
            [("created_at", pymongo.ASCENDING)], expireAfterSeconds=3600
        )
        await amadeus_flight_pricing.create_index(
            [("created_at", pymongo.ASCENDING)], expireAfterSeconds=900
        )
        # print("✅ TTL indexes created successfully!")
    
    except Exception as e:
    	pass
        # print(f"❌ Error creating TTL indexes: {str(e)}")