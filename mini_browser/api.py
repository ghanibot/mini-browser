"""
mini-browser HTTP API server.
Exposes /search and /fetch as JSON endpoints for any language/agent.

Run: python -m mini_browser.api
     uvicorn mini_browser.api:app --port 7842
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from mini_browser import search, fetch
from mini_browser.token_counter import count_tokens
from mini_browser import cache as _cache

app = FastAPI(
    title="mini-browser",
    description="Token-efficient web search and browsing for AI agents",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str
    max_results: int = 3
    max_tokens: int = 1500
    output_format: str = "text"


class FetchRequest(BaseModel):
    url: str
    query: str = ""
    max_tokens: int = 1500
    output_format: str = "text"


class SearchResponse(BaseModel):
    result: str
    tokens: int
    cached: bool = False


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.4.0"}


@app.get("/cache/stats")
def cache_stats():
    return _cache.stats()


@app.delete("/cache")
def clear_cache():
    _cache.clear()
    return {"cleared": True}


@app.post("/search", response_model=SearchResponse)
def api_search(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")

    key = _cache.make_key("search", req.query, req.max_results, req.max_tokens, req.output_format)
    cached_val = _cache.get(key)
    cached = cached_val is not None

    result = search(
        req.query,
        max_results=req.max_results,
        max_tokens=req.max_tokens,
        output_format=req.output_format,
    )
    return SearchResponse(result=result, tokens=count_tokens(result), cached=cached)


@app.get("/search", response_model=SearchResponse)
def api_search_get(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(3, ge=1, le=10),
    max_tokens: int = Query(1500, ge=100, le=8000),
    output_format: str = Query("text", pattern="^(text|json)$"),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="q cannot be empty")

    result = search(q, max_results=max_results, max_tokens=max_tokens, output_format=output_format)
    return SearchResponse(result=result, tokens=count_tokens(result))


@app.post("/fetch", response_model=SearchResponse)
def api_fetch(req: FetchRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="url cannot be empty")

    result = fetch(req.url, query=req.query, max_tokens=req.max_tokens, output_format=req.output_format)
    return SearchResponse(result=result, tokens=count_tokens(result))


@app.get("/fetch", response_model=SearchResponse)
def api_fetch_get(
    url: str = Query(..., description="URL to fetch"),
    query: str = Query("", description="Optional focus query"),
    max_tokens: int = Query(1500, ge=100, le=8000),
):
    result = fetch(url, query=query, max_tokens=max_tokens)
    return SearchResponse(result=result, tokens=count_tokens(result))


def run(host: str = "127.0.0.1", port: int = 7842):
    import uvicorn
    uvicorn.run("mini_browser.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
