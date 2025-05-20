from fastapi import APIRouter, HTTPException, Body
from app.api.db.collections import categories_collection
from app.api.models.travelpackages import TravelPackageCategory
from typing import List

router = APIRouter()

# Create a new category
@router.post("/category", tags=["Travel Packages"], response_model=TravelPackageCategory,
    summary="Create a new category", description="Create a new travel package category.")
async def create_category(category: TravelPackageCategory = Body(...)):
    try:
        await categories_collection.insert_one(category.dict())
        return category
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get all categories
@router.get("/categories", tags=["Travel Packages"], response_model=List[TravelPackageCategory],
    summary="Get all categories", description="Retrieve all travel package categories.")
async def get_categories():
    try:
        categories = await categories_collection.find().to_list(100)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 


# Get a category by ID
@router.get("/category/{category_id}", tags=["Travel Packages"], response_model=TravelPackageCategory,
    summary="Get a category", description="Retrieve a travel package category by ID.")
async def get_category(category_id: str):
    category = await categories_collection.find_one({"id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Update a category
@router.put("/category/{category_id}", tags=["Travel Packages"], summary="Update a category")
async def update_category(category_id: str, category: TravelPackageCategory):
    try:
        result = await categories_collection.update_one({"id": category_id}, {"$set": category.dict()})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Delete a category
@router.delete("/category/{category_id}", tags=["Travel Packages"], summary="Delete a category")
async def delete_category(category_id: str):
    try:
        result = await categories_collection.delete_one({"id": category_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
