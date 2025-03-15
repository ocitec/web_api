from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict
from uuid import uuid4
from app.api.db.collections import visa_collection
from app.api.services.auth_service import get_current_admin_user  
from app.api.models.visa import VisaApplication

router = APIRouter()


@router.post("/visa", tags=["Visa Applications"])
def visa_contact():
    """
    Create a new visa application (Public).
    """
    if payload.id in visa_applications_db:
        raise HTTPException(status_code=400, detail="Visa application already exists.")
    
    return {"status": "success", "message": "Welcome to Visa Department"}


