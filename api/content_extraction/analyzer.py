import re
from typing import Dict, List

KEY_PATTERNS = {
    "ubicacion": r"(lima|perú|remoto|presencial|híbrido)",
    "precio": r"(s\/\.?\s?\d+|\$\s?\d+|\d+\s?(usd|soles))",
    "pago": r"(mensual|quincenal|por hora|anual)",
    "modalidad": r"(remoto|presencial|híbrido)",
    "contrato": r"(tiempo completo|part time|freelance|contrato)"
}

def analyze_text(text: str, query: str) -> Dict:
    findings: Dict[str, List[str]] = {}

    for key, pattern in KEY_PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            findings[key] = list(set(matches))[:3]

    # Relevancia básica
    relevance = sum(1 for term in query.lower().split() if term in text.lower())

    return {
        "relevance": relevance,
        "insights": findings
    }
