from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import tour_packages_collection
from app.api.services.auth_service import get_current_admin_user  
from app.api.models.tour_packages import TourPackage, TourPackageUpdate

router = APIRouter()


@router.post("/tour-packages", tags=["Tour Packages"])
async def create_tour_package(payload: TourPackage, user: Dict = Depends(get_current_admin_user)):
    """
    Create a new tour package (Admin Only).
    """
    package_data = payload.dict()
    result = await tour_packages_collection.insert_one(package_data)
    
    if result.inserted_id:
        return {"status": "success", "message": "Tour package created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create tour package")
    


@router.get("/tour-packages", tags=["Tour Packages"], response_model=List[TourPackage])
async def get_all_tour_packages():
    """
    Retrieve all tour packages (Public).
    """
    packages = await tour_packages_collection.find().to_list(None)
    return {"status": "success", "data": packages}


@router.get("/tour-packages/{package_id}", tags=["Tour Packages"], response_model=TourPackage)
def get_tour_package(package_id: str):
    """
    Retrieve a specific tour package by ID (Public).
    """
    if package_id not in tour_packages_db:
        raise HTTPException(status_code=404, detail="Tour package not found.")
    
    return tour_packages_db[package_id]

@router.put("/tour-packages/{package_id}", tags=["Tour Packages"])
async def update_tour_package(package_id: str, payload: TourPackageUpdate, user: Dict = Depends(get_current_admin_user)):
    """
    Update a tour package by ID (Admin Only).
    """
    # Validate ObjectId
    if not ObjectId.is_valid(package_id):
        raise HTTPException(status_code=400, detail="Invalid package ID format.")

    update_data = {k: v for k, v in payload.dict().items() if v is not None}

    result = await tour_packages_collection.update_one(
        {"_id": ObjectId(package_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tour package not found.")

    return {"status": "success", "message": "Tour package updated successfully"}

@router.delete("/tour-packages/{package_id}", tags=["Tour Packages"])
async def delete_tour_package(package_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Delete a tour package by ID (Admin Only).
    """
    result = await tour_packages_collection.delete_one({"id": package_id})
    
    if result.deleted_count == 1:
        return {"status": "success", "message": "Tour package deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Tour package not found")
