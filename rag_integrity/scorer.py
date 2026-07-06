"""Reliability scorer - combines grounding, citation, and chunking signals into
one explainable 0-100 score per answer, with a breakdown of exactly why.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .citation_verifier import CitationResult
from .grounding import GroundingResult


@dataclass
class ReliabilityScore:
    score: float
    grounding_score: float
    citation_penalty: float
    chunking_penalty: float
    verdict: str
    breakdown: List[str] = field(default_factory=list)


def score_answer(
    grounding_result: GroundingResult,
    citation_result: Optional[CitationResult] = None,
    chunk_issue_count: int = 0,
    unreliable_threshold: float = 50.0,
) -> ReliabilityScore:
    """Combine a GroundingResult, an optional CitationResult, and a chunk issue
    count into one explainable reliability score (0-100).
    """
    breakdown: List[str] = [f"grounding score: {grounding_result.grounding_score}"]
    score = grounding_result.grounding_score

    citation_penalty = 0.0
    if citation_result is not None and not citation_result.all_verified:
        failed = sum(1 for c in citation_result.checks if not c.found)
        citation_penalty = min(30.0, failed * 10.0)
        breakdown.append(f"citation penalty: -{citation_penalty} ({failed} unverifiable citation(s))")

    chunking_penalty = min(20.0, chunk_issue_count * 5.0)
    if chunking_penalty:
        breakdown.append(f"chunking penalty: -{chunking_penalty} ({chunk_issue_count} chunk issue(s))")

    final = max(0.0, score - citation_penalty - chunking_penalty)
    if final < unreliable_threshold:
        verdict = "unreliable"
    elif final < 80:
        verdict = "needs review"
    else:
        verdict = "reliable"
    breakdown.append(f"final score: {round(final, 1)} -> {verdict}")

    return ReliabilityScore(
        score=round(final, 1),
        grounding_score=grounding_result.grounding_score,
        citation_penalty=citation_penalty,
        chunking_penalty=chunking_penalty,
        verdict=verdict,
        breakdown=breakdown,
    )
