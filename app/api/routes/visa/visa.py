from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict
from uuid import uuid4
from bson import ObjectId
from app.api.db.collections import visa_collection, visa_country_collection, country_collection
from app.api.services.auth_service import get_current_admin_user  
from app.api.models.visa import VisaApplication, VisaFee, VisaCountry, Country, VisaApplicationResponse, VisaRequetsResponse, VisaDetailsResponse

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
            {**{k: v for k, v in visa.items() if k != "_id"}, "id": str(visa["_id"])} for visa in visa_countries
        ]

        formatted_countries = [
            {**{k: v for k, v in country.items() if k != "_id"}, "id": str(country["_id"])} for country in countries
        ]
        
        return VisaDetailsResponse(
            status_code=200,
            visa_countries=[VisaCountry(**visa) for visa in formatted_process_visa],
            countries=[Country(**country) for country in formatted_countries]
        )
    
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }


@router.post("/add_visa_country", tags=["Visa"])
async def add_visa_country(request: List[VisaCountry]):
    try:
        # Convert all incoming request data to dictionaries
        visa_country_data = [item.dict() for item in request]

        # Extract unique fields for filtering
        categories = set(item["category"] for item in visa_country_data)
        countries = set(item["country"] for item in visa_country_data)

        # Query DB for existing entries with matching fields
        existing_cursor = visa_country_collection.find({
            "$or": [
                {"category": {"$in": list(categories)}},
                {"country": {"$in": list(countries)}}
            ]
        })
        existing_entries = await existing_cursor.to_list(length=1000)

        existing_combinations = {(item["country"], item["category"]) for item in existing_entries}
        
        # Filter new visa countries that don’t already exist
        new_visa_entries = [
            item for item in visa_country_data
             if (item["country"], item["category"]) not in existing_combinations
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


@router.get(
    "/info", 
    tags=["Visa"],
    summary="Fetch visa information",
    description="This endpoint fetches a visa country information."
)
async def get_visa_info(
    visa_id: str = Query(..., description="visa ID")
):

    try:
        visa_record = await visa_country_collection.find_one(
            { 
                "_id": ObjectId(visa_id)
            }
        )

        if not visa_record:
            return {
                "status_code": 404,
                "message": "Visa record not found"
            }

        # Convert ObjectId to string safely
        visa_record["id"] = str(visa_record["_id"])
        del visa_record["_id"]

        return {"status_code": 200, "data": visa_record}

    except Exception as e:
        logging.error(f"Error fetching record: {str(e)}")
        return {
            "status_code": 500,
            "message": "Internal server error"
        }


