from pydantic import BaseModel, Field
from typing import Dict

# Pydantic model for Flight Deals
class FlightDeal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    airline: str
    origin: str
    destination: str
    price: float
    currency: str
    travel_dates: Dict[str, str]  # Example: {"departure": "2024-06-01", "return": "2024-06-15"}
    created_at: str = Field(default_factory=lambda: str(uuid4()))