# heurísticas para extraer campos tipo ubicacion, precio, fechas, pagos, detalles.
import re
from typing import Optional, List

def extract_location(text: str) -> Optional[str]:
    patterns = [
        r"(?:ubicaci[oó]n|lugar|ciudad|localizaci[oó]n)[:\-\s]+([A-Za-zÁÉÍÓÚáéíóú0-9\,\-\s]+)",
        r"\b(en|en la|en el)\s+([A-Z][A-Za-zÁÉÍÓÚáéíóú\s]+(?:,|\b))",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            # return first capturing group that looks like a place
            g = next((g for g in m.groups() if g), None)
            if g:
                return g.strip().strip(",:")
    return None

def extract_prices(text: str) -> List[str]:
    # detecta formatos S/. 1,200, $1200, 1200 PEN, 1200 USD
    patterns = [
        r"S\/\.\s?\d{1,3}(?:[,\.\d]{0,})",
        r"\$\s?\d{1,3}(?:[,\.\d]{0,})",
        r"\b\d{1,3}(?:[,\.\d]{0,})\s?(PEN|USD|EUR|S\/\.)\b",
    ]
    found = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            found.append(m.group().strip())
    return list(dict.fromkeys(found))  # dedupe preserve order

def extract_payment_terms(text: str) -> Optional[str]:
    patterns = [
        r"(pago(?:s)?(?: mensuales| mensuales)?|remuneraci[oó]n|salario|sueldo)[:\-\s]+([A-Za-z0-9\$\S \,\.]+)",
        r"(pago(?:s)?|mensualidad)[:\-\s]+([A-Za-z0-9\$\S \,\.]+)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(2).strip()
    return None

def extract_dates(text: str) -> List[str]:
    # formatos simples: DD/MM/YYYY, YYYY-MM-DD, 12 de enero de 2025
    patterns = [
        r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b",
        r"\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b",
        r"\b\d{1,2}\s+de\s+[A-Za-záéíóú]+\s+de\s+\d{4}\b",
    ]
    found = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            found.append(m.group())
    return list(dict.fromkeys(found))
