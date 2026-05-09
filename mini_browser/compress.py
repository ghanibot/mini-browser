import re
from mini_browser.token_counter import count_tokens


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [s.strip() for s in parts if len(s.strip()) > 25]


def _score(sentence: str, query_words: set[str]) -> float:
    words = set(re.sub(r"[^\w\s]", "", sentence).lower().split())
    if not words:
        return 0.0
    overlap = len(query_words & words)
    # bigram bonus
    tokens = sentence.lower().split()
    bigrams = {f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)}
    query_bigrams = set()
    qlist = list(query_words)
    for i in range(len(qlist) - 1):
        query_bigrams.add(f"{qlist[i]} {qlist[i+1]}")
    bigram_bonus = len(query_bigrams & bigrams) * 0.5
    return (overlap + bigram_bonus) / (1 + len(words) ** 0.25)


def _clean_artifacts(text: str) -> str:
    text = re.sub(r"[^\x00-\x7FÀ-ɏЀ-ӿĀ-ſ一-鿿　-〿가-힯؀-ۿऀ-ॿঀ-৿]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compress(text: str, query: str, max_tokens: int = 1000) -> str:
    """
    Compress text to max_tokens using sentence-level relevance scoring.
    Keeps sentences most relevant to query, preserving original order.
    """
    if not text:
        return ""

    text = _clean_artifacts(text)
    words = text.split()

    if len(words) <= max_tokens:
        return text

    sentences = _split_sentences(text)
    if not sentences:
        return " ".join(words[:max_tokens])

    query_words = set(re.sub(r"[^\w\s]", "", query).lower().split())

    scored: list[tuple[float, int, str]] = []
    for idx, sent in enumerate(sentences):
        base_score = _score(sent, query_words)
        # sentences near top of article get slight bonus (news puts key facts first)
        position_bonus = 1.0 / (1.0 + idx * 0.04)
        scored.append((base_score * (1 + position_bonus), idx, sent))

    scored.sort(key=lambda x: x[0], reverse=True)

    selected: list[tuple[int, str]] = []
    total_tokens = 0
    seen: set[str] = set()

    for _, idx, sent in scored:
        fingerprint = " ".join(sent.lower().split()[:8])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)

        sent_tokens = count_tokens(sent)
        if total_tokens + sent_tokens > max_tokens:
            break
        selected.append((idx, sent))
        total_tokens += sent_tokens

    selected.sort(key=lambda x: x[0])
    return " ".join(s for _, s in selected)
