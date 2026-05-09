try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_urls(query: str, max_results: int = 5) -> list[dict]:
    """
    Search DuckDuckGo and return list of result dicts with href, title, body.
    """
    try:
        results = list(DDGS().text(query, max_results=max_results))
        return results
    except Exception:
        return []
