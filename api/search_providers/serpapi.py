# search_providers/serpapi.py
import httpx
from typing import List, Dict
from fastapi import HTTPException

def search_serpapi(query: str, limit: int, api_key: str) -> List[Dict]:
    """
    Consulta SerpAPI (Google) y devuelve una lista de resultados normalizados
    Cada resultado: { "title", "url", "snippet", "source" }
    """
    endpoint = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": limit,
        "hl": "es",
        "gl": "pe",
        "api_key": api_key
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(endpoint, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SerpAPI error: {e}")

    results = []
    # SerpAPI -> 'organic_results' for Google
    for item in data.get("organic_results", [])[:limit]:
        title = item.get("title") or item.get("position") or ""
        url = item.get("link") or item.get("url") or ""
        snippet = item.get("snippet") or item.get("snippet_highlighted_words") or ""
        if url:
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": "serpapi"
            })
    return results
