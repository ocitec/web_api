from pydantic import BaseModel, Field, EmailStr
from uuid import uuid4
from typing import Optional, Dict, Any, List
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


class VisaFee(BaseModel):
    name: str
    amount: float


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

class VisaCountry(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    category: str
    country: str
    amount: List[VisaFee]
    image: str
    description: str
    documents: str
    faqs: str
    

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "#123456",
                "category": "Tourist",
                "country": "United States",
                "amount": [
                    {"name": "Adult", "amount": 200000.01},
                    {"name": "Child", "amount": 150000}
                ],
                "image": "https://freeimage.com",
                "description":"short details about the visa country",
                "documents": "Documents required for the visa",
                "faqs": "Frequently asked questions about the visa country"
            }
        }


class Country(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    iata_code: str
    country: str
    capital: str

    class Config:
        populate_by_name = True

class VisaDetailsResponse(BaseModel):
    status_code: int
    visa_countries: List[VisaCountry]
    countries: List[Country]

    class Config:
        json_schema_extra = {
            "example": {
                "visa_countries": [
                    {
                        "id": "1",
                        "category": "Tourist",
                        "country": "United States",
                        "amount": [
                            {"name": "Adult", "amount": 200000.01},
                            {"name": "Child", "amount": 150000}
                        ],
                        "image": "https://",
                        "description": "Visa info",
                        "documents": "Passport, Photo",
                        "faqs": "Some FAQs"
                    },
                ],
                "countries": [
                    {
                        "id": "1",
                        "iata_code": "NG", 
                        "country": "Nigeria", 
                        "capital": "Abuja"
                    }
                ],

            }
        }




# class VisaCountries(BaseModel):
#     category: str
#     country: str
#     amount: List[VisaFee]
#     image: str
#     description: str
#     documents: str
#     faqs: str
    

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "category": "Tourist",
#                 "country": "United States",
#                 "image": "https://freeimage.com",
#                 "description":"short details about the visa country",
#                 "documents": "Documents required for the visa",
#                 "faqs": "Frequently asked questions about the visa country"
#             }
#         }

