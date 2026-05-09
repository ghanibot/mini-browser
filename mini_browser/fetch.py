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

# Sites known to require JS rendering
_JS_HEAVY_DOMAINS = {
    "tradingview.com", "yahoo.com", "finance.yahoo.com",
    "twitter.com", "x.com", "instagram.com", "facebook.com",
    "bloomberg.com", "wsj.com", "ft.com", "investing.com",
    "nasdaq.com", "marketwatch.com", "cnbc.com",
    "stockbit.com", "idx.co.id", "investing.co.id",
}


def _needs_js(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower().removeprefix("www.")
        return any(d in domain for d in _JS_HEAVY_DOMAINS)
    except Exception:
        return False


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


def _playwright_fetch(url: str, timeout: int = 20) -> str | None:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                ],
            )
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
            # mask webdriver flag
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = context.new_page()
            try:
                page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
            except Exception:
                # networkidle timeout — still try to get content
                pass
            page.wait_for_timeout(2500)
            html = page.content()
            browser.close()

        text = _trafilatura_extract(html)
        return text or _bs_extract(html)
    except Exception:
        return None


def fetch_clean(url: str, timeout: int = 12) -> str | None:
    """
    Fetch URL and extract main content as clean text.

    Strategy:
    1. If JS-heavy domain → go straight to Playwright
    2. Otherwise try httpx + trafilatura (fast path)
    3. If content too short → fallback to BeautifulSoup
    4. If still empty → fallback to Playwright
    """
    if not url or not url.startswith(("http://", "https://")):
        return None

    # Fast path for simple sites
    if not _needs_js(url):
        try:
            response = httpx.get(url, timeout=timeout, headers=_HEADERS, follow_redirects=True)
            response.raise_for_status()
            html = response.text

            text = _trafilatura_extract(html)
            if text:
                return text

            text = _bs_extract(html)
            if text:
                return text
        except Exception:
            pass

    # Playwright fallback — handles JS-heavy and failed fast-path
    return _playwright_fetch(url, timeout=timeout)
