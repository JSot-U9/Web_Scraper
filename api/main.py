# /home/deployer/scraper/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from search_providers.aggregator import aggregate_search
from extractors.page_extractor import extract_page_data
import asyncio

app = FastAPI(title="Search + Page Extractor")

class SearchRequest(BaseModel):
    q: str
    limit: int = 10
    concurrency: int = 5   # opcional: controla concurrencia de fetches
    min_relevance: float = 0.15  # filtro mínimo

@app.post("/search")
async def search(req: SearchRequest):
    q = req.q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query empty")

    # 1) obtener URLs desde el agregador (ya async)
    raw_results = await aggregate_search(q, req.limit)
    if not raw_results:
        return {"query": q, "results": [], "count": 0}

    # 2) limitar URLs y extraer
    urls = [r.get("url") for r in raw_results if r.get("url")]
    semaphore = asyncio.Semaphore(req.concurrency)
    tasks = []

    async def _worker(u):
        async with semaphore:
            try:
                return await extract_page_data(u, q)
            except Exception as e:
                return {"url": u, "error": "extract_error", "detail": str(e)}

    for u in urls:
        tasks.append(asyncio.create_task(_worker(u)))

    pages = await asyncio.gather(*tasks)

    # 3) filtrar por relevancia
    pages_filtered = [p for p in pages if p.get("relevance", 0) >= req.min_relevance and "error" not in p]

    # 4) ordenar por relevance desc
    pages_sorted = sorted(pages_filtered, key=lambda x: x.get("relevance", 0), reverse=True)

    return {"query": q, "results": pages_sorted, "count": len(pages_sorted)}
