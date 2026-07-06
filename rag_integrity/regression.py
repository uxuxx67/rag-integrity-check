"""Regression runner - replays a YAML-defined set of question / expected-answer
/ expected-source pairs against real pipeline outputs, and reports pass/fail
per case so RAG regressions are caught before users notice.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CaseResult:
    question: str
    passed: bool
    reasons: List[str] = field(default_factory=list)


@dataclass
class RegressionReport:
    total: int
    passed: int
    failed: int
    cases: List[CaseResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round(self.pass_rate, 4),
            "cases": [
                {"question": c.question, "passed": c.passed, "reasons": c.reasons} for c in self.cases
            ],
        }


def _check_case(case: Dict[str, Any], response: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    answer = response.get("answer", "")

    for phrase in case.get("expected_answer_contains", []):
        if phrase.lower() not in answer.lower():
            reasons.append(f"answer missing expected phrase: '{phrase}'")

    expected_sources = set(case.get("expected_sources", []))
    actual_sources = set(response.get("sources", []))
    missing_sources = expected_sources - actual_sources
    if missing_sources:
        reasons.append(f"missing expected source(s): {sorted(missing_sources)}")

    for phrase in case.get("forbidden_phrases", []):
        if phrase.lower() in answer.lower():
            reasons.append(f"answer contains forbidden phrase: '{phrase}'")

    return reasons


def run(regression_set: Dict[str, Any], responses_by_question: Dict[str, Dict[str, Any]]) -> RegressionReport:
    """regression_set: {"cases": [{"question": ..., "expected_answer_contains": [...],
    "expected_sources": [...], "forbidden_phrases": [...]}, ...]}
    responses_by_question: dict question -> {"answer": ..., "sources": [...]}
    """
    cases = regression_set.get("cases", [])
    results: List[CaseResult] = []
    for case in cases:
        question = case["question"]
        response = responses_by_question.get(question, {})
        reasons = _check_case(case, response)
        results.append(CaseResult(question=question, passed=not reasons, reasons=reasons))
    passed = sum(1 for r in results if r.passed)
    return RegressionReport(total=len(results), passed=passed, failed=len(results) - passed, cases=results)
