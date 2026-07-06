from rag_integrity.retrieval_audit import audit_retrieval, coverage_summary


def test_flags_low_relevance_as_blind_spot():
    evaluations = [{"question": "What is our refund policy for digital goods?", "relevance_scores": [0.1, 0.05]}]
    spots = audit_retrieval(evaluations, relevance_threshold=0.3)
    assert len(spots) == 1
    assert spots[0].question.startswith("What is our refund")


def test_well_covered_question_not_flagged():
    evaluations = [{"question": "What is our refund policy?", "relevance_scores": [0.9]}]
    spots = audit_retrieval(evaluations, relevance_threshold=0.3)
    assert not spots


def test_coverage_summary_percentages():
    evaluations = [
        {"question": "q1", "relevance_scores": [0.9]},
        {"question": "q2", "relevance_scores": [0.05]},
    ]
    summary = coverage_summary(evaluations, relevance_threshold=0.3)
    assert summary["total_questions"] == 2
    assert summary["blind_spots"] == 1
    assert summary["coverage_pct"] == 50.0


def test_empty_scores_treated_as_zero_relevance():
    evaluations = [{"question": "q", "relevance_scores": []}]
    spots = audit_retrieval(evaluations, relevance_threshold=0.1)
    assert len(spots) == 1
