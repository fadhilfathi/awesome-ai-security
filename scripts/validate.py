"""Schema and semantic validation for every file in ``data/entries``.

JSON Schema can express shape: types, patterns, enumerations, lengths. It
cannot express the rules that make this catalogue worth trusting -- that a
tier 1 entry cites a primary source, that no two entries quietly point at the
same advisory, that a file's name matches the id inside it, or that nobody has
let a verification date rot. This module runs both layers and reports every
violation it can find in a single pass, so fixing a batch of entries means
one run, not one run per mistake.

Usage::

    python scripts/validate.py [--json] [--strict] [--max-age-days N]

Severity model
--------------
Every violation carries a severity:

``error``
    The entry is wrong: it breaks the schema, or a rule stated in
    ``AGENTS.md`` / ``docs/`` that no tool can infer from the text.
``warning``
    The entry is not wrong, but it is going stale, or something about it
    deserves a human glance before it ships.

Exit code is ``0`` when no ``error`` was reported, ``1`` when at least one was.
``--strict`` additionally makes ``warning`` fatal. The JSON report's ``valid``
field follows exactly the same rule: true when the process would exit 0.

Rule slugs
----------
Stable, machine-readable identifiers. One slug per check, printed in square
brackets before the message and exposed in ``--json`` output:

``unreadable_entry``
    The file could not be parsed as a YAML mapping.
``schema_invalid``
    One or more JSON Schema errors (every error for the entry is collected,
    not just the first).
``filename_id_mismatch``
    The file stem differs from the ``id`` field.
``duplicate_id``
    Two or more files declare the same ``id``.
``missing_primary_source``
    A tier 1 or tier 2 entry has no ``primary`` source.
``missing_source``
    A tier 3 entry has no sources at all.
``duplicate_url_in_entry``
    The same URL appears twice inside one entry. Always an error; a comment
    never excuses it.
``duplicate_url_across_entries``
    Two entries cite the same URL. Error unless the citing file carries a
    ``duplicate-primary-source:`` or ``duplicate-source:`` comment explaining
    why.
``cve_malformed``
    A ``cve`` entry is not ``CVE-YYYY-NNNN[NNNN]``.
``cve_duplicate_in_entry``
    The same CVE id appears twice in one entry.
``tier1_impact_missing_evidence``
    Heuristic lint, see below.
``blank_text_field``
    ``summary``, ``impact``, or ``mitigation`` is present but only whitespace.
    The schema's ``minLength`` accepts ``"   "``; this check does not.
``date_in_future``
    ``date`` is later than today.
``last_verified_in_future``
    ``last_verified`` is later than today.
``stale_entry``
    Warning: ``last_verified`` is older than the staleness horizon
    (``--max-age-days``, default 365).

A note on ``tier1_impact_missing_evidence``
------------------------------------------
This check is a keyword lint, not a proof. It looks for any of
``TIER1_EVIDENCE_KEYWORDS`` in the ``impact`` text:

    exploit, exploitation, exploited, in the wild, real-world, real world,
    affected, attackers, attacker, campaign, victims, users were

If none appear, the entry is reported. The intent is narrow and honest: catch
a tier 1 entry that forgot to state its evidence at all. Passing the check
means the writer mentioned real-world exploitation or affected users somewhere
in the field -- it does **not** mean the claim is true, that the cited source
says it, or that the entry deserves tier 1. That judgement stays human, and
belongs to the tier rules in ``docs/`` and to whoever reviews the entry.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Bootstrap: allow `python scripts/validate.py` (sys.path[0] is scripts/) as
# well as `from scripts.validate import main` from the repo root.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.entries import (  # noqa: E402
    ENTRY_DIR,
    ValidationError,
    entry_files,
    load_entry,
    load_schema,
    today,
)

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"

DEFAULT_MAX_AGE_DAYS = 365

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}")

#: Comment keys a file may carry to justify reusing a URL already cited
#: elsewhere in the catalogue, e.g. ``# duplicate-primary-source: also cited
#: by some-other-entry``. Matched against YAML comment lines only.
DUPLICATE_URL_COMMENT_KEYS = ("duplicate-primary-source", "duplicate-source")
_DUPLICATE_URL_COMMENT = re.compile(
    r"^[ \t]*#[ \t]*("
    + "|".join(re.escape(k) for k in DUPLICATE_URL_COMMENT_KEYS)
    + r")[ \t]*:",
    re.MULTILINE,
)


#: Vocabulary for the tier 1 impact lint. Deliberately small and legible; see
#: the module docstring for what passing this check does and does not mean.
TIER1_EVIDENCE_KEYWORDS = (
    "exploit",
    "exploitation",
    "exploited",
    "in the wild",
    "real-world",
    "real world",
    "affected",
    "attacker",
    "attackers",
    "campaign",
    "victims",
    "users were",
)


@dataclass(frozen=True)
class Violation:
    """One problem found in one entry file."""

    entry_id: str
    file: str
    rule: str
    message: str
    severity: str = SEVERITY_ERROR

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.entry_id,
            "file": self.file,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity,
        }

    def as_text(self) -> str:
        return f"{self.file}: [{self.rule}] {self.message}"


def _rel(path: Path) -> str:
    """Repository-relative, forward-slash path for stable output."""
    try:
        return path.resolve().relative_to(Path(_REPO_ROOT)).as_posix()
    except ValueError:
        return path.as_posix()


def _has_duplicate_url_comment(text: str) -> bool:
    return _DUPLICATE_URL_COMMENT.search(text) is not None


def _parse_date(value: str) -> _dt.date | None:
    """Parse ``YYYY-MM`` or ``YYYY-MM-DD``; None when not parseable.

    ``date`` is allowed to carry only month precision. It is anchored to the
    first of the month, which is the earliest day the value can denote, so a
    month-only date in the current month never reads as being in the future.
    """
    raw = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}", raw):
        raw = f"{raw}-01"
    try:
        return _dt.date.fromisoformat(raw)
    except ValueError:
        return None


class _Loader:
    """Builds a :class:`Violation` bound to a file, with the boilerplate out."""

    def __init__(self, path: Path, entry_id: str) -> None:
        self.file = _rel(path)
        self.entry_id = entry_id

    def __call__(
        self,
        rule: str,
        message: str,
        severity: str = SEVERITY_ERROR,
        entry_id: str | None = None,
    ) -> Violation:
        return Violation(
            entry_id=self.entry_id if entry_id is None else entry_id,
            file=self.file,
            rule=rule,
            message=message,
            severity=severity,
        )


def _schema_validator(schema: dict[str, Any]) -> Any:
    """Compile the Draft 2020-12 validator. Not done at import time."""
    from jsonschema import Draft202012Validator

    return Draft202012Validator(schema)


def _check_schema(validator: Any, entry: Any, load: _Loader) -> list[Violation]:
    found: list[Violation] = []
    errors = sorted(
        validator.iter_errors(entry.data), key=lambda e: list(e.absolute_path)
    )
    for error in errors:
        where = ".".join(str(p) for p in error.absolute_path) or "<entry>"
        found.append(load("schema_invalid", f"{where}: {error.message}"))
    return found


def _check_identity(entry: Any, load: _Loader) -> list[Violation]:
    found: list[Violation] = []
    stem = entry.path.stem
    if entry.id and entry.id != stem:
        found.append(
            load(
                "filename_id_mismatch",
                f"file is named {stem!r} but declares id {entry.id!r}",
            )
        )
    return found


def _check_sources(entry: Any, load: _Loader) -> list[Violation]:
    found: list[Violation] = []
    tier = entry.tier
    if tier in (1, 2):
        if not entry.primary_sources:
            found.append(
                load(
                    "missing_primary_source",
                    f"tier {tier} entry needs at least one source with kind: primary",
                )
            )
    elif tier == 3 and not entry.sources:
        found.append(
            load("missing_source", "tier 3 entry needs at least one source of any kind")
        )

    seen: dict[str, int] = {}
    for url in entry.source_urls:
        seen[url] = seen.get(url, 0) + 1
    for url, count in sorted(seen.items()):
        if count > 1:
            found.append(
                load(
                    "duplicate_url_in_entry",
                    f"url {url} is cited {count} times in this entry",
                )
            )
    return found


def _check_cve(entry: Any, load: _Loader) -> list[Violation]:
    found: list[Violation] = []
    seen: set[str] = set()
    for cve in entry.cve:
        if not CVE_PATTERN.fullmatch(cve):
            found.append(
                load(
                    "cve_malformed",
                    f"cve {cve!r} is not of the form CVE-YYYY-NNNN[NNNN]",
                )
            )
        if cve in seen:
            found.append(
                load("cve_duplicate_in_entry", f"cve {cve} is listed more than once")
            )
        seen.add(cve)
    return found


def _check_tier1_impact(entry: Any, load: _Loader) -> list[Violation]:
    if entry.tier != 1:
        return []
    impact = str(entry.get("impact") or "").lower()
    if any(keyword in impact for keyword in TIER1_EVIDENCE_KEYWORDS):
        return []
    return [
        load(
            "tier1_impact_missing_evidence",
            "tier 1 impact should state real-world exploitation or affected users; "
            f"none of the lint keywords appear ({', '.join(TIER1_EVIDENCE_KEYWORDS)})",
        )
    ]


def _check_text_fields(entry: Any, load: _Loader) -> list[Violation]:
    found: list[Violation] = []
    for field in ("summary", "impact", "mitigation"):
        value = entry.get(field)
        if isinstance(value, str) and not value.strip():
            found.append(
                load("blank_text_field", f"{field} is empty or whitespace-only")
            )
    return found


def _check_dates(
    entry: Any, load: _Loader, now: _dt.date, max_age_days: int
) -> list[Violation]:
    found: list[Violation] = []

    disclosed = entry.get("date")
    if isinstance(disclosed, str):
        parsed = _parse_date(disclosed)
        if parsed is not None and parsed > now:
            found.append(
                load(
                    "date_in_future",
                    f"date {disclosed} is later than today ({now.isoformat()})",
                )
            )

    verified = entry.get("last_verified")
    if isinstance(verified, str):
        parsed = _parse_date(verified)
        if parsed is None:
            return found
        if parsed > now:
            found.append(
                load(
                    "last_verified_in_future",
                    f"last_verified {verified} is later than today ({now.isoformat()})",
                )
            )
            return found
        age_days = (now - parsed).days
        if age_days > max_age_days:
            found.append(
                load(
                    "stale_entry",
                    f"last_verified {verified} is {age_days} days old, "
                    f"beyond the {max_age_days} day horizon; re-check the sources",
                    severity=SEVERITY_WARNING,
                )
            )
    return found


def _check_url_uniqueness(
    entries: list[tuple[Path, Any, str]],
    loads: dict[Path, _Loader],
) -> list[Violation]:
    """Catalogue-wide URL uniqueness, with the comment escape hatch."""
    first_owner: dict[str, str] = {}
    found: list[Violation] = []
    for path, entry, text in entries:
        load = loads[path]
        excused = _has_duplicate_url_comment(text)
        for url in entry.source_urls:
            owner = first_owner.get(url)
            if owner is None:
                first_owner[url] = entry.id
                continue
            if excused:
                continue
            found.append(
                load(
                    "duplicate_url_across_entries",
                    f"url {url} is already cited by entry {owner}; add a "
                    "'duplicate-primary-source:' or 'duplicate-source:' comment "
                    "in this file to explain the reuse",
                )
            )
    return found


def _check_duplicate_ids(
    entries: list[tuple[Path, Any, str]], loads: dict[Path, _Loader]
) -> list[Violation]:
    first_file: dict[str, str] = {}
    found: list[Violation] = []
    for path, entry, _text in entries:
        entry_id = entry.id
        if not entry_id:
            continue
        previous = first_file.get(entry_id)
        if previous is not None:
            found.append(
                loads[path](
                    "duplicate_id",
                    f"id {entry_id!r} is already declared by {previous}",
                    entry_id=entry_id,
                )
            )
        else:
            first_file[entry_id] = _rel(path)
    return found


def collect_violations(max_age_days: int = DEFAULT_MAX_AGE_DAYS) -> list[Violation]:
    """Run every check over ``data/entries`` and return the violations found."""
    schema = load_schema()
    validator = _schema_validator(schema)
    now = today()

    entries: list[tuple[Path, Any, str]] = []
    loads: dict[Path, _Loader] = {}
    found: list[Violation] = []

    for path in entry_files():
        rel = _rel(path)
        try:
            entry = load_entry(path)
        except ValidationError as exc:
            found.append(
                Violation(
                    entry_id=path.stem,
                    file=rel,
                    rule="unreadable_entry",
                    message=str(exc),
                )
            )
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:  # pragma: no cover - load_entry already read it
            text = ""
        loads[path] = _Loader(path, entry.id or path.stem)
        entries.append((path, entry, text))

    for path, entry, _text in entries:
        load = loads[path]
        found.extend(_check_schema(validator, entry, load))
        found.extend(_check_identity(entry, load))
        found.extend(_check_sources(entry, load))
        found.extend(_check_cve(entry, load))
        found.extend(_check_tier1_impact(entry, load))
        found.extend(_check_text_fields(entry, load))
        found.extend(_check_dates(entry, load, now, max_age_days))

    found.extend(_check_duplicate_ids(entries, loads))
    found.extend(_check_url_uniqueness(entries, loads))

    found.sort(key=lambda v: (v.entry_id, v.file, v.rule, v.message))
    return found


def has_errors(violations: list[Violation]) -> bool:
    return any(v.severity == SEVERITY_ERROR for v in violations)


def render_text(violations: list[Violation]) -> str:
    return "\n".join(v.as_text() for v in violations)


def build_report(violations: list[Violation], strict: bool) -> dict[str, Any]:
    errors = sum(1 for v in violations if v.severity == SEVERITY_ERROR)
    warnings = sum(1 for v in violations if v.severity == SEVERITY_WARNING)
    valid = errors == 0 and (not strict or warnings == 0)
    return {
        "valid": valid,
        "error_count": errors,
        "warning_count": warnings,
        "violations": [v.as_dict() for v in violations],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate",
        description="Validate data/entries against the schema and the catalogue rules.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON report instead of text",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as fatal",
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
    violations = collect_violations(max_age_days=args.max_age_days)
    report = build_report(violations, strict=args.strict)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        if violations:
            print(render_text(violations))
        errors = report["error_count"]
        warnings = report["warning_count"]
        print(
            f"{len(violations)} violation(s): {errors} error(s), {warnings} warning(s)"
            f" across {len(entry_files())} entr(ies) in {ENTRY_DIR.name}/"
        )

    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
