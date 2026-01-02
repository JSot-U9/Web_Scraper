# extrae texto visible y limpia
from bs4 import BeautifulSoup
import re
from typing import Tuple

def extract_visible_text(html: str) -> str:
    """
    Elimina scripts/styles y devuelve texto plano compacto.
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def first_n_sentences(text: str, n: int = 3) -> str:
    # heurística simple por puntos.
    parts = text.split(".")
    parts = [p.strip() for p in parts if p.strip()]
    return ". ".join(parts[:n]) + (". " if parts else "")
