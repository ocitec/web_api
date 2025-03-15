from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.api.db.collections import agencymgt_collection
from app.api.services.auth_service import get_current_admin_user 
from app.api.models.about import AgencyMgt

router = APIRouter()

@router.post("/save-agencymgt", tags=["About"])
async def add_agencymgtt(request: AgencyMgt):

    try:
        is_exist = await agencymgt_collection.find_one()

        if not is_exist:

            insert_record = await agencymgt_collection.insert_one(request.dict())

            return {
                "status": "success",
                "id": str(insert_record.inserted_id)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/agencymgt", tags=["About"])
async def get_agencymgt():
    
    try:
        agencymgt_data = await agencymgt_collection.find_one()

        if not agencymgt_data:
            raise HTTPException(status_code=404, detail="No 'Agency' information found.")

        agencymgt_data["_id"] = str(agencymgt_data["_id"])

        return {"status": "success", "data": agencymgt_data}
            

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

 