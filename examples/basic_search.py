"""
Basic usage example for mini-browser.
"""

from mini_browser import search, fetch
from mini_browser.token_counter import count_tokens

# --- Example 1: Web search ---
print("=== Web Search ===")
result = search("latest advances in AI agents 2025", max_results=3, max_tokens=800)
print(result)
print(f"\nTokens used: {count_tokens(result)}")

print("\n" + "=" * 60 + "\n")

# --- Example 2: Fetch specific URL ---
print("=== Fetch URL ===")
result = fetch(
    "https://en.wikipedia.org/wiki/Large_language_model",
    query="token efficiency context window",
    max_tokens=500,
)
print(result)
print(f"\nTokens used: {count_tokens(result)}")
