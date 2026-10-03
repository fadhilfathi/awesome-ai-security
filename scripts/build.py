"""Generate the README generated-blocks and dist/entries.json.

data/entries/*.yml is the single source of truth. Everything this script emits
is derived from those files: no numbers are typed by hand and no build time is
stamped into the output, so running the build twice is byte-identical and
`--check` is a meaningful CI gate.

Usage:
    python scripts/build.py            regenerate README.md and dist/entries.json
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

SCHEMA_VERSION = 1
ENTRY_REL_DIR = "data/entries"

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
    """Where an entry's detail lives. Entries have no standalone page, so the
    anchor is the entry file itself, reachable from dist/entries.json."""
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
        title = md_link(entry.title, url) if url else md_cell(entry.title)
        source = source_label(url) if url else "see entry file"
        rows.append(
            [
                tier_badge(entry.tier),
                title,
                md_cell(entry.get("date", "")),
                md_cell(entry.get("target", "")),
                md_cell(source),
            ]
        )
    return md_table(["Tier", "Entry", "Date", "Target", "Source"], rows)


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
    return md_table(["Attack class", "T1", "T2", "T3", "Total"], rows)


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


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build.py",
        description=(
            "Generate README.md generated-blocks and dist/entries.json from "
            "data/entries/*.yml."
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

    schema = load_schema()
    entries = load_all_entries()
    readme = build_readme(entries, schema)
    payload = build_entries_json(entries, schema)

    committed_readme = read_optional(README_PATH)
    committed_payload = read_optional(DIST_PATH)

    if args.check or args.dry_run:
        drift = line_diff(README_PATH.name, committed_readme, readme)
        drift += line_diff(DIST_PATH.name, committed_payload, payload)
        if drift:
            for line in drift:
                print(ascii_text(line))
        if not args.quiet:
            verb = "check" if args.check else "dry run"
            state = "drift found" if drift else "up to date"
            print(f"build {verb}: {state}; nothing written.")
        return 1 if drift else 0

    write_text(README_PATH, readme)
    write_text(DIST_PATH, payload)
    if not args.quiet:
        noun = "entry" if len(entries) == 1 else "entries"
        print(
            f"build: wrote {README_PATH.name} and {DIST_PATH.name} "
            f"from {len(entries)} {noun}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
