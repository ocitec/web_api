from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

# Pydantic Model for storing flight offers
class AmadeusFlightOffer(BaseModel):
    user_id: str  # Associate offer with a user
    search_params: Dict[str, Any]  # Store search parameters
    flight_offers: Dict[str, Any]  # Store Amadeus response data
    created_at: datetime = datetime.utcnow()  # Store creation time