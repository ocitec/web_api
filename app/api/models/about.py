from pydantic import BaseModel
from typing import Optional

# Pydantic model for updating About page
class AboutUpdateRequest(BaseModel):
    about_us: str
    mission: str
    vision: str
    values: str


class AgencyMgt(BaseModel):
    coy_name: str
    contact_firstname: str
    contact_lastname: str
    address_1: str
    address_2: Optional[str]
    city: str
    state: str
    postal_code: str
    country_code: str
    agency_country_code: str
    agency_phone_number: str
    agency_email: str
    base_currency: str

    class Config:
        json_schema_extra = {
            "example": {
                "coy_name": "Company's name",
                "contact_firstname": "Atanda",
                "contact_lastname": "Hilary",
                "address_1": "21 sample street, lagos",
                "address_2": "22 sample street, lagos",
                "city": "Lagos",
                "state": "Lagos",
                "postal_code": "100001",
                "country_code": "234",
                "agency_country_code": "0001",
                "agency_phone_number": "09876542342",
                "agency_email": "sample@email.com",
                "base_currency": "NGN"
            }
        }

