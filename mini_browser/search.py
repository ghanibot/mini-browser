from urllib.parse import urlparse

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_urls(
    query: str,
    max_results: int = 5,
    timelimit: str | None = None,
) -> list[dict]:
    """
    Search DuckDuckGo. Returns list of dicts: href, title, body.

    timelimit: "d" (day), "w" (week), "m" (month), "y" (year)
    """
    try:
        kwargs: dict = {"max_results": max_results * 2}
        if timelimit:
            kwargs["timelimit"] = timelimit

        results = list(DDGS().text(query, **kwargs))
        results = _dedup_domains(results, max_results)
        return results
    except Exception:
        return []


def _dedup_domains(results: list[dict], limit: int) -> list[dict]:
    """Keep at most 1 result per domain to maximize source diversity."""
    seen_domains: set[str] = set()
    out: list[dict] = []
    for r in results:
        url = r.get("href", "")
        try:
            domain = urlparse(url).netloc.removeprefix("www.")
        except Exception:
            domain = url
        if domain not in seen_domains:
            seen_domains.add(domain)
            out.append(r)
        if len(out) >= limit:
            break
    return out
