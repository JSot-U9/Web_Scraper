import os
import httpx

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"

async def search_serper(query: str, limit: int = 5):
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "q": query,
        "num": limit,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(SERPER_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    results = []
    for item in data.get("organic", [])[:limit]:
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet"),
            "source": "serper"
        })

    return results
