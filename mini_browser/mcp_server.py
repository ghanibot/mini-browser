"""
MCP (Model Context Protocol) server for mini-browser.
Exposes web_search and web_fetch as tools for Claude, Cursor, and any MCP-compatible host.

Run: mini-browser mcp
"""

from mini_browser import search, fetch


def run() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        raise ImportError(
            "MCP package not installed.\n"
            "Install: pip install mini-browser[mcp]"
        )

    mcp = FastMCP(
        "mini-browser",
        instructions=(
            "mini-browser provides token-efficient web search and page fetching. "
            "Use web_search to find information on any topic. "
            "Use web_fetch to read a specific URL. "
            "Both tools return clean, compressed text optimized to minimize token usage."
        ),
    )

    @mcp.tool()
    def web_search(query: str, max_results: int = 3, max_tokens: int = 1000) -> str:
        """
        Search the web for current information.

        Args:
            query: What to search for
            max_results: Number of pages to retrieve (1-10)
            max_tokens: Token budget for output (100-4000)
        """
        return search(query, max_results=max_results, max_tokens=max_tokens)

    @mcp.tool()
    def web_fetch(url: str, query: str = "", max_tokens: int = 1000) -> str:
        """
        Fetch and read a specific URL.

        Args:
            url: The URL to fetch
            query: Optional — focus extraction on this topic for better relevance
            max_tokens: Token budget for output (100-4000)
        """
        return fetch(url, query=query, max_tokens=max_tokens)

    mcp.run()
