from rag_integrity.grounding import check_grounding


def _chunk(chunk_id, text):
    return {"id": chunk_id, "text": text}


def test_fully_grounded_answer():
    chunks = [_chunk("c1", "The mitochondrion is the powerhouse of the cell and produces ATP.")]
    result = check_grounding("The mitochondrion is the powerhouse of the cell.", chunks)
    assert result.grounding_score == 100.0
    assert not result.unsupported_sentences


def test_unsupported_sentence_flagged():
    chunks = [_chunk("c1", "Paris is the capital of France.")]
    result = check_grounding("Paris is the capital of France. The moon is made of cheese.", chunks)
    assert result.grounding_score < 100.0
    assert "moon is made of cheese" in result.unsupported_sentences[0].lower()


def test_empty_answer_returns_full_score():
    result = check_grounding("", [_chunk("c1", "text")])
    assert result.grounding_score == 100.0


def test_best_chunk_id_is_tracked():
    chunks = [_chunk("wrong", "irrelevant text about cars"), _chunk("right", "the sky is blue during the day")]
    result = check_grounding("The sky is blue during the day.", chunks)
    assert result.sentences[0].best_chunk_id == "right"
