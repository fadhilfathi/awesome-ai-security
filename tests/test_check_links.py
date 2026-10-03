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

from scripts.check_links import main, render_json


def test_json_output_parses_when_there_is_nothing_to_check(capsys):
    """--json must stay valid JSON even with zero URLs.

    Regression: the empty-catalogue branch used to print
    "no source URLs to check." regardless of --json, which broke the
    workflow step that parses the report.
    """
    assert main(["--json", "--no-state"]) == 0

    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload == {"results": []}


def test_text_output_stays_human_readable_when_empty(capsys):
    """The non-JSON path keeps its plain sentence; the two modes differ."""
    assert main(["--no-state"]) == 0

    out = capsys.readouterr().out
    assert "no source URLs to check" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)


def test_json_mode_output_is_never_empty(capsys):
    """An empty stdout would make the consumer's size check misreport it.

    The workflow treats a zero-byte report as an upstream failure, so a
    valid empty result set must still be non-empty bytes.
    """
    assert main(["--json", "--no-state"]) == 0

    assert capsys.readouterr().out.strip() != ""


def test_render_json_of_no_results_is_a_stable_document():
    """render_json([], {}) is the exact document the empty path emits."""
    assert json.loads(render_json([], {})) == {"results": []}
