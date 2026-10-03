"""Shared loading primitives for the catalogue.

This module is the seam between the YAML files in ``data/entries`` and every
script in ``scripts/``. It deliberately does no policy: tier requirements,
duplicate detection, and field checks live in ``validate.py`` so that this
module stays a plain, fast, dependency-light reader that the generator and
the tests can both trust.

Public API (stable, consumed by scripts/, tests/, and .github/workflows):

    REPO_ROOT          Path to the repository root.
    ENTRY_GLOB         Relative glob matching every entry file.
    load_entry(path)   -> Entry
    load_all_entries() -> list[Entry]
    Entry              .path, .data, .sources, .primary_sources,
                       .secondary_sources, .source_urls
    ValidationError    Raised by load_entry for an unreadable/unparseable file.

Scripts are expected to be runnable both as ``python scripts/validate.py`` and
as ``from scripts.validate import main``.
"""

from __future__ import annotations

import datetime as _dt
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTRY_DIR = REPO_ROOT / "data" / "entries"
SCHEMA_PATH = REPO_ROOT / "data" / "schema.json"
README_PATH = REPO_ROOT / "README.md"
DIST_PATH = REPO_ROOT / "dist" / "entries.json"
ENTRY_GLOB = "data/entries/*.yml"


class ValidationError(Exception):
    """An entry file could not be read as a mapping, or could not be parsed."""


@dataclass(frozen=True)
class Entry:
    """One parsed ``data/entries/<id>.yml`` file.

    ``data`` is kept as the raw mapping so that validators can inspect fields
    they were not modelled on, and so that JSON export is lossless.
    """

    path: Path
    data: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.data.get("id", ""))

    @property
    def tier(self) -> int:
        value = self.data.get("tier")
        return int(value) if isinstance(value, int) else 0

    @property
    def attack_class(self) -> str:
        return str(self.data.get("attack_class", ""))

    @property
    def title(self) -> str:
        return str(self.data.get("title", ""))

    @property
    def sources(self) -> list[dict[str, Any]]:
        value = self.data.get("sources")
        return list(value) if isinstance(value, list) else []

    @property
    def primary_sources(self) -> list[dict[str, Any]]:
        return [s for s in self.sources if s.get("kind") == "primary"]

    @property
    def secondary_sources(self) -> list[dict[str, Any]]:
        return [s for s in self.sources if s.get("kind") == "secondary"]

    @property
    def source_urls(self) -> list[str]:
        return [str(s.get("url")) for s in self.sources if s.get("url")]

    @property
    def primary_urls(self) -> list[str]:
        return [str(s.get("url")) for s in self.primary_sources if s.get("url")]

    @property
    def cve(self) -> list[str]:
        value = self.data.get("cve")
        return [str(v) for v in value] if isinstance(value, list) else []

    @property
    def last_verified(self) -> str:
        return str(self.data.get("last_verified", ""))

    @property
    def last_verified_date(self) -> _dt.date | None:
        raw = self.last_verified
        try:
            return _dt.date.fromisoformat(raw)
        except ValueError:
            return None

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]


def load_entry(path: Path) -> Entry:
    """Parse one entry file. Raises ValidationError if unreadable or malformed."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"{path}: cannot read file: {exc}") from exc
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ValidationError(f"{path}: invalid YAML: {exc}") from exc
    if parsed is None:
        raise ValidationError(f"{path}: file is empty")
    if not isinstance(parsed, dict):
        raise ValidationError(
            f"{path}: top level must be a mapping, found {type(parsed).__name__}"
        )
    return Entry(path=path, data=parsed)


def entry_files() -> list[Path]:
    """Every entry file, sorted by filename so output is deterministic."""
    return sorted(ENTRY_DIR.glob("*.yml"))


def iter_entries() -> Iterator[Entry]:
    for path in entry_files():
        yield load_entry(path)


def load_all_entries() -> list[Entry]:
    return list(iter_entries())


def load_schema() -> dict[str, Any]:
    """The JSON Schema, parsed. Single source of truth for shape validation."""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def today() -> _dt.date:
    """Today's UTC date, for defaults and staleness checks."""
    return _dt.datetime.now(_dt.UTC).date()
