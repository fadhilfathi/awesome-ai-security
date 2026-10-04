"""Detail-page and SVG-matrix tests.

Two guarantees matter here beyond "the file exists":

1. Deleting an entry must delete its page. A page for a deleted id keeps a
   retired finding readable and inflates the apparent size of the catalogue.
2. ``--check`` must notice a hand-edited page and must never repair it. A check
   that quietly rewrites what it is checking is not a gate.

Everything runs inside the ``tmp_catalogue`` sandbox, so nothing here can touch
the real ``docs/entries`` or the committed README.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from conftest import Sandbox, secondary_source

from scripts.build import ATTACK_CLASS_LABELS

Factory = Callable[..., Path]
Build = Callable[..., tuple[int, str]]

SVG_NS = "{http://www.w3.org/2000/svg}"

#: Page section headings, in the order a page must present them.
REQUIRED_SECTIONS = ("## Summary", "## Impact", "## Mitigation", "## Sources")


def block_of(text: str, name: str) -> str:
    match = re.search(
        rf"<!-- BEGIN:GENERATED:{name} -->\n(.*?)\n<!-- END:GENERATED:{name} -->",
        text,
        re.DOTALL,
    )
    assert match is not None, f"no generated block named {name!r}"
    return match.group(1)


def row_span(svg: str, label: str) -> list[str]:
    """Every emitted line belonging to one labelled row.

    A row is the class label plus the three cells drawn under it, so this is
    what tells a populated row apart from an empty one.
    """
    lines = svg.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if f">{label}</text>" in line), None
    )
    assert start is not None, f"no row labelled {label!r} in the SVG"
    span = []
    for line in lines[start + 1 :]:
        if '<text class="m-label"' in line:
            break
        span.append(line)
    cells = [line for line in span if "<rect " in line]
    assert len(cells) == 3, f"row {label!r} drew {len(cells)} cells, expected 3"
    return span


def row_counts(svg: str, label: str) -> list[str]:
    """The count numerals printed in one row, in column order."""
    return re.findall(r">(\d+)</text>", "\n".join(row_span(svg, label)))


# --------------------------------------------------------------------------
# page generation
# --------------------------------------------------------------------------


def test_one_page_is_written_per_entry(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    entry_factory("zulu-entry", attack_class="JAILBREAK")
    assert run_build()[0] == 0

    assert sorted(p.name for p in tmp_catalogue.pages_dir.glob("*.md")) == [
        "alpha-entry.md",
        "zulu-entry.md",
    ]


def test_a_page_carries_its_title_badge_metadata_and_sections_in_order(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory(
        "beta-entry",
        title="A synthetic entry with a distinctive title",
        tier=3,
        attack_class="DATA_EXFILTRATION",
        cve=["CVE-2026-1111", "CVE-2026-2222"],
        last_verified="2019-11-05",
    )
    run_build()

    page = tmp_catalogue.page("beta-entry")
    assert page.splitlines()[0] == "# A synthetic entry with a distinctive title"
    assert page.splitlines()[2] == "`T3 [=-]` **Tier 3 - Theoretical**"

    positions = [page.index(heading) for heading in REQUIRED_SECTIONS]
    assert positions == sorted(positions), "sections are out of order"

    for row in (
        "| Id | `beta-entry` |",
        "| Tier | `T3 [=-]` **Tier 3 - Theoretical** |",
        "| Attack class | Data exfiltration |",
        "| Last verified | 2019-11-05 |",
        "| CVE | CVE-2026-1111, CVE-2026-2222 |",
    ):
        assert row in page, row


def test_a_page_omits_the_cve_row_when_no_cve_is_recorded(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    assert "| CVE |" not in tmp_catalogue.page("alpha-entry")


def test_every_relative_link_on_a_page_resolves_to_a_real_path(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    """Back links must resolve, not merely look like plausible paths.

    A link can be well-formed markdown and still point nowhere: the page
    lives in docs/entries/, so ../../docs/TIERS.md escapes the repo root and
    renders as a dead link on GitHub. This asserts the resolved target
    exists on disk.
    """
    entry_factory("alpha-entry")
    run_build()

    page_path = tmp_catalogue.pages_dir / "alpha-entry.md"
    page = page_path.read_text(encoding="utf-8")

    targets = re.findall(r"\]\(([^)]+)\)", page)
    assert targets, "the page should link somewhere"
    for raw in targets:
        target = raw.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (page_path.parent / target).resolve()
        assert resolved.exists(), f"{raw} resolves outside the repo: {resolved}"


def test_sources_are_tagged_primary_or_secondary_with_titles_as_link_text(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory(
        "alpha-entry",
        sources=[
            {
                "url": "https://example.invalid/alpha/advisory",
                "kind": "primary",
                "title": "Synthetic vendor advisory",
            },
            {
                "url": "https://example.invalid/alpha/coverage",
                "kind": "secondary",
                "title": "Synthetic news coverage",
            },
        ],
    )
    run_build()

    page = tmp_catalogue.page("alpha-entry")
    assert (
        "- **PRIMARY** - "
        "[Synthetic vendor advisory](https://example.invalid/alpha/advisory)" in page
    )
    assert (
        "- **SECONDARY** - "
        "[Synthetic news coverage](https://example.invalid/alpha/coverage)" in page
    )
    assert page.index("**PRIMARY**") < page.index("**SECONDARY**")


def test_a_secondary_source_is_not_labelled_primary(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", sources=[secondary_source("alpha-entry")])
    run_build()

    page = tmp_catalogue.page("alpha-entry")
    assert "**SECONDARY**" in page
    assert "**PRIMARY**" not in page


# --------------------------------------------------------------------------
# orphan removal
# --------------------------------------------------------------------------


def test_deleting_an_entry_deletes_its_page(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    doomed = entry_factory("doomed-entry")
    entry_factory("kept-entry")
    run_build()
    page = tmp_catalogue.pages_dir / "doomed-entry.md"
    assert page.exists()

    doomed.unlink()
    assert run_build()[0] == 0

    assert not page.exists()
    assert [p.name for p in tmp_catalogue.pages_dir.glob("*.md")] == ["kept-entry.md"]
    assert "doomed-entry.md" not in tmp_catalogue.readme()


def test_check_reports_an_orphaned_page_without_deleting_it(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry = entry_factory("alpha-entry")
    run_build()
    entry.unlink()

    code, out = run_build("--check")

    assert code == 1
    assert "alpha-entry.md" in out
    assert (tmp_catalogue.pages_dir / "alpha-entry.md").exists()


# --------------------------------------------------------------------------
# drift detection, and the no-write guarantee
# --------------------------------------------------------------------------


def test_check_detects_a_missing_page(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()
    (tmp_catalogue.pages_dir / "alpha-entry.md").unlink()

    assert run_build("--check")[0] == 1


def test_check_detects_a_hand_edited_page_and_writes_nothing(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()
    page = tmp_catalogue.pages_dir / "alpha-entry.md"
    page.write_text(
        page.read_text(encoding="utf-8") + "\nHAND EDITED PAGE\n",
        encoding="utf-8",
        newline="\n",
    )
    tampered = page.read_bytes()

    code, out = run_build("--check")

    assert code == 1
    assert "docs/entries/alpha-entry.md" in out
    # The hard part: --check reports, it does not repair.
    assert page.read_bytes() == tampered
    assert run_build("--check")[0] == 1


def test_check_detects_a_missing_svg(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()
    tmp_catalogue.svg_path.unlink()

    assert run_build("--check")[0] == 1


def test_a_clean_tree_passes_check_over_pages_readme_and_dist(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    assert run_build("--check")[0] == 0


# --------------------------------------------------------------------------
# the README entry index
# --------------------------------------------------------------------------


def test_the_index_links_every_entry_to_its_page(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", tier=2)
    entry_factory("beta-entry", tier=1)
    run_build()

    index = block_of(tmp_catalogue.readme(), "entry-index")
    assert "(docs/entries/alpha-entry.md)" in index
    assert "(docs/entries/beta-entry.md)" in index


def test_the_index_groups_by_tier_with_tier_one_first(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("tier-three", tier=3)
    entry_factory("tier-two", tier=2)
    entry_factory("tier-one", tier=1)
    run_build()

    index = block_of(tmp_catalogue.readme(), "entry-index")
    order = [
        index.index(f"docs/entries/tier-{name}.md") for name in ("one", "two", "three")
    ]
    assert order == sorted(order), "the index is not ordered Tier 1, 2, 3"


def test_the_index_never_leaks_a_raw_enum_value(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", attack_class="CREDENTIAL_EXPOSURE")
    run_build()

    index = block_of(tmp_catalogue.readme(), "entry-index")
    assert "Credential exposure" in index
    assert "CREDENTIAL_EXPOSURE" not in index


# --------------------------------------------------------------------------
# empty catalogue
# --------------------------------------------------------------------------


def test_an_empty_catalogue_writes_no_pages_and_says_so(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    assert run_build()[0] == 0

    pages = tmp_catalogue.pages_dir
    assert not pages.exists() or list(pages.glob("*.md")) == []

    index = block_of(tmp_catalogue.readme(), "entry-index")
    assert "No entry pages yet." in index
    assert "docs/entries/" not in index


def test_an_empty_catalogue_still_passes_check(
    tmp_catalogue: Sandbox, run_build: Build
) -> None:
    run_build()
    assert run_build("--check")[0] == 0


# --------------------------------------------------------------------------
# determinism
# --------------------------------------------------------------------------


def test_two_builds_are_byte_identical_across_pages_readme_svg_and_dist(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", tier=1)
    entry_factory("zulu-entry", attack_class="JAILBREAK", tier=3)
    run_build()

    snapshot = {
        path: path.read_bytes()
        for path in [
            tmp_catalogue.readme_path,
            tmp_catalogue.dist_path,
            tmp_catalogue.svg_path,
            *sorted(tmp_catalogue.pages_dir.glob("*.md")),
        ]
    }

    run_build()

    assert {p: p.read_bytes() for p in snapshot} == snapshot


def test_pages_carry_no_build_clock(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    from scripts.entries import today

    entry_factory("alpha-entry", last_verified="2019-11-05")
    run_build()

    raw = tmp_catalogue.page("alpha-entry")
    assert today().isoformat() not in raw
    assert "2019-11-05" in raw


# --------------------------------------------------------------------------
# the SVG matrix
# --------------------------------------------------------------------------


def test_the_matrix_svg_is_written_and_referenced_from_the_readme(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    assert tmp_catalogue.svg_path.exists()
    assert "![Attack class by evidence tier](docs/attack-matrix.svg)" in (
        block_of(tmp_catalogue.readme(), "matrix")
    )


def test_the_svg_is_well_formed_xml(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    root = ET.fromstring(tmp_catalogue.svg_path.read_text(encoding="utf-8"))
    assert root.tag == f"{SVG_NS}svg"


def test_the_svg_has_no_script_and_no_remote_reference(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    raw = tmp_catalogue.svg_path.read_text(encoding="utf-8")
    assert "<script" not in raw
    # The only permitted URL is the SVG namespace, which is an identifier.
    urls = re.findall(r"https?://[^\s\"'<>]+", raw)
    assert urls == ["http://www.w3.org/2000/svg"]
    assert "@import" not in raw
    assert "<style" in raw


def test_the_svg_carries_a_title_a_desc_and_the_img_role(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    root = ET.fromstring(tmp_catalogue.svg_path.read_text(encoding="utf-8"))
    assert root.get("role") == "img"
    assert root.find(f"{SVG_NS}title") is not None
    desc = root.find(f"{SVG_NS}desc")
    assert desc is not None and desc.text


def test_the_svg_labels_every_attack_class(
    tmp_catalogue: Sandbox, run_build: Build, attack_classes: list[str]
) -> None:
    assert run_build()[0] == 0

    raw = tmp_catalogue.svg_path.read_text(encoding="utf-8")
    for attack_class in attack_classes:
        assert ATTACK_CLASS_LABELS[attack_class] in raw, attack_class


def test_the_svg_keeps_empty_rows_visible(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    raw = tmp_catalogue.svg_path.read_text(encoding="utf-8")
    # Three cells per row, fifteen rows, all of them present in the markup.
    assert raw.count('class="m-label"') == 15
    assert raw.count("<rect ") == 45


def test_a_populated_row_and_an_empty_row_render_differently(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry", attack_class="JAILBREAK", tier=2)
    run_build()

    svg = tmp_catalogue.svg_path.read_text(encoding="utf-8")
    populated_cells = [ln for ln in row_span(svg, "Jailbreak") if "<rect " in ln]
    empty_cells = [
        ln for ln in row_span(svg, "Prompt injection (direct)") if "<rect " in ln
    ]
    filled = [cell for cell in populated_cells if 'fill="none"' not in cell]
    assert len(filled) == 1, "exactly one cell of the Jailbreak row is documented"

    populated_cell, empty_cell = filled[0], empty_cells[0]
    # The teeth: a documented cell and an undocumented one must not be the
    # same markup, which is the claim the whole design rests on.
    assert populated_cell != empty_cell
    assert 'fill="#ef8a62"' in populated_cell
    assert "stroke-dasharray" not in populated_cell
    assert 'fill="none"' in empty_cell
    assert "stroke-dasharray" in empty_cell
    # A zero cell carries no numeral, so it cannot read as "a small count".
    assert row_counts(svg, "Jailbreak") == ["1"]
    assert row_counts(svg, "Prompt injection (direct)") == []


def test_the_svg_survives_an_attack_class_label_needing_xml_escaping(
    tmp_catalogue: Sandbox,
    entry_factory: Factory,
    run_build: Build,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.build as build_module

    monkeypatch.setitem(
        build_module.ATTACK_CLASS_LABELS, "JAILBREAK", "Jailbreak <b>bold</b>"
    )
    entry_factory("alpha-entry")
    run_build()

    raw = tmp_catalogue.svg_path.read_text(encoding="utf-8")
    assert "Jailbreak &lt;b&gt;bold&lt;/b&gt;" in raw
    ET.fromstring(raw)


def test_the_svg_is_ascii_only(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    raw = tmp_catalogue.svg_path.read_bytes()
    raw.decode("ascii")


def test_the_svg_scales_with_a_viewbox_rather_than_forcing_a_width(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    root = ET.fromstring(tmp_catalogue.svg_path.read_text(encoding="utf-8"))
    assert root.get("viewBox"), "a viewBox is what makes the picture scale"
    view_w, view_h = (float(v) for v in root.get("viewBox").split()[2:])
    assert view_w == float(root.get("width"))
    assert view_h == float(root.get("height"))


def test_the_committed_tree_has_a_matching_svg_and_pages(run_build: Build) -> None:
    """The shipped docs must already be in sync with data/entries."""
    code, out = run_build("--check")
    assert code == 0, out


def test_the_dist_permalink_points_at_the_generated_page(
    tmp_catalogue: Sandbox, entry_factory: Factory, run_build: Build
) -> None:
    entry_factory("alpha-entry")
    run_build()

    payload: dict[str, Any] = json.loads(tmp_catalogue.dist())
    assert payload["entries"][0]["_permalink"] == "docs/entries/alpha-entry.md"
