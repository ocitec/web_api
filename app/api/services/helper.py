from datetime import datetime
import json
import redis.asyncio as aioredis
from app.config import REDIS_URL
from app.api.db.collections import agencymgt_collection, currency_collection

# Create Redis Connection Pool
redis = aioredis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_current_date():
    """Returns the current UTC date/time in ISO format."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

async def coy_profile():
    """Fetches agency profile, using Redis caching for faster performance."""
    cache_key = "agency_profile"

    # Check Redis Cache First
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # Fetch from MongoDB if not in cache
    agencymgt_data = await agencymgt_collection.find_one()

    if agencymgt_data:
        agencymgt_data["_id"] = str(agencymgt_data["_id"])  # Convert ObjectId to string

        # Store in Redis with 1-hour expiration
        await redis.setex(cache_key, 3600, json.dumps(agencymgt_data))

    return agencymgt_data or None

async def get_default_currency():
    """Fetches the default currency, using Redis caching to reduce DB queries."""
    cache_key = "default_currency"

    # Check Redis Cache First
    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # Fetch from MongoDB if not in cache
    currency = await currency_collection.find_one({"default": "Yes"})

    if currency:
        currency["_id"] = str(currency["_id"])  # Convert ObjectId to string

        # Store in Redis with 30-minute expiration
        await redis.setex(cache_key, 1800, json.dumps(currency))

    return currency or None

async def close_redis():
    """Closes Redis connection when shutting down."""
    await redis.close()
