from pydantic import BaseModel

# Pydantic model for updating About page
class AboutUpdateRequest(BaseModel):
    about_us: str
    mission: str
    vision: str
    values: str