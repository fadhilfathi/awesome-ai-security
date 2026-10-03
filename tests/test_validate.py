"""Validator tests: every rule slug, each with a paired clean case.

Design rule for this module: a rule test asserts the exact slug appears in the
JSON report. Asserting only a nonzero exit code would pass for the wrong
reason, since a dozen rules can each produce exit 1.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml
from conftest import ATTACK_CLASSES, EVIDENCE_IMPACT

from scripts.entries import today
from scripts.validate import (
    DUPLICATE_URL_COMMENT_KEYS,
    TIER1_EVIDENCE_KEYWORDS,
    Violation,
    build_report,
    has_errors,
)

Factory = Callable[..., Path]
Run = Callable[..., Any]

#: Every rule slug the validator documents, transcribed from its docstring.
ALL_RULES = (
    "unreadable_entry",
    "schema_invalid",
    "filename_id_mismatch",
    "duplicate_id",
    "missing_primary_source",
    "missing_source",
    "duplicate_url_in_entry",
    "duplicate_url_across_entries",
    "cve_malformed",
    "cve_duplicate_in_entry",
    "tier1_impact_missing_evidence",
    "blank_text_field",
    "date_in_future",
    "last_verified_in_future",
    "stale_entry",
)
# The contract enumerates sixteen slugs but lists fifteen; the implementation
# and its docstring both carry those same fifteen. Pinned here so a genuine
# sixteenth rule cannot be added without this test noticing.
assert len(ALL_RULES) == 15
assert len(set(ALL_RULES)) == 15

SHARED_URL = "https://example.invalid/shared-advisory"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def source(url: str, kind: str = "primary", title: str = "Synthetic source") -> dict:
    return {"url": url, "kind": kind, "title": title}


def drop_key(path: Path, key: str) -> None:
    """Remove one top-level key from a written entry file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    del data[key]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def two_entries_sharing_a_url(entry_factory: Factory, **second_kwargs: Any) -> None:
    entry_factory("first-entry", sources=[source(SHARED_URL, title="Shared")])
    entry_factory(
        "second-entry", sources=[source(SHARED_URL, title="Shared")], **second_kwargs
    )


# --------------------------------------------------------------------------
# baseline and plumbing
# --------------------------------------------------------------------------


def test_default_entry_is_clean(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("synthetic-entry")
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]
    assert result.report["violations"] == []
    assert result.report["error_count"] == 0
    assert result.report["warning_count"] == 0
    assert result.report["valid"] is True
    assert result.code == 0


def test_empty_catalogue_is_clean(run_validate: Run) -> None:
    result = run_validate()
    assert result.slugs == set()
    assert result.report["violations"] == []
    assert result.report["error_count"] == 0
    assert result.code == 0


def test_empty_catalogue_text_mode_reports_zero(run_validate: Run) -> None:
    result = run_validate(json_output=False)
    assert "0 violation(s): 0 error(s), 0 warning(s)" in result.text
    assert result.code == 0


def test_json_report_has_the_documented_shape(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry")
    result = run_validate()
    assert set(result.report) == {"valid", "error_count", "warning_count", "violations"}
    assert isinstance(result.report["valid"], bool)
    assert isinstance(result.report["error_count"], int)
    assert isinstance(result.report["warning_count"], int)
    assert isinstance(result.report["violations"], list)


def test_violation_records_carry_the_documented_keys(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier=0)
    result = run_validate()
    assert result.report["violations"]
    for record in result.report["violations"]:
        assert set(record) == {"id", "file", "rule", "message", "severity"}
        assert record["severity"] in {"error", "warning"}
        assert record["message"]
    assert all(
        r["file"].endswith("data/entries/synthetic-entry.yml")
        for r in result.report["violations"]
    )


def test_text_output_names_the_slug_and_counts(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier=0)
    result = run_validate(json_output=False)
    assert "[schema_invalid]" in result.text
    assert "data/entries/synthetic-entry.yml" in result.text
    assert "1 violation(s): 1 error(s), 0 warning(s)" in result.text
    assert "across 1 entr(ies) in entries/" in result.text
    assert result.code == 1


def test_severity_helpers_and_strict_report() -> None:
    warning = Violation("i", "f", "stale_entry", "m", "warning")
    error = Violation("i", "f", "schema_invalid", "m", "error")
    assert has_errors([]) is False
    assert has_errors([warning]) is False
    assert has_errors([warning, error]) is True

    loose = build_report([warning], strict=False)
    assert (loose["valid"], loose["error_count"], loose["warning_count"]) == (
        True,
        0,
        1,
    )
    assert loose["violations"] == [warning.as_dict()]
    assert build_report([warning], strict=True)["valid"] is False
    assert build_report([error], strict=False)["valid"] is False


# --------------------------------------------------------------------------
# unreadable_entry
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "body"),
    [
        ("empty-file.yml", ""),
        ("only-comment.yml", "# nothing but a comment\n"),
        ("bare-list.yml", "- one\n- two\n"),
        ("broken-yaml.yml", 'id: "unterminated\ntier: [1, 2\n'),
        ("scalar.yml", "just-a-string\n"),
    ],
)
def test_unreadable_entry(
    tmp_catalogue, run_validate: Run, filename: str, body: str
) -> None:
    (tmp_catalogue.entries_dir / filename).write_text(body, encoding="utf-8")
    result = run_validate()
    assert result.slugs == {"unreadable_entry"}
    violation = result.violations("unreadable_entry")[0]
    assert Path(violation["file"]).name == filename
    assert violation["id"] == Path(filename).stem
    assert violation["severity"] == "error"
    assert result.code == 1


def test_unreadable_entry_leaves_its_neighbour_alone(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("good-entry")
    (tmp_catalogue.entries_dir / "broken.yml").write_text("- oops\n", encoding="utf-8")
    result = run_validate()
    assert result.slugs == {"unreadable_entry"}
    assert [v["id"] for v in result.violations("unreadable_entry")] == ["broken"]


# --------------------------------------------------------------------------
# schema_invalid: attack_class enum
# --------------------------------------------------------------------------


@pytest.mark.parametrize("attack_class", ATTACK_CLASSES)
def test_schema_accepts_every_enum_value(
    entry_factory: Factory, run_validate: Run, attack_class: str
) -> None:
    entry_factory("synthetic-entry", attack_class=attack_class)
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]
    assert result.code == 0


@pytest.mark.parametrize(
    "attack_class",
    [
        "PROMPT_INJECTION",
        "prompt_injection_direct",
        "OTHER_",
        "",
        "PROMPT-INJECTION-DIRECT",
        "TOOLPOISONING",
    ],
)
def test_schema_rejects_near_miss_attack_class(
    entry_factory: Factory, run_validate: Run, attack_class: str
) -> None:
    entry_factory("synthetic-entry", attack_class=attack_class)
    result = run_validate()
    assert result.slugs == {"schema_invalid"}
    violation = result.violations("schema_invalid")[0]
    assert "attack_class" in violation["message"]
    assert result.code == 1


def test_attack_class_failure_names_only_that_field(
    entry_factory: Factory, run_validate: Run
) -> None:
    """Proves the enum rejection is the class rule, not a generic one."""
    entry_factory("synthetic-entry", attack_class="OTHER_")
    result = run_validate()
    assert len(result.violations("schema_invalid")) == 1
    assert "attack_class" in result.violations("schema_invalid")[0]["message"]


# --------------------------------------------------------------------------
# schema_invalid: tier, dates, shape
# --------------------------------------------------------------------------


@pytest.mark.parametrize("tier", [0, 4, -1, 99])
def test_schema_rejects_tier_outside_one_to_three(
    entry_factory: Factory, run_validate: Run, tier: int
) -> None:
    entry_factory("synthetic-entry", tier=tier)
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("tier" in v["message"] for v in result.violations("schema_invalid"))
    assert result.code == 1


@pytest.mark.parametrize("tier", [1, 2, 3])
def test_schema_accepts_tier_one_to_three(
    entry_factory: Factory, run_validate: Run, tier: int
) -> None:
    entry_factory("synthetic-entry", tier=tier)
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


@pytest.mark.parametrize(
    "date",
    ["2001/02/03", "03-02-2001", "2001-2-3", "20010203", "2001-02-03-04", "Feb 2001"],
)
def test_schema_rejects_bad_date_format(
    entry_factory: Factory, run_validate: Run, date: str
) -> None:
    entry_factory("synthetic-entry", date=date)
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("date" in v["message"] for v in result.violations("schema_invalid"))
    assert "date_in_future" not in result.slugs


def test_schema_rejects_a_non_integer_tier(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier="2")
    result = run_validate()
    assert result.slugs == {"schema_invalid"}
    assert any("tier" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_a_blank_id(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("synthetic-entry", id="  ")
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("id" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_an_unknown_top_level_key(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", confidence="high")
    result = run_validate()
    assert result.slugs == {"schema_invalid"}
    assert "confidence" in result.violations("schema_invalid")[0]["message"]


def test_schema_rejects_a_short_summary(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", summary="too short")
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("summary" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_angle_brackets_in_a_title(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", title="A synthetic <script>title</script> here")
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("title" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_a_non_https_source_url(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", sources=[source("http://example.invalid/plain")])
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("url" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_an_unknown_source_kind(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry", sources=[source("https://example.invalid/x", "third")]
    )
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("kind" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_a_source_without_a_title(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry",
        sources=[{"url": "https://example.invalid/x", "kind": "primary"}],
    )
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("title" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_an_empty_source_list(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", sources=[])
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any("sources" in v["message"] for v in result.violations("schema_invalid"))


def test_schema_rejects_a_malformed_last_verified(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", last_verified="2001-2-3")
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert any(
        "last_verified" in v["message"] for v in result.violations("schema_invalid")
    )
    assert "last_verified_in_future" not in result.slugs


def test_schema_collects_every_error_for_one_entry(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier=9, attack_class="NOPE", target="")
    result = run_validate()
    assert result.slugs == {"schema_invalid"}
    assert len(result.violations("schema_invalid")) == 3


# --------------------------------------------------------------------------
# filename_id_mismatch
# --------------------------------------------------------------------------


def test_filename_id_mismatch(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("declared-id", filename="different-file")
    result = run_validate()
    assert result.slugs == {"filename_id_mismatch"}
    message = result.violations("filename_id_mismatch")[0]["message"]
    assert "different-file" in message
    assert "declared-id" in message
    assert result.code == 1


def test_filename_id_mismatch_paired_with_matching_name(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("declared-id", filename="declared-id")
    result = run_validate()
    assert result.slugs == set()


# --------------------------------------------------------------------------
# duplicate_id
# --------------------------------------------------------------------------


def test_duplicate_id_across_two_files(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("shared-id", filename="first-file")
    entry_factory("shared-id", filename="second-file")
    result = run_validate()
    duplicates = result.violations("duplicate_id")
    assert len(duplicates) == 1
    assert duplicates[0]["id"] == "shared-id"
    assert Path(duplicates[0]["file"]).name == "second-file.yml"
    assert "first-file" in duplicates[0]["message"]
    assert result.code == 1


def test_duplicate_id_paired_with_distinct_ids(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("first-id", filename="first-id")
    entry_factory("second-id", filename="second-id")
    result = run_validate()
    assert result.slugs == set()


def test_duplicate_id_is_not_raised_by_a_filename_mismatch_alone(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("declared-id", filename="different-file")
    result = run_validate()
    assert result.slugs == {"filename_id_mismatch"}
    assert result.violations("duplicate_id") == []


# --------------------------------------------------------------------------
# missing_primary_source / missing_source
# --------------------------------------------------------------------------


@pytest.mark.parametrize("tier", [1, 2])
def test_missing_primary_source_for_tier_one_and_two(
    entry_factory: Factory, run_validate: Run, tier: int
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=tier,
        impact=EVIDENCE_IMPACT,
        sources=[source(f"https://example.invalid/secondary-{tier}", "secondary")],
    )
    result = run_validate()
    assert result.slugs == {"missing_primary_source"}
    violation = result.violations("missing_primary_source")[0]
    assert f"tier {tier} entry" in violation["message"]
    assert result.code == 1


@pytest.mark.parametrize("tier", [1, 2])
def test_missing_primary_source_paired_with_a_primary_added(
    entry_factory: Factory, run_validate: Run, tier: int
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=tier,
        impact=EVIDENCE_IMPACT,
        sources=[source(f"https://example.invalid/primary-{tier}", "primary")],
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


def test_tier_three_with_only_a_secondary_source_passes(
    entry_factory: Factory, run_validate: Run
) -> None:
    """The asymmetry is the rule: tier 3 needs a source, not a primary."""
    entry_factory(
        "synthetic-entry",
        tier=3,
        sources=[source("https://example.invalid/secondary-only", "secondary")],
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]
    assert result.code == 0


def test_missing_source_for_tier_three(
    entry_factory: Factory, run_validate: Run
) -> None:
    """An emptied sources array is caught by the schema first, so the semantic
    rule is reached by omitting the key outright."""
    path = entry_factory("synthetic-entry", tier=3)
    drop_key(path, "sources")

    result = run_validate()
    assert "missing_source" in result.slugs
    violation = result.violations("missing_source")[0]
    assert "tier 3" in violation["message"]
    assert "schema_invalid" in result.slugs
    assert result.code == 1


def test_missing_source_paired_with_any_source(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier=3)
    result = run_validate()
    assert "missing_source" not in result.slugs
    assert result.slugs == set()


def test_missing_source_does_not_fire_for_a_tier_one_entry(
    entry_factory: Factory, run_validate: Run
) -> None:
    path = entry_factory("synthetic-entry", tier=1)
    drop_key(path, "sources")
    result = run_validate()
    assert "missing_source" not in result.slugs
    assert "missing_primary_source" in result.slugs


# --------------------------------------------------------------------------
# duplicate_url_in_entry
# --------------------------------------------------------------------------


def test_duplicate_url_in_entry(entry_factory: Factory, run_validate: Run) -> None:
    url = "https://example.invalid/repeated"
    entry_factory(
        "synthetic-entry",
        sources=[source(url, "primary", "First"), source(url, "secondary", "Second")],
    )
    result = run_validate()
    assert "duplicate_url_in_entry" in result.slugs
    violation = result.violations("duplicate_url_in_entry")[0]
    assert url in violation["message"]
    assert "cited 2 times" in violation["message"]
    assert result.code == 1


def test_duplicate_url_in_entry_is_never_excused_by_a_comment(
    entry_factory: Factory, run_validate: Run
) -> None:
    url = "https://example.invalid/repeated-excused"
    entry_factory(
        "synthetic-entry",
        comment="duplicate-primary-source: the same advisory is listed twice",
        sources=[source(url, "primary", "First"), source(url, "secondary", "Second")],
    )
    result = run_validate()
    assert "duplicate_url_in_entry" in result.slugs
    assert "duplicate_url_across_entries" not in result.slugs


def test_duplicate_url_in_entry_paired_with_two_distinct_urls(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry",
        sources=[
            source("https://example.invalid/one", "primary", "One"),
            source("https://example.invalid/two", "secondary", "Two"),
        ],
    )
    result = run_validate()
    assert "duplicate_url_in_entry" not in result.slugs
    assert result.slugs == set()


# --------------------------------------------------------------------------
# duplicate_url_across_entries
# --------------------------------------------------------------------------


def test_duplicate_url_across_entries(
    entry_factory: Factory, run_validate: Run
) -> None:
    two_entries_sharing_a_url(entry_factory)
    result = run_validate()
    assert result.slugs == {"duplicate_url_across_entries"}
    violation = result.violations("duplicate_url_across_entries")[0]
    assert violation["id"] == "second-entry"
    assert SHARED_URL in violation["message"]
    assert "first-entry" in violation["message"]
    assert result.code == 1


@pytest.mark.parametrize("comment_key", DUPLICATE_URL_COMMENT_KEYS)
def test_duplicate_url_across_entries_is_excused_by_a_comment(
    entry_factory: Factory, run_validate: Run, comment_key: str
) -> None:
    two_entries_sharing_a_url(
        entry_factory, comment=f"{comment_key}: also cited by first-entry"
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]
    assert result.code == 0


def test_a_comment_that_is_not_a_recognised_key_does_not_excuse(
    entry_factory: Factory, run_validate: Run
) -> None:
    two_entries_sharing_a_url(
        entry_factory, comment="shared-source: reuse explained somewhere"
    )
    result = run_validate()
    assert result.slugs == {"duplicate_url_across_entries"}


def test_the_excusing_key_is_anchored_to_the_start_of_a_comment_line(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    """A leading word before the key defeats the escape hatch.

    That is the regex as written -- ``^[ \\t]*#`` then the key -- and it keeps
    the hatch from being switched on accidentally by an unrelated note that
    merely mentions the key.
    """
    two_entries_sharing_a_url(
        entry_factory, comment="see also duplicate-primary-source: reused here"
    )
    result = run_validate()
    assert result.slugs == {"duplicate_url_across_entries"}, result.report["violations"]


def test_the_excusing_key_works_when_indented_under_a_comment(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    two_entries_sharing_a_url(entry_factory, comment="  duplicate-source: reused")
    assert run_validate().slugs == set()


def test_the_excusing_key_does_not_rescue_a_key_hidden_in_a_yaml_value(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    """The hatch is matched against raw comment lines, not parsed YAML."""
    two_entries_sharing_a_url(entry_factory)
    path = tmp_catalogue.entries_dir / "second-entry.yml"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nduplicate-primary-source: stray\n",
        encoding="utf-8",
    )
    result = run_validate()
    assert "schema_invalid" in result.slugs
    assert "duplicate_url_across_entries" in result.slugs


def test_duplicate_url_across_entries_paired_with_distinct_urls(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("first-entry")
    entry_factory("second-entry")
    result = run_validate()
    assert "duplicate_url_across_entries" not in result.slugs
    assert result.slugs == set()


def test_duplicate_url_across_entries_flags_only_the_second_citer(
    entry_factory: Factory, run_validate: Run
) -> None:
    two_entries_sharing_a_url(entry_factory)
    result = run_validate()
    assert len(result.violations("duplicate_url_across_entries")) == 1


def test_a_secondary_url_shared_across_entries_is_also_flagged(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "first-entry", sources=[source("https://example.invalid/sec", "secondary")]
    )
    entry_factory(
        "second-entry", sources=[source("https://example.invalid/sec", "secondary")]
    )
    result = run_validate()
    assert result.slugs == {"duplicate_url_across_entries"}


# --------------------------------------------------------------------------
# cve_malformed / cve_duplicate_in_entry
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cve_id",
    [
        "CVE-26-1234",
        "cve-2026-1234",
        "CVE-2026-123",
        "CVE 2026 1234",
        "CVE-2026-12345678",
    ],
)
def test_cve_malformed(entry_factory: Factory, run_validate: Run, cve_id: str) -> None:
    entry_factory("synthetic-entry", cve=[cve_id])
    result = run_validate()
    assert "cve_malformed" in result.slugs
    assert cve_id in result.violations("cve_malformed")[0]["message"]
    assert result.code == 1


@pytest.mark.parametrize(
    "cve_id", ["CVE-2026-0000", "CVE-2026-00000", "CVE-2026-0000000"]
)
def test_cve_well_formed_ids_pass(
    entry_factory: Factory, run_validate: Run, cve_id: str
) -> None:
    entry_factory("synthetic-entry", cve=[cve_id])
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


def test_cve_duplicate_in_entry(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("synthetic-entry", cve=["CVE-2026-00000", "CVE-2026-00000"])
    result = run_validate()
    assert "cve_duplicate_in_entry" in result.slugs
    assert "CVE-2026-00000" in result.violations("cve_duplicate_in_entry")[0]["message"]


def test_cve_duplicate_in_entry_paired_with_two_distinct_ids(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", cve=["CVE-2026-00000", "CVE-2026-00001"])
    result = run_validate()
    assert "cve_duplicate_in_entry" not in result.slugs
    assert result.slugs == set()


def test_the_same_cve_id_in_two_entries_is_not_a_duplicate_in_entry(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("first-entry", cve=["CVE-2026-00000"])
    entry_factory("second-entry", cve=["CVE-2026-00000"])
    result = run_validate()
    assert result.violations("cve_duplicate_in_entry") == []
    assert result.slugs == set()


# --------------------------------------------------------------------------
# tier1_impact_missing_evidence
# --------------------------------------------------------------------------


def test_tier1_impact_missing_evidence(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=1,
        impact="The synthetic outcome is described here with no stated evidence.",
    )
    result = run_validate()
    assert result.slugs == {"tier1_impact_missing_evidence"}
    assert result.code == 1


def test_tier1_impact_with_exploit_passes(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=1,
        impact="The synthetic source states that exploit activity was observed.",
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


@pytest.mark.parametrize("keyword", TIER1_EVIDENCE_KEYWORDS)
def test_every_documented_keyword_clears_the_lint(
    entry_factory: Factory, run_validate: Run, keyword: str
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=1,
        impact=(
            "A synthetic statement padded out to satisfy the schema length "
            f"rules that happens to mention {keyword} somewhere inside it."
        ),
    )
    result = run_validate()
    assert result.slugs == set(), (keyword, result.report["violations"])


@pytest.mark.parametrize("tier", [2, 3])
def test_tier1_lint_ignores_non_tier_one_entries(
    entry_factory: Factory, run_validate: Run, tier: int
) -> None:
    entry_factory(
        f"tier-{tier}-entry",
        tier=tier,
        impact="No evidence vocabulary appears anywhere in this synthetic text.",
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


def test_tier1_lint_is_case_insensitive(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory(
        "synthetic-entry",
        tier=1,
        impact="The synthetic source states EXPLOIT activity was seen upstream.",
    )
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


def test_tier1_lint_message_lists_the_expected_keywords(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", tier=1, impact="No stated evidence in this field.")
    message = run_validate().violations("tier1_impact_missing_evidence")[0]["message"]
    for keyword in TIER1_EVIDENCE_KEYWORDS:
        assert keyword in message


# --------------------------------------------------------------------------
# blank_text_field
# --------------------------------------------------------------------------


@pytest.mark.parametrize("field", ["summary", "impact", "mitigation"])
def test_blank_text_field(
    entry_factory: Factory, run_validate: Run, field: str
) -> None:
    entry_factory("synthetic-entry", **{field: "   "})
    result = run_validate()
    assert "blank_text_field" in result.slugs
    assert field in result.violations("blank_text_field")[0]["message"]
    assert result.code == 1


@pytest.mark.parametrize("field", ["summary", "impact", "mitigation"])
def test_blank_text_field_paired_with_real_text(
    entry_factory: Factory, run_validate: Run, field: str
) -> None:
    values = {
        "summary": "A perfectly ordinary synthetic summary long enough to pass.",
        "impact": "A perfectly ordinary synthetic impact string of adequate length.",
        "mitigation": "A perfectly ordinary synthetic mitigation note goes here.",
    }
    entry_factory("synthetic-entry", **{field: values[field]})
    result = run_validate()
    assert "blank_text_field" not in result.slugs
    assert result.slugs == set()


def test_blank_summary_trips_both_the_schema_and_the_lint(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", summary="  ")
    result = run_validate()
    assert {"schema_invalid", "blank_text_field"} <= result.slugs
    assert any("summary" in v["message"] for v in result.violations("blank_text_field"))


def test_a_present_but_empty_mitigation_is_blank(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", mitigation="")
    result = run_validate()
    assert "blank_text_field" in result.slugs
    assert "schema_invalid" in result.slugs


# --------------------------------------------------------------------------
# date_in_future / last_verified_in_future
# --------------------------------------------------------------------------


def test_date_in_future(entry_factory: Factory, run_validate: Run, days_ahead) -> None:
    entry_factory("synthetic-entry", date=days_ahead(30))
    result = run_validate()
    assert result.slugs == {"date_in_future"}
    assert days_ahead(30) in result.violations("date_in_future")[0]["message"]
    assert result.code == 1


def test_date_in_future_paired_with_a_past_date(
    entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("synthetic-entry", date="2001-02-03")
    result = run_validate()
    assert "date_in_future" not in result.slugs
    assert result.slugs == set()


def test_date_today_is_not_in_the_future(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", date=days_ahead(0))
    result = run_validate()
    assert result.slugs == set(), result.report["violations"]


def test_tomorrow_is_in_the_future(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", date=days_ahead(1))
    assert "date_in_future" in run_validate().slugs


def test_month_only_date_in_the_current_month_is_not_in_the_future(
    entry_factory: Factory, run_validate: Run
) -> None:
    """YYYY-MM is anchored to the first of the month, the earliest day the
    value can denote, so it cannot read as future within the current month."""
    entry_factory("synthetic-entry", date=today().strftime("%Y-%m"))
    result = run_validate()
    assert "date_in_future" not in result.slugs
    assert result.slugs == set(), result.report["violations"]


def test_month_only_date_in_a_later_month_is_in_the_future(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", date=days_ahead(70)[:7])
    assert "date_in_future" in run_validate().slugs


def test_last_verified_in_future(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ahead(10))
    result = run_validate()
    assert result.slugs == {"last_verified_in_future"}
    assert result.violations("last_verified_in_future")[0]["severity"] == "error"
    assert result.code == 1


def test_last_verified_in_future_paired_with_today(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ahead(0))
    result = run_validate()
    assert "last_verified_in_future" not in result.slugs
    assert result.slugs == set()


def test_a_future_last_verified_suppresses_the_stale_warning(
    entry_factory: Factory, run_validate: Run, days_ahead
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ahead(5))
    assert run_validate("--max-age-days", "1").slugs == {"last_verified_in_future"}


# --------------------------------------------------------------------------
# stale_entry
# --------------------------------------------------------------------------


def test_stale_entry_is_a_warning_and_exits_zero(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    result = run_validate()
    assert result.slugs == {"stale_entry"}
    violation = result.violations("stale_entry")[0]
    assert violation["severity"] == "warning"
    assert "400 days old" in violation["message"]
    assert "365 day horizon" in violation["message"]
    assert result.report["error_count"] == 0
    assert result.report["warning_count"] == 1
    assert result.report["valid"] is True
    assert result.code == 0


def test_stale_entry_is_fatal_under_strict(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    result = run_validate("--strict")
    assert result.slugs == {"stale_entry"}
    assert result.report["valid"] is False
    assert result.code == 1


def test_max_age_days_widening_clears_the_stale_warning(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    assert "stale_entry" in run_validate("--max-age-days", "365").slugs
    assert "stale_entry" not in run_validate("--max-age-days", "500").slugs


def test_max_age_days_narrowing_creates_the_stale_warning(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(100))
    assert run_validate("--max-age-days", "365").slugs == set()
    assert "stale_entry" in run_validate("--max-age-days", "30").slugs


def test_the_horizon_boundary_day_is_not_stale(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(365))
    assert "stale_entry" not in run_validate("--max-age-days", "365").slugs
    assert "stale_entry" in run_validate("--max-age-days", "364").slugs


def test_max_age_days_message_names_the_horizon(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    result = run_validate("--max-age-days", "42")
    assert "42 day horizon" in result.violations("stale_entry")[0]["message"]


def test_a_fresh_entry_is_not_stale(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("synthetic-entry")
    result = run_validate()
    assert "stale_entry" not in result.slugs
    assert result.report["warning_count"] == 0


def test_stale_counts_one_warning_per_stale_entry(
    tmp_catalogue, entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("fresh-entry")
    entry_factory("stale-one", last_verified=days_ago(400))
    entry_factory("stale-two", last_verified=days_ago(900))
    result = run_validate()
    assert result.report["warning_count"] == 2
    assert {v["id"] for v in result.violations("stale_entry")} == {
        "stale-one",
        "stale-two",
    }


# --------------------------------------------------------------------------
# exit-code contract
# --------------------------------------------------------------------------


def test_clean_catalogue_exits_zero(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    entry_factory("clean-entry")
    entry_factory("another-clean-entry", tier=2)
    result = run_validate()
    assert result.slugs == set()
    assert result.code == 0


def test_an_error_exits_one(entry_factory: Factory, run_validate: Run) -> None:
    entry_factory("synthetic-entry", tier=1, impact="No evidence vocabulary at all.")
    result = run_validate()
    assert result.report["error_count"] >= 1
    assert result.report["valid"] is False
    assert result.code == 1


def test_warning_only_exits_zero_without_strict(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    result = run_validate()
    assert result.report["warning_count"] == 1
    assert result.report["error_count"] == 0
    assert result.code == 0


def test_warning_only_exits_one_under_strict(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", last_verified=days_ago(400))
    result = run_validate("--strict")
    assert result.report["warning_count"] == 1
    assert result.report["error_count"] == 0
    assert result.code == 1


def test_error_and_warning_together_exit_one_either_way(
    entry_factory: Factory, run_validate: Run, days_ago
) -> None:
    entry_factory("synthetic-entry", tier=0, last_verified=days_ago(400))
    loose = run_validate()
    strict = run_validate("--strict")
    assert {"schema_invalid", "stale_entry"} <= loose.slugs
    assert loose.report["error_count"] == 1
    assert loose.report["warning_count"] == 1
    assert loose.code == 1
    assert strict.code == 1


# --------------------------------------------------------------------------
# slug coverage guard
# --------------------------------------------------------------------------


def test_every_documented_slug_is_reachable_in_one_catalogue(
    tmp_catalogue, entry_factory: Factory, run_validate: Run, days_ahead, days_ago
) -> None:
    """One catalogue that trips every documented slug at once.

    Cheap to read, and it fails if a slug is renamed, dropped, or accidentally
    made unreachable because an earlier check short-circuits the loop.
    """
    entries_dir = tmp_catalogue.entries_dir
    (entries_dir / "aaa-unreadable.yml").write_text("", encoding="utf-8")

    entry_factory("bbb-bad-class", attack_class="OTHER_")
    entry_factory("ccc-declared-id", filename="ccc-file-name")
    entry_factory("ddd-twin", filename="ddd-first-file")
    entry_factory("ddd-twin", filename="ddd-second-file")
    entry_factory(
        "eee-no-primary",
        tier=2,
        sources=[source("https://example.invalid/eee", "secondary")],
    )
    drop_key(entry_factory("fff-no-sources", tier=3), "sources")
    entry_factory(
        "ggg-url-twice",
        sources=[
            source("https://example.invalid/ggg", "primary", "One"),
            source("https://example.invalid/ggg", "secondary", "Two"),
        ],
    )
    entry_factory("hhh-first-citer", sources=[source(SHARED_URL)])
    entry_factory("iii-second-citer", sources=[source(SHARED_URL)])
    entry_factory("jjj-bad-cve", cve=["CVE-26-1"])
    entry_factory("kkk-dup-cve", cve=["CVE-2026-00000", "CVE-2026-00000"])
    entry_factory("lll-no-evidence", tier=1, impact="No evidence vocabulary here.")
    entry_factory("mmm-blank", mitigation="   ")
    entry_factory("nnn-future-date", date=days_ahead(30))
    entry_factory("ooo-future-verified", last_verified=days_ahead(5))
    entry_factory("ppp-stale", last_verified=days_ago(900))

    result = run_validate()
    assert set(ALL_RULES) <= result.slugs, sorted(set(ALL_RULES) - result.slugs)
    assert result.slugs <= set(ALL_RULES), sorted(result.slugs - set(ALL_RULES))
    assert result.code == 1
    assert result.report["valid"] is False


def test_the_validator_documents_exactly_the_slugs_it_can_emit(
    tmp_catalogue, entry_factory: Factory, run_validate: Run
) -> None:
    """The slug set is a public contract for ``--json`` consumers.

    The docstring is what a reader relies on; the reachable slug set is what
    the code can actually produce. Comparing the two catches a rule that is
    added, renamed, or dropped on only one side.
    """
    from scripts import validate as module

    lines = Path(module.__file__).read_text(encoding="utf-8").splitlines()
    start = lines.index("Rule slugs")
    end = lines.index("A note on ``tier1_impact_missing_evidence``")
    body = "\n".join(lines[start:end])
    documented = set(re.findall(r"^``([a-z][a-z0-9_]*)``$", body, re.MULTILINE))
    assert documented == set(ALL_RULES), documented ^ set(ALL_RULES)

    # A slug that silently became dead code would still be documented; this
    # pins that the module still exposes the vocabulary the rules rely on.
    assert "exploit" in module.TIER1_EVIDENCE_KEYWORDS
    assert "in the wild" in module.TIER1_EVIDENCE_KEYWORDS
    assert set(module.DUPLICATE_URL_COMMENT_KEYS) == {
        "duplicate-primary-source",
        "duplicate-source",
    }
    entry_factory("guard-entry", attack_class="OTHER_")
    assert run_validate().slugs == {"schema_invalid"}
