from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, DATABASE_NAME

# Initialize MongoDB Client
client = AsyncIOMotorClient(MONGODB_URI)
database = client[DATABASE_NAME]
