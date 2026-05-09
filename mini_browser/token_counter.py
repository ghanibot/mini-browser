try:
    import tiktoken

    _enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        return len(_enc.encode(text))

except ImportError:
    def count_tokens(text: str) -> int:
        return int(len(text.split()) * 1.33)


def token_stats(original: str, compressed: str) -> dict:
    orig_tokens = count_tokens(original)
    comp_tokens = count_tokens(compressed)
    saved = orig_tokens - comp_tokens
    pct = round((saved / orig_tokens * 100) if orig_tokens > 0 else 0, 1)
    return {
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "saved_tokens": saved,
        "savings_pct": pct,
    }
