import httpx
from app.config import FREEPIK_API

async def fetch_freepik_image(item_name: str):
    headers = {"x-freepik-api-key": FREEPIK_API}
    params = {
        "term": item_name,
        "filters[content_type][photo]": 1,
        "filters[orientation][landscape]": 1,
        "limit": 1,
        "order": "relevance"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.freepik.com/v1/resources", headers=headers, params=params)
        response.raise_for_status()  # Ensure we raise an exception for HTTP errors
        data = response.json()
        if data["data"]:
            return data["data"][0]["image"]["source"]["url"]
        return None
