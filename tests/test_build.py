"""Build tests: generated blocks, drift detection, idempotence, no writes.

The guarantees under test here are the ones CI leans on. If ``--check`` ever
writes, stops noticing drift, or stamps a build time into the output, the gate
silently stops meaning anything.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import README_SKELETON, Sandbox, secondary_source

from scripts.build import (
    ATTACK_CLASS_LABELS,
    SCHEMA_VERSION,
    TIER_PIPS,
    md_table,
    tier_badge,
)
from scripts.entries import today

Factory = Callable[..., Path]
Build = Callable[..., tuple[int, str]]

BLOCK_NAMES = (
    "count",
    "tier-legend",
    "tier1",
    "matrix",
    "catalogue",
    "entry-index",
    "footer",
)


def block_of(text: str, name: str) -> str:
    match = re.search(
        rf"<!-- BEGIN:GENERATED:{name} -->\n(.*?)\n<!-- END:GENERATED:{name} -->",
        text,
        re.DOTALL,
    )
    assert match is not None, f"no generated block named {name!r}"
    return match.group(1)


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue
        rows.append(cells)
    return rows


# --------------------------------------------------------------------------
# markers and block rendering
# --------------------------------------------------------------------------


def test_build_writes_content_into_every_marker_block(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    code, out = run_build()
    assert code == 0
    assert "1 entry" in out

    text = tmp_catalogue.readme()
    for name in BLOCK_NAMES:
        begin = f"<!-- BEGIN:GENERATED:{name} -->"
        end = f"<!-- END:GENERATED:{name} -->"
        assert text.count(begin) == 1, name
        assert text.count(end) == 1, name
        body = block_of(text, name)
        assert body.strip(), name
        assert "placeholder" not in body, name


def test_build_preserves_every_marker_and_the_prose_around_them(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    code, _ = run_build()
    assert code == 0
    text = tmp_catalogue.readme()
    assert "# awesome-ai-security" in text
    assert "Trailing prose outside every block" in text
    assert "Scaffold README owned by the test suite." in text
    for name in BLOCK_NAMES:
        assert f"<!-- BEGIN:GENERATED:{name} -->" in text
        assert f"<!-- END:GENERATED:{name} -->" in text
    assert text.count("<!--") == 2 * len(BLOCK_NAMES)


def test_build_reports_a_missing_marker_by_name(tmp_catalogue: Sandbox) -> None:
    import scripts.build as build_module
    from scripts.build import apply_blocks, render_blocks

    stripped = re.sub(
        r"<!-- BEGIN:GENERATED:matrix -->\n.*?\n<!-- END:GENERATED:matrix -->",
        "no matrix markers here",
        README_SKELETON,
        flags=re.DOTALL,
    )
    with pytest.raises(SystemExit) as caught:
        apply_blocks(stripped, render_blocks([], build_module.load_schema()))
    assert "missing generated markers" in str(caught.value)
    assert "matrix" in str(caught.value)


def test_build_exits_when_the_readme_is_absent(
    tmp_catalogue: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scripts.build as build_module

    tmp_catalogue.readme_path.unlink()
    with pytest.raises(SystemExit, match="nothing to update"):
        build_module.main([])


# --------------------------------------------------------------------------
# idempotence and the no-build-timestamp rule
# --------------------------------------------------------------------------


def test_two_builds_are_byte_identical(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", tier=1)
    entry_factory("beta-entry", tier=2)
    assert run_build()[0] == 0
    first_readme = tmp_catalogue.readme_path.read_bytes()
    first_dist = tmp_catalogue.dist_path.read_bytes()

    assert run_build()[0] == 0
    assert tmp_catalogue.readme_path.read_bytes() == first_readme
    assert tmp_catalogue.dist_path.read_bytes() == first_dist


@pytest.mark.parametrize("fixed_date", ["2019-11-05", "2001-02-03"])
def test_generated_output_carries_no_build_clock(
    tmp_catalogue: Sandbox,
    entry_factory: Factory,
    run_build: Build,
    fixed_date: str,
) -> None:
    """The count block reflects the data's newest last_verified, not today.

    This is the rule that stops a CI drift check from flapping: a build
    timestamp stamped into the output would make every run differ from the
    committed file and the gate would always fail. Two runs over the same data
    must produce identical bytes, and the date shown must be the data's.
    """
    entry_factory("synthetic-entry", last_verified=fixed_date)
    assert run_build()[0] == 0
    first_readme = tmp_catalogue.readme_path.read_bytes()
    first_dist = tmp_catalogue.dist_path.read_bytes()

    assert run_build()[0] == 0
    assert tmp_catalogue.readme_path.read_bytes() == first_readme
    assert tmp_catalogue.dist_path.read_bytes() == first_dist

    assert block_of(tmp_catalogue.readme(), "count") == (
        f"**1** entry; last verified **{fixed_date}**."
    )
    assert today().isoformat() not in tmp_catalogue.readme()
    assert today().isoformat() not in tmp_catalogue.dist()


def test_the_count_block_tracks_the_newest_last_verified_in_the_data(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", last_verified="2001-02-03")
    entry_factory("beta-entry", last_verified="2019-11-05")
    entry_factory("gamma-entry", last_verified="2010-06-07")
    assert run_build()[0] == 0
    assert block_of(tmp_catalogue.readme(), "count") == (
        "**3** entries; last verified **2019-11-05**."
    )


def test_dist_payload_has_no_wall_clock_field(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    payload = tmp_catalogue.dist_json()
    assert set(payload) == {"generated_from", "schema_version", "count", "entries"}
    assert payload["schema_version"] == SCHEMA_VERSION
    assert "generated_on" not in payload
    assert "built_at" not in payload


def test_check_and_build_agree_on_a_clean_tree(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    code, out = run_build("--check")
    assert code == 0
    assert "up to date" in out
    assert "nothing written" in out


# --------------------------------------------------------------------------
# drift detection
# --------------------------------------------------------------------------


DRIFT_EDIT = "HAND EDITED INSIDE A GENERATED BLOCK"


def test_check_detects_a_hand_edit_inside_a_block(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    assert run_build("--check")[0] == 0

    text = tmp_catalogue.readme()
    marker = "<!-- BEGIN:GENERATED:footer -->\n"
    head, tail = text.split(marker, 1)
    tampered = head + marker + f"{DRIFT_EDIT}\n" + tail
    tmp_catalogue.write_readme(tampered)

    code, out = run_build("--check")
    assert code == 1
    assert DRIFT_EDIT in out
    assert "committed/README.md" in out
    assert "generated/README.md" in out
    # Only the removed side carries the injected line; a generator would never
    # produce it, which is precisely why the check must fail.
    assert f"-{DRIFT_EDIT}" in out
    assert f"+{DRIFT_EDIT}" not in out


def test_check_detects_a_deleted_generated_file(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    tmp_catalogue.dist_path.unlink()
    code, out = run_build("--check")
    assert code == 1
    assert "entries.json" in out
    assert "drift found" in out


def test_check_detects_a_changed_entry(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    entry_factory("synthetic-entry", tier=1)
    code, out = run_build("--check")
    assert code == 1
    assert "drift found" in out
    assert run_build()[0] == 0
    assert run_build("--check")[0] == 0


def test_dry_run_reports_drift_and_writes_nothing(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry")
    assert run_build("--quiet")[0] == 0
    before = tmp_catalogue.readme_path.read_bytes()
    entry_factory("second-entry")
    code, out = run_build("--dry-run")
    assert code == 1
    assert "dry run" in out
    assert tmp_catalogue.readme_path.read_bytes() == before


def test_check_never_writes_even_against_a_drifted_tree(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    """The hard guarantee: a failing --check must leave the tree byte-identical."""
    entry_factory("alpha-entry", tier=1)
    assert run_build()[0] == 0

    # Drift the README by hand and delete the dist output, so both artefacts
    # would differ from a fresh build.
    text = tmp_catalogue.readme()
    tmp_catalogue.write_readme(
        text.replace("Everything is graded", "Nothing is graded")
    )
    tmp_catalogue.dist_path.unlink()

    readme_before = tmp_catalogue.readme_path.read_bytes()
    dist_before = tmp_catalogue.bytes_of(tmp_catalogue.dist_path)
    assert dist_before is None

    assert run_build("--check")[0] == 1
    assert tmp_catalogue.readme_path.read_bytes() == readme_before
    assert tmp_catalogue.bytes_of(tmp_catalogue.dist_path) is None

    assert run_build("--check", "--quiet")[0] == 1
    assert tmp_catalogue.readme_path.read_bytes() == readme_before


def test_a_no_op_check_on_an_unbuilt_tree_reports_drift(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    code, out = run_build("--check")
    assert code == 1
    assert "drift found" in out
    assert not tmp_catalogue.dist_path.exists()


# --------------------------------------------------------------------------
# zero entries
# --------------------------------------------------------------------------


def test_empty_catalogue_builds_a_valid_readme_and_payload(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    code, out = run_build()
    assert code == 0
    assert "0 entries" in out

    text = tmp_catalogue.readme()
    assert "**0** entries; nothing verified yet." in block_of(text, "count")
    assert "The catalogue is empty." in block_of(text, "catalogue")
    assert "No entry has met the Tier 1 bar yet." in block_of(text, "tier1")

    payload = tmp_catalogue.dist_json()
    assert payload["count"] == 0
    assert payload["entries"] == []
    assert payload["generated_from"] == "data/entries"


def test_matrix_lists_all_fifteen_classes_with_zeroes(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    assert run_build()[0] == 0
    rows = table_rows(block_of(tmp_catalogue.readme(), "matrix"))
    assert rows[0] == ["Attack class", "T1", "T2", "T3", "Total"]
    body = rows[1:-1]
    total = rows[-1]
    assert len(body) == 15
    assert [r[0] for r in body] == list(ATTACK_CLASS_LABELS.values())
    assert all(r[1:] == ["0", "0", "0", "0"] for r in body)
    assert total == ["**Total**", "0", "0", "0", "0"]


def test_matrix_rows_follow_schema_order_with_a_partial_catalogue(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build, schema
) -> None:
    enum = list(schema["properties"]["attack_class"]["enum"])
    entry_factory("only-entry", attack_class="JAILBREAK", tier=2)
    assert run_build()[0] == 0
    rows = table_rows(block_of(tmp_catalogue.readme(), "matrix"))
    assert [r[0] for r in rows[1:-1]] == [ATTACK_CLASS_LABELS[name] for name in enum]
    jailbreak = rows[1 + enum.index("JAILBREAK")]
    assert jailbreak == ["Jailbreak", "0", "1", "0", "1"]
    assert rows[-1] == ["**Total**", "0", "1", "0", "1"]


def test_attack_class_labels_are_an_explicit_mapping() -> None:
    """Labels come from ATTACK_CLASS_LABELS, not from title-casing the enum.

    DATA_EXFILTRATION must render as "Data exfiltration", never "Data
    Exfiltration" or the raw enum value.
    """
    assert ATTACK_CLASS_LABELS["DATA_EXFILTRATION"] == "Data exfiltration"
    assert ATTACK_CLASS_LABELS["PROMPT_INJECTION_DIRECT"] == (
        "Prompt injection (direct)"
    )
    for enum_value, label in ATTACK_CLASS_LABELS.items():
        assert enum_value not in label, label
        assert label, enum_value
        assert not label.isupper()


def test_no_raw_enum_value_leaks_into_a_heading(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry", attack_class="DATA_EXFILTRATION", tier=2)
    assert run_build()[0] == 0
    text = tmp_catalogue.readme()
    heading = [
        line
        for line in block_of(text, "catalogue").splitlines()
        if line.startswith("###")
    ]
    assert heading == ["### Data exfiltration"]
    assert "DATA_EXFILTRATION" not in block_of(text, "catalogue")
    assert "DATA_EXFILTRATION" not in block_of(text, "matrix")


# --------------------------------------------------------------------------
# tier badges
# --------------------------------------------------------------------------


def test_tier_badge_is_one_string_everywhere(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", tier=1)
    entry_factory("beta-entry", tier=2)
    entry_factory("gamma-entry", tier=3)
    assert run_build()[0] == 0
    text = tmp_catalogue.readme()

    legend = block_of(text, "tier-legend")
    for tier in (1, 2, 3):
        badge = tier_badge(tier)
        assert badge in legend, badge

    tier1_rows = table_rows(block_of(text, "tier1"))
    catalogue_rows = table_rows(block_of(text, "catalogue"))

    assert tier1_rows[0][0] == "Tier"
    assert tier1_rows[1][0] == tier_badge(1) == f"`T1 [{TIER_PIPS[1]}]`"
    assert {row[0] for row in catalogue_rows[1:]} == {
        tier_badge(1),
        tier_badge(2),
        tier_badge(3),
    }
    # The legend quotes exactly the same badge string, not a re-typed copy.
    for tier in (1, 2, 3):
        legend_line = next(
            line for line in legend.splitlines() if f"Tier {tier} -" in line
        )
        assert f"Badge {tier_badge(tier)}." in legend_line


def test_tier_badge_pips_are_distinct_per_tier() -> None:
    badges = [tier_badge(tier) for tier in (1, 2, 3)]
    assert len(set(badges)) == 3
    assert badges == ["`T1 [===]`", "`T2 [==-]`", "`T3 [=-]`"]
    assert tier_badge(0) == "`T0 [---]`"
    assert tier_badge(9) == "`T0 [---]`"


# --------------------------------------------------------------------------
# tier 1 ordering
# --------------------------------------------------------------------------


def test_tier1_block_orders_newest_disclosure_first(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("oldest-entry", tier=1, date="2019-01-05")
    entry_factory("middle-entry", tier=1, date="2020-06-15")
    entry_factory("newest-entry", tier=1, date="2021-11-30")
    assert run_build()[0] == 0

    rows = table_rows(block_of(tmp_catalogue.readme(), "tier1"))
    assert rows[0] == ["Tier", "Entry", "Date", "Target", "Primary source"]
    assert [row[2] for row in rows[1:]] == ["2021-11-30", "2020-06-15", "2019-01-05"]
    assert "newest-entry" in rows[1][1]
    assert "oldest-entry" in rows[3][1]


def test_tier1_block_ties_break_by_id(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("zulu-entry", tier=1, date="2020-01-01")
    entry_factory("alpha-entry", tier=1, date="2020-01-01")
    assert run_build()[0] == 0
    rows = table_rows(block_of(tmp_catalogue.readme(), "tier1"))
    assert "alpha-entry" in rows[1][1]
    assert "zulu-entry" in rows[2][1]


def test_tier1_block_excludes_other_tiers(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("tier-two-entry", tier=2)
    entry_factory("tier-three-entry", tier=3)
    assert run_build()[0] == 0
    assert "No entry has met the Tier 1 bar yet." in block_of(
        tmp_catalogue.readme(), "tier1"
    )


def test_month_only_dates_sort_against_full_dates(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("month-entry", tier=1, date="2020-03")
    entry_factory("day-entry", tier=1, date="2020-03-15")
    assert run_build()[0] == 0
    rows = table_rows(block_of(tmp_catalogue.readme(), "tier1"))
    assert [row[2] for row in rows[1:]] == ["2020-03-15", "2020-03"]


def test_tier1_row_links_entry_to_page_and_source_to_primary(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    """Title points at the detail page; the source column picks primary_url.

    Both columns used to carry the same link, which made the source column
    redundant and left the entry's own page unreachable from the table.
    """
    entry_factory(
        "beta-entry",
        tier=1,
        sources=[
            secondary_source("beta-entry"),
            {
                "url": "https://example.invalid/beta-entry/advisory",
                "kind": "primary",
                "title": "Primary",
            },
        ],
    )
    entry_factory("gamma-entry", tier=1)
    assert run_build()[0] == 0
    rows = table_rows(block_of(tmp_catalogue.readme(), "tier1"))[1:]
    assert len(rows) == 2
    # Entry column -> the generated detail page for that id.
    assert rows[0][1] == (
        "[Synthetic test entry about example-product](docs/entries/beta-entry.md)"
    )
    # Primary source column -> the primary URL, not the secondary listed first.
    assert rows[0][4] == (
        "[example.invalid](https://example.invalid/beta-entry/advisory)"
    )
    assert "gamma-entry" in rows[1][1]
    assert rows[1][4].startswith("[example.invalid](")


# --------------------------------------------------------------------------
# dist payload
# --------------------------------------------------------------------------


def test_dist_entries_are_sorted_and_carry_a_permalink(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("zulu-entry")
    entry_factory("alpha-entry")
    assert run_build()[0] == 0
    payload = tmp_catalogue.dist_json()
    assert [e["id"] for e in payload["entries"]] == ["alpha-entry", "zulu-entry"]
    assert payload["entries"][0]["_permalink"] == "docs/entries/alpha-entry.md"
    assert payload["count"] == 2


def test_dist_entries_follow_schema_field_order(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build, schema
) -> None:
    entry_factory("synthetic-entry")
    assert run_build()[0] == 0
    order = list(schema["properties"])
    record = tmp_catalogue.dist_json()["entries"][0]
    keys = [key for key in record if key != "_permalink"]
    assert keys[: len(order)] == [key for key in order if key in record]


def test_dist_output_is_ascii_only(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry", target="example-produkt mit Umlauten: f\xfcr")
    assert run_build()[0] == 0
    raw = tmp_catalogue.dist()
    assert raw.isascii()
    assert "f\\u00fcr" in raw
    assert "\xfc" not in raw


def test_readme_renders_non_ascii_as_entities(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("synthetic-entry", title="A synthetic caf\xe9 flavoured entry")
    assert run_build()[0] == 0
    text = tmp_catalogue.readme()
    assert text.isascii()
    assert "caf&#233;" in text


# --------------------------------------------------------------------------
# formatting helpers
# --------------------------------------------------------------------------


def test_md_cell_escapes_pipes_and_backslashes() -> None:
    from scripts.build import md_cell

    assert md_cell("a|b") == "a\\|b"
    assert md_cell("back\\slash") == "back\\\\slash"
    assert md_cell("plain") == "plain"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("plain", "plain"),
        ("line\nbreak", "line break"),
        ("tab\there", "tab here"),
        ("  padded  ", "padded"),
        ("caf\xe9", "caf&#233;"),
        ("\u4e2d\u6587", "&#20013;&#25991;"),
    ],
)
def test_ascii_text_collapses_whitespace_and_escapes_non_ascii(
    value: str, expected: str
) -> None:
    from scripts.build import ascii_text

    assert ascii_text(value) == expected


def test_md_link_percent_encodes_spaces_and_parens() -> None:
    from scripts.build import md_link

    link = md_link("A title", "https://example.invalid/a b/(c)")
    assert link == "[A title](https://example.invalid/a%20b/%28c%29)"


def test_md_table_emits_a_header_and_alignment_row() -> None:
    lines = md_table(["A", "B"], [["1", "2"]])
    assert lines == ["| A | B |", "| --- | --- |", "| 1 | 2 |"]


def test_date_sort_key_orders_missing_parts_first() -> None:
    from scripts.build import date_sort_key

    assert date_sort_key("2020-03-15") > date_sort_key("2020-03")
    assert date_sort_key("2020-03") > date_sort_key("")
    assert date_sort_key("2019-12-31") < date_sort_key("2020-01-01")


def test_source_label_strips_the_scheme_and_path() -> None:
    from scripts.build import source_label

    assert source_label("https://example.invalid/a/b") == "example.invalid"
    assert source_label("") == ""


# --------------------------------------------------------------------------
# real catalogue invariants
# --------------------------------------------------------------------------


def test_the_committed_readme_matches_the_committed_entries(
    run_build: Build, real_entries: list[Any]
) -> None:
    """The shipped README must already be in sync with data/entries.

    This runs against the real tree, so it is the one place a genuine drift in
    the repository is caught.
    """
    code, out = run_build("--check")
    assert code == 0, out


def test_the_committed_dist_payload_matches_the_entry_count(
    run_build: Build, real_entries: list[Any]
) -> None:
    assert run_build("--check")[0] == 0
    payload = json.loads(Path("dist/entries.json").read_text(encoding="utf-8"))
    assert payload["count"] == len(real_entries)


def test_real_entries_all_load_and_carry_an_id(real_entries: list[Any]) -> None:
    assert [e.id for e in real_entries] == sorted(e.id for e in real_entries)
    for entry in real_entries:
        assert entry.id == entry.path.stem
        assert entry.tier in (1, 2, 3)
        assert entry.attack_class
        assert entry.sources
