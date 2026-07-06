"""Citation verifier - checks that citations/source references in an answer
actually point to a document that exists, instead of trusting the model's
word for it. A follow-up quote check confirms the cited passage is present.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

CITATION_PATTERN = re.compile(r"\[(\d+)\]|\(Source:\s*([^)]+)\)", re.IGNORECASE)


@dataclass
class CitationCheck:
    citation_id: str
    found: bool
    message: str = ""


@dataclass
class CitationResult:
    all_verified: bool
    checks: List[CitationCheck] = field(default_factory=list)


def _extract_citation_ids(answer: str) -> List[str]:
    ids = []
    for match in CITATION_PATTERN.finditer(answer):
        ids.append((match.group(1) or match.group(2) or "").strip())
    return [i for i in ids if i]


def verify_citations(
    answer: str,
    documents: Dict[str, str],
    citation_map: Optional[Dict[str, str]] = None,
    quote: Optional[str] = None,
) -> CitationResult:
    """Verify every citation referenced in `answer`.

    documents: dict of doc_id -> full document text.
    citation_map: optional dict mapping the citation token as it appears in the
        answer (e.g. "1") to the actual doc_id in `documents`. If omitted, the
        citation token is assumed to be the doc_id itself.
    quote: optional exact phrase that should appear in the cited document(s);
        useful when checking one specific claim rather than the whole answer.
    """
    citation_map = citation_map or {}
    ids = _extract_citation_ids(answer)
    checks: List[CitationCheck] = []

    for cid in ids:
        doc_id = citation_map.get(cid, cid)
        doc_text = documents.get(doc_id)
        if doc_text is None:
            checks.append(CitationCheck(cid, False, f"cited document '{doc_id}' not found in provided documents"))
            continue
        if quote and quote.lower() not in doc_text.lower():
            checks.append(CitationCheck(cid, False, f"quote not found in document '{doc_id}'"))
            continue
        checks.append(CitationCheck(cid, True, "document exists and is available"))

    all_verified = all(c.found for c in checks) if checks else True
    return CitationResult(all_verified=all_verified, checks=checks)
