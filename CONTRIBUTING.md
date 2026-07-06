# Contributing to RAG Integrity Check

Thanks for considering a contribution! This project favors explicit, inspectable heuristics over opaque "trust me" scores — every flag should be traceable to a specific check.

## Adding a grounding heuristic

1. Extend `grounding.py` with the new signal (keep it lexical/statistical, not a hidden model call).
2. Return it as part of the existing `GroundingResult` breakdown, don't silently fold it into the score without a labeled field.
3. Add test cases in `tests/test_grounding.py` covering supported and unsupported claims.

## Adding a chunking check

New checks in `chunking_analyzer.py` should return a `ChunkIssue` with a clear `kind` and human-readable `message`, and come with tests in `tests/test_chunking_analyzer.py`.

## Code style

Keep `rag_integrity/` free of network calls and model API calls — this library observes and scores documents/answers you already have; fetching or generating them is your integration's job, not this library's.

## Tests

Run `pytest` before opening a PR. New features should ship with tests.
