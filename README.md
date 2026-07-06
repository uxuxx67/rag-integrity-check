# RAG Integrity Check

*[Русская версия](README.ru.md)*

Verifies that answers from your RAG (retrieval-augmented generation) pipeline are actually backed by the documents you retrieved — not invented, not miscited, and not hiding a blind spot in your knowledge base.

## Why

Retrieval-augmented generation is supposed to keep LLMs honest by grounding answers in real documents. In practice it often doesn't: models still hallucinate on top of retrieved context, cite sources that don't say what's claimed, and confidently answer questions the knowledge base has no real coverage for. Teams usually find out from an angry user, not from their evals.

## Core ideas

1. **Grounding Checker** — scores how much of an answer is actually supported by the retrieved chunks, and flags sentences that look invented (unsupported claims).
2. **Citation Verifier** — checks that every citation/source reference in an answer actually appears in the document it points to, instead of trusting the model's word for it.
3. **Chunking Analyzer** — inspects a chunking strategy for common failure modes: sentences split mid-way, headers stripped, chunks too small or too large.
4. **Retrieval Auditor** — runs a batch of evaluation questions through your retrieval step and finds "blind spots": topics with no good matching documents, where the model is likely to hallucinate instead of admit it doesn't know.
5. **Reliability Scorer** — combines grounding, citation, and chunking signals into one explainable 0-100 score per answer, with a breakdown of why.
6. **Regression Runner** — replays a YAML-defined set of question / expected-source pairs against your pipeline's outputs and tracks pass rate over time, with history in SQLite.
7. **Reporters** — text / JSON / JUnit XML output, so it drops into any CI pipeline.

## Quick start

```bash
pip install -r requirements.txt

# Score a single answer against retrieved chunks
python -m rag_integrity.cli check --answer answer.json --docs examples/sample_documents.json

# Audit retrieval coverage against an evaluation question set
python -m rag_integrity.cli audit-retrieval examples/sample_documents.json eval_questions.json

# Run the regression suite against real pipeline outputs
python -m rag_integrity.cli regression examples/example_regression_set.yaml responses.jsonl
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full module breakdown and data flow.

## Files

- `rag_integrity/grounding.py` — grounding / hallucination scoring
- `rag_integrity/citation_verifier.py` — verifies citations against source documents
- `rag_integrity/chunking_analyzer.py` — analyzes chunk boundaries for quality issues
- `rag_integrity/retrieval_audit.py` — finds knowledge-base blind spots
- `rag_integrity/scorer.py` — combined 0-100 reliability score
- `rag_integrity/regression.py` — YAML regression suite runner
- `rag_integrity/storage.py` — SQLite-backed run history
- `rag_integrity/reporters.py` — text / JSON / JUnit XML rendering
- `rag_integrity/cli.py` — command-line entry point
- `tests/` — unit tests for every module
- `examples/` — a worked example document set and regression suite

## Roadmap

- Embedding-based grounding (currently lexical-overlap based, fully offline)
- Native LangChain / LlamaIndex retriever adapters
- Web dashboard for retrieval blind-spot trends over time

## License

MIT — see [LICENSE](LICENSE).
