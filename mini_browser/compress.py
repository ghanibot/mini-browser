import re


def compress(text: str, query: str, max_tokens: int = 1000, chunk_size: int = 150) -> str:
    """
    Compress text to max_tokens by keeping chunks most relevant to query.

    Uses keyword overlap scoring — no external dependencies, works for any AI.
    """
    if not text:
        return ""

    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"[ \t]{2,}", " ", text)

    words = text.split()

    if len(words) <= max_tokens:
        return text

    chunks: list[str] = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)

    query_words = set(re.sub(r"[^\w\s]", "", query).lower().split())

    scored: list[tuple[int, int, str]] = []
    for idx, chunk in enumerate(chunks):
        chunk_words = set(re.sub(r"[^\w\s]", "", chunk).lower().split())
        score = len(query_words & chunk_words)
        scored.append((score, idx, chunk))

    scored.sort(key=lambda x: (x[0], -x[1]), reverse=True)

    result_chunks: list[tuple[int, str]] = []
    total_words = 0

    for score, idx, chunk in scored:
        chunk_word_count = len(chunk.split())
        if total_words + chunk_word_count > max_tokens:
            remaining = max_tokens - total_words
            if remaining > 20:
                partial = " ".join(chunk.split()[:remaining])
                result_chunks.append((idx, partial))
                total_words += remaining
            break
        result_chunks.append((idx, chunk))
        total_words += chunk_word_count

    result_chunks.sort(key=lambda x: x[0])
    return "\n\n".join(chunk for _, chunk in result_chunks)
