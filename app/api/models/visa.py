from pydantic import BaseModel, Field, EmailStr

# Pydantic model for Visa Application
class VisaApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    applicant_name: str
    email: EmailStr
    phone: str
    passport_number: str
    nationality: str
    visa_type: str  # e.g., Tourist, Business, Student
    destination_country: str
    travel_date: str
    status: str = "Pending"  # Default status