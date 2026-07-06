"""Grounding checker - scores how well an answer is supported by retrieved chunks.

Uses lexical word-overlap between each answer sentence and the retrieved chunks
(no embeddings, no model calls) so results are fully offline and reproducible.
Sentences with low overlap against every chunk are flagged as likely
unsupported claims (possible hallucinations).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "for",
    "and", "or", "that", "this", "it", "as", "by", "with", "be", "has", "have",
    "had", "but", "not", "you", "your", "we", "our", "from", "at", "can",
}


def _tokenize(text: str) -> List[str]:
    return [w for w in re.findall(r"[a-zA-Z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _text_of(chunk: Any) -> str:
    return chunk.text if hasattr(chunk, "text") else chunk.get("text", "")


def _id_of(chunk: Any) -> Optional[str]:
    return chunk.id if hasattr(chunk, "id") else chunk.get("id")


def _overlap_ratio(sentence_tokens: List[str], chunk_tokens: List[str]) -> float:
    if not sentence_tokens:
        return 0.0
    chunk_set = set(chunk_tokens)
    matched = sum(1 for t in sentence_tokens if t in chunk_set)
    return matched / len(sentence_tokens)


@dataclass
class SentenceGrounding:
    sentence: str
    supported: bool
    overlap_ratio: float
    best_chunk_id: Optional[str] = None


@dataclass
class GroundingResult:
    grounding_score: float  # 0-100
    sentences: List[SentenceGrounding] = field(default_factory=list)
    unsupported_sentences: List[str] = field(default_factory=list)


def check_grounding(answer: str, chunks: List[Any], overlap_threshold: float = 0.4) -> GroundingResult:
    """Score how well `answer` is grounded in `chunks`.

    Splits the answer into sentences, and for each sentence finds the chunk
    with the highest word-overlap ratio. A sentence is "supported" if that
    best ratio meets `overlap_threshold`. The overall grounding_score is the
    percentage of supported sentences.
    """
    sentences = _split_sentences(answer)
    results: List[SentenceGrounding] = []
    unsupported: List[str] = []

    chunk_token_cache = [(_id_of(c), _tokenize(_text_of(c))) for c in chunks]

    for sentence in sentences:
        tokens = _tokenize(sentence)
        best_ratio = 0.0
        best_chunk_id = None
        for chunk_id, chunk_tokens in chunk_token_cache:
            ratio = _overlap_ratio(tokens, chunk_tokens)
            if ratio > best_ratio:
                best_ratio = ratio
                best_chunk_id = chunk_id
        supported = best_ratio >= overlap_threshold
        results.append(
            SentenceGrounding(
                sentence=sentence,
                supported=supported,
                overlap_ratio=round(best_ratio, 3),
                best_chunk_id=best_chunk_id,
            )
        )
        if not supported:
            unsupported.append(sentence)

    if not results:
        return GroundingResult(grounding_score=100.0, sentences=[], unsupported_sentences=[])

    score = 100.0 * sum(1 for r in results if r.supported) / len(results)
    return GroundingResult(grounding_score=round(score, 1), sentences=results, unsupported_sentences=unsupported)
