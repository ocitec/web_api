from fastapi import FastAPI, APIRouter, HTTPException, Query
from app.api.db.collections import country_collection
from app.api.models.country import Countries
from typing import List

router = APIRouter()

@router.post("/add_country", tags=["Country"])
async def add_country(request: List[Countries]):
    try:
        country_data = [country.dict() for country in request]
        
        iata_codes = [country["iata_code"] for country in country_data]
        names = [country["country"] for country in country_data]
        
        existing_country_cursor = country_collection.find({
            "$or": [
                {"iata_code": {"$in": iata_codes}},
                {"country": {"$in": names}}
            ]
        })
        
        exisiting_countries = await existing_country_cursor.to_list(length=1000)

        existing_iata_codes = {country["iata_code"] for country in exisiting_countries}
        existing_names = {country["country"] for country in exisiting_countries}

        country_data_add = [
            country for country in country_data 
            if country["iata_code"] not in existing_iata_codes and country["country"] not in existing_names
        ]
        
        if country_data_add:
            result = await country_collection.insert_many(country_data_add)

        return {
            "status": "success",
            "inserted_count": len(country_data_add)
        }

    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }


@router.get("/search_countries", tags=["Country"], 
    summary="Search for countries.", 
    description="Search for countries by country name, or IATA code.")
async def search_countries(query: str = Query(..., min_length=2)):

    try:
        search_results_cursor = country_collection.find(
            {"$or": [
                {"iata_code": {"$regex": query, "$options": "i"}},
                {"country": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(10)

        search_results = await search_results_cursor.to_list(length=10)

        return [{"iata_code": result["iata_code"], "name": result["country"]} for result in search_results]
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }


@router.get("/country_list", tags=["Airport"], 
    summary="Search for country list.", 
    description="Search for the list of countries.")
async def list_countries():

    try:
        # Convert cursor to list (set length to None for all results)
        countries = await country_collection.find({}).to_list(None)

        # Convert ObjectId to string
        formatted_countries = [
            {**airport, "_id": str(airport["_id"])} for airport in countries
        ]

        return formatted_countries
    
    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Internal server error: {str(e)}"
        }

