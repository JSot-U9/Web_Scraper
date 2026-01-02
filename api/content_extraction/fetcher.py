import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AcademicScraper/1.0)"
}

async def fetch_html(url: str) -> str:
    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers=HEADERS
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.text
    except Exception:
        return ""
