#!/usr/bin/env python3
"""
Auto-configure mini-browser for all supported AI CLI agents.

Detects which agents are installed and adds mini-browser as MCP server.

Usage:
    python scripts/setup_agents.py           # configure all detected agents
    python scripts/setup_agents.py --dry-run # preview changes without writing
    python scripts/setup_agents.py --agent claude-code  # specific agent only
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

HOME = Path.home()

MCP_ENTRY = {
    "command": "mini-browser",
    "args": ["mcp"],
    "env": {},
}

# Agent definitions: name, CLI binary, config path, JSON key structure
AGENTS = {
    "claude-code": {
        "binaries": ["claude"],
        "config_paths": [
            HOME / ".claude" / "claude_desktop_config.json",
        ],
        "mcp_key": ["mcpServers"],
        "description": "Claude Code (Anthropic CLI)",
    },
    "codex": {
        "binaries": ["codex"],
        "config_paths": [
            HOME / ".codex" / "config.json",
        ],
        "mcp_key": ["mcpServers"],
        "description": "OpenAI Codex CLI",
    },
    "gemini": {
        "binaries": ["gemini"],
        "config_paths": [
            HOME / ".gemini" / "settings.json",
        ],
        "mcp_key": ["mcpServers"],
        "description": "Google Gemini CLI",
    },
    "opencode": {
        "binaries": ["opencode"],
        "config_paths": [
            HOME / ".config" / "opencode" / "config.json",
            Path.cwd() / "opencode.json",
        ],
        "mcp_key": ["mcp"],
        "description": "OpenCode CLI",
    },
    "cursor": {
        "binaries": ["cursor"],
        "config_paths": [
            HOME / ".cursor" / "mcp.json",
            HOME / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp.json",
            HOME / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "mcp.json",
        ],
        "mcp_key": ["mcpServers"],
        "description": "Cursor IDE",
    },
    "continue": {
        "binaries": ["continue"],
        "config_paths": [
            HOME / ".continue" / "config.json",
        ],
        "mcp_key": ["mcpServers"],
        "description": "Continue.dev",
    },
    "aider": {
        "binaries": ["aider"],
        "config_paths": [],
        "mcp_key": None,
        "description": "Aider (CLI only — use: aider --exec 'mini-browser search')",
        "cli_only": True,
    },
    "goose": {
        "binaries": ["goose"],
        "config_paths": [
            HOME / ".config" / "goose" / "config.yaml",
        ],
        "mcp_key": ["mcpServers"],
        "description": "Goose AI (Block)",
    },
}


def _is_installed(binaries: list[str]) -> bool:
    return any(shutil.which(b) for b in binaries)


def _nested_set(d: dict, keys: list[str], value: dict) -> None:
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    target = d.setdefault(keys[-1], {})
    target["mini-browser"] = value


def _nested_get(d: dict, keys: list[str]) -> dict:
    for key in keys:
        d = d.get(key, {})
    return d


def configure_agent(name: str, cfg: dict, dry_run: bool = False) -> str:
    if cfg.get("cli_only"):
        return f"  [OK] {cfg['description']} — CLI only, no MCP config needed\n    Use: mini-browser search \"query\""

    config_paths = cfg["config_paths"]
    if not config_paths:
        return f"  [!!] {cfg['description']} — no config path known"

    # Find existing config or use first path
    config_path = None
    for p in config_paths:
        if p.exists():
            config_path = p
            break
    if config_path is None:
        config_path = config_paths[0]

    try:
        if config_path.exists():
            existing = json.loads(config_path.read_text(encoding="utf-8"))
        else:
            existing = {}

        # Check if already configured
        current = _nested_get(existing, cfg["mcp_key"])
        if "mini-browser" in current:
            return f"  [OK] {cfg['description']} — already configured ({config_path})"

        _nested_set(existing, cfg["mcp_key"], MCP_ENTRY)

        if not dry_run:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(
                json.dumps(existing, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return f"  [OK] {cfg['description']} — configured ({config_path})"
        else:
            return f"  [~~] {cfg['description']} — would write to {config_path} [DRY RUN]"

    except Exception as e:
        return f"  [!!] {cfg['description']} — error: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Configure mini-browser MCP for AI CLI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported agents:
  claude-code, codex, gemini, opencode, cursor, continue, aider, goose

Examples:
  python scripts/setup_agents.py
  python scripts/setup_agents.py --dry-run
  python scripts/setup_agents.py --agent claude-code --agent codex
  python scripts/setup_agents.py --all
""",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--agent", action="append", dest="agents", metavar="NAME",
                        help="Configure specific agent (can repeat)")
    parser.add_argument("--all", action="store_true", help="Configure all agents (even not installed)")
    args = parser.parse_args()

    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("mini-browser agent setup")
    print("=" * 40)

    targets = args.agents or list(AGENTS.keys())

    configured = 0
    skipped = 0

    for name in targets:
        if name not in AGENTS:
            print(f"  [!!] Unknown agent: {name}")
            continue

        cfg = AGENTS[name]
        installed = _is_installed(cfg["binaries"])

        if not installed and not args.all:
            skipped += 1
            continue

        status = "installed" if installed else "not found"
        print(f"\n[{name}] ({status})")
        result = configure_agent(name, cfg, dry_run=args.dry_run)
        print(result)
        configured += 1

    print(f"\n{'─' * 40}")
    if args.dry_run:
        print(f"DRY RUN — no files written. Remove --dry-run to apply.")
    else:
        print(f"Done. {configured} agent(s) processed, {skipped} skipped (not installed).")
        print("\nNext: restart your AI agent to load mini-browser tools.")
        print("Test: ask your agent to 'search for latest AI news'")


if __name__ == "__main__":
    main()
