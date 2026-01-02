import os
import re
import math
from typing import List, Dict
from urllib.parse import urlparse, urlunparse

import httpx

# ===== SERPER CONFIG =====
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"

# ==============================
# HTML FETCHER
# ==============================
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

# ==============================
# HTML TEXT EXTRACTION
# ==============================
from bs4 import BeautifulSoup

def extract_visible_text(html: str) -> str:
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())

# ==============================
# CONTENT ANALYSIS
# ==============================
KEY_PATTERNS = {
    "ubicacion": r"(lima|perú|remoto|presencial|híbrido)",
    "precio_salario": r"(s\/\.?\s?\d+|\$\s?\d+|\d+\s?(usd|soles))",
    "tipo_pago": r"(mensual|quincenal|por hora|anual)",
    "modalidad": r"(remoto|presencial|híbrido)",
    "contrato": r"(tiempo completo|part time|freelance|contrato)"
}

def analyze_text(text: str, query: str) -> Dict:
    insights = {}

    for key, pattern in KEY_PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            insights[key] = list(set(
                m if isinstance(m, str) else m[0] for m in matches
            ))[:3]

    relevance = sum(
        1 for term in query.lower().split()
        if term in text.lower()
    )

    return {
        "relevance": relevance,
        "insights": insights
    }

# ==============================
# SERPER SEARCH
# ==============================
async def search_serper(query: str, limit: int = 5) -> List[Dict]:
    if not SERPER_API_KEY:
        return []

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {"q": query, "num": limit}

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(SERPER_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    results = []
    for item in data.get("organic", [])[:limit]:
        results.append({
            "title": item.get("title") or "",
            "url": item.get("link") or "",
            "snippet": item.get("snippet") or "",
            "source": "serper"
        })

    return results

# ==============================
# NORMALIZATION & DEDUP
# ==============================
def normalize_url(raw_url: str) -> str:
    try:
        p = urlparse(raw_url)
    except Exception:
        return raw_url.strip()

    scheme = p.scheme or "https"
    netloc = p.netloc.lower()
    path = p.path or "/"
    path = re.sub(r"/{2,}", "/", path)

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return urlunparse((scheme, netloc, path, "", "", ""))

def dedupe_results(results: List[Dict]) -> List[Dict]:
    index = {}
    for r in results:
        key = normalize_url(r.get("url", ""))
        if key not in index or len(r.get("snippet", "")) > len(index[key].get("snippet", "")):
            index[key] = r
    return list(index.values())

# ==============================
# SCORING
# ==============================
def _term_presence_score(title: str, snippet: str, query: str) -> float:
    if not query:
        return 0.0

    terms = query.lower().split()
    text = f"{title} {snippet}".lower()

    hits = sum(1 for t in terms if t in text)
    return min(1.0, hits / max(len(terms), 1))

def _snippet_length_score(snippet: str) -> float:
    return min(1.0, len(snippet) / 200.0) if snippet else 0.0

def _compute_score(item: Dict, query: str) -> float:
    title = item.get("title", "")
    snippet = item.get("snippet", "")
    term_score = _term_presence_score(title, snippet, query)
    snippet_score = _snippet_length_score(snippet)

    score = (0.6 * term_score) + (0.4 * snippet_score)
    return score if math.isfinite(score) else 0.0

# ==============================
# AGGREGATOR (PUBLIC)
# ==============================
async def aggregate_search(query: str, limit: int = 10) -> List[Dict]:
    results: List[Dict] = []

    try:
        results.extend(await search_serper(query, limit))
    except Exception:
        pass

    if not results:
        return []

    results = dedupe_results(results)

    for r in results:
        r["score"] = _compute_score(r, query)

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]

    # ===== CONTENT ENRICHMENT =====
    for r in results:
        html = await fetch_html(r["url"])
        text = extract_visible_text(html)
        r["analysis"] = analyze_text(text, query)

    return results
