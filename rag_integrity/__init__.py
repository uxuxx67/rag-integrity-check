"""RAG Integrity Check - verifies grounding, citations, chunking, and retrieval
coverage for retrieval-augmented generation (RAG) pipelines.

Public API re-exports for convenience:
    from rag_integrity import check_grounding, verify_citations, analyze_chunks, audit_retrieval, score_answer
"""
from .grounding import check_grounding, GroundingResult
from .citation_verifier import verify_citations, CitationResult
from .chunking_analyzer import analyze_chunks, ChunkIssue
from .retrieval_audit import audit_retrieval, BlindSpot
from .scorer import score_answer, ReliabilityScore
from .storage import Storage
from .exceptions import RagIntegrityError, ConfigError, RegressionError

__version__ = "0.1.0"

__all__ = [
    "check_grounding",
    "GroundingResult",
    "verify_citations",
    "CitationResult",
    "analyze_chunks",
    "ChunkIssue",
    "audit_retrieval",
    "BlindSpot",
    "score_answer",
    "ReliabilityScore",
    "Storage",
    "RagIntegrityError",
    "ConfigError",
    "RegressionError",
]
