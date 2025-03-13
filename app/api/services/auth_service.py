from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

# Simulated API Key (Store securely in env variables in production)
API_KEY = "mysecureapikey"
api_key_header = APIKeyHeader(name="X-API-KEY")

def get_current_admin_user(api_key: str = Security(api_key_header)):
    """Validate API key for admin operations."""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return {"role": "admin"}
