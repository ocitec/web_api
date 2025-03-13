import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get allowed domains from .env
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")  # Convert to list

AMADEUS_BASE_URL = os.getenv("AMADEUS_ENTERPRISE_BASE_URL")
AMADEUS_AUTH_URL = os.getenv("AMADEUS_AUTH_URL")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_ENTERPRISE_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_ENTERPRISE_CLIENT_SECRET")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")