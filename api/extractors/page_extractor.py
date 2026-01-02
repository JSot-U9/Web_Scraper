# orquesta la extracción por página
from .page_fetcher import fetch_html
from .text_cleaner import extract_visible_text, first_n_sentences
from .fields import extract_location, extract_prices, extract_payment_terms, extract_dates
from .relevance import relevance_score
from typing import Dict, Optional
import asyncio

async def extract_page_data(url: str, query: str, timeout: int = 18) -> Dict:
    """
    Intenta descargar la página y extraer campos clave relacionados con `query`.
    Devuelve dict con keys: url, title (snippet), relevance, location, prices, payments, dates, excerpt
    """
    html = await fetch_html(url, timeout=timeout)
    if not html:
        return {
            "url": url,
            "error": "fetch_failed"
        }

    text = extract_visible_text(html)
    excerpt = first_n_sentences(text, n=3)

    return {
        "url": url,
        "excerpt": excerpt,
        "relevance": relevance_score(text, query),
        "location": extract_location(text),
        "prices": extract_prices(text),
        "payments": extract_payment_terms(text),
        "dates": extract_dates(text)
    }
