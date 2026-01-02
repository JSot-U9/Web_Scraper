# score simple de relevancia entre query y texto
def relevance_score(text: str, query: str) -> float:
    if not query:
        return 0.0
    q_terms = [t.strip().lower() for t in query.split() if t.strip()]
    text_l = text.lower()
    matches = sum(1 for t in q_terms if t in text_l)
    return matches / max(1, len(q_terms))
