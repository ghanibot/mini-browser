"""
Simple in-memory TTL cache for search and fetch results.
Avoids redundant network calls for repeated queries.
"""

import hashlib
import time
from typing import Any

_store: dict[str, tuple[float, Any]] = {}

DEFAULT_TTL = 1800  # 30 minutes


def _key(*parts: str) -> str:
    raw = "|".join(str(p) for p in parts)
    return hashlib.md5(raw.encode()).hexdigest()


def get(key: str) -> Any | None:
    entry = _store.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.time() - ts > DEFAULT_TTL:
        del _store[key]
        return None
    return value


def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    _store[key] = (time.time(), value)


def make_key(*parts) -> str:
    return _key(*parts)


def clear() -> None:
    _store.clear()


def stats() -> dict:
    now = time.time()
    alive = sum(1 for ts, _ in _store.values() if now - ts <= DEFAULT_TTL)
    return {"total": len(_store), "alive": alive, "ttl_seconds": DEFAULT_TTL}
