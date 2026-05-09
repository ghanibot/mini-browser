<div align="center">

```
 ███╗   ███╗██╗███╗   ██╗██╗    ██████╗ ██████╗  ██████╗ ██╗    ██╗███████╗███████╗██████╗
 ████╗ ████║██║████╗  ██║██║    ██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝██╔════╝██╔══██╗
 ██╔████╔██║██║██╔██╗ ██║██║    ██████╔╝██████╔╝██║   ██║██║ █╗ ██║███████╗█████╗  ██████╔╝
 ██║╚██╔╝██║██║██║╚██╗██║██║    ██╔══██╗██╔══██╗██║   ██║██║███╗██║╚════██║██╔══╝  ██╔══██╗
 ██║ ╚═╝ ██║██║██║ ╚████║██║    ██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝███████║███████╗██║  ██║
 ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝╚══════╝╚══════╝╚═╝  ╚═╝
```

**Token-efficient web search & browsing for AI agents**

*Search smarter. Spend less tokens. Get better answers.*

[![Python](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-8b5cf6.svg)](https://modelcontextprotocol.io)
[![Token Savings](https://img.shields.io/badge/token%20savings-up%20to%2090%25-f97316.svg)]()
[![Works With Any AI](https://img.shields.io/badge/works%20with-any%20AI-06b6d4.svg)]()

</div>

---

## The Problem

When AI agents browse the web, they waste thousands of tokens on HTML boilerplate, navigation menus, ads, and irrelevant content. A single page fetch can consume 10,000+ tokens — most of it noise.

```
Without mini-browser:   raw HTML → 12,000 tokens → $$$
With mini-browser:      clean text →   800 tokens → $
```

## The Solution

**mini-browser** is a lightweight Python tool that sits between your AI agent and the web. It:

1. **Searches** — queries DuckDuckGo (no API key required)
2. **Fetches** — retrieves the actual page content
3. **Extracts** — strips all HTML noise, keeps only the main content
4. **Compresses** — filters chunks by relevance to your query
5. **Returns** — clean, dense, relevant text within your token budget

Works with **any AI** — from GPT and Claude to local models and text-only systems.

---

## Features

- **Zero API keys required** — uses DuckDuckGo for search
- **Up to 90% token reduction** compared to raw HTML fetching
- **Relevance-aware compression** — keeps content most relevant to your query
- **Token budget control** — set exact output token limits
- **Three interfaces** — Python API, CLI, and MCP server
- **Universal AI compatibility** — works with any model that can call Python or run shell commands
- **No hallucination risk** — returns real web content, not generated text

---

## Installation

```bash
pip install mini-browser
```

With MCP support (for Claude Desktop, Cursor, etc.):

```bash
pip install mini-browser[mcp]
```

---

## Usage

### Python API

The simplest interface — one function call:

```python
from mini_browser import search, fetch

# Search the web
result = search("latest AI agent frameworks 2025", max_results=3, max_tokens=800)
print(result)

# Fetch a specific URL
result = fetch("https://docs.python.org/3/", query="async generators", max_tokens=500)
print(result)
```

### CLI

Perfect for AI agents that can execute shell commands:

```bash
# Search
mini-browser search "OpenAI GPT-5 release date"

# Search with options
mini-browser search "rust vs go performance 2025" --max-results 5 --max-tokens 1200 --stats

# Fetch a URL
mini-browser fetch https://arxiv.org/abs/2401.00001 --query "transformer attention"

# Fetch with token stats
mini-browser fetch https://example.com --max-tokens 500 --stats
```

### MCP Server

For Claude Desktop, Cursor, and any MCP-compatible host:

```bash
mini-browser mcp
```

Add to your MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mini-browser": {
      "command": "mini-browser",
      "args": ["mcp"]
    }
  }
}
```

Claude will then have access to `web_search` and `web_fetch` tools automatically.

---

## Token Savings Example

Fetching a news article about AI:

| Method | Tokens Used | Cost (GPT-4o) |
|--------|------------|---------------|
| Raw HTML | ~14,000 | ~$0.042 |
| Just text (no compression) | ~3,200 | ~$0.010 |
| **mini-browser** | **~800** | **~$0.002** |

**Savings: ~94%**

---

## How It Works

```
User Query
    │
    ▼
┌─────────────┐
│   Search    │  DuckDuckGo → top N URLs + snippets
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Fetch    │  httpx → raw HTML per URL
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Extract   │  trafilatura → main content only (no nav/ads/footer)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Compress   │  chunk → score by query relevance → top chunks within budget
└──────┬──────┘
       │
       ▼
Clean text output (within token budget)
```

---

## API Reference

### `search(query, max_results=3, max_tokens=1000)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | str | required | Search query |
| `max_results` | int | 3 | Number of pages to fetch and process |
| `max_tokens` | int | 1000 | Maximum tokens in output |

Returns: `str` — clean, relevant text from top search results

### `fetch(url, query="", max_tokens=1000)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | required | URL to fetch |
| `query` | str | `""` | Optional topic for relevance filtering |
| `max_tokens` | int | 1000 | Maximum tokens in output |

Returns: `str` — clean text from the page

---

## Integration Examples

### LangChain Tool

```python
from langchain.tools import Tool
from mini_browser import search

web_search_tool = Tool(
    name="web_search",
    func=lambda q: search(q, max_tokens=800),
    description="Search the web for current information. Returns clean, token-efficient text.",
)
```

### OpenAI Function Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_tokens": {"type": "integer", "default": 800}
            },
            "required": ["query"]
        }
    }
}]

# In your tool execution:
if tool_call.function.name == "web_search":
    args = json.loads(tool_call.function.arguments)
    result = search(args["query"], max_tokens=args.get("max_tokens", 800))
```

### Any Text-Only AI (Shell Interface)

Even models that can only process text can use mini-browser via shell:

```
AI output: Run command: mini-browser search "what is the latest Python version"
Shell result: Python 3.13.0 was released on October 7, 2024...
AI processes clean result → answers user
```

---

## Requirements

- Python 3.10+
- No API keys needed
- Internet connection

### Dependencies

| Package | Purpose |
|---------|---------|
| `duckduckgo-search` | Web search without API key |
| `httpx` | Fast async-capable HTTP client |
| `trafilatura` | State-of-the-art main content extraction |
| `tiktoken` | Accurate token counting (OpenAI-compatible) |
| `mcp` *(optional)* | Model Context Protocol server |

---

## Contributing

Contributions welcome. Please open an issue first to discuss what you'd like to change.

```bash
git clone https://github.com/ghanibot/mini-browser
cd mini-browser
pip install -e ".[dev]"
```

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built to make every token count.

**[Report Issues](https://github.com/ghanibot/mini-browser/issues)** · **[Discussions](https://github.com/ghanibot/mini-browser/discussions)**

</div>
