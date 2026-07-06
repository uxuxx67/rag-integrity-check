"""Retrieval auditor - runs a batch of evaluation questions through your
retrieval step's relevance scores and finds knowledge-base blind spots: topics
with no well-matching document, where a model is likely to hallucinate rather
than admit it has no good source.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List


@dataclass
class BlindSpot:
    question: str
    best_relevance: float
    reason: str


def _question_of(item: Any) -> str:
    return item["question"] if isinstance(item, dict) else item.question


def _scores_of(item: Any) -> List[float]:
    return item.get("relevance_scores", []) if isinstance(item, dict) else item.relevance_scores


def audit_retrieval(evaluations: List[Any], relevance_threshold: float = 0.3) -> List[BlindSpot]:
    """evaluations: list of {"question": str, "relevance_scores": [float, ...]}
    (or RetrievalResult-like objects). Returns a BlindSpot for every question
    whose best retrieved relevance score is below `relevance_threshold`.
    """
    blind_spots: List[BlindSpot] = []
    for item in evaluations:
        question = _question_of(item)
        scores = _scores_of(item)
        best = max(scores) if scores else 0.0
        if best < relevance_threshold:
            blind_spots.append(
                BlindSpot(
                    question=question,
                    best_relevance=round(best, 3),
                    reason=f"best retrieved relevance {best:.2f} is below threshold {relevance_threshold}",
                )
            )
    return blind_spots


def coverage_summary(evaluations: List[Any], relevance_threshold: float = 0.3) -> dict:
    """Return an aggregate coverage summary: total questions, blind spot count,
    and coverage percentage - useful for a single at-a-glance health metric.
    """
    total = len(evaluations)
    spots = audit_retrieval(evaluations, relevance_threshold)
    covered = total - len(spots)
    coverage_pct = round(100.0 * covered / total, 1) if total else 100.0
    return {
        "total_questions": total,
        "blind_spots": len(spots),
        "covered": covered,
        "coverage_pct": coverage_pct,
    }
