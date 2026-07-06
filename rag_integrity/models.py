"""Shared dataclasses used across rag_integrity modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Chunk:
    id: str
    text: str
    source: str = ""
    start: Optional[int] = None
    end: Optional[int] = None


@dataclass
class Document:
    id: str
    text: str
    title: str = ""


@dataclass
class RetrievalResult:
    question: str
    chunks: List[Chunk] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)
