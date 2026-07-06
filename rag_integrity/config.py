"""Centralized environment-variable configuration for RAG Integrity Check.

Keeps configuration explicit and in one place rather than scattering
os.environ.get() calls across modules.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    db_path: str = "rag_integrity.db"
    default_report_format: str = "text"
    # Minimum fraction of an answer sentence's words that must overlap with
    # some retrieved chunk for that sentence to be considered "grounded".
    grounding_overlap_threshold: float = 0.4
    # Minimum relevance score (0-1) a retrieved chunk must have for a question
    # to NOT be flagged as a knowledge-base blind spot.
    blind_spot_relevance_threshold: float = 0.3
    # Reliability score (0-100) below which scorer.score_answer marks an
    # answer as "unreliable" rather than just "needs review".
    unreliable_score_threshold: float = 50.0

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            db_path=os.environ.get("RAG_INTEGRITY_DB", "rag_integrity.db"),
            default_report_format=os.environ.get("RAG_INTEGRITY_REPORT_FORMAT", "text"),
            grounding_overlap_threshold=float(
                os.environ.get("RAG_INTEGRITY_GROUNDING_THRESHOLD", "0.4")
            ),
            blind_spot_relevance_threshold=float(
                os.environ.get("RAG_INTEGRITY_BLINDSPOT_THRESHOLD", "0.3")
            ),
            unreliable_score_threshold=float(
                os.environ.get("RAG_INTEGRITY_UNRELIABLE_THRESHOLD", "50")
            ),
        )
