"""
Example: integrating mini-browser with an AI agent (Anthropic Claude).

Install: pip install mini-browser anthropic
"""

import anthropic
from mini_browser import search, fetch

client = anthropic.Anthropic()

tools = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information. "
            "Returns clean, token-efficient text from top results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Number of results (default 3)"},
                "max_tokens": {"type": "integer", "description": "Token budget (default 800)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_fetch",
        "description": "Fetch and read a specific URL. Returns clean, token-efficient content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "query": {"type": "string", "description": "Optional focus topic"},
                "max_tokens": {"type": "integer", "description": "Token budget (default 800)"},
            },
            "required": ["url"],
        },
    },
]


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "web_search":
                    result = search(
                        block.input["query"],
                        max_results=block.input.get("max_results", 3),
                        max_tokens=block.input.get("max_tokens", 800),
                    )
                elif block.name == "web_fetch":
                    result = fetch(
                        block.input["url"],
                        query=block.input.get("query", ""),
                        max_tokens=block.input.get("max_tokens", 800),
                    )
                else:
                    result = "Unknown tool."

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    answer = run_agent("What are the most significant AI breakthroughs in the last 3 months?")
    print(answer)
