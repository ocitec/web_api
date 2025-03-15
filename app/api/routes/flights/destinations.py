from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import destinations_collection
from app.api.services.auth_service import get_current_admin_user 
from app.api.models.destination import Destination

router = APIRouter()


@router.post("/destinations", tags=["Destinations"])
def create_destination(payload: Destination, user: Dict = Depends(get_current_admin_user)):
    """
    Create a new travel destination (Admin Only).
    """
    if payload.id in destinations_db:
        raise HTTPException(status_code=400, detail="Destination already exists.")
    
    destinations_db[payload.id] = payload.dict()
    return {"status": "success", "message": "Destination added successfully", "data": payload.dict()}

@router.get("/destinations", tags=["Destinations"], response_model=List[Destination])
def get_all_destinations():
    """
    Retrieve all destinations (Public).
    """
    return list(destinations_db.values())

@router.get("/destinations/{destination_id}", tags=["Destinations"], response_model=Destination)
def get_destination(destination_id: str):
    """
    Retrieve a specific destination by ID (Public).
    """
    if destination_id not in destinations_db:
        raise HTTPException(status_code=404, detail="Destination not found.")
    
    return destinations_db[destination_id]

@router.put("/destinations/{destination_id}", tags=["Destinations"])
def update_destination(destination_id: str, payload: Destination, user: Dict = Depends(get_current_admin_user)):
    """
    Update a destination by ID (Admin Only).
    """
    if destination_id not in destinations_db:
        raise HTTPException(status_code=404, detail="Destination not found.")

    destinations_db[destination_id] = payload.dict()
    return {"status": "success", "message": "Destination updated successfully", "data": payload.dict()}

@router.delete("/destinations/{destination_id}", tags=["Destinations"])
def delete_destination(destination_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Delete a destination by ID (Admin Only).
    """
    if destination_id not in destinations_db:
        raise HTTPException(status_code=404, detail="Destination not found.")

    del destinations_db[destination_id]
    return {"status": "success", "message": "Destination deleted successfully"}
