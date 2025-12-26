# search_providers/bing.py
import httpx
from typing import List, Dict
from fastapi import HTTPException

def search_bing(query: str, limit: int, api_key: str) -> List[Dict]:
    """
    Consulta Bing Web Search API v7.
    Requiere BING_API_KEY en el entorno (Ocp-Apim-Subscription-Key).
    """
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": limit, "textDecorations": False, "textFormat": "Raw"}
    try:
        with httpx.Client(timeout=12.0, headers=headers) as client:
            r = client.get(endpoint, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bing API error: {e}")

    results = []
    web = data.get("webPages", {}).get("value", [])
    for item in web[:limit]:
        title = item.get("name", "")
        url = item.get("url", "")
        snippet = item.get("snippet", "") or item.get("displayUrl", "")
        if url:
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": "bing"
            })
    return results
