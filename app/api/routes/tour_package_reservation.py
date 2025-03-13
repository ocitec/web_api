from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import tour_reservations_collection
from app.api.services.auth_service import get_current_admin_user 
from app.api.models.tour_packages import TourPackageReservation

router = APIRouter()

@router.post("/tour-package-reservations", tags=["Tour Package Reservations"])
def create_tour_reservation(payload: TourPackageReservation):
    """
    Create a new tour package reservation (Public).
    """
    if payload.id in tour_reservations_db:
        raise HTTPException(status_code=400, detail="Reservation already exists.")
    
    tour_reservations_db[payload.id] = payload.dict()
    return {"status": "success", "message": "Reservation created successfully", "data": payload.dict()}

@router.get("/tour-package-reservations", tags=["Tour Package Reservations"], response_model=List[TourPackageReservation])
def get_all_reservations(user: Dict = Depends(get_current_admin_user)):
    """
    Retrieve all reservations (Admin Only).
    """
    return list(tour_reservations_db.values())

@router.get("/tour-package-reservations/{reservation_id}", tags=["Tour Package Reservations"], response_model=TourPackageReservation)
def get_reservation(reservation_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Retrieve a specific reservation by ID (Admin Only).
    """
    if reservation_id not in tour_reservations_db:
        raise HTTPException(status_code=404, detail="Reservation not found.")
    
    return tour_reservations_db[reservation_id]

@router.put("/tour-package-reservations/{reservation_id}", tags=["Tour Package Reservations"])
def update_reservation(reservation_id: str, payload: TourPackageReservation, user: Dict = Depends(get_current_admin_user)):
    """
    Update a reservation by ID (Admin Only).
    """
    if reservation_id not in tour_reservations_db:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    tour_reservations_db[reservation_id] = payload.dict()
    return {"status": "success", "message": "Reservation updated successfully", "data": payload.dict()}

@router.delete("/tour-package-reservations/{reservation_id}", tags=["Tour Package Reservations"])
def delete_reservation(reservation_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Delete a reservation by ID (Admin Only).
    """
    if reservation_id not in tour_reservations_db:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    del tour_reservations_db[reservation_id]
    return {"status": "success", "message": "Reservation deleted successfully"}
