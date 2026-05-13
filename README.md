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
[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)]()
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-8b5cf6.svg)](https://modelcontextprotocol.io)
[![Token Savings](https://img.shields.io/badge/token%20savings-up%20to%2090%25-f97316.svg)]()

</div>

---

## The Problem

When AI agents browse the web, they waste thousands of tokens on HTML boilerplate, navigation menus, ads, and irrelevant content. A single page fetch can consume 10,000+ tokens — most of it noise. JS-heavy sites like Yahoo Finance simply return nothing.

```
Without mini-browser:   raw HTML → 12,000 tokens  →  $$$
With mini-browser:      clean text →   800 tokens  →  $
```

## The Solution

**mini-browser** sits between your AI agent and the web:

1. **Searches** — DuckDuckGo (default, no API key) or Tavily (optional, higher quality), spam filtered, recency-aware
2. **Fetches** — full Playwright browser for JS-heavy sites (Yahoo Finance, TradingView, Bloomberg), fast httpx for simple sites
3. **Extracts** — trafilatura + BeautifulSoup strip all noise (nav/ads/footer)
4. **Compresses** — sentence-level relevance scoring keeps only what matters for your query
5. **Returns** — clean text within your token budget, cached for 30 minutes

Works with **any AI** — Claude Code, Codex CLI, Gemini CLI, OpenCode, or any model that can call Python or run shell commands.

---

## Quick Start

```bash
# Install
pip install git+https://github.com/ghanibot/mini-browser.git

# Install Playwright browser (one-time, ~150MB)
python -m playwright install chromium

# Configure your AI agents (auto-detects Claude Code, Codex, Gemini, OpenCode...)
mini-browser setup-agents

# Test it
mini-browser search "latest AI news today"
```

---

## Supported AI Agents

| Agent | Method | Setup |
|-------|--------|-------|
| **Claude Code** | MCP server | `mini-browser setup-agents` |
| **OpenAI Codex CLI** | MCP server | `mini-browser setup-agents` |
| **Google Gemini CLI** | MCP server | `mini-browser setup-agents` |
| **OpenCode** | MCP server | `mini-browser setup-agents` |
| **Cursor** | MCP server | `mini-browser setup-agents` |
| **Continue.dev** | MCP server | `mini-browser setup-agents` |
| **Aider** | CLI shell | `mini-browser search "query"` |
| **Any OpenAI agent** | Tool calling | `from mini_browser.tools import TOOLS_OPENAI` |
| **Any Anthropic agent** | Tool calling | `from mini_browser.tools import TOOLS_ANTHROPIC` |
| **Any HTTP agent** | REST API | `mini-browser serve` |

---

## Installation

### Standard (recommended)
```bash
pip install git+https://github.com/ghanibot/mini-browser.git
python -m playwright install chromium
```

### With MCP support
```bash
pip install "mini-browser[mcp] @ git+https://github.com/ghanibot/mini-browser.git"
```

### With Tavily search
```bash
pip install "mini-browser[tavily] @ git+https://github.com/ghanibot/mini-browser.git"
```

### With PDF support
```bash
pip install "mini-browser[pdf] @ git+https://github.com/ghanibot/mini-browser.git"
```

### Full (all features)
```bash
pip install "mini-browser[full] @ git+https://github.com/ghanibot/mini-browser.git"
python -m playwright install chromium
```

**Requirements:** Python 3.10+, internet connection. No API keys needed for default DuckDuckGo search; Tavily requires a `TAVILY_API_KEY` (see [Configuration](#search-provider) below).

---

## Usage

### CLI (works with any AI that can run shell commands)

```bash
# Search
mini-browser search "harga saham Tesla terbaru"
mini-browser search "latest AI news" --max-results 5 --max-tokens 2000

# Fetch a specific URL (supports JS sites, PDFs)
mini-browser fetch https://finance.yahoo.com/quote/TSLA/
mini-browser fetch https://arxiv.org/pdf/2401.00001 --query "transformer attention"

# Deep multi-source research
mini-browser search "US Iran war 2026 latest" --max-results 5

# With token stats
mini-browser search "bitcoin price today" --stats
```

### Python API

```python
from mini_browser import search, fetch

# Web search — returns clean text, token-efficient
result = search("harga dolar rupiah hari ini", max_results=3, max_tokens=1500)
print(result)

# Fetch specific URL (Yahoo Finance, TradingView, PDFs — all work)
result = fetch("https://finance.yahoo.com/quote/TSLA/", query="stock price")
print(result)

# JSON output for programmatic use
import json
result = search("AI news", output_format="json")
data = json.loads(result)
# [{"title": "...", "url": "...", "content": "...", "tokens": 423}, ...]
```

### MCP Server (Claude Code, Codex, Gemini, OpenCode, Cursor)

**Auto-setup (recommended):**
```bash
mini-browser setup-agents
# Restart your AI agent — tools are now available
```

**Manual setup** — add to your agent's MCP config:
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

Config file locations:
- Claude Code: `~/.claude/claude_desktop_config.json`
- Codex CLI: `~/.codex/config.json`
- Gemini CLI: `~/.gemini/settings.json`
- OpenCode: `~/.config/opencode/config.json`
- Cursor: `~/.cursor/mcp.json`

Ready-to-use configs also available in the [`configs/`](configs/) directory.

Once configured, your AI agent gets 3 tools:
- **`web_search`** — search the web for real-time info
- **`web_fetch`** — read any URL (JS sites, PDFs)
- **`deep_research`** — multi-source deep research

### HTTP API (for any language / bima-agent / Node.js)

```bash
# Start server
mini-browser serve
# → running at http://127.0.0.1:7842
# → docs at http://127.0.0.1:7842/docs
```

```bash
# Use from any language
curl "http://127.0.0.1:7842/search?q=bitcoin+price+today&max_tokens=800"
curl -X POST http://127.0.0.1:7842/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://finance.yahoo.com/quote/TSLA/", "query": "stock price"}'
```

### OpenAI / Anthropic Tool Calling

```python
from mini_browser.tools import TOOLS_OPENAI, TOOLS_ANTHROPIC, handle_tool_call

# OpenAI / Codex / Gemini
response = openai_client.chat.completions.create(
    model="gpt-4o",
    tools=TOOLS_OPENAI,
    messages=messages,
)

# Anthropic / Claude
response = anthropic_client.messages.create(
    model="claude-opus-4-7",
    tools=TOOLS_ANTHROPIC,
    messages=messages,
)

# Execute tool call (works for any provider)
result = handle_tool_call(tool_name, tool_arguments)
```

---

## Features

| Feature | Details |
|---------|---------|
| **Full JS rendering** | Playwright headless Chrome with stealth mode — Yahoo Finance, TradingView, Bloomberg all work |
| **PDF support** | Auto-detected by URL/content-type, extracted via pdfplumber |
| **Smart compression** | Sentence-level relevance scoring with bigram matching and position weighting |
| **TTL cache** | 30-minute in-memory cache — repeated queries return instantly |
| **Parallel fetch** | Multiple URLs fetched simultaneously via ThreadPoolExecutor |
| **Spam filtering** | Domain blocklist + unique-word ratio filter removes low-quality results |
| **Recency detection** | Queries containing "terbaru/latest/hari ini" auto-apply DuckDuckGo time filter |
| **Retry with backoff** | Failed fetches retry 2x with exponential backoff |
| **Configurable domains** | Add custom JS-heavy domains via env var or `.mini-browser.json` |
| **No API keys** | Uses DuckDuckGo by default — completely free. Optional Tavily provider for higher quality |

---

## Token Savings

Fetching a news article:

| Method | Tokens | Cost (GPT-4o) |
|--------|--------|---------------|
| Raw HTML | ~14,000 | ~$0.042 |
| Plain text | ~3,200 | ~$0.010 |
| **mini-browser** | **~800** | **~$0.002** |

**Savings: ~94%**

---

## Configuration

### Search Provider

By default, mini-browser uses DuckDuckGo (no API key required). You can switch to [Tavily](https://tavily.com) for higher-quality, AI-optimized search results.

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `MINI_BROWSER_SEARCH_PROVIDER` | Search backend to use: `duckduckgo` or `tavily` | `duckduckgo` |
| `TAVILY_API_KEY` | Your Tavily API key (required when provider is `tavily`) | — |

```bash
# Install with Tavily support
pip install "mini-browser[tavily] @ git+https://github.com/ghanibot/mini-browser.git"

# Use Tavily as search provider
export MINI_BROWSER_SEARCH_PROVIDER=tavily
export TAVILY_API_KEY=tvly-YOUR_API_KEY

mini-browser search "latest AI news today"
```

Get a free Tavily API key (1,000 credits/month) at [app.tavily.com](https://app.tavily.com).

### Custom JS-heavy domains

**Via env var:**
```bash
MINI_BROWSER_JS_DOMAINS=mysite.com,other.com mini-browser search "query"
```

**Via config file** (`.mini-browser.json` in current dir or `~/.mini-browser/config.json`):
```json
{
  "js_domains": ["mysite.com", "other.com"]
}
```

**In Python:**
```python
from mini_browser.config import add_js_domain
add_js_domain("mysite.com")
```

### Cache

```python
from mini_browser import cache
cache.clear()           # clear all
print(cache.stats())    # {"total": 5, "alive": 3, "ttl_seconds": 1800}
```

---

## How It Works

```
Query
  │
  ▼
DuckDuckGo search → top N URLs (spam filtered, recency-aware, dedup domains)
  │
  ├─ Parallel fetch (ThreadPoolExecutor)
  │     │
  │     ├─ Simple site → httpx → trafilatura → BS4 fallback
  │     └─ JS-heavy site → Playwright stealth → trafilatura → BS4 fallback
  │              └─ PDF detected → pdfplumber / pypdf
  │
  ▼
Sentence-level compression (relevance scored, bigram bonus, dedup, token budget)
  │
  ▼
Cache result (TTL 30min)
  │
  ▼
Clean text output (within token budget)
```

---

## Contributing

```bash
git clone https://github.com/ghanibot/mini-browser
cd mini-browser
pip install -e ".[dev]"
python -m playwright install chromium
```

Issues and PRs welcome at [github.com/ghanibot/mini-browser/issues](https://github.com/ghanibot/mini-browser/issues)

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built to make every token count.

**[Report Issues](https://github.com/ghanibot/mini-browser/issues)** · **[Discussions](https://github.com/ghanibot/mini-browser/discussions)**

</div>
