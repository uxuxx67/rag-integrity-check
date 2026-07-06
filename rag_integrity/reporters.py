"""Render RegressionReport / ReliabilityScore results as text, JSON, or JUnit
XML so they drop into any CI system."""
from __future__ import annotations

import json
from typing import Any
from xml.sax.saxutils import escape


def render_regression_text(report: Any) -> str:
    lines = [
        f"Total: {report.total}  Passed: {report.passed}  Failed: {report.failed}  "
        f"Pass rate: {report.pass_rate:.1%}"
    ]
    for case in report.cases:
        status = "PASS" if case.passed else "FAIL"
        lines.append(f"[{status}] {case.question}")
        for reason in case.reasons:
            lines.append(f"    - {reason}")
    lines.append("PASS" if report.failed == 0 else "FAIL")
    return "\n".join(lines)


def render_regression_json(report: Any) -> str:
    return json.dumps(report.to_dict(), indent=2)


def render_regression_junit(report: Any) -> str:
    cases = []
    for case in report.cases:
        name = escape(case.question)
        if case.passed:
            cases.append(f'  <testcase classname="rag_integrity" name="{name}"/>')
        else:
            message = escape("; ".join(case.reasons))
            cases.append(
                f'  <testcase classname="rag_integrity" name="{name}">'
                f'<failure message="{message}"/></testcase>'
            )
    body = "\n".join(cases)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<testsuite name="rag_integrity" tests="{report.total}" failures="{report.failed}">\n{body}\n</testsuite>\n'
    )


REGRESSION_RENDERERS = {
    "text": render_regression_text,
    "json": render_regression_json,
    "junit": render_regression_junit,
}


def render_score_text(score: Any) -> str:
    lines = [f"Reliability score: {score.score}/100 ({score.verdict})"]
    for line in score.breakdown:
        lines.append(f"  - {line}")
    return "\n".join(lines)


def render_score_json(score: Any) -> str:
    return json.dumps(
        {
            "score": score.score,
            "verdict": score.verdict,
            "grounding_score": score.grounding_score,
            "citation_penalty": score.citation_penalty,
            "chunking_penalty": score.chunking_penalty,
            "breakdown": score.breakdown,
        },
        indent=2,
    )


SCORE_RENDERERS = {"text": render_score_text, "json": render_score_json}
