"""
Domain configuration for mini-browser.

JS-heavy domains (need Playwright) can be extended via:
  1. Env var:  MINI_BROWSER_JS_DOMAINS=mysite.com,other.com
  2. Local:    .mini-browser.json  → {"js_domains": ["mysite.com"]}
  3. Global:   ~/.mini-browser/config.json → same format
"""

import json
import os
from pathlib import Path

_DEFAULT_JS_DOMAINS: set[str] = {
    "tradingview.com",
    "yahoo.com",
    "finance.yahoo.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "facebook.com",
    "bloomberg.com",
    "wsj.com",
    "ft.com",
    "investing.com",
    "nasdaq.com",
    "marketwatch.com",
    "cnbc.com",
    "stockbit.com",
    "idx.co.id",
    "investing.co.id",
    "reuters.com",
    "theatlantic.com",
    "nytimes.com",
    "washingtonpost.com",
    "pluang.com",
    "bareksa.com",
}

_CONFIG_PATHS = [
    Path.cwd() / ".mini-browser.json",
    Path.home() / ".mini-browser" / "config.json",
]

_cached_domains: set[str] | None = None


def get_js_domains() -> set[str]:
    """Return full set of JS-heavy domains (default + user-configured)."""
    global _cached_domains
    if _cached_domains is not None:
        return _cached_domains

    extra: set[str] = set()

    # 1. Env var
    env = os.environ.get("MINI_BROWSER_JS_DOMAINS", "")
    if env:
        extra.update(d.strip() for d in env.split(",") if d.strip())

    # 2. Config files
    for path in _CONFIG_PATHS:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                extra.update(data.get("js_domains", []))
            except Exception:
                pass

    _cached_domains = _DEFAULT_JS_DOMAINS | extra
    return _cached_domains


def reload() -> None:
    """Force reload config (useful after editing config file)."""
    global _cached_domains
    _cached_domains = None


def add_js_domain(domain: str) -> None:
    """Add a domain to JS-heavy list at runtime."""
    global _cached_domains
    domains = get_js_domains()
    domains.add(domain.removeprefix("www."))
    _cached_domains = domains


def get_search_provider() -> str:
    """Return the configured search provider ('duckduckgo' or 'tavily')."""
    return os.environ.get("MINI_BROWSER_SEARCH_PROVIDER", "duckduckgo").lower()
