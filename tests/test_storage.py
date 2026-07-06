import os
import tempfile

import pytest

from rag_integrity.regression import CaseResult, RegressionReport
from rag_integrity.storage import Storage


@pytest.fixture
def storage():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = Storage(path)
    yield store
    os.remove(path)


def test_record_and_read_check(storage):
    storage.record_check("what is x?", True, 92.5, ["grounding score: 92.5"])
    history = storage.history(kind="check")
    assert len(history) == 1
    assert history[0]["passed"] == 1


def test_record_regression(storage):
    report = RegressionReport(
        total=2, passed=1, failed=1, cases=[CaseResult("q1", True), CaseResult("q2", False, ["missing phrase"])]
    )
    storage.record_regression(report)
    history = storage.history(kind="regression")
    assert len(history) == 1
    assert history[0]["score"] == 50.0


def test_pass_rate_trend_averages_scores(storage):
    for total, passed in ((1, 1), (1, 0)):
        report = RegressionReport(total=total, passed=passed, failed=total - passed, cases=[])
        storage.record_regression(report)
    trend = storage.pass_rate_trend(kind="regression", limit=10)
    assert trend == 50.0


def test_pass_rate_trend_none_when_no_history(storage):
    assert storage.pass_rate_trend(kind="check") is None
