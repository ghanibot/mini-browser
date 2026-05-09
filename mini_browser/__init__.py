"""
mini-browser: Token-efficient web search and browsing for AI agents.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .search import search_urls
from .fetch import fetch_clean
from .compress import compress
from .token_counter import count_tokens
from . import cache

__version__ = "0.4.0"
__all__ = [
    "search", "fetch",
    "search_urls", "fetch_clean", "compress", "count_tokens",
]


def _detect_timelimit(query: str) -> str | None:
    q = query.lower()
    if any(k in q for k in ("hari ini", "today", "terbaru", "latest", "terkini", "sekarang", "now", "harga")):
        return "w"
    if any(k in q for k in ("bulan ini", "this month", "minggu ini", "this week")):
        return "m"
    if any(k in q for k in ("tahun ini", "this year")):
        return "y"
    return None


def _clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _format_results(results: list[dict], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)
    return "\n\n---\n\n".join(
        f"## {r['title']}\nSource: {r['url']}\n\n{r['content']}"
        for r in results
        if r.get("content")
    )


def search(
    query: str,
    max_results: int = 3,
    max_tokens: int = 1500,
    output_format: str = "text",
) -> str:
    """
    Search the web and return clean, token-efficient text.

    Args:
        query: Search query string
        max_results: Number of search results to process
        max_tokens: Maximum tokens in output (approximate)
        output_format: "text" (default) or "json"

    Returns:
        Clean relevant text, or JSON array if output_format="json"
    """
    cache_key = cache.make_key("search", query, max_results, max_tokens, output_format)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    timelimit = _detect_timelimit(query)
    urls = search_urls(query, max_results=max_results, timelimit=timelimit)

    if not urls:
        return "No results found."

    header_overhead = 80 * len(urls)
    token_budget_per_result = max(80, (max_tokens - header_overhead) // max(len(urls), 1))

    def _process(result: dict) -> dict | None:
        url = result.get("href", "")
        title = result.get("title", "No title")
        snippet = result.get("body", "")

        full_text = fetch_clean(url)
        content = _clean_text(full_text) if full_text else _clean_text(snippet)

        if not content:
            return None

        compressed = compress(content, query, max_tokens=token_budget_per_result)
        if not compressed:
            return None

        return {
            "title": title,
            "url": url,
            "content": compressed,
            "tokens": count_tokens(compressed),
        }

    # Parallel fetch — all URLs at once
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(len(urls), 4)) as executor:
        futures = {executor.submit(_process, r): r for r in urls}
        for future in as_completed(futures):
            item = future.result()
            if item:
                results.append(item)

    # Restore original order (as_completed scrambles it)
    url_order = {r.get("href", ""): i for i, r in enumerate(urls)}
    results.sort(key=lambda x: url_order.get(x["url"], 999))

    if not results:
        return "No content could be retrieved."

    output = _format_results(results, output_format)
    cache.set(cache_key, output)
    return output


def fetch(
    url: str,
    query: str = "",
    max_tokens: int = 1500,
    output_format: str = "text",
) -> str:
    """
    Fetch a URL and return clean, token-efficient content.

    Args:
        url: URL to fetch (http/https, including PDFs)
        query: Optional query for relevance-based filtering
        max_tokens: Maximum tokens in output (approximate)
        output_format: "text" (default) or "json"

    Returns:
        Clean text from the page, or JSON if output_format="json"
    """
    cache_key = cache.make_key("fetch", url, query, max_tokens, output_format)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    content = fetch_clean(url)
    if not content:
        return "Failed to fetch or extract content from URL."

    content = _clean_text(content)

    if query:
        compressed = compress(content, query, max_tokens=max_tokens)
    else:
        words = content.split()
        # estimate token budget: tokens ≈ words * 1.35
        word_limit = int(max_tokens / 1.35)
        compressed = " ".join(words[:word_limit])

    if output_format == "json":
        result = json.dumps({
            "url": url,
            "content": compressed,
            "tokens": count_tokens(compressed),
        }, ensure_ascii=False, indent=2)
    else:
        result = compressed

    cache.set(cache_key, result)
    return result
