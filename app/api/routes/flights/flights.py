from fastapi import APIRouter, HTTPException, Body
from app.api.services.amadeus_service import amadeus_api
from bson import ObjectId
from app.api.models.flight_booking import FlightSearchRequest, FlightPricingRequest
from app.api.db.collections import amadeus_flight_offers

router = APIRouter()

@router.post("/search", tags=["Flights"], 
    summary="Flight  searches to find the cheapest flights for a given itinerary", 
    description="Flight search API with:\
                - One-way trips\
                - Round-trip flights\
                - Multi-city flights\
                - Cabin class selection"
    )

async def search_flights_endpoint(payload: FlightSearchRequest = Body(...)):
    
    # Validate trip type
    if payload.trip_type not in ["one-way", "round-trip", "multi-city"]:
        raise HTTPException(status_code=400, detail="Invalid trip_type. Use 'one-way', 'round-trip', or 'multi-city'.")

    # Validate for one-way & round-trip
    if payload.trip_type in ["one-way", "round-trip"]:
        if len(payload.origins) != 1 or len(payload.destinations) != 1 or len(payload.departure_dates) != 1 or len(payload.cabin) != 1:
            raise HTTPException(status_code=400, detail="For one-way and round-trip, provide exactly one origin, destination, departure date, and cabin class.")

    # Round-trip requires return date
    if payload.trip_type == "round-trip" and not payload.return_date:
        raise HTTPException(status_code=400, detail="Return date is required for round-trip.")

    # Validate multi-city inputs
    if payload.trip_type == "multi-city":
        if len(payload.origins) != len(payload.destinations) or len(payload.origins) != len(payload.departure_dates) or len(payload.origins) != len(payload.cabin):
            raise HTTPException(status_code=400, detail="For multi-city, the number of origins, destinations, departure dates, and cabins must match.")

    # Construct request payload
    origin_destinations = []
    
    if payload.trip_type in ["one-way", "round-trip"]:
        origin_destinations.append({
            "id": "1",
            "originLocationCode": payload.origins[0],
            "destinationLocationCode": payload.destinations[0],
            "departureDateTimeRange": {
                "date": payload.departure_dates[0]
            }
        })

        # Add return segment for round-trip
        if payload.trip_type == "round-trip":
            origin_destinations.append({
                "id": "2",
                "originLocationCode": payload.destinations[0],
                "destinationLocationCode": payload.origins[0],
                "departureDateTimeRange": {
                    "date": payload.return_date
                }
            })
    
    elif payload.trip_type == "multi-city":
        for i in range(len(payload.origins)):
            origin_destinations.append({
                "originLocationCode": payload.origins[i],
                "destinationLocationCode": payload.destinations[i],
                "departureDateTimeRange": {
                    "date":  payload.departure_dates[i]
                },
                # "cabin": payload.cabin[i]
            })

    results = await amadeus_api.search_flights(origin_destinations, 
                                        payload.adults, payload.children, 
                                        payload.infants, payload.cabin[0])

    
    if "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])

    return results



@router.post("/pricing", tags=["Flights"],
    summary="To confirm the real-time price before proceeding to book",
    description="The Flight pricing confirms the availability and final price \
    (including taxes and fees) of flights returned by the Flight Search Endpoint")
async def get_flight_pricing_route(payload: FlightPricingRequest = Body(...)):

    # try:
        # Find matching document in MongoDB
    record = await amadeus_flight_offers.find_one({"_id": ObjectId(payload.data_id)})

    if not record:
        raise HTTPException(status_code=404, detail="No matching flight offer found.") # return user to booking page

    # Find matching flight offer in `flight_offers.data`
    matching_offer = next(
        (
            offer for offer in record["flight_offers"]["data"]
            if offer.get("id") == payload.flight_offer.get("id")
            and offer.get("type") == payload.flight_offer.get("type")
            and offer.get("source") == payload.flight_offer.get("source")
        ),
        None
    )

    if not matching_offer:
        raise HTTPException(status_code=404, detail="Flight offer not found in stored data.")

    # Fetch pricing details from Amadeus API
    pricing_details = await amadeus_api.get_flight_pricing(matching_offer)

    return pricing_details

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))



