import redis.asyncio as aioredis
from datetime import datetime
import json
import logging
import asyncio
from app.config import REDIS_URL
from app.api.db.collections import agencymgt_collection, currency_collection

# Configure Logging
logging.basicConfig(level=logging.INFO)  # Set to ERROR in production
logger = logging.getLogger(__name__)

redis = None


async def set_redis_instance():
    """Initialize Redis connection."""
    global redis
    try:
        redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        await redis.ping()
        logger.info("✅ Redis is connected successfully!")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        redis = None  


def get_current_date():
    
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def convertDateTime(date_string):
    # Convert the given date string to a formatted date
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%a, %b %d, %Y, %I:%M %p")  # Format: Fri, Jun 17, 2025, 10:10 PM
    except ValueError as e:
        return f"Invalid date format: {e}"


async def coy_profile():
    
    cache_key = "agency_profile"

    if redis:
        try:
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Redis error (coy_profile): {e}")

    
    try:
        agencymgt_data = await agencymgt_collection.find_one()
        if agencymgt_data:
            agencymgt_data["_id"] = str(agencymgt_data["_id"])
            if redis:
                await redis.setex(cache_key, 3600, json.dumps(agencymgt_data))  # Cache for 1 hour
        return agencymgt_data
    except Exception as e:
        logger.error(f"MongoDB error (coy_profile): {e}")
        return None


async def get_default_currency():
    
    cache_key = "default_currency"

    if redis:
        try:
            cached_data = await redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Redis error (get_default_currency): {e}")

    
    try:
        currency = await currency_collection.find_one({"default": "Yes"})
        if currency:
            currency["_id"] = str(currency["_id"])
            if redis:
                await redis.setex(cache_key, 1800, json.dumps(currency))  # Cache for 30 minutes
        return currency
    except Exception as e:
        logger.error(f"MongoDB error (get_default_currency): {e}")
        return None


async def startup():
    """Run at application startup to initialize Redis."""
    await set_redis_instance()


async def shutdown():
    """Closes Redis connection when shutting down."""
    global redis
    if redis is not None:
        await redis.close()
        logger.info("🔻 Redis connection closed.")


# Ensure Redis is initialized when running as a standalone script
if __name__ == "__main__":
    asyncio.run(startup())
