"""
MCP (Model Context Protocol) server for mini-browser.
Compatible with: Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor, and any MCP host.

Run:  mini-browser mcp
"""

from mini_browser import search, fetch
from mini_browser.tools import _deep_research


def run() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise ImportError(
            "MCP package not installed.\n"
            "Install: pip install mini-browser[mcp]  or  pip install mcp"
        )

    mcp = FastMCP(
        "mini-browser",
        instructions=(
            "mini-browser gives you real-time web access with minimal token usage.\n"
            "- web_search: find current info on any topic\n"
            "- web_fetch: read a specific URL (supports JS sites, PDFs)\n"
            "- deep_research: multi-source research on complex topics\n"
            "Always prefer these tools over your training data for time-sensitive questions."
        ),
    )

    @mcp.tool()
    def web_search(query: str, max_results: int = 3, max_tokens: int = 1500) -> str:
        """
        Search the web for current, real-time information.

        Use for: news, stock prices, weather, recent events, product prices,
        anything that changes over time or happened after your training cutoff.

        Args:
            query: What to search for — be specific
            max_results: Pages to fetch (1-10, default 3)
            max_tokens: Output token budget (100-4000, default 1500)
        """
        return search(query, max_results=max_results, max_tokens=max_tokens)

    @mcp.tool()
    def web_fetch(url: str, query: str = "", max_tokens: int = 1500) -> str:
        """
        Fetch and read content from a specific URL.

        Supports: JavaScript-heavy sites (Yahoo Finance, TradingView, Bloomberg),
        PDFs, paywalled articles, and any standard webpage.

        Args:
            url: Full URL to fetch (must start with http:// or https://)
            query: Optional focus topic for relevance filtering
            max_tokens: Output token budget (100-4000, default 1500)
        """
        return fetch(url, query=query, max_tokens=max_tokens)

    @mcp.tool()
    def deep_research(topic: str, max_tokens: int = 1000) -> str:
        """
        Deep multi-source research on a topic.

        Generates 3 sub-queries, fetches from multiple sources, returns synthesized content.
        Use for: complex topics that need breadth, comparisons, multi-angle analysis.

        Args:
            topic: Research topic or question
            max_tokens: Token budget per sub-query (default 1000)
        """
        return _deep_research(topic, max_tokens=max_tokens)

    mcp.run()
