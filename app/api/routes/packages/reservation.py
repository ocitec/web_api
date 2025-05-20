from fastapi import APIRouter, HTTPException, Body
from app.api.db.collections import reservations_collection
from app.api.models.travelpackages import TravelPackageReservation
from typing import List

router = APIRouter()

@router.post("/reserve", tags=["Travel Packages"], response_model=TravelPackageReservation,
    summary="Create a reservation", description="Create a reservation for a travel package.")
async def create_reservation(reservation: TravelPackageReservation = Body(...)):
    try:
        await reservations_collection.insert_one(reservation.dict())
        # send email notification
        return reservation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/reservations/{package_id}", tags=["Travel Packages"], response_model=List[TravelPackageReservation],
    summary="Get reservations for a package", description="Retrieve all reservations for a specific travel package.")
async def get_reservations(package_id: str):
    try:
        reservations = await reservations_collection.find({"package_id": package_id}).to_list(100)
        return reservations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reservation/{reservation_id}", tags=["Travel Packages"], summary="Delete a reservation")
async def delete_reservation(reservation_id: str):
    try:
        result = await reservations_collection.delete_one({"id": reservation_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"message": "Reservation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
