# fetch HTML pages (async)
import httpx
from typing import Optional

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ScraperBot/1.0; +https://example.com/bot)"
}

async def fetch_html(url: str, timeout: int = 20) -> Optional[str]:
    """
    Descarga HTML de una URL. Devuelve None si falla.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url, headers=DEFAULT_HEADERS)
            r.raise_for_status()
            return r.text
    except Exception:
        return None
