"""Contract tests for scripts/check_links.py.

Network behaviour is out of scope here: this module exists so that the
output contract the weekly workflow depends on is pinned, offline. The
workflow redirects stdout into a file and parses it as JSON, so the shape
of the output is an interface, not a convenience.

The empty-catalogue case is the one that actually broke in CI: an early
return printed a prose sentence, and the downstream step died on
json.loads. These tests are deliberately network-free so they run
everywhere.
"""

from __future__ import annotations

import json

import pytest
from conftest import Sandbox

from scripts.check_links import main, render_json, was_known_bad


def test_json_output_parses_when_there_is_nothing_to_check(
    tmp_catalogue: Sandbox, capsys
):
    """--json must stay valid JSON even with zero URLs.

    Regression: the empty-catalogue branch used to print
    "no source URLs to check." regardless of --json, which broke the
    workflow step that parses the report.
    """
    assert main(["--json", "--no-state"]) == 0

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload == {"results": []}


def test_text_output_stays_human_readable_when_empty(tmp_catalogue: Sandbox, capsys):
    """The non-JSON path keeps its plain sentence; the two modes differ."""
    assert main(["--no-state"]) == 0

    out = capsys.readouterr().out
    assert "no source URLs to check" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_json_mode_output_is_never_empty(tmp_catalogue: Sandbox, capsys):
    """An empty stdout would make the consumer's size check misreport it.

    The workflow treats a zero-byte report as an upstream failure, so a
    valid empty result set must still be non-empty bytes.
    """
    assert main(["--json", "--no-state"]) == 0

    assert capsys.readouterr().out.strip() != ""


def test_render_json_of_no_results_is_a_stable_document():
    """render_json([], {}) is the exact document the empty path emits."""
    assert json.loads(render_json([], {})) == {"results": []}


def test_a_healthy_link_last_run_is_not_a_repeat_failure():
    """Regression: presence in the state file is not the same as having failed.

    Every checked URL is recorded in the state file, including healthy ones.
    Treating mere presence as a prior failure made a first-time break escalate
    to a tracking issue immediately, so the two-consecutive-runs rule the
    workflow relies on never actually gated anything.
    """
    healthy = {"results": {"https://example.test/a": {"status": "ok", "code": 200}}}

    assert was_known_bad("https://example.test/a", healthy) is False


def test_a_link_failing_both_runs_is_a_repeat_failure():
    failing = {"results": {"https://example.test/a": {"status": "broken", "code": 404}}}

    assert was_known_bad("https://example.test/a", failing) is True


def test_a_redirect_last_run_does_not_count_as_a_prior_failure():
    """A redirect is a healthy outcome, so it must not arm the repeat rule."""
    redirected = {
        "results": {"https://example.test/a": {"status": "redirect", "code": 301}}
    }

    assert was_known_bad("https://example.test/a", redirected) is False


def test_a_url_absent_from_state_is_not_a_repeat_failure():
    """A newly added URL has no history, so it cannot be a repeat."""
    assert was_known_bad("https://example.test/new", {"results": {}}) is False
    assert was_known_bad("https://example.test/new", {}) is False
