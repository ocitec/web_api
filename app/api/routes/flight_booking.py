from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId, errors
from typing import Dict
from app.api.services.amadeus_service import AmadeusEnterpriseAPI
from app.api.services.auth_service import get_current_admin_user
from app.api.db.collections import flight_bookings_collection, amadeus_flight_pricing
from app.api.models.flight_booking import FlightBookingRequest

router = APIRouter()
amadeus_api = AmadeusEnterpriseAPI()


@router.post("/flight-order", tags=["Flight Booking"])
async def book_flight_order_route(
    payload: FlightBookingRequest
):
    """
    Books a flight and returns the flight order details.
    """
    try:
        # Validate ObjectId before query
        try:
            object_id = ObjectId(payload.data_id)
        except errors.InvalidId:
            raise HTTPException(status_code=400, detail="Invalid data_id format.")

        # Retrieve flight pricing record
        record = await amadeus_flight_pricing.find_one({"_id": object_id})
        if not record:
            raise HTTPException(status_code=404, detail="No matching flight offer found.")

        # Extract flight offer details
        flight_offers = record["flight_pricing"]["data"].get("flightOffers", [])
        if not flight_offers:
            raise HTTPException(status_code=404, detail="No flight offers found in record.")

        # Validate number of travelers
        no_of_travelers = len(flight_offers[0]["travelerPricings"])
        if len(payload.travelers) != no_of_travelers:
            raise HTTPException(status_code=409, detail="Number of travelers mismatch.")

        # Process booking
        booking_details = await amadeus_api.book_flight_order(record["flight_pricing"], payload.travelers)

        return booking_details

    except HTTPException:
        raise  # Re-raise existing HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking flight: {str(e)}")



@router.get("/bookings", tags=["Flight Booking"])
async def get_bookings():

    return {"status": "success", "data": "bookings Data"}



@router.delete("/cancel/{booking_id}", tags=["Flight Booking"])
def cancel_flight_order(booking_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Cancels a flight booking (Admin Only).
    """
    pass


