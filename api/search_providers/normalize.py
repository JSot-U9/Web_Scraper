# search_providers/normalize.py
from urllib.parse import urlparse, urlunparse
import re
from typing import Dict, List

def normalize_url(raw_url: str) -> str:
    """
    Normaliza URL para deduplicación:
    - Lowercase host
    - Quitar query y fragment
    - Quitar barra final salvo si es la raíz
    """
    try:
        p = urlparse(raw_url)
    except Exception:
        return raw_url.strip()

    scheme = p.scheme or "http"
    netloc = p.netloc.lower()
    path = p.path or "/"

    # Elimina barras dobles
    path = re.sub(r"/{2,}", "/", path)

    # Normalizar: remove trailing slash except root
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    normalized = urlunparse((scheme, netloc, path, "", "", ""))
    return normalized

def dedupe_results(results: List[Dict]) -> List[Dict]:
    """
    Deduplica por URL normalizada. Mantiene la versión con snippet más largo
    (proxy simple de calidad).
    """
    index = {}
    for r in results:
        key = normalize_url(r.get("url", ""))
        existing = index.get(key)
        if not existing:
            index[key] = r
        else:
            # preferir snippet más largo (proxy calidad), si igual, mantener el existente
            if len(r.get("snippet", "") or "") > len(existing.get("snippet", "") or ""):
                index[key] = r
    return list(index.values())
