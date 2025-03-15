from pydantic import BaseModel, Field
from typing import Optional
from app.api.services.helper import get_current_date

class Currency(BaseModel):
    default: str = Field(..., description="Indicates if this is the default currency (Yes/No)")
    name: str = Field(..., description="Full name of the currency")
    symbol: str = Field(..., description="Currency symbol (e.g., ₦, $, €)")
    code: str = Field(..., min_length=3, max_length=3, description="3-letter currency code (ISO 4217)")
    rate: float = Field(..., description="Exchange rate relative to a base currency")
    created_at: str = Field(default_factory=get_current_date, description="Timestamp of creation")
    created_by: str = Field(default="Ola", description="Admin who created the record")
    updated_at: Optional[str] = Field(None, description="Timestamp of last update")
    updated_by: Optional[str] = Field(None, description="Admin who last updated the record")

    class Config:
        json_schema_extra = {
            "example": {
                "default": "Yes",
                "name": "Nigerian Naira",
                "symbol": "₦",
                "code": "NGN",
                "rate": 1567.50,
                "created_at": "2024-03-13T12:00:00Z",
                "created_by": "Ola",
                "updated_at": None,
                "updated_by": None
            }
        }
