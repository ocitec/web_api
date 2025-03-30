from fastapi import FastAPI, APIRouter, HTTPException, Query
from app.api.db.collections import airports_collection, carrier_collection
from app.api.models.airports import Airports, Carrier
from typing import List

router = APIRouter()

@router.post("/add_airports")
async def add_airports(request: List[Airports]):
    try:
        # Convert the list of Airport Pydantic models to dictionaries
        airports_data = [airport.dict() for airport in request]
        
        # Collect the IATA codes and names from the incoming airports to check if they already exist
        iata_codes = [airport["iata_code"] for airport in airports_data]
        names = [airport["name"] for airport in airports_data]
        
        # Check for existing airports with matching IATA codes or names in a single query
        existing_airports_cursor = airports_collection.find({
            "$or": [
                {"iata_code": {"$in": iata_codes}},
                {"name": {"$in": names}}
            ]
        })
        
        # Convert the cursor to a list
        existing_airports = await existing_airports_cursor.to_list(length=1000)

        # Create a set of existing IATA codes and names for fast lookup
        existing_iata_codes = {airport["iata_code"] for airport in existing_airports}
        existing_names = {airport["name"] for airport in existing_airports}

        # Filter out the airports that already exist
        airports_data_add = [
            airport for airport in airports_data 
            if airport["iata_code"] not in existing_iata_codes and airport["name"] not in existing_names
        ]
        
        # If there are new airports to add, insert them
        if airports_data_add:
            result = await airports_collection.insert_many(airports_data_add)

        return {
            "status": "success",
            "inserted_count": len(airports_data_add)  # Return number of inserted records
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search_airports", tags=["Airport"], 
    summary="Search for airport.", 
    description="Search for airports by name, city, or IATA code.")
async def search_airports(query: str = Query(..., min_length=2)):

    try:
        search_results_cursor = airports_collection.find(
            {"$or": [
                {"iata_code": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}},
                {"city": {"$regex": query, "$options": "i"}}
            ]}
        ).limit(10)

        search_results = await search_results_cursor.to_list(length=10)

        return [{"iata_code": result["iata_code"], "name": result["name"]} for result in search_results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/list", tags=["Airport"], 
    summary="Search for airport.", 
    description="Search for the list of airports and cities.")
async def list_airports():

    try:
        # Convert cursor to list (set length to None for all results)
        airport_cities = await airports_collection.find({}).to_list(None)

        # Convert ObjectId to string
        formatted_airports = [
            {**airport, "_id": str(airport["_id"])} for airport in airport_cities
        ]

        return formatted_airports
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@router.post("/add_carrier", tags=["Airport"])
async def add_carrier(request: List[Carrier]):
    try:
        # Convert the list of Carrier Pydantic models to dictionaries
        carrier_data = [carrier.dict() for carrier in request]
        
        # Collect the IATA codes and names from the incoming carrier to check if they already exist
        iata_codes = [carrier["iata_code"] for carrier in carrier_data]
        names = [carrier["name"] for carrier in carrier_data]
        
        # Check for existing carrier with matching IATA codes or names in a single query
        exisiting_carrier_cursor = carrier_collection.find({
            "$or": [
                {"iata_code": {"$in": iata_codes}},
                {"name": {"$in": names}}
            ]
        })
        
        # Convert the cursor to a list
        exisiting_carrier = await exisiting_carrier_cursor.to_list(length=1000)

        # Create a set of existing IATA codes and names for fast lookup
        existing_iata_codes = {carrier["iata_code"] for carrier in exisiting_carrier}
        existing_names = {carrier["name"] for carrier in exisiting_carrier}

        # Filter out the carriers that already exist
        carriers_data_add = [
            carrier for carrier in carrier_data 
            if carrier["iata_code"] not in existing_iata_codes and carrier["name"] not in existing_names
        ]
        
        # If there are new carriers to add, insert them
        if carriers_data_add:
            result = await carrier_collection.insert_many(carriers_data_add)

        return {
            "status": "success",
            "inserted_count": len(carriers_data_add)  # Return number of inserted records
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")