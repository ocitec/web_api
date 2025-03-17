from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import visa_collection
from app.api.services.auth_service import get_current_admin_user  
from app.api.models.visa import VisaApplication, VisaApplicationResponse, VisaRequetsResponse

router = APIRouter()


@router.post("/submit_visa_request", response_model=VisaApplicationResponse,
    summary="Submit visa request form",
    description="",
    tags=["Visa Applications"]
    )
async def visa_request(request: VisaApplication):

    try:
        result = await visa_collection.insert_one(request.dict())

        visa_email = request.email
        # send email notification to visa helpdesk and client.

        return VisaApplicationResponse(
            status="success",
            message="Request sent successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    


@router.get("/requests", response_model=VisaRequetsResponse, 
    summary="Retrieve visa requests", 
    description="Fetch all visa requests.")
async def visa_requests(user: Dict = Depends(get_current_admin_user)):
    try:
        visa_cursor = visa_collection.find({}).sort("created_at", -1)
        
        visa_data = await visa_cursor.to_list(length=500)  
        
        for visa in visa_data:
            visa["_id"] = str(visa["_id"])

        return VisaRequetsResponse(
            status=200,
            data=visa_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


