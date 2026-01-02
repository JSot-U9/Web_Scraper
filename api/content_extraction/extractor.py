from bs4 import BeautifulSoup

def extract_visible_text(html: str) -> str:
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    # Eliminar ruido
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())
    return text
