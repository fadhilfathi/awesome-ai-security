"""Statistics for the catalogue, computed from ``data/entries`` and nothing else.

Every number this script prints is counted from the entry files at the moment
it runs. There is no hand-maintained tally anywhere: if a file is added,
removed, or edited, the next run reports the new figures, and a figure that
cannot be traced to a count of files has no way to appear here. The README and
``dist/entries.json`` are generated from these files too, so this script exists
to make the shape of the catalogue inspectable without opening the YAML.

Usage::

    python scripts/stats.py [--json] [--max-age-days N]

The staleness horizon (``--max-age-days``, default 365) only affects the
``stale_entries`` figure; every other statistic is horizon-free.

Output is plain ASCII on purpose: no box drawing, no emoji, no non-ASCII
characters, so the tables render identically on a Windows cp1252 terminal, in
a POSIX shell, and in CI logs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Bootstrap: allow `python scripts/stats.py` as well as
# `from scripts.stats import main` from the repo root.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.entries import (  # noqa: E402
    ENTRY_DIR,
    load_all_entries,
    load_schema,
    today,
)

DEFAULT_MAX_AGE_DAYS = 365

TIERS = (1, 2, 3)


def attack_classes() -> list[str]:
    """The enum from ``data/schema.json``, in schema order.

    Read from the schema rather than hardcoded so the two can never drift.
    Raises ``KeyError`` if the schema is reshaped under this script.
    """
    schema = load_schema()
    return list(schema["properties"]["attack_class"]["enum"])


def _oldest(values: list[str]) -> str | None:
    return min(values) if values else None


def _newest(values: list[str]) -> str | None:
    return max(values) if values else None


def compute_stats(max_age_days: int = DEFAULT_MAX_AGE_DAYS) -> dict[str, Any]:
    """Every statistic the README could show, as a plain nested dict."""
    entries = load_all_entries()
    classes = attack_classes()
    now = today()

    per_tier = {str(tier): 0 for tier in TIERS}
    per_class = {name: 0 for name in classes}
    matrix = {name: {str(tier): 0 for tier in TIERS} for name in classes}

    cve_ids: set[str] = set()
    entries_with_cve = 0
    primary_urls: set[str] = set()

    disclosure_dates: list[str] = []
    verified_dates: list[str] = []
    stale_entries = 0

    for entry in entries:
        tier = str(entry.tier)
        if tier in per_tier:
            per_tier[tier] += 1

        name = entry.attack_class
        if name in per_class:
            per_class[name] += 1
            if tier in matrix[name]:
                matrix[name][tier] += 1

        if entry.cve:
            entries_with_cve += 1
            cve_ids.update(entry.cve)

        primary_urls.update(entry.primary_urls)

        date_value = entry.get("date")
        if isinstance(date_value, str) and date_value:
            disclosure_dates.append(date_value)

        verified = entry.last_verified_date
        if verified is not None:
            verified_dates.append(verified.isoformat())
            if (now - verified).days > max_age_days:
                stale_entries += 1

    return {
        "total_entries": len(entries),
        "by_tier": per_tier,
        "by_attack_class": per_class,
        "matrix_attack_class_by_tier": matrix,
        "attack_class_order": classes,
        "tier_order": [str(tier) for tier in TIERS],
        "distinct_cve_ids": len(cve_ids),
        "entries_with_cve": entries_with_cve,
        "distinct_primary_source_urls": len(primary_urls),
        "oldest_date": _oldest(disclosure_dates),
        "newest_date": _newest(disclosure_dates),
        "oldest_last_verified": _oldest(verified_dates),
        "newest_last_verified": _newest(verified_dates),
        "stale_entries": stale_entries,
        "max_age_days": max_age_days,
        "generated_on": now.isoformat(),
    }


def _table(
    headers: list[str], rows: list[list[str]], align_right: list[bool]
) -> list[str]:
    """Fixed-width ASCII table. ``align_right[i]`` right-aligns column ``i``."""
    widths = [len(h) for h in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def render(cells: list[str]) -> str:
        out = []
        for index, cell in enumerate(cells):
            if align_right[index]:
                out.append(cell.rjust(widths[index]))
            else:
                out.append(cell.ljust(widths[index]))
        return "  ".join(out).rstrip()

    separator = "  ".join("-" * width for width in widths)
    return [render(headers), separator, *(render(row) for row in rows)]


def _or_dash(value: str | None) -> str:
    return value if value else "-"


def render_text(stats: dict[str, Any]) -> str:
    """Human-readable report: plain ASCII, one labelled block per statistic."""
    lines: list[str] = []
    lines.append("awesome-ai-security catalogue statistics")
    lines.append(f"source: {ENTRY_DIR.as_posix().rsplit('/', 1)[-1]}/*.yml")
    lines.append(f"computed on: {stats['generated_on']}")
    lines.append("")

    lines.append("Totals")
    lines.extend(
        _table(
            ["metric", "value"],
            [
                ["total entries", str(stats["total_entries"])],
                ["entries with a CVE", str(stats["entries_with_cve"])],
                ["distinct CVE ids", str(stats["distinct_cve_ids"])],
                [
                    "distinct primary-source URLs",
                    str(stats["distinct_primary_source_urls"]),
                ],
            ],
            [False, True],
        )
    )
    lines.append("")

    lines.append("Entries per evidence tier")
    lines.extend(
        _table(
            ["tier", "entries"],
            [[tier, str(stats["by_tier"][tier])] for tier in stats["tier_order"]],
            [False, True],
        )
    )
    lines.append("")

    lines.append("Entries per attack class")
    lines.extend(
        _table(
            ["attack_class", "entries"],
            [
                [name, str(stats["by_attack_class"][name])]
                for name in stats["attack_class_order"]
            ],
            [False, True],
        )
    )
    lines.append("")

    lines.append("Attack class x evidence tier")
    rows = []
    for name in stats["attack_class_order"]:
        cells = stats["matrix_attack_class_by_tier"][name]
        rows.append([name, *(str(cells[tier]) for tier in stats["tier_order"])])
    lines.extend(
        _table(["attack_class", *stats["tier_order"]], rows, [False, True, True, True])
    )
    lines.append("")

    lines.append("Date coverage")
    lines.extend(
        _table(
            ["metric", "value"],
            [
                ["oldest disclosure date", _or_dash(stats["oldest_date"])],
                ["newest disclosure date", _or_dash(stats["newest_date"])],
                ["oldest last_verified", _or_dash(stats["oldest_last_verified"])],
                ["newest last_verified", _or_dash(stats["newest_last_verified"])],
                [
                    f"entries older than {stats['max_age_days']} days",
                    str(stats["stale_entries"]),
                ],
            ],
            [False, True],
        )
    )

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stats",
        description="Print catalogue statistics, all derived from data/entries.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON instead of a text report",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_MAX_AGE_DAYS,
        metavar="N",
        help=f"staleness horizon for last_verified (default: {DEFAULT_MAX_AGE_DAYS})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    stats = compute_stats(max_age_days=args.max_age_days)
    if args.json:
        print(json.dumps(stats, indent=2, sort_keys=True))
    else:
        print(render_text(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
