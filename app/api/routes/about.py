from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.api.db.collections import about_collection
from app.api.services.auth_service import get_current_admin_user 
from app.api.models.about import AboutUpdateRequest

router = APIRouter()

@router.post("/save-about", tags=["About"])
async def add_about(payload: AboutUpdateRequest):

    try:
        is_exist = await about_collection.find_one()

        if not is_exist:

            insert_record = await about_collection.insert_one(payload.dict())

            return {
                "status": "success",
                "id": str(insert_record.inserted_id)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/about", tags=["About"])
async def get_about():
    """
    Retrieve profile details (About Us, Mission, Vision, Values).
    """
    try:
        about_data = await about_collection.find_one()

        if not about_data:
            raise HTTPException(status_code=404, detail="No 'About' information found.")

        about_data["_id"] = str(about_data["_id"])

        return {"status": "success", "data": about_data}
            

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    

@router.put("/update", tags=["About"])
async def update_about(
    payload: AboutUpdateRequest,
    user: Dict = Depends(get_current_admin_user)
):
    """
    Update profile details (Admin Only).
    """
    try:
        existing_about = await about_collection.find_one()

        if not existing_about:
            raise HTTPException(status_code=404, detail="No 'About' information found.")

        # Update the existing record
        update_result = await about_collection.update_one(
            {"_id": existing_about["_id"]}, 
            {"$set": payload.dict()}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update 'About' information.")

        return {"status": "success", "message": "About page updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/delete", tags=["About"])
async def delete_about(
    user: Dict = Depends(get_current_admin_user)
):
    """
    Delete 'About' information (Admin Only).
    """
    try:
        delete_result = await about_collection.delete_one({})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="No 'About' information found to delete.")

        return {"status": "success", "message": "About page deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")