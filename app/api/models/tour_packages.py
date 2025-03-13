from pydantic import BaseModel, Field, EmailStr

# Pydantic model for Tour Package
class TourPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    price: float
    duration: int  # Number of days
    location: str
    available_slots: int

# Pydantic model for Tour Package Update
class TourPackageUpdate(BaseModel):
    name: str
    description: str
    price: float
    duration: int
    location: str
    available_slots: int


class TourPackageReservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    package_id: str
    full_name: str
    email: EmailStr 
    phone: str
    number_of_people: int
    reservation_date: str
    status: str = "Pending"  # Default status