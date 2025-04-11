from fastapi import APIRouter, HTTPException, Depends, Path, Query
from bson import ObjectId, errors
from typing import Dict
# from app.api.services.amadeus_service import AmadeusEnterpriseAPI
from app.api.services.flightBookingService import FlightBookingService
from app.api.services.auth_service import get_current_admin_user
from app.api.db.collections import flight_bookings_collection, amadeus_flight_pricing, amadeus_flight_bookings
from app.api.models.flight_booking import FlightBookingRequest, FlightBookingOrder, FlightOrderIssuarance
import logging


router = APIRouter()
amadeus_api = FlightBookingService()


@router.post("/flight-order", tags=["Flights"],
    summary="The Flight Orders endpoint performs the final booking for a chosen flight",
    description="The endpoint provides a unique booking ID and reservation details once the reservation is completed.")
async def book_flight_order_route(
    payload: FlightBookingRequest
):
 
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
        print(booking_details);

        return booking_details

    except HTTPException:
        raise  # Re-raise existing HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking flight: {str(e)}")



@router.post("/order_issue", tags=["Flights"], summary="", description="")
async def ticket(request: FlightOrderIssuarance):
    try:
        ticket = await amadeus_api.flight_issue(orderData=request.dict())

        if ticket == False:
            raise HTTPException(status_code=500, detail=f"Error Issuring Ticket: {str(e)}")
        
        return ticket

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Issuring Ticket: {str(e)}")




@router.get(
    "/booking-order", 
    tags=["Flights"],
    summary="Fetch booking record",
    description="This endpoint fetches a booking record for modification."
)
async def get_bookings(
    booking_id: str = Query(..., description="The booking ID"),
    reference: str = Query(..., description="The reference ID")
):

    try:
        booking_record = await amadeus_flight_bookings.find_one(
            { 
                "_id": ObjectId(booking_id), 
                "data.id": reference  # Fixed array notation
            }
        )

        if not booking_record:
            raise HTTPException(status_code=404, detail="Booking record not found")

        # Convert ObjectId to string safely
        booking_record["id"] = str(booking_record["_id"])
        del booking_record["_id"]

        return {"status_code": 200, "data": booking_record}

    except Exception as e:
        logging.error(f"Error fetching record: {str(e)}")
        return {
            "status_code": 500,
            "message": "Internal server error"
        }



@router.delete("/cancel/{booking_id}", tags=["Flights"],
    summary="Cancel Booking",
    description="This endpoint cancel booking record")
def cancel_flight_order(booking_id: str = Path(..., example="eJzTd9cPd3J3CgwGAAtcAmw%3D"), user: Dict = Depends(get_current_admin_user)):
    pass


