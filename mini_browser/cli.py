"""
mini-browser CLI — usable by any AI agent that can run shell commands.
"""

import argparse
import sys

from mini_browser import search, fetch
from mini_browser.token_counter import count_tokens


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mini-browser",
        description="Token-efficient web search and browsing for AI agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mini-browser search "latest AI news"
  mini-browser search "python async best practices" --max-results 5 --max-tokens 800
  mini-browser fetch https://example.com --query "pricing"
  mini-browser fetch https://docs.python.org/3/ --max-tokens 500 --stats
  mini-browser mcp
""",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    search_p = subparsers.add_parser("search", help="Search the web")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--max-results", type=int, default=3, metavar="N",
                          help="Number of results to fetch (default: 3)")
    search_p.add_argument("--max-tokens", type=int, default=1000, metavar="N",
                          help="Token budget for output (default: 1000)")
    search_p.add_argument("--stats", action="store_true",
                          help="Print token usage stats to stderr")

    fetch_p = subparsers.add_parser("fetch", help="Fetch a URL")
    fetch_p.add_argument("url", help="URL to fetch")
    fetch_p.add_argument("--query", default="", metavar="TEXT",
                         help="Focus extraction on this topic")
    fetch_p.add_argument("--max-tokens", type=int, default=1000, metavar="N",
                         help="Token budget for output (default: 1000)")
    fetch_p.add_argument("--stats", action="store_true",
                         help="Print token usage stats to stderr")

    subparsers.add_parser("mcp", help="Start MCP server (for Claude, Cursor, etc.)")

    args = parser.parse_args()

    if args.command == "search":
        result = search(args.query, max_results=args.max_results, max_tokens=args.max_tokens)
        print(result)
        if args.stats:
            tokens = count_tokens(result)
            print(f"\n[mini-browser] Output: {tokens} tokens", file=sys.stderr)

    elif args.command == "fetch":
        result = fetch(args.url, query=args.query, max_tokens=args.max_tokens)
        print(result)
        if args.stats:
            tokens = count_tokens(result)
            print(f"\n[mini-browser] Output: {tokens} tokens", file=sys.stderr)

    elif args.command == "mcp":
        from mini_browser.mcp_server import run
        run()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
