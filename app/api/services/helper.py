from datetime import datetime
# import aioredis
import json
from app.api.db.collections import agencymgt_collection, currency_collection

# Connect to Redis
# REDIS_URL = "redis://localhost:6379" 
# redis = aioredis.from_url(REDIS_URL, decode_responses=True)

def get_current_date():
    """
    Get the current UTC timestamp in ISO format.
    Example: '2024-03-14T10:15:30Z'
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

async def coy_profile():
    cache_key = "agency_profile"

    # cached_data = await redis.get(cache_key)
    # if cached_data:
    #     return json.loads(cached_data)

    agencymgt_data = await agencymgt_collection.find_one()

    if agencymgt_data:
        agencymgt_data["_id"] = str(agencymgt_data["_id"]) 

        # Store in Redis with expiration (1 hour)
        # await redis.setex(cache_key, 3600, json.dumps(agencymgt_data))

    return agencymgt_data or None

async def get_default_currency():
    cache_key = "default_currency"

    # cached_data = await redis.get(cache_key)
    # if cached_data:
    #     return json.loads(cached_data)

    currency = await currency_collection.find_one({"default": "Yes"})

    if currency:
        currency["_id"] = str(currency["_id"])  # Convert ObjectId to string

        # Store in Redis with expiration (30 minutes)
        # await redis.setex(cache_key, 1800, json.dumps(currency))

    return currency or None
