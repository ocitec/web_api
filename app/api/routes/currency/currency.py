from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from typing import Dict, List
from app.api.db.collections import currency_collection
from app.api.services.auth_service import get_current_admin_user
from app.api.models.currency import Currency

router = APIRouter()

# Add a new currency
@router.post("/currency", tags=["Currency"])
async def add_currency(request: Currency, user: Dict = Depends(get_current_admin_user)):
    """
    Add a new currency (Admin Only).
    """
    try:
        insert_record = await currency_collection.insert_one(request.dict())

        return {
            "status": "success",
            "id": str(insert_record.inserted_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get all currencies
@router.get("/currencies", tags=["Currency"])
async def get_all_currencies():
    """
    Retrieve all currencies.
    """
    try:
        currencies = await currency_collection.find().to_list(length=None)

        if not currencies:
            raise HTTPException(status_code=404, detail="No currency records found.")

        # Convert ObjectId to string
        for currency in currencies:
            currency["_id"] = str(currency["_id"])

        return {"status": "success", "data": currencies}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Get a single currency by ID
@router.get("/currency/{currency_id}", tags=["Currency"], response_model=Dict)
async def get_currency_by_id(currency_id: str):
    """
    Retrieve a currency by its ID.
    """
    try:
        currency_data = await currency_collection.find_one({"_id": ObjectId(currency_id)})

        if not currency_data:
            raise HTTPException(status_code=404, detail="Currency not found.")

        currency_data["_id"] = str(currency_data["_id"])
        return {"status": "success", "data": currency_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Update a currency by ID
@router.put("/currency/{currency_id}", tags=["Currency"])
async def update_currency(currency_id: str, request: Currency, user: Dict = Depends(get_current_admin_user)):
    """
    Update a currency record (Admin Only).
    """
    try:
        update_data = request.dict(exclude_unset=True)  # Get only provided fields
        update_data["updated_at"] = datetime.utcnow().isoformat()  # Add timestamp
        update_data["updated_by"] = user.get("name", "Admin")  # Capture admin name

        update_result = await currency_collection.update_one(
            {"_id": ObjectId(currency_id)},
            {"$set": update_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Currency not found or no changes made.")

        return {"status": "success", "message": "Currency updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Delete a currency by ID
@router.delete("/currency/{currency_id}", tags=["Currency"])
async def delete_currency(currency_id: str, user: Dict = Depends(get_current_admin_user)):
    """
    Delete a currency record (Admin Only).
    """
    try:
        delete_result = await currency_collection.delete_one({"_id": ObjectId(currency_id)})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Currency not found.")

        return {"status": "success", "message": "Currency deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
