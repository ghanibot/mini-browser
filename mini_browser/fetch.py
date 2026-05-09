import httpx
import trafilatura


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_clean(url: str, timeout: int = 10) -> str | None:
    """
    Fetch URL and extract main content as clean text.
    Returns None on failure.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        response = httpx.get(url, timeout=timeout, headers=_HEADERS, follow_redirects=True)
        response.raise_for_status()

        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
        )
        return text or None

    except Exception:
        return None
