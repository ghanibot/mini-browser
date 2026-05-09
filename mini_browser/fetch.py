import re
import httpx
import trafilatura


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _bs_fallback(html: str) -> str | None:
    """Simple paragraph extraction without trafilatura."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(separator=" ", strip=True) for p in paragraphs)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text if len(text) > 100 else None
    except Exception:
        return None


def fetch_clean(url: str, timeout: int = 12) -> str | None:
    """
    Fetch URL and extract main content as clean text.
    Tries trafilatura first, falls back to BeautifulSoup paragraph extraction.
    Returns None on total failure.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    try:
        response = httpx.get(url, timeout=timeout, headers=_HEADERS, follow_redirects=True)
        response.raise_for_status()
        html = response.text

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,
            favor_recall=True,
        )

        if text and len(text.split()) > 50:
            return text

        # fallback
        return _bs_fallback(html)

    except Exception:
        return None
