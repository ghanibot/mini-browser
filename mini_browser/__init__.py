"""
mini-browser: Token-efficient web search and browsing for AI agents.
"""

from .search import search_urls
from .fetch import fetch_clean
from .compress import compress
from .token_counter import count_tokens

__version__ = "0.1.0"
__all__ = ["search", "fetch", "search_urls", "fetch_clean", "compress", "count_tokens"]


def search(query: str, max_results: int = 3, max_tokens: int = 1000) -> str:
    """
    Search the web and return clean, token-efficient text.

    Args:
        query: Search query string
        max_results: Number of search results to process
        max_tokens: Maximum tokens in output (approximate)

    Returns:
        Clean, relevant text from top search results
    """
    urls = search_urls(query, max_results=max_results)

    if not urls:
        return "No results found."

    all_content = []
    budget_per_result = max_tokens // max(len(urls), 1)

    for result in urls:
        url = result.get("href", "")
        title = result.get("title", "No title")
        snippet = result.get("body", "")

        full_text = fetch_clean(url)
        content = full_text or snippet

        if not content:
            continue

        compressed = compress(content, query, max_tokens=budget_per_result)
        if compressed:
            all_content.append(f"## {title}\nSource: {url}\n\n{compressed}")

    if not all_content:
        return "No content could be retrieved."

    return "\n\n---\n\n".join(all_content)


def fetch(url: str, query: str = "", max_tokens: int = 1000) -> str:
    """
    Fetch a URL and return clean, token-efficient content.

    Args:
        url: URL to fetch
        query: Optional query for relevance-based filtering
        max_tokens: Maximum tokens in output (approximate)

    Returns:
        Clean text from the page
    """
    content = fetch_clean(url)
    if not content:
        return "Failed to fetch or extract content from URL."

    if query:
        return compress(content, query, max_tokens=max_tokens)

    words = content.split()
    return " ".join(words[:max_tokens])
