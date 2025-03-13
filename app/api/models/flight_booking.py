from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class FlightSearchRequest(BaseModel):
    trip_type: str  # "one-way", "round-trip", "multi-city"
    origins: List[str]  # List of departure airport codes
    destinations: List[str]  # List of arrival airport codes
    departure_dates: List[str]  # List of departure dates (YYYY-MM-DD)
    return_date: Optional[str] = None  # Return date for round-trip (YYYY-MM-DD)
    cabin: List[str]  # Cabin class per segment (ECONOMY, BUSINESS, FIRST)
    adults: int = 1  # Number of adult passengers
    children: int = 0  # Number of children (2-12 years)
    infants: int = 0  # Number of infants (under 2 years)


# Define request body schema for flight pricing
class FlightPricingRequest(BaseModel):
    data_id: str
    flight_offer: Dict[str, Any]



# Define request body schema for flight booking
class FlightBookingRequest(BaseModel):
    data_id: str  
    travelers: List[Dict[str, Any]]  