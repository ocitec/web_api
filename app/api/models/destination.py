from pydantic import BaseModel, Field
from typing import List

# Pydantic model for Destination
class Destination(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    country: str
    description: str
    best_time_to_visit: str
    attractions: List[str]  # List of places to visit