# Architecture

*[Русская версия](ARCHITECTURE.ru.md)*

## Data flow

```
answer + retrieved chunks --> grounding.check() --> GroundingResult
answer + citations + documents --> citation_verifier.verify() --> CitationResult
document + chunks --> chunking_analyzer.analyze() --> ChunkIssue[]
questions + retrieval results --> retrieval_audit.audit() --> BlindSpot[]
(GroundingResult, CitationResult, ChunkIssue[]) --> scorer.score() --> ReliabilityScore
regression set (yaml) + responses --> regression.run() --> RegressionReport --> storage.record()
```

`cli.py` ties these together as standalone commands (`check`, `audit-retrieval`, `regression`, `report`) so any of them can be used independently or wired into a larger eval pipeline.

## Modules

| Module | Responsibility |
|---|---|
| `grounding.py` | Score how well an answer is supported by retrieved chunks; flag unsupported sentences |
| `citation_verifier.py` | Confirm cited sources actually contain what's claimed |
| `chunking_analyzer.py` | Detect chunk boundary problems (split sentences, lost headers, bad sizes) |
| `retrieval_audit.py` | Find knowledge-base blind spots across a question set |
| `scorer.py` | Combine all signals into one explainable 0-100 reliability score |
| `regression.py` | Run a YAML regression suite against pipeline outputs |
| `storage.py` | Persist run history to SQLite |
| `reporters.py` | Render results as text / JSON / JUnit XML |
| `config.py` | Centralized environment-variable configuration |
| `cli.py` | Command-line commands tying everything together |

## Design principles

1. **No hidden model calls.** Every score is derived from explicit lexical/statistical checks against the documents and answer you already have — fully offline and reproducible.
2. **Explainable over clever.** Every score comes with a breakdown of exactly which checks passed or failed and why.
3. **History lives in one place (SQLite)**, so regression tracking and reporting read from the same source of truth.
4. **CI-first.** Every command has a meaningful exit code so it works in any CI system without extra plumbing.
