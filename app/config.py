import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine the environment (default to "development")
APP_ENV = os.getenv("APP_ENV", "development").lower()


# Default configurations
CONFIG = {
    "development": {
        "DEBUG": os.getenv("APP_DEBUG"),
        "HOST": os.getenv("HOST"),
        "PORT": os.getenv("PORT"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "AMADEUS_BASE_URL": os.getenv("AMADEUS_ENTERPRISE_BASE_URL"), 
        "AMADEUS_AUTH_URL": os.getenv("AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("AMADEUS_ENTERPRISE_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("AMADEUS_ENTERPRISE_CLIENT_SECRET"),
        "API_AIRPORTS_URL": os.getenv("https://api.amadeus.com/v1/reference-data/locations"),
        "MONGODB_URI": os.getenv("MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("PAYSTACK_SECRET"),
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "EMAIL_SENDER": os.getenv("EMAIL_SENDER"),
        "APP_URL": os.getenv("APP_URL")
    },
    "staging": {
        "HOST": os.getenv("STAGING_HOST"),
        "PORT": os.getenv("STAGING_PORT"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "AMADEUS_BASE_URL": os.getenv("STAGING_AMADEUS_BASE_URL"),
        "AMADEUS_AUTH_URL": os.getenv("STAGING_AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("STAGING_AMADEUS_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("STAGING_AMADEUS_CLIENT_SECRET"),
        "API_AIRPORTS_URL": os.getenv("https://api.amadeus.com/v1/reference-data/locations"),
        "MONGODB_URI": os.getenv("STAGING_MONGODB_URI"),
        "DATABASE_NAME": os.getenv("DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("STAGING_PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("STAGING_PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("STAGING_PAYSTACK_SECRET"),
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "EMAIL_SENDER": os.getenv("EMAIL_SENDER"),
        "APP_URL": os.getenv("APP_URL")
    },
    "production": {
        "DEBUG": os.getenv("PROD_APP_DEBUG"),
        "HOST": os.getenv("PROD_HOST"),
        "PORT": os.getenv("PROD_PORT"),
        "REDIS_URL": os.getenv("REDIS_URL"),
        "AMADEUS_BASE_URL": os.getenv("PROD_AMADEUS_BASE_URL"),
        "AMADEUS_AUTH_URL": os.getenv("PROD_AMADEUS_AUTH_URL"),
        "AMADEUS_CLIENT_ID": os.getenv("PROD_AMADEUS_CLIENT_ID"),
        "AMADEUS_CLIENT_SECRET": os.getenv("PROD_AMADEUS_CLIENT_SECRET"),
        "API_AIRPORTS_URL": os.getenv("https://api.amadeus.com/v1/reference-data/locations"),
        "MONGODB_URI": os.getenv("PROD_MONGODB_URI"),
        "DATABASE_NAME": os.getenv("PROD_DATABASE_NAME"),
        "PAYSTACK_URL": os.getenv("PROD_PAYSTACK_URL"),
        "PAYSTACK_API_KEY": os.getenv("PROD_PAYSTACK_API_KEY"),
        "PAYSTACK_SECRET": os.getenv("PROD_PAYSTACK_SECRET"),
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "EMAIL_SENDER": os.getenv("EMAIL_SENDER"),
        "APP_URL": os.getenv("APP_URL")
    },
}

# Get configurations based on the environment
ENV_CONFIG = CONFIG.get(APP_ENV, CONFIG["development"])

HOST = ENV_CONFIG["HOST"]
PORT = ENV_CONFIG["PORT"]
APP_DEBUG = ENV_CONFIG["DEBUG"]

# Global variables
REDIS_URL = ENV_CONFIG["REDIS_URL"]
AMADEUS_BASE_URL = ENV_CONFIG["AMADEUS_BASE_URL"]
AMADEUS_AUTH_URL = ENV_CONFIG["AMADEUS_AUTH_URL"]
AMADEUS_CLIENT_ID = ENV_CONFIG["AMADEUS_CLIENT_ID"]
AMADEUS_CLIENT_SECRET = ENV_CONFIG["AMADEUS_CLIENT_SECRET"]
API_AIRPORTS_URL = ENV_CONFIG["API_AIRPORTS_URL"]
MONGODB_URI = ENV_CONFIG["MONGODB_URI"]
DATABASE_NAME = ENV_CONFIG["DATABASE_NAME"]
PAYSTACK_URL = ENV_CONFIG["PAYSTACK_URL"]
PAYSTACK_API_KEY = ENV_CONFIG["PAYSTACK_API_KEY"]
PAYSTACK_SECRET = ENV_CONFIG["PAYSTACK_SECRET"]
SENDGRID_API_KEY = ENV_CONFIG["SENDGRID_API_KEY"]
EMAIL_SENDER = ENV_CONFIG["EMAIL_SENDER"]
APP_URL = ENV_CONFIG["APP_URL"]

# Allowed Origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")  # Convert to list
# print(APP_ENV)
# print(f"Loaded {APP_ENV} configuration")
