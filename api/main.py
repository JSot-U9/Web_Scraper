# main.py
# Ruta: /home/deployer/scraper/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from search_providers.aggregator import aggregate_search

app = FastAPI(title="Search Aggregator API")

class SearchRequest(BaseModel):
    q: str
    limit: int = 10

@app.on_event("startup")
async def startup_event():
    # lugar para inicializar conexiones si añades cache/redis más adelante
    pass

@app.post("/search")
async def search(req: SearchRequest):
    q = req.q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Query empty")

    results: List[Dict] = await aggregate_search(q, req.limit)
    return {"query": q, "results": results, "count": len(results)}
