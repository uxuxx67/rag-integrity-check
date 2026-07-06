"""Chunking analyzer - detects common chunk-boundary quality issues that hurt
retrieval and grounding: chunks that are too small/large, that cut a sentence
in half, or that consist of a bare header with no body content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ChunkIssue:
    kind: str
    chunk_id: str
    message: str


def _text_of(chunk: Any) -> str:
    return chunk.text if hasattr(chunk, "text") else chunk.get("text", "")


def _id_of(chunk: Any) -> str:
    return chunk.id if hasattr(chunk, "id") else chunk.get("id", "?")


def _looks_like_sentence_start(text: str) -> bool:
    return bool(text) and (text[0].isupper() or text[0].isdigit())


def _looks_like_sentence_end(text: str) -> bool:
    return bool(text) and text.rstrip()[-1:] in ".!?\"'"


def analyze_chunks(chunks: List[Any], min_size: int = 100, max_size: int = 2000) -> List[ChunkIssue]:
    """Inspect a list of chunks and return a list of ChunkIssue for anything
    that looks like a chunking mistake.
    """
    issues: List[ChunkIssue] = []
    for chunk in chunks:
        text = _text_of(chunk)
        chunk_id = _id_of(chunk)
        stripped = text.strip()
        length = len(stripped)

        if length < min_size:
            issues.append(ChunkIssue("too_small", chunk_id, f"chunk is {length} chars, below minimum {min_size}"))
        if length > max_size:
            issues.append(ChunkIssue("too_large", chunk_id, f"chunk is {length} chars, above maximum {max_size}"))
        if stripped and not _looks_like_sentence_start(stripped):
            issues.append(ChunkIssue("mid_sentence_start", chunk_id, "chunk does not start at a sentence boundary"))
        if stripped and not _looks_like_sentence_end(stripped):
            issues.append(ChunkIssue("mid_sentence_end", chunk_id, "chunk does not end at sentence punctuation"))
        if re.match(r"^#{1,6}\s*\S*\s*$", stripped):
            issues.append(ChunkIssue("header_only", chunk_id, "chunk contains only a header with no body content"))
    return issues
