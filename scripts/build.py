"""Generate the README generated-blocks, dist/entries.json and entry pages.

data/entries/*.yml is the single source of truth. Everything this script emits
is derived from those files: no numbers are typed by hand and no build time is
stamped into the output, so running the build twice is byte-identical and
`--check` is a meaningful CI gate.

Outputs, all generated and none of them hand-edited:

* README.md -- every block between a BEGIN/END:GENERATED marker.
* dist/entries.json -- the same data, machine readable.
* docs/attack-matrix.svg -- the tier matrix, drawn from the counts.
* docs/entries/<id>.md -- one detail page per entry, swept when an id goes away.

Usage:
    python scripts/build.py            regenerate every generated file
    python scripts/build.py --check    fail if the committed output has drifted
    python scripts/build.py --dry-run  show the diff, write nothing
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from entries import (  # noqa: E402  (path bootstrap must run first)
    DIST_PATH,
    README_PATH,
    Entry,
    load_all_entries,
    load_schema,
)

# scripts/build_pages.py imports the helpers and constants defined below, so
# main() imports it lazily: a module-level import in both directions is
# circular.

SCHEMA_VERSION = 1
ENTRY_REL_DIR = "data/entries"
PAGE_REL_DIR = "docs/entries"
PAGE_GLOB = "docs/entries/*.md"

#: Repository root. Patched by the test fixtures alongside README_PATH and
#: DIST_PATH, so every generated path is derived from it rather than captured
#: at import time.
REPO_ROOT = _SCRIPTS_DIR.parent
SVG_REL_PATH = "docs/attack-matrix.svg"


def svg_path() -> Path:
    return REPO_ROOT / SVG_REL_PATH


def pages_dir() -> Path:
    return REPO_ROOT / PAGE_REL_DIR


_BLOCK_RE = re.compile(
    r"(?P<begin><!-- BEGIN:GENERATED:(?P<name>[A-Za-z0-9_-]+) -->)"
    r"(?P<body>.*?)"
    r"(?P<end><!-- END:GENERATED:(?P=name) -->)",
    re.DOTALL,
)


# Human-readable names for every attack_class enum value. Written out on
# purpose: title-casing the raw enum produces things like "Tool Poisoning"
# at best and "Data Exfiltration" instead of "Data exfiltration" at worst.
ATTACK_CLASS_LABELS: dict[str, str] = {
    "PROMPT_INJECTION_DIRECT": "Prompt injection (direct)",
    "PROMPT_INJECTION_INDIRECT": "Prompt injection (indirect)",
    "TOOL_POISONING": "Tool poisoning",
    "AGENT_PRIVILEGE_ABUSE": "Agent privilege abuse",
    "DATA_EXFILTRATION": "Data exfiltration",
    "SUPPLY_CHAIN_PACKAGE": "Supply chain (package)",
    "SUPPLY_CHAIN_MODEL": "Supply chain (model)",
    "CODE_ASSISTANT_ABUSE": "Code assistant abuse",
    "TRAINING_DATA_POISONING": "Training data poisoning",
    "MODEL_THEFT_EXTRACTION": "Model theft and extraction",
    "JAILBREAK": "Jailbreak",
    "INSECURE_OUTPUT_HANDLING": "Insecure output handling",
    "CREDENTIAL_EXPOSURE": "Credential exposure",
    "DENIAL_OF_SERVICE": "Denial of service",
    "OTHER": "Other",
}

# One badge style for every table in the document: a filled pip count that
# reads at a glance and stays legible inside a GitHub table cell.
TIER_LABELS: dict[int, str] = {
    1: "Confirmed in the wild",
    2: "Demonstrated",
    3: "Theoretical",
}
TIER_CRITERIA: dict[int, str] = {
    1: (
        "A real system was affected, and a vendor advisory, postmortem, or "
        "CVE record states the finding."
    ),
    2: (
        "The researcher reproduced the attack against a real build or model, "
        "but no occurrence outside a controlled setting is on record."
    ),
    3: ("The attack is argued from prior work; no working demonstration is published."),
}
TIER_PIPS: dict[int, str] = {1: "===", 2: "==-", 3: "=-"}


# --------------------------------------------------------------------------
# SVG matrix
# --------------------------------------------------------------------------

# The matrix encodes TIER in the cell fill and COUNT in the numeral. That split
# is deliberate:
#
# * Tier is the categorical, urgent axis ("what is real versus what is only
#   argued"), so it gets the colour ramp: tier 1 is the darkest fill, tier 3
#   the palest. The ramp is a fixed three-stop sequence keyed on the tier, never
#   on the count, so a class with fifty tier-3 entries cannot out-shout a class
#   with one tier-1 entry. Urgency does not scale with how often something was
#   filed.
# * Count is the magnitude axis, so it gets a numeral inside the cell: exact,
#   greppable, and it survives being copied out of the picture. A lightness ramp
#   for counts would need a colour-scale legend and would rescale every time an
#   entry was added.
#
# A count of zero means "nothing filed here yet", not "this is rare", so it is
# drawn as an unfilled cell with a dashed hairline and no numeral. An empty box
# cannot be misread as a small value the way a pale fill can.
#
# The file is standalone by requirement: no script, no remote reference, no
# external stylesheet. The only `<style>` is inline and the only URL anywhere in
# it is the SVG namespace declaration, which is an identifier, not a fetch.

_TIER_FILLS = {1: "#b2182b", 2: "#ef8a62", 3: "#67a9cf"}
_ZERO_CELL_FILL = "none"
_CELL_STROKE = "#24292f"
_HAIRLINE_STROKE = "#8c959f"
_INK = "#24292f"
_MUTED_INK = "#57606a"

_SVG_CELL = 30.0
_SVG_ROW = 24.0
_SVG_LABEL_W = 210.0
_SVG_HEAD_H = 34.0
_SVG_PAD = 10.0
_SVG_TOTAL_H = 26.0
_SVG_FONT = "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"


def _xml_escape(value: Any) -> str:
    """Escape text for XML content and attribute values."""
    text = str(value)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text.replace('"', "&quot;").replace("'", "&#39;")


def _num(value: float) -> str:
    """One decimal place at most, no trailing zeros, no locale separator.

    Every coordinate goes through here so the file is byte-identical on every
    machine: `repr()` would expose platform float formatting, and a bare
    f-string default would emit `30.0` where `30` reads better.
    """
    text = f"{value:.1f}"
    return text[:-2] if text.endswith(".0") else text


def render_matrix_svg(entries: list[Entry], schema: dict[str, Any]) -> str:
    """The attack-class-by-tier matrix as a self-contained SVG document."""
    enum = list(schema["properties"]["attack_class"]["enum"])
    counts: dict[tuple[str, int], int] = {}
    for entry in entries:
        key = (entry.attack_class, entry.tier)
        counts[key] = counts.get(key, 0) + 1

    width = _num(_SVG_PAD + _SVG_LABEL_W + _SVG_CELL * 3 + _SVG_PAD)
    height = _num(
        _SVG_PAD + _SVG_HEAD_H + _SVG_ROW * len(enum) + _SVG_TOTAL_H + _SVG_PAD
    )
    label_x = _num(_SVG_PAD + 4)
    grid_x = _SVG_PAD + _SVG_LABEL_W
    head_y = _num(_SVG_HEAD_H - 14)
    foot_y = _num(_SVG_HEAD_H + _SVG_ROW * len(enum) + 17)
    cell = _num(_SVG_CELL)
    row = _num(_SVG_ROW)

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' viewBox="0 0 {width} {height}" width="{width}" height="{height}"'
            ' role="img" aria-labelledby="matrix-title matrix-desc">'
        ),
        '<title id="matrix-title">Attack class by evidence tier</title>',
        (
            '<desc id="matrix-desc">A grid of the '
            f"{len(enum)} attack classes against the three evidence tiers. "
            "Each cell shows how many entries of that class sit at that tier. "
            "Cell colour encodes the tier, darkest for Tier 1, confirmed in "
            "the wild, and palest for Tier 3, theoretical. A cell with no "
            "numeral and only a dashed hairline border means nothing has been "
            "filed for that combination yet. The same figures are listed in "
            "the table below.</desc>"
        ),
        "<style>",
        f".m-label{{font:13px {_SVG_FONT};fill:{_INK}}}",
        f".m-head{{font:12px {_SVG_FONT};fill:{_MUTED_INK}}}",
        (
            f".m-num{{font:12px {_SVG_FONT};fill:#ffffff;text-anchor:middle;"
            "dominant-baseline:middle}"
        ),
        f".m-note{{font:11px {_SVG_FONT};fill:{_MUTED_INK}}}",
        "</style>",
    ]

    for index, tier in enumerate((1, 2, 3)):
        centre = _num(grid_x + index * _SVG_CELL + _SVG_CELL / 2)
        out.append(
            f'<text class="m-head" x="{centre}" y="{head_y}"'
            f' text-anchor="middle">T{tier}</text>'
        )

    for row_index, attack_class in enumerate(enum):
        y = _SVG_HEAD_H + row_index * _SVG_ROW
        label = ATTACK_CLASS_LABELS.get(attack_class, attack_class)
        out.append(
            f'<text class="m-label" x="{label_x}"'
            f' y="{_num(y + _SVG_ROW / 2 + 4)}">{_xml_escape(label)}</text>'
        )
        for index, tier in enumerate((1, 2, 3)):
            n = counts.get((attack_class, tier), 0)
            x = _num(grid_x + index * _SVG_CELL)
            if n:
                out.append(
                    f'<rect x="{x}" y="{_num(y)}" width="{cell}" height="{row}"'
                    f' fill="{_TIER_FILLS[tier]}" stroke="{_CELL_STROKE}"'
                    ' stroke-width="1"/>'
                )
                out.append(
                    f'<text class="m-num"'
                    f' x="{_num(grid_x + index * _SVG_CELL + _SVG_CELL / 2)}"'
                    f' y="{_num(y + _SVG_ROW / 2 + 1)}">{n}</text>'
                )
            else:
                # Not yet documented, not low: no fill and no numeral, so the
                # cell cannot be read as "a small amount of tier N".
                out.append(
                    f'<rect x="{x}" y="{_num(y)}" width="{cell}" height="{row}"'
                    f' fill="{_ZERO_CELL_FILL}" stroke="{_HAIRLINE_STROKE}"'
                    ' stroke-width="1" stroke-dasharray="2 2"/>'
                )

    totals = [sum(counts.get((cls, tier), 0) for cls in enum) for tier in (1, 2, 3)]
    out.append(
        f'<text class="m-note" x="{label_x}" y="{foot_y}">'
        f"{len(entries)} entries; dashed empty cells are not yet documented.</text>"
    )
    for index, n in enumerate(totals):
        centre = _num(grid_x + index * _SVG_CELL + _SVG_CELL / 2)
        out.append(
            f'<text class="m-head" x="{centre}" y="{foot_y}"'
            f' text-anchor="middle">{n}</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# formatting helpers
# --------------------------------------------------------------------------


def tier_badge(tier: int) -> str:
    """The one tier badge used in every generated table."""
    level = tier if tier in TIER_PIPS else 0
    pips = TIER_PIPS.get(level, "---")
    return f"`T{level} [{pips}]`"


def ascii_text(value: Any) -> str:
    """Collapse whitespace and keep the output pure ASCII.

    Non-ASCII characters become HTML numeric references, which GitHub renders
    back to the intended character while the committed file stays cp1252-safe.
    """
    text = " ".join(str(value).split())
    return "".join(ch if ord(ch) < 128 else f"&#{ord(ch)};" for ch in text)


def md_cell(value: Any) -> str:
    """Escape a value for use inside a markdown table cell."""
    text = ascii_text(value)
    return text.replace("\\", "\\\\").replace("|", "\\|")


def md_link(label: Any, url: str) -> str:
    href = ascii_text(url).replace(" ", "%20").replace("(", "%28").replace(")", "%29")
    return f"[{md_cell(label)}]({href})"


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """A GitHub-flavoured markdown table, header row and alignment row included."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def date_sort_key(value: str) -> tuple[int, int, int]:
    """Sort key for YYYY-MM or YYYY-MM-DD; missing parts sort as the 1st."""
    parts = value.split("-")
    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2][:2]) if len(parts) > 2 and parts[2] else 1
    except ValueError:
        return (0, 0, 0)
    return (year, month, day)


def entry_sort_key(entry: Entry) -> tuple[Any, ...]:
    """Newest disclosure first, ties broken by id so output is stable."""
    date = date_sort_key(str(entry.get("date", "")))
    return (tuple(-part for part in date), entry.id)


def primary_url(entry: Entry) -> str:
    urls = entry.primary_urls
    return urls[0] if urls else (entry.source_urls[0] if entry.source_urls else "")


def source_label(url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/", 1)[0]
    return host or url


def permalink(entry: Entry) -> str:
    """Where an entry's detail lives: its generated page under docs/entries."""
    return f"{PAGE_REL_DIR}/{entry.id}.md"


def entry_file_rel_path(entry: Entry) -> str:
    return f"{ENTRY_REL_DIR}/{entry.id}.yml"


def sorted_entries(entries: list[Entry]) -> list[Entry]:
    return sorted(entries, key=lambda e: e.id)


# --------------------------------------------------------------------------
# block renderers
# --------------------------------------------------------------------------


def render_count(entries: list[Entry]) -> list[str]:
    total = len(entries)
    dates = [d for d in (e.last_verified_date for e in entries) if d is not None]
    if not total:
        return ["**0** entries; nothing verified yet."]
    newest = max(dates).isoformat() if dates else "unknown"
    noun = "entry" if total == 1 else "entries"
    return [f"**{total}** {noun}; last verified **{newest}**."]


def render_tier_legend(_entries: list[Entry]) -> list[str]:
    lines = []
    for tier in (1, 2, 3):
        lines.append(
            f"- **Tier {tier} - {TIER_LABELS[tier]}.** "
            f"Badge {tier_badge(tier)}. {TIER_CRITERIA[tier]}"
        )
    return lines


def render_tier1(entries: list[Entry]) -> list[str]:
    tier1 = sorted((e for e in entries if e.tier == 1), key=entry_sort_key)
    if not tier1:
        return [
            "No entry has met the Tier 1 bar yet. Nothing is filed here on the "
            "strength of a proof of concept alone."
        ]
    rows = []
    for entry in tier1:
        url = primary_url(entry)
        # The title links to the entry's own detail page; the Source column
        # carries the primary source itself. Linking the title straight to the
        # source made the two columns redundant and hid the entry page.
        title = md_link(entry.title, permalink(entry))
        if url:
            source = md_link(source_label(url), url)
        else:
            source = md_cell("no primary source")
        rows.append(
            [
                tier_badge(entry.tier),
                title,
                md_cell(entry.get("date", "")),
                md_cell(entry.get("target", "")),
                source,
            ]
        )
    return md_table(["Tier", "Entry", "Date", "Target", "Primary source"], rows)


def render_matrix(entries: list[Entry], schema: dict[str, Any]) -> list[str]:
    enum = schema["properties"]["attack_class"]["enum"]
    counts: dict[tuple[str, int], int] = {}
    for entry in entries:
        key = (entry.attack_class, entry.tier)
        counts[key] = counts.get(key, 0) + 1

    rows = []
    for attack_class in enum:
        per_tier = [counts.get((attack_class, tier), 0) for tier in (1, 2, 3)]
        rows.append(
            [md_cell(ATTACK_CLASS_LABELS.get(attack_class, attack_class))]
            + [str(n) for n in per_tier]
            + [str(sum(per_tier))]
        )
    rows.append(
        [md_cell("**Total**")]
        + [str(sum(counts.get((cls, tier), 0) for cls in enum)) for tier in (1, 2, 3)]
        + [str(len(entries))]
    )

    # The picture first, then the same numbers as text. The table is not
    # redundant: it is what a screen reader reads out, what `grep` matches, and
    # what still works where an image will not load. The image is referenced
    # with `![]()` rather than inlined because GitHub's markdown sanitizer drops
    # inline `<svg>` elements entirely, leaving orphaned label text behind.
    return [
        f"![Attack class by evidence tier]({SVG_REL_PATH})",
        "",
        md_cell(
            "Cell colour encodes the evidence tier (darkest is Tier 1, "
            "confirmed in the wild); the numeral is how many entries sit "
            "there. A dashed empty cell means nothing is filed under that "
            "class at that tier yet."
        ),
        "",
    ] + md_table(["Attack class", "T1", "T2", "T3", "Total"], rows)


def render_catalogue(entries: list[Entry], schema: dict[str, Any]) -> list[str]:
    enum = schema["properties"]["attack_class"]["enum"]
    grouped: dict[str, list[Entry]] = {cls: [] for cls in enum}
    for entry in entries:
        grouped.setdefault(entry.attack_class, []).append(entry)

    if not entries:
        return [
            "The catalogue is empty. Entries appear here as soon as they are "
            "filed under data/entries and pass validation."
        ]

    lines: list[str] = []
    for attack_class in enum:
        members = sorted(grouped.get(attack_class, []), key=entry_sort_key)
        if not members:
            continue
        label = ATTACK_CLASS_LABELS.get(attack_class, attack_class)
        lines.append(f"### {md_cell(label)}")
        lines.append("")
        rows = [
            [
                tier_badge(entry.tier),
                md_cell(entry.title),
                md_cell(entry.get("date", "")),
                md_cell(entry.get("target", "")),
            ]
            for entry in members
        ]
        lines.extend(md_table(["Tier", "Title", "Date", "Target"], rows))
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def render_footer(_entries: list[Entry]) -> list[str]:
    return [
        "Every entry is graded on the evidence behind it, not on how alarming "
        "it sounds.",
        "",
        "- [docs/TIERS.md](docs/TIERS.md) - what each tier means and how to "
        "disagree with one.",
        "- [docs/METHODOLOGY.md](docs/METHODOLOGY.md) - how a finding is "
        "verified before it is filed.",
        "- [docs/TAXONOMY.md](docs/TAXONOMY.md) - the attack classes and the "
        "tie-break rule between them.",
        "- [dist/entries.json](dist/entries.json) - the same data, machine readable.",
    ]


def render_entry_index(entries: list[Entry]) -> list[str]:
    """Every entry as a link to its detail page, grouped by tier, Tier 1 first."""
    if not entries:
        return [
            "No entry pages yet. This index fills in as entries are filed under "
            "data/entries and pass validation."
        ]

    lines: list[str] = []
    for tier in (1, 2, 3):
        members = sorted((e for e in entries if e.tier == tier), key=entry_sort_key)
        if not members:
            continue
        lines.append(f"### {tier_badge(tier)} Tier {tier} - {TIER_LABELS[tier]}")
        lines.append("")
        for entry in members:
            label = ATTACK_CLASS_LABELS.get(entry.attack_class, entry.attack_class)
            lines.append(
                f"- {md_link(entry.title, permalink(entry))} "
                f"- {md_cell(label)} - {md_cell(entry.get('date', ''))}"
            )
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return lines


# --------------------------------------------------------------------------
# document generation
# --------------------------------------------------------------------------


def render_blocks(entries: list[Entry], schema: dict[str, Any]) -> dict[str, str]:
    return {
        "count": render_count(entries),
        "tier-legend": render_tier_legend(entries),
        "tier1": render_tier1(entries),
        "matrix": render_matrix(entries, schema),
        "catalogue": render_catalogue(entries, schema),
        "entry-index": render_entry_index(entries),
        "footer": render_footer(entries),
    }


def apply_blocks(readme: str, blocks: dict[str, str]) -> str:
    """Replace every marker body, leaving the markers themselves untouched."""

    def replace(match: re.Match[str]) -> str:
        name = match.group("name")
        if name not in blocks:
            return match.group(0)
        body = "\n".join(blocks[name]).strip("\n")
        return f"{match.group('begin')}\n{body}\n{match.group('end')}"

    updated = _BLOCK_RE.sub(replace, readme)
    missing = [name for name in blocks if f"BEGIN:GENERATED:{name} " not in updated]
    if missing:
        raise SystemExit(
            "README.md is missing generated markers: " + ", ".join(sorted(missing))
        )
    return updated


def read_optional(path: Path) -> str | None:
    """The committed file's contents, or None if it has not been built yet."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def build_readme(entries: list[Entry], schema: dict[str, Any]) -> str:
    current = read_optional(README_PATH)
    if not current:
        raise SystemExit(f"{README_PATH} is missing; nothing to update.")
    return apply_blocks(current, render_blocks(entries, schema))


def build_entries_json(entries: list[Entry], schema: dict[str, Any]) -> str:
    order = list(schema.get("properties", {}))
    payload_entries = []
    for entry in sorted_entries(entries):
        data = entry.data
        ordered = {key: data[key] for key in order if key in data}
        for key in sorted(data):
            if key not in ordered:
                ordered[key] = data[key]
        ordered["_permalink"] = permalink(entry)
        payload_entries.append(ordered)

    payload = {
        "generated_from": ENTRY_REL_DIR,
        "schema_version": SCHEMA_VERSION,
        "count": len(payload_entries),
        "entries": payload_entries,
    }
    return json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=False) + "\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def orphan_pages(pages: dict[str, str]) -> list[Path]:
    """Generated pages on disk whose entry no longer exists.

    A page for a deleted id is not a harmless leftover: it keeps a retired
    entry readable, and it inflates what the catalogue appears to hold. The
    whole directory is generated, so anything in it that the current entry set
    does not name is an orphan by definition.
    """
    directory = pages_dir()
    if not directory.is_dir():
        return []
    return [p for p in sorted(directory.glob("*.md")) if p.name not in pages]


def write_pages(pages: dict[str, str]) -> list[Path]:
    """Write every page and delete the orphans. Returns the removed paths."""
    directory = pages_dir()
    removed = orphan_pages(pages)
    for name in sorted(pages):
        write_text(directory / name, pages[name])
    for path in removed:
        path.unlink()
    return removed


def line_diff(label: str, committed: str | None, fresh: str) -> list[str]:
    if committed == fresh:
        return []
    old = (committed or "").splitlines()
    new = fresh.splitlines()
    return list(
        difflib.unified_diff(
            old,
            new,
            fromfile=f"committed/{label}",
            tofile=f"generated/{label}",
            lineterm="",
            n=2,
        )
    )


def pages_drift(pages: dict[str, str]) -> list[str]:
    """Diff the committed page set against what this entry set generates."""
    lines: list[str] = []
    directory = pages_dir()
    for name in sorted(pages):
        lines += line_diff(
            f"{PAGE_REL_DIR}/{name}", read_optional(directory / name), pages[name]
        )
    for path in orphan_pages(pages):
        lines.append(
            f"- {PAGE_REL_DIR}/{path.name} is generated from an entry that no "
            f"longer exists; run the build to remove it."
        )
    return lines


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build.py",
        description=(
            "Generate README.md generated-blocks, dist/entries.json, the "
            "attack-matrix SVG and docs/entries/*.md from data/entries/*.yml."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="do not write anything; exit 1 if the committed output has drifted",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="print the diff that would be applied, write nothing",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the summary line"
    )
    args = parser.parse_args(argv)

    from build_pages import render_pages

    schema = load_schema()
    entries = load_all_entries()
    readme = build_readme(entries, schema)
    payload = build_entries_json(entries, schema)
    svg = render_matrix_svg(entries, schema)
    pages = render_pages(entries)

    committed_readme = read_optional(README_PATH)
    committed_payload = read_optional(DIST_PATH)

    if args.check or args.dry_run:
        drift = line_diff(README_PATH.name, committed_readme, readme)
        drift += line_diff(DIST_PATH.name, committed_payload, payload)
        drift += line_diff(SVG_REL_PATH, read_optional(svg_path()), svg)
        drift += pages_drift(pages)
        if drift:
            for line in drift:
                print(ascii_text(line))
        if not args.quiet:
            verb = "check" if args.check else "dry run"
            state = "drift found" if drift else "up to date"
            print(f"build {verb}: {state}; nothing written.")
        return 1 if drift else 0

    removed = write_pages(pages)
    write_text(README_PATH, readme)
    write_text(DIST_PATH, payload)
    write_text(svg_path(), svg)
    if not args.quiet:
        noun = "entry" if len(entries) == 1 else "entries"
        print(
            f"build: wrote {README_PATH.name}, {DIST_PATH.name}, "
            f"{SVG_REL_PATH} and {len(pages)} page(s) from {len(entries)} {noun}."
        )
        for path in removed:
            print(f"build: removed orphan page {PAGE_REL_DIR}/{path.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
