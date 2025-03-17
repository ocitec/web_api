from pydantic import BaseModel, Field, EmailStr
from uuid import uuid4
from typing import Optional, Dict, Any
from datetime import datetime

# Pydantic model for Visa Application
class VisaApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    first_name: str
    last_name: str
    dob: str
    gender: str
    email: EmailStr
    nationality: str    
    phone_number: str
    address: str
    purpose_of_visit: str # tourism, business, study, work, family visit
    prefered_destination_country: str
    travel_start_date: Optional[str]
    travel_end_date: Optional[str]
    visa_type: str # tourist visa, student visa, work visa
    visa_history: str # Have you ever applied for a visa before? or Have you ever been denied a visa? Yes / No
    passport: str # Do you have a valid passport? (Yes/No)
    travel_arrange: str # Do you already have travel arrangements? (Yes/No)
    hear_about_us: Optional[str] # How did you hear about us? (Options like search engine, referral, advertisement, etc.)
    question: Optional[str] # Any specific questions or concerns regarding your visa application?
    terms_conditions: str # I agree to the terms and conditions
    private_policy: str # I agree to the privacy policy
    created_at: datetime = datetime.utcnow()

    class config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "dob": "2002-03-15",
                "gender": "Male",
                "email": "sample@email.com",
                "nationality": "Nigerian"  ,  
                "phone_number": "+2348123456789",
                "address": "1, john doe street, lagos island, Lagos State",
                "purpose_of_visit": "study"  ,
                "prefered_destination_country": "USA",
                "travel_start_date": "2025-10-15",
                "travel_end_date": "2026-01-20",
                "visa_type": "Student Visa",
                "visa_history": "No",
                "passport": "Yes",
                "travel_arrange": "Yes",
                "hear_about_us": "referral",
                "question": "",
                "terms_conditions": "Yes",
                "private_policy": "Yes" 
            }
        }


class VisaApplicationResponse(BaseModel):
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Request sent successfully"
            }
        }


class VisaRequetsResponse(BaseModel):
    status: int
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "data": [
                    {}
                ]
            }
        }
