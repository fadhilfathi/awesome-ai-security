"""Render one markdown detail page per catalogue entry.

`data/entries/*.yml` stays the single source of truth. This module turns each
entry into a readable page under `docs/entries/<id>.md` so the README can stay a
scannable index while the depth of an entry -- summary, impact, mitigation,
sources -- stays one click away.

The pages are generated. `scripts/build.py` owns writing them and sweeping away
pages whose entry has been deleted, because an orphaned page is worse than a
missing one: it keeps a retired entry readable and it makes the catalogue look
larger than it is.

Nothing here is computed by hand and nothing is stamped with a build clock, so
running the build twice produces byte-identical pages and `--check` is a real
gate rather than a formality.

Formatting helpers (`tier_badge`, `ATTACK_CLASS_LABELS`, the `md_*` family) are
imported from `scripts.build` so a page and the README cannot drift apart in
how they spell a tier or an attack class.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from build import (  # noqa: E402  (path bootstrap must run first)
    ATTACK_CLASS_LABELS,
    PAGE_REL_DIR,
    TIER_LABELS,
    entry_file_rel_path,
    md_cell,
    md_link,
    md_table,
    tier_badge,
)
from entries import Entry  # noqa: E402

#: README.md section every page links back to.
CATALOGUE_ANCHOR = "README.md#full-catalogue"

_NOT_RECORDED = "Not recorded in the entry file."


def page_rel_path(entry: Entry) -> str:
    """Repository-relative path of an entry's page, e.g. ``docs/entries/x.md``."""
    return f"{PAGE_REL_DIR}/{entry.id}.md"


def page_file_name(entry: Entry) -> str:
    return f"{entry.id}.md"


# --------------------------------------------------------------------------
# formatting helpers
# --------------------------------------------------------------------------


def _ascii_block(value: Any) -> str:
    """Non-ASCII becomes a numeric reference; line breaks are preserved.

    `ascii_text()` from build.py collapses whitespace, which is right for a
    table cell and wrong for body prose: an entry's summary is several
    paragraphs, and flattening it into one line would lose the structure the
    author wrote.
    """
    return "".join(ch if ord(ch) < 128 else f"&#{ord(ch)};" for ch in str(value))


def _paragraphs(value: Any, fallback: str = _NOT_RECORDED) -> list[str]:
    """Body prose as markdown paragraphs, blank-line separated."""
    raw = _ascii_block(value).strip()
    if not raw:
        return [fallback]
    blocks = [" ".join(part.split()) for part in raw.split("\n\n")]
    return [block for block in blocks if block] or [fallback]


def _tier_line(entry: Entry) -> str:
    label = TIER_LABELS.get(entry.tier, "Ungraded")
    return f"{tier_badge(entry.tier)} **Tier {entry.tier} - {label}**"


def _metadata_rows(entry: Entry) -> list[list[str]]:
    rows = [
        ["Id", f"`{md_cell(entry.id)}`"],
        ["Tier", _tier_line(entry)],
        [
            "Attack class",
            md_cell(ATTACK_CLASS_LABELS.get(entry.attack_class, entry.attack_class)),
        ],
        ["Target", md_cell(entry.get("target", ""))],
        ["Disclosure date", md_cell(entry.get("date", ""))],
        ["Last verified", md_cell(entry.last_verified or "")],
    ]
    if entry.cve:
        rows.append(["CVE", md_cell(", ".join(entry.cve))])
    return rows


def _source_line(kind: str, source: dict[str, Any]) -> str:
    """One bullet: the evidence kind, then the source title as the link text."""
    url = str(source.get("url") or "")
    title = str(source.get("title") or url or "Untitled source")
    rendered = md_link(title, url) if url else md_cell(title)
    return f"- **{kind.upper()}** - {rendered}"


def _source_lines(entry: Entry) -> list[str]:
    """Primary sources first, then secondary, each in the order the file lists."""
    lines = [_source_line("primary", source) for source in entry.primary_sources]
    lines += [_source_line("secondary", source) for source in entry.secondary_sources]
    if not lines:
        return ["- SECONDARY - no source is recorded for this entry yet."]
    return lines


# --------------------------------------------------------------------------
# page rendering
# --------------------------------------------------------------------------


def render_page(entry: Entry) -> str:
    """The full markdown text of one entry's page."""
    lines = [
        f"# {md_cell(entry.title)}",
        "",
        _tier_line(entry),
        "",
    ]
    lines += md_table(["Field", "Value"], _metadata_rows(entry))
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines += _paragraphs(entry.get("summary", ""))
    lines.append("")
    lines.append("## Impact")
    lines.append("")
    lines += _paragraphs(entry.get("impact", ""))
    lines.append("")
    lines.append("## Mitigation")
    lines.append("")
    lines += _paragraphs(entry.get("mitigation", ""))
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines += _source_lines(entry)
    lines.append("")
    lines.append(
        f"Generated from `{entry_file_rel_path(entry)}` by `scripts/build.py`. "
        "Never hand-edit this page: change the entry file and rebuild."
    )
    lines.append("")
    lines.append(
        # Pages sit in docs/entries/, so a sibling doc is one level up. Going
        # ../../docs/ would resolve outside the repo and render as a dead link.
        f"Back to the [catalogue](../../{CATALOGUE_ANCHOR}), "
        "to [what the tiers mean](../TIERS.md), "
        f"or to the [entry file](../../{entry_file_rel_path(entry)})."
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def render_pages(entries: list[Entry]) -> dict[str, str]:
    """Every page, keyed by file name, in sorted order so output is stable."""
    return {
        page_file_name(entry): render_page(entry)
        for entry in sorted(entries, key=lambda e: e.id)
    }
