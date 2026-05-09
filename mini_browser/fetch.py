"""
Fetch and extract clean text from URLs.

Strategy per request:
  1. PDF URL/content-type → pdf.extract_pdf()
  2. JS-heavy domain → Playwright (persistent browser)
  3. Simple site → httpx + trafilatura → BS4 fallback → Playwright last resort
  4. Retry up to 2x with backoff on failure
"""

import re
import time
import atexit
import httpx
import trafilatura

from mini_browser.config import get_js_domains
from mini_browser.pdf import extract_pdf, is_pdf_url, is_pdf_response

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

# --- Persistent Playwright browser ---

_pw = None
_browser = None


def _get_browser():
    global _pw, _browser
    if _browser is None:
        try:
            from playwright.sync_api import sync_playwright
            _pw = sync_playwright().start()
            _browser = _pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                ],
            )
        except Exception:
            _browser = None
    return _browser


def _shutdown_browser():
    global _pw, _browser
    try:
        if _browser:
            _browser.close()
        if _pw:
            _pw.stop()
    except Exception:
        pass
    _browser = None
    _pw = None


atexit.register(_shutdown_browser)


# --- Extraction helpers ---

def _trafilatura_extract(html: str) -> str | None:
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
        favor_precision=False,
        favor_recall=True,
    )
    return text if text and len(text.split()) > 50 else None


def _bs_extract(html: str) -> str | None:
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


def _playwright_fetch_html(url: str, timeout: int = 20) -> str | None:
    browser = _get_browser()
    if browser is None:
        return None
    try:
        context = browser.new_context(
            user_agent=_HEADERS["User-Agent"],
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            viewport={"width": 1280, "height": 800},
            extra_http_headers={
                "Accept-Language": _HEADERS["Accept-Language"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
        except Exception:
            pass
        page.wait_for_timeout(2000)
        html = page.content()
        context.close()
        return html
    except Exception:
        return None


def _needs_js(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower().removeprefix("www.")
        return any(d in domain for d in get_js_domains())
    except Exception:
        return False


# --- Main fetch function ---

def fetch_clean(url: str, timeout: int = 12, retries: int = 2) -> str | None:
    """
    Fetch URL and return clean text. Handles HTML, JS-heavy sites, and PDFs.
    Retries up to `retries` times with exponential backoff.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            result = _fetch_once(url, timeout)
            if result:
                return result
        except Exception as e:
            last_error = e

        if attempt < retries:
            time.sleep(1.5 ** attempt)

    return None


def _fetch_once(url: str, timeout: int) -> str | None:
    # PDF: detect by URL pattern first
    if is_pdf_url(url):
        try:
            resp = httpx.get(url, timeout=timeout, headers=_HEADERS, follow_redirects=True)
            resp.raise_for_status()
            return extract_pdf(resp.content)
        except Exception:
            return None

    # JS-heavy: go straight to Playwright
    if _needs_js(url):
        html = _playwright_fetch_html(url, timeout=timeout)
        if html:
            return _trafilatura_extract(html) or _bs_extract(html)
        return None

    # Fast path: httpx
    try:
        resp = httpx.get(url, timeout=timeout, headers=_HEADERS, follow_redirects=True)
        resp.raise_for_status()

        # Check if response is actually a PDF
        content_type = resp.headers.get("content-type", "")
        if is_pdf_response(content_type):
            return extract_pdf(resp.content)

        html = resp.text
        text = _trafilatura_extract(html)
        if text:
            return text

        text = _bs_extract(html)
        if text:
            return text

    except Exception:
        pass

    # Last resort: Playwright
    html = _playwright_fetch_html(url, timeout=timeout)
    if html:
        return _trafilatura_extract(html) or _bs_extract(html)

    return None
