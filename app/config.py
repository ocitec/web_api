import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine the environment (default to "development")
APP_ENV = os.getenv("APP_ENV", "development").lower()

# Default configurations
CONFIG = {
    "development": {
        "HOST": os.getenv("HOST"),
        "PORT": os.getenv("PORT"),
        "AMADEUS_BASE_URL": os.getenv("AMADEUS_ENTERPRISE_BASE_URL"), 
        "AMADEUS_AUTH_URL": os.getenv("AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("AMADEUS_ENTERPRISE_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("AMADEUS_ENTERPRISE_CLIENT_SECRET"),
        "MONGODB_URI": os.getenv("MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("PAYSTACK_SECRET"),
    },
    "staging": {
        "HOST": os.getenv("STAGING_HOST"),
        "PORT": os.getenv("STAGING_PORT"),
        "AMADEUS_BASE_URL": os.getenv("STAGING_AMADEUS_BASE_URL"),
        "AMADEUS_AUTH_URL": os.getenv("STAGING_AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("STAGING_AMADEUS_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("STAGING_AMADEUS_CLIENT_SECRET"),
        "MONGODB_URI": os.getenv("STAGING_MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("STAGING_PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("STAGING_PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("STAGING_PAYSTACK_SECRET"),
    },
    "production": {
        "HOST": os.getenv("PROD_HOST"),
        "PORT": os.getenv("PROD_PORT"),
        "AMADEUS_BASE_URL": os.getenv("PROD_AMADEUS_BASE_URL"),
        "AMADEUS_AUTH_URL": os.getenv("PROD_AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("PROD_AMADEUS_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("PROD_AMADEUS_CLIENT_SECRET"),
        "MONGODB_URI": os.getenv("PROD_MONGODB_URI"),
        "DATABASE_NAME": os.getenv("PROD_DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("PROD_PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("PROD_PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("PROD_PAYSTACK_SECRET"),
    },
}

# Get configurations based on the environment
ENV_CONFIG = CONFIG.get(APP_ENV, CONFIG["development"])

HOST = ENV_CONFIG["HOST"]
PORT = ENV_CONFIG["PORT"]

# Global variables
AMADEUS_BASE_URL = ENV_CONFIG["AMADEUS_BASE_URL"]
AMADEUS_AUTH_URL = ENV_CONFIG["AMADEUS_AUTH_URL"]
AMADEUS_CLIENT_ID = ENV_CONFIG["AMADEUS_CLIENT_ID"]
AMADEUS_CLIENT_SECRET = ENV_CONFIG["AMADEUS_CLIENT_SECRET"]
MONGODB_URI = ENV_CONFIG["MONGODB_URI"]
DATABASE_NAME = ENV_CONFIG["DATABASE_NAME"]
PAYSTACK_URL = ENV_CONFIG["PAYSTACK_URL"]
PAYSTACK_API_KEY = ENV_CONFIG["PAYSTACK_API_KEY"]
PAYSTACK_SECRET = ENV_CONFIG["PAYSTACK_SECRET"]

# Allowed Origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")  # Convert to list

# print(f"Loaded {APP_ENV} configuration")
