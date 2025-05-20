from fastapi import FastAPI, APIRouter, HTTPException, Query, Body
from app.api.db.collections import travelpackages_collection
from app.api.models.travelpackages import TravelPackageInfo, NewTravelPackageResponse, UpdateTravelPackageRequest, \
    TravelPackageCategory, TravelPackageReservation
from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.son import SON
from app.api.services.freepik import fetch_freepik_image

router = APIRouter()

# Travel Packages
@router.post("/add_travel_package", tags=["Travel Packages"], response_model=NewTravelPackageResponse,
    summary="Add a new travel package", 
    description="Create a new travel package with the provided information.")
async def add_travel_package(package: TravelPackageInfo = Body(...)):
    try:
        await travelpackages_collection.insert_one(package.dict())
        return package
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_travel_package/{id}", tags=["Travel Packages"], 
        summary="Update travel package", 
        description="Update details of an existing travel package.")
async def update_travel_package(id: str, package: UpdateTravelPackageRequest):
    try:
        result = await travelpackages_collection.update_one({"id": id}, {"$set": package.dict()})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Travel package not found")
        return {"status_code": 201, "message": "Travel package updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/one_travel_package/{id}", tags=["Travel Packages"], response_model=TravelPackageInfo,
    summary="Get travel package", description="Retrieve details of a travel package by ID.")
async def one_travel_package(id: str):
    package = await travelpackages_collection.find_one({"id": id}) 
    if not package:
        raise HTTPException(status_code=404, detail="Travel package not found")
    return package


@router.delete("/remove_travel_package/{id}", tags=["Travel Packages"], summary="Remove travel package")
async def remove_travel_package(id: str):
    result = await travelpackages_collection.delete_one({"id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Travel package not found")
    return {"status_code": 201 , "message": "Travel package removed successfully"}


@router.get("/active/travel_packages", tags=["Travel Packages"], response_model=List[TravelPackageInfo],
    summary="List travel packages", description="Return all available travel packages.")
async def travel_packages():
    packages = await travelpackages_collection.find({"status": "active"}).to_list(100)
    return packages


@router.get("/active/{sortby}/travel_packages/{name}", tags=["Travel Packages"], response_model=List[TravelPackageInfo],
    summary="List travel packages by season, destination etc", description="Return all available travel packages.")
async def travel_packages(sortby: str, name: str):
    try:
        column = "category" if sortby == 'season' else "country"
        packages = await travelpackages_collection.find({"status": "active", column: name }).to_list(1000)
        return packages
    except Exception as e:
        return e


@router.get("/active/{category_type}/travel_packages", tags=["Travel Packages"], response_model=List[TravelPackageInfo],
    summary="List travel packages", description=f"Return all available features, trending travel packages.")
async def travel_packages(category_type: str):
    query = {}
    sort = None
    limit = 3 if category_type == 'featured' else 1000

    if category_type == "latest":
        sort = [("created_at", -1)]
        limit = 4
    else:
        query = {"status": "active", category_type: True}

    cursor = travelpackages_collection.find(query)
    if sort:
        cursor = cursor.sort(sort)

    packages = await cursor.to_list(limit)


    return packages


@router.get("/active/{field}", tags=["Travel Packages"],
            summary="List travel packages", description="Return all travel packages by category or country.")
async def by_dynamic_field(field: str):
    pipeline = [{"$match": {"status": "active"}}]

    # Unwind if field is an array (e.g., category)
    if field == "category":
        pipeline.append({"$unwind": f"${field}"})

    # Group by the field (e.g., "category" or "country")
    pipeline.append({"$group": {"_id": f"${field}"}})
    
    # Sort and limit
    pipeline.extend([
        {"$sort": SON([("_id", 1)])},
        {"$limit": 100}
    ])

    data = await travelpackages_collection.aggregate(pipeline).to_list(length=None)

    # Append image for each value
    for item in data:
        key = item["_id"]
        image_url = await fetch_freepik_image(key)
        item["image_url"] = image_url

    return data


@router.get("/travel_packages", tags=["Travel Packages"], response_model=List[TravelPackageInfo],
    summary="List travel packages", description="Return all travel packages.")
async def travel_packages():
    packages = await travelpackages_collection.find().to_list(100)
    return packages


