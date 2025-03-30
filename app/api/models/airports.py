from pydantic import BaseModel
from typing import Optional

# Pydantic model for Airport
class Airports(BaseModel):
    iata_code: str
    name: str
    city: str
    country: str
    

    class Config:
        json_schema_extra = {
            "example": {
                "iata_code": "JFK",
                "name": "John F. Kennedy International Airport",
                "city": "New York",
                "country": "United States"
            }
        }


# Pydantic model for Carrier
class Carrier(BaseModel):
    iata_code: str
    name: str
    

    class Config:
        json_schema_extra = {
            "example": {
                "iata_code": "LH",
                "name": "Lufthansa ",
            }
        }

