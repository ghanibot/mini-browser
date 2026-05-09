"""
Universal tool definitions for mini-browser.

Exports tool schemas in OpenAI / Anthropic format and a unified handler.
Drop-in for any agent that supports function/tool calling.

Usage:
    from mini_browser.tools import TOOLS_OPENAI, TOOLS_ANTHROPIC, handle_tool_call

    # OpenAI / Codex / OpenCode / Gemini
    response = client.chat.completions.create(
        model="gpt-4o",
        tools=TOOLS_OPENAI,
        messages=messages,
    )

    # Anthropic / Claude
    response = client.messages.create(
        model="claude-opus-4-7",
        tools=TOOLS_ANTHROPIC,
        messages=messages,
    )

    # Execute tool call from any provider
    result = handle_tool_call(tool_name, tool_input_dict)
"""

from mini_browser import search, fetch
from mini_browser import cache as _cache

# ── Schema (shared) ───────────────────────────────────────────

_SEARCH_PARAMS = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query — be specific for best results",
        },
        "max_results": {
            "type": "integer",
            "description": "Number of web pages to fetch (1–10, default 3)",
            "default": 3,
        },
        "max_tokens": {
            "type": "integer",
            "description": "Token budget for output (100–4000, default 1500)",
            "default": 1500,
        },
    },
    "required": ["query"],
}

_FETCH_PARAMS = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "Full URL to fetch (http/https). Supports JS-heavy sites and PDFs.",
        },
        "query": {
            "type": "string",
            "description": "Optional focus topic — extracts content most relevant to this",
            "default": "",
        },
        "max_tokens": {
            "type": "integer",
            "description": "Token budget for output (100–4000, default 1500)",
            "default": 1500,
        },
    },
    "required": ["url"],
}

_DEEP_RESEARCH_PARAMS = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "Research topic — will be split into multiple sub-queries for depth",
        },
        "max_tokens": {
            "type": "integer",
            "description": "Token budget per sub-query (default 1000)",
            "default": 1000,
        },
    },
    "required": ["topic"],
}

# ── OpenAI format (Codex, OpenCode, Gemini, GPT) ─────────────

TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current, real-time information. "
                "Returns clean, token-efficient text from top results. "
                "Use for: news, prices, facts, recent events."
            ),
            "parameters": _SEARCH_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": (
                "Fetch and read a specific URL. "
                "Supports JavaScript-heavy sites (finance, social media), PDFs, and paywalled sites. "
                "Returns clean, token-efficient content."
            ),
            "parameters": _FETCH_PARAMS,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deep_research",
            "description": (
                "Multi-angle deep research on a topic. "
                "Generates multiple sub-queries, fetches and synthesizes results from several sources. "
                "Use for complex questions that need breadth."
            ),
            "parameters": _DEEP_RESEARCH_PARAMS,
        },
    },
]

# ── Anthropic / Claude format ─────────────────────────────────

TOOLS_ANTHROPIC = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current, real-time information. "
            "Returns clean, token-efficient text from top results. "
            "Use for: news, prices, facts, recent events, anything that changes over time."
        ),
        "input_schema": _SEARCH_PARAMS,
    },
    {
        "name": "web_fetch",
        "description": (
            "Fetch and read a specific URL. "
            "Supports JavaScript-heavy sites (Yahoo Finance, TradingView, Bloomberg), "
            "PDFs, and most websites. Returns clean, token-efficient content."
        ),
        "input_schema": _FETCH_PARAMS,
    },
    {
        "name": "deep_research",
        "description": (
            "Multi-angle deep research. Breaks topic into sub-queries, "
            "fetches multiple sources, returns synthesized content. "
            "Best for complex topics needing breadth."
        ),
        "input_schema": _DEEP_RESEARCH_PARAMS,
    },
]

# ── Gemini format (Google) ────────────────────────────────────

TOOLS_GEMINI = {
    "function_declarations": [
        {
            "name": "web_search",
            "description": (
                "Search the web for current information. Returns clean, relevant text."
            ),
            "parameters": _SEARCH_PARAMS,
        },
        {
            "name": "web_fetch",
            "description": "Fetch and extract content from a URL. Supports JS sites and PDFs.",
            "parameters": _FETCH_PARAMS,
        },
        {
            "name": "deep_research",
            "description": "Deep multi-source research on a topic.",
            "parameters": _DEEP_RESEARCH_PARAMS,
        },
    ]
}

# ── Tool handler ──────────────────────────────────────────────

def handle_tool_call(name: str, arguments: dict) -> str:
    """
    Execute a mini-browser tool call. Works with any provider.

    Args:
        name: Tool name ("web_search", "web_fetch", "deep_research")
        arguments: Dict of tool arguments

    Returns:
        String result to pass back to the model
    """
    if name == "web_search":
        return search(
            query=arguments["query"],
            max_results=int(arguments.get("max_results", 3)),
            max_tokens=int(arguments.get("max_tokens", 1500)),
        )

    elif name == "web_fetch":
        return fetch(
            url=arguments["url"],
            query=arguments.get("query", ""),
            max_tokens=int(arguments.get("max_tokens", 1500)),
        )

    elif name == "deep_research":
        return _deep_research(
            topic=arguments["topic"],
            max_tokens=int(arguments.get("max_tokens", 1000)),
        )

    else:
        return f"Unknown tool: {name}"


def _deep_research(topic: str, max_tokens: int = 1000) -> str:
    """Multi-angle research: generate sub-queries, search each, combine."""
    import re

    sub_queries = [
        topic,
        f"{topic} latest news",
        f"{topic} analysis details",
    ]

    parts = []
    seen_content: set[str] = set()

    for q in sub_queries:
        result = search(q, max_results=2, max_tokens=max_tokens)
        fingerprint = result[:80].strip()
        if fingerprint not in seen_content and len(result) > 50:
            seen_content.add(fingerprint)
            parts.append(f"[Query: {q}]\n{result}")

    if not parts:
        return f"No results found for: {topic}"

    return f"Deep Research: {topic}\n{'='*40}\n\n" + "\n\n---\n\n".join(parts)
