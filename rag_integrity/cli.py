"""Command-line entry point for RAG Integrity Check.

Commands:
  check           <answer.json> <docs.json>     - score one answer for grounding/citations/chunking
  audit-retrieval <docs.json> <evaluations.json> - find knowledge-base blind spots
  regression      <set.yaml> <responses>         - run a regression suite against pipeline outputs
"""
from __future__ import annotations

import argparse
import json
import sys

from .chunking_analyzer import analyze_chunks
from .citation_verifier import verify_citations
from .config import Config
from .grounding import check_grounding
from .regression import run as run_regression
from .reporters import REGRESSION_RENDERERS, SCORE_RENDERERS
from .retrieval_audit import audit_retrieval, coverage_summary
from .scorer import score_answer
from .storage import Storage


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: str):
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_check(args: argparse.Namespace) -> int:
    config = Config.from_env()
    payload = _load_json(args.answer)
    docs = _load_json(args.docs)

    answer = payload["answer"]
    chunks = payload.get("chunks", [])

    grounding_result = check_grounding(answer, chunks, config.grounding_overlap_threshold)

    documents = {d["id"]: d["text"] for d in docs} if isinstance(docs, list) else docs
    citation_result = verify_citations(answer, documents, payload.get("citation_map"))

    chunk_issues = analyze_chunks(chunks) if chunks else []
    score = score_answer(grounding_result, citation_result, len(chunk_issues), config.unreliable_score_threshold)

    renderer = SCORE_RENDERERS.get(args.format or config.default_report_format, SCORE_RENDERERS["text"])
    print(renderer(score))

    storage = Storage(config.db_path)
    storage.record_check(payload.get("question", ""), score.verdict != "unreliable", score.score, score.breakdown)

    return 0 if score.verdict != "unreliable" else 1


def cmd_audit_retrieval(args: argparse.Namespace) -> int:
    config = Config.from_env()
    evaluations = _load_json(args.evaluations)
    summary = coverage_summary(evaluations, config.blind_spot_relevance_threshold)
    spots = audit_retrieval(evaluations, config.blind_spot_relevance_threshold)
    print(json.dumps({"summary": summary, "blind_spots": [s.__dict__ for s in spots]}, indent=2))
    return 0 if not spots else 1


def cmd_regression(args: argparse.Namespace) -> int:
    config = Config.from_env()
    regression_set = _load_yaml(args.regression_set)

    if args.responses.endswith(".jsonl"):
        with open(args.responses, "r", encoding="utf-8") as f:
            responses = [json.loads(line) for line in f if line.strip()]
    else:
        responses = _load_json(args.responses)

    responses_by_question = {r["question"]: r for r in responses}
    report = run_regression(regression_set, responses_by_question)

    storage = Storage(config.db_path)
    storage.record_regression(report)

    renderer = REGRESSION_RENDERERS.get(args.format or config.default_report_format, REGRESSION_RENDERERS["text"])
    print(renderer(report))

    return 0 if report.failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag_integrity", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="score one answer for grounding/citations/chunking")
    p_check.add_argument("--answer", required=True, help="path to a JSON file with answer/chunks/citation_map")
    p_check.add_argument("--docs", required=True, help="path to a JSON file/list of source documents")
    p_check.add_argument("--format", choices=list(SCORE_RENDERERS.keys()), default=None)
    p_check.set_defaults(func=cmd_check)

    p_audit = sub.add_parser("audit-retrieval", help="find knowledge-base blind spots")
    p_audit.add_argument("docs")
    p_audit.add_argument("evaluations")
    p_audit.set_defaults(func=cmd_audit_retrieval)

    p_reg = sub.add_parser("regression", help="run a regression suite against pipeline outputs")
    p_reg.add_argument("regression_set")
    p_reg.add_argument("responses")
    p_reg.add_argument("--format", choices=list(REGRESSION_RENDERERS.keys()), default=None)
    p_reg.set_defaults(func=cmd_regression)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
