from rag_integrity.citation_verifier import verify_citations


def test_verified_numeric_citation_passes():
    documents = {"1": "Revenue grew 12% in Q3, driven by strong holiday sales."}
    answer = "Revenue grew 12% in Q3 [1]."
    result = verify_citations(answer, documents)
    assert result.all_verified
    assert result.checks[0].found


def test_missing_document_fails():
    documents = {"1": "some text"}
    answer = "This claim cites a missing source [2]."
    result = verify_citations(answer, documents)
    assert not result.all_verified


def test_source_style_citation():
    documents = {"policy.pdf": "Refunds are processed within 14 business days."}
    answer = "Refunds take 14 business days (Source: policy.pdf)."
    result = verify_citations(answer, documents)
    assert result.all_verified


def test_citation_map_resolves_alias():
    documents = {"internal-doc-42": "The warranty covers one year."}
    answer = "The warranty covers one year [1]."
    result = verify_citations(answer, documents, citation_map={"1": "internal-doc-42"})
    assert result.all_verified


def test_no_citations_is_trivially_verified():
    result = verify_citations("No citations here at all.", {})
    assert result.all_verified
