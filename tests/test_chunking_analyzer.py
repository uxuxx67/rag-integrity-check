from rag_integrity.chunking_analyzer import analyze_chunks


def _chunk(chunk_id, text):
    return {"id": chunk_id, "text": text}


def test_flags_too_small_chunk():
    issues = analyze_chunks([_chunk("c1", "Short.")], min_size=50)
    assert "too_small" in [i.kind for i in issues]


def test_flags_too_large_chunk():
    issues = analyze_chunks([_chunk("c1", "A" * 3000 + ".")], max_size=2000)
    assert "too_large" in [i.kind for i in issues]


def test_flags_mid_sentence_boundaries():
    issues = analyze_chunks([_chunk("c1", "and then the results showed")], min_size=1)
    kinds = [i.kind for i in issues]
    assert "mid_sentence_start" in kinds
    assert "mid_sentence_end" in kinds


def test_well_formed_chunk_has_no_boundary_issues():
    issues = analyze_chunks(
        [_chunk("c1", "This is a complete sentence that ends properly.")], min_size=1, max_size=10000
    )
    kinds = [i.kind for i in issues]
    assert "mid_sentence_start" not in kinds
    assert "mid_sentence_end" not in kinds


def test_flags_header_only_chunk():
    issues = analyze_chunks([_chunk("c1", "## Section Title")], min_size=1)
    assert "header_only" in [i.kind for i in issues]
