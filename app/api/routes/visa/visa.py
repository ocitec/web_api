from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import visa_collection, visa_country_collection, country_collection
from app.api.services.auth_service import get_current_admin_user  
from app.api.models.visa import VisaApplication, VisaApplicationResponse, VisaRequetsResponse, VisaDetailsResponse, VisaCountries

router = APIRouter()


@router.post("/submit_visa_request", tags=["Visa"], response_model=VisaApplicationResponse,
    summary="Submit visa request form",
    description="",
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
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }
    


@router.get("/requests", tags=["Visa"], response_model=VisaRequetsResponse, 
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
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }


@router.get("/visa_details", tags=["Visa"], response_model=VisaDetailsResponse,
    summary="",
    description="")
async def visa_details():
    try:

        visa_countries = await visa_country_collection.find({}).to_list(None)
        countries = await country_collection.find({}).to_list(None)

        # Convert ObjectId to string
        formatted_process_visa = [
            {**visa, "_id": str(visa["_id"])} for visa in visa_countries
        ]

        formatted_countries = [
            {**country, "_id": str(country["_id"])} for country in countries
        ]
        
        return VisaDetailsResponse(
            status_code=200,
            visa_countries=formatted_process_visa,
            countries=formatted_countries
        )
    
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }


@router.post("/add_visa_country", tags=["Visa"])
async def add_visa_country(request: List[VisaCountries]):
    try:
        # Convert all incoming request data to dictionaries
        visa_country_data = [item.dict() for item in request]

        # Extract unique fields for filtering
        categories = set(item["category"] for item in visa_country_data)
        countries = set(item["country"] for item in visa_country_data)
        images = set(item["image"] for item in visa_country_data)

        # Query DB for existing entries with matching fields
        existing_cursor = visa_country_collection.find({
            "$or": [
                {"category": {"$in": list(categories)}},
                {"country": {"$in": list(countries)}},
                {"image": {"$in": list(images)}}
            ]
        })
        existing_entries = await existing_cursor.to_list(length=1000)

        # Extract existing values for fast lookup
        existing_categories = {entry["category"] for entry in existing_entries}
        existing_countries = {entry["country"] for entry in existing_entries}
        existing_images = {entry["image"] for entry in existing_entries}

        # Filter new visa countries that don’t already exist
        new_visa_entries = [
            item for item in visa_country_data
            if item["category"] not in existing_categories and
               item["country"] not in existing_countries and
               item["image"] not in existing_images
        ]

        # Insert only non-duplicate entries
        if new_visa_entries:
            await visa_country_collection.insert_many(new_visa_entries)

        return {
            "status": "success",
            "inserted_count": len(new_visa_entries)
        }

    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }
