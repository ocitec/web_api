from pydantic import BaseModel, Field, constr, conlist, conint, confloat
from uuid import uuid4
from typing import Optional, List, Literal
from datetime import datetime
import re

class IdentifiedModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))


class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str]
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class TravelAmount(BaseModel):
    type: str
    amount: str


class TravelPackageInfo(IdentifiedModel, TimestampedModel):
    name: str = Field(..., min_length=3)
    description: Optional[str]
    country: str
    # address: str
    category: conlist(str, min_length=1)
    images: conlist(str, min_length=1)
    traveldate: datetime
    amount: conlist(TravelAmount, min_length=1)
    rating: Optional[confloat(ge=1.0, le=5.0)]
    status: str = Field(..., pattern=r"^(active|inactive)$")
    featured: bool = False
    trending: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Summer Getaway",
                "description": "A perfect summer vacation package.",
                "country": "Greece",
                # "country": "123, Greece way park",
                "category": ["summer", "beach"],
                "images": ["beach1.jpg", "beach2.jpg"],
                "traveldate": "2025-07-10T00:00:00Z",
                "amount": [
                    {"type": "standard", "amount": "$1500.00"},
                    {"type": "premium", "amount": "$3000.00"}
                ],
                "rating": 4.5,
                "status": "active",
                "featured": True,
                "trending": True,
                "created_at": "2025-05-15T00:00:00Z",
                "created_by": "admin",
                "updated_at": "2025-05-15T00:00:00Z",
                "updated_by": "admin"
            }
        }


class NewTravelPackageResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    created_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1234567800987654321",
                "name": "Summer Getaway",
                "created_at": "2025-05-15T00:00:00Z",
                "created_by": "admin"
            }
        }


class UpdateTravelPackageRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    country: Optional[str]
    category: Optional[List[str]]
    images: Optional[List[str]]
    traveldate: Optional[datetime]
    amount: Optional[List[TravelAmount]]
    rating: Optional[confloat(ge=1.0, le=5.0)]
    status: Literal["active", "inactive"]
    featured: Optional[bool]
    trending: Optional[bool]
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str]


class TravelPackageCategory(IdentifiedModel, TimestampedModel):
    name: str = Field(..., min_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Summer",
                "created_at": "2025-05-15T00:00:00Z",
                "created_by": "admin",
                "updated_at": "2025-05-15T00:00:00Z",
                "updated_by": "admin"
            }
        }


class TravelPackageReservation(IdentifiedModel, TimestampedModel):
    package_id: str
    firstname: str = Field(..., min_length=3)
    lastname: str = Field(..., min_length=3)
    email: str
    phone_number: str = Field(..., pattern=r"^\d{9,12}$")
    custom_message: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "package_id": "1234567890",
                "firstname": "John",
                "lastname": "Doe",
                "email": "sample@email.com",
                "phone_number": "1234567890",
                "custom_message": "Can I get a pick-up service for this package?",
                "created_at": "2025-05-15T00:00:00Z",
                "created_by": "admin",
                "updated_at": "2025-05-15T00:00:00Z",
                "updated_by": "admin"
            }
        }
