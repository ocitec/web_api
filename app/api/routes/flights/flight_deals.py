from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import flight_deals_collection
from app.api.services.auth_service import get_current_admin_user 
from app.api.models.flight_deals import FlightDeal

router = APIRouter()


@router.post("/flight-deals", tags=["Flight Deals"])
async def create_flight_deal(
    payload: FlightDeal, 
    user: Dict = Depends(get_current_admin_user)
):
    """
    Create a new flight deal (Admin Only).
    """
    existing_deal = await flight_deals_collection.find_one({"airline": payload.airline, "origin": payload.origin, "destination": payload.destination})
    
    if existing_deal:
        raise HTTPException(status_code=400, detail="Flight deal already exists.")

    insert_result = await flight_deals_collection.insert_one(payload.dict())

    if not insert_result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to insert flight deal.")

    return {"status": "success", "message": "Flight deal added successfully", "id": str(insert_result.inserted_id)}


@router.get("/flight-deals", tags=["Flight Deals"])
async def get_all_flight_deals():

    deals = await flight_deals_collection.find().to_list(None)

    for deal in deals:
        deal["_id"] = str(deal["_id"])  # Convert ObjectId to string for JSON serialization

    return {"status": "success", "data": deals}



@router.get("/flight-deals/{deal_id}", tags=["Flight Deals"])
async def get_flight_deal(deal_id: str):

    try:
        deal = await flight_deals_collection.find_one({"_id": ObjectId(deal_id)})

        if not deal:
            raise HTTPException(status_code=404, detail="Flight deal not found.")

        deal["_id"] = str(deal["_id"])
        return {"status": "success", "data": deal}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deal ID format.")


@router.put("/flight-deals/{deal_id}", tags=["Flight Deals"])
async def update_flight_deal(
    deal_id: str,
    payload: FlightDeal, 
    user: Dict = Depends(get_current_admin_user)
):
    """
    Update a flight deal by ID (Admin Only).
    """
    try:
        update_result = await flight_deals_collection.update_one(
            {"_id": ObjectId(deal_id)}, {"$set": payload.dict()}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Flight deal not found or no changes made.")

        return {"status": "success", "message": "Flight deal updated successfully"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deal ID format.")


@router.delete("/flight-deals/{deal_id}", tags=["Flight Deals"])
async def delete_flight_deal(
    deal_id: str, 
    user: Dict = Depends(get_current_admin_user)
):
    """
    Delete a flight deal by ID (Admin Only).
    """
    try:
        delete_result = await flight_deals_collection.delete_one({"_id": ObjectId(deal_id)})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Flight deal not found.")

        return {"status": "success", "message": "Flight deal deleted successfully"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid deal ID format.")