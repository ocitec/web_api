from pydantic import BaseModel
from typing import Optional

# Pydantic model for Airport
class Countries(BaseModel):
    iata_code: str
    country: str
    capital: str
    

    class Config:
        json_schema_extra = {
            "example": {
                "iata_code": "NG",
                "country": "Nigeria",
                "capital": "Abuja"
            }
        }

