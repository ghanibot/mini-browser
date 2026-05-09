import re
from urllib.parse import urlparse

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

# Domains known for spam, clickbait, or low-quality content
_BLOCKLIST_PATTERNS = [
    r"\.store/",
    r"\.xyz/",
    r"\.click/",
    r"\.buzz/",
    r"\.top/",
    r"\.icu/",
    r"\.vip/",
    r"blogspot\.com",
    r"wordpress\.com",
]

_BLOCKLIST_RE = re.compile("|".join(_BLOCKLIST_PATTERNS))

# Minimum snippet length to filter near-empty results
_MIN_SNIPPET_WORDS = 8


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
        kwargs: dict = {"max_results": max_results * 3}
        if timelimit:
            kwargs["timelimit"] = timelimit

        results = list(DDGS().text(query, **kwargs))
        results = _filter_and_dedup(results, max_results)
        return results
    except Exception:
        return []


def _is_quality(result: dict) -> bool:
    url = result.get("href", "")
    snippet = result.get("body", "")
    title = result.get("title", "")

    if _BLOCKLIST_RE.search(url):
        return False

    if len(snippet.split()) < _MIN_SNIPPET_WORDS:
        return False

    # Detect low-quality landing pages: title == snippet start or very high repetition
    combined = (title + " " + snippet).lower()
    words = combined.split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.35:  # >65% repeated words = low quality
            return False

    return True


def _filter_and_dedup(results: list[dict], limit: int) -> list[dict]:
    """Filter spam, deduplicate domains, return up to limit results."""
    seen_domains: set[str] = set()
    out: list[dict] = []
    for r in results:
        if not _is_quality(r):
            continue
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
