from rag_integrity.citation_verifier import CitationCheck, CitationResult
from rag_integrity.grounding import GroundingResult
from rag_integrity.scorer import score_answer


def test_fully_grounded_verified_answer_is_reliable():
    grounding = GroundingResult(grounding_score=100.0)
    citation = CitationResult(all_verified=True, checks=[])
    result = score_answer(grounding, citation, chunk_issue_count=0)
    assert result.verdict == "reliable"
    assert result.score == 100.0


def test_unverified_citation_lowers_score():
    grounding = GroundingResult(grounding_score=90.0)
    citation = CitationResult(all_verified=False, checks=[CitationCheck("1", False, "missing")])
    result = score_answer(grounding, citation, chunk_issue_count=0)
    assert result.score < 90.0
    assert result.citation_penalty > 0


def test_low_grounding_is_unreliable():
    grounding = GroundingResult(grounding_score=20.0)
    result = score_answer(grounding, None, chunk_issue_count=0, unreliable_threshold=50.0)
    assert result.verdict == "unreliable"


def test_chunking_issues_apply_penalty():
    grounding = GroundingResult(grounding_score=100.0)
    result = score_answer(grounding, None, chunk_issue_count=3)
    assert result.chunking_penalty == 15.0
    assert result.score == 85.0
