"""Shared fixtures for the test suite.

Two facts about this repository shape everything below.

1. ``scripts/build.py`` puts ``scripts/`` on ``sys.path`` and imports the
   top-level module name ``entries``, while ``scripts/validate.py`` and
   ``scripts/stats.py`` import the package-qualified ``scripts.entries``. Both
   module objects stay live at the same time and each one owns its own
   ``ENTRY_DIR`` global, so a fixture that patches only
   ``scripts.entries.ENTRY_DIR`` still lets ``build.py`` read the real
   ``data/entries/``. ``tmp_catalogue`` patches both.
2. ``data/schema.json`` is the contract every test validates against, so
   ``SCHEMA_PATH`` is deliberately *not* redirected. Only mutable state moves:
   the entry directory, ``README.md`` and ``dist/entries.json``.

Nothing here may touch the real ``data/entries/``, ``README.md`` or
``dist/entries.json``; ``REAL_ENTRY_DIR`` is captured at import time so
``real_entries`` keeps working even inside a test that redirected everything
else.
"""

from __future__ import annotations

import importlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

import scripts.build as build_module
import scripts.entries as entries_module
import scripts.stats as stats_module
import scripts.validate as validate_module
from scripts.entries import Entry, ValidationError, load_entry, today

#: The module object ``scripts/build.py`` imports from. Distinct from
#: ``scripts.entries`` even though both are called ``entries``.
LEGACY_ENTRIES_MODULE = importlib.import_module("entries")

assert LEGACY_ENTRIES_MODULE is not entries_module, (
    "build.py is expected to own a separate module object; if that ever "
    "changes, tmp_catalogue's patching strategy must change with it"
)

#: Captured before any monkeypatching, so real-data assertions stay real.
REAL_ENTRY_DIR = Path(entries_module.ENTRY_DIR)

#: Hand-written copy of the schema's enum. Tests assert the shipped schema
#: still matches this, so widening the enum cannot silently pass a test.
ATTACK_CLASSES = (
    "PROMPT_INJECTION_DIRECT",
    "PROMPT_INJECTION_INDIRECT",
    "TOOL_POISONING",
    "AGENT_PRIVILEGE_ABUSE",
    "DATA_EXFILTRATION",
    "SUPPLY_CHAIN_PACKAGE",
    "SUPPLY_CHAIN_MODEL",
    "CODE_ASSISTANT_ABUSE",
    "TRAINING_DATA_POISONING",
    "MODEL_THEFT_EXTRACTION",
    "JAILBREAK",
    "INSECURE_OUTPUT_HANDLING",
    "CREDENTIAL_EXPOSURE",
    "DENIAL_OF_SERVICE",
    "OTHER",
)

#: Fixed past date, never "today": staleness and ordering assertions must not
#: depend on when the suite runs.
FIXED_DATE = "2001-02-03"

EVIDENCE_IMPACT = (
    "Synthetic text for the test suite only: the cited source states "
    "real-world exploitation and affected users in this hypothetical case."
)

#: Key order for generated YAML, so failures read top-down.
_KEY_ORDER = (
    "id",
    "title",
    "tier",
    "attack_class",
    "target",
    "date",
    "summary",
    "impact",
    "mitigation",
    "sources",
    "cve",
    "last_verified",
)

README_SKELETON = """# awesome-ai-security

Scaffold README owned by the test suite. Only the generated blocks matter.

<!-- BEGIN:GENERATED:count -->
placeholder-count-block
<!-- END:GENERATED:count -->

## Evidence tiers

<!-- BEGIN:GENERATED:tier-legend -->
placeholder-tier-legend-block
<!-- END:GENERATED:tier-legend -->

## Start here: confirmed in the wild

<!-- BEGIN:GENERATED:tier1 -->
placeholder-tier1-block
<!-- END:GENERATED:tier1 -->

## Attack class x evidence tier

<!-- BEGIN:GENERATED:matrix -->
placeholder-matrix-block
<!-- END:GENERATED:matrix -->

## Full catalogue

<!-- BEGIN:GENERATED:catalogue -->
placeholder-catalogue-block
<!-- END:GENERATED:catalogue -->

## Entry pages

<!-- BEGIN:GENERATED:entry-index -->
placeholder-entry-index-block
<!-- END:GENERATED:entry-index -->

## How to read this list

<!-- BEGIN:GENERATED:footer -->
placeholder-footer-block
<!-- END:GENERATED:footer -->

Trailing prose outside every block, which a build must not touch.
"""

_BLOCK_RE = re.compile(
    r"<!-- BEGIN:GENERATED:([A-Za-z0-9_-]+) -->\n(.*?)\n<!-- END:GENERATED:\1 -->",
    re.DOTALL,
)
_MARKER_RE = re.compile(r"<!-- (?:BEGIN|END):GENERATED:([A-Za-z0-9_-]+) -->")


@dataclass(frozen=True)
class Sandbox:
    """A throwaway catalogue root: entries dir, README and dist output."""

    root: Path
    entries_dir: Path
    readme_path: Path
    dist_path: Path

    def write_readme(self, text: str) -> Path:
        self.readme_path.write_text(text, encoding="utf-8", newline="\n")
        return self.readme_path

    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def readme(self) -> str:
        return self.read(self.readme_path)

    def dist(self) -> str:
        return self.read(self.dist_path)

    def dist_json(self) -> dict[str, Any]:
        return json.loads(self.dist())

    def bytes_of(self, path: Path) -> bytes | None:
        return path.read_bytes() if path.exists() else None

    @property
    def pages_dir(self) -> Path:
        """The generated detail-page directory inside the sandbox."""
        return self.root / "docs" / "entries"

    @property
    def docs_dir(self) -> Path:
        """The docs directory inside the sandbox (pages live under it)."""
        return self.root / "docs"

    @property
    def svg_path(self) -> Path:
        return self.root / "docs" / "attack-matrix.svg"

    def page(self, entry_id: str) -> str:
        return self.read(self.pages_dir / f"{entry_id}.md")


@dataclass(frozen=True)
class ValidationRun:
    """One ``scripts/validate.py`` invocation and everything it printed."""

    code: int
    report: dict[str, Any] | None
    text: str

    @property
    def slugs(self) -> set[str]:
        """Rule slugs present in the JSON report."""
        assert self.report is not None, "this run was not asked for JSON"
        return {v["rule"] for v in self.report["violations"]}

    def violations(self, rule: str) -> list[dict[str, str]]:
        assert self.report is not None, "this run was not asked for JSON"
        return [v for v in self.report["violations"] if v["rule"] == rule]


@dataclass(frozen=True)
class ReadmeTools:
    """Helpers for pulling generated blocks and tables out of README text."""

    @staticmethod
    def blocks(text: str) -> dict[str, list[str]]:
        return {m.group(1): m.group(2).splitlines() for m in _BLOCK_RE.finditer(text)}

    @staticmethod
    def block(text: str, name: str) -> list[str]:
        blocks = ReadmeTools.blocks(text)
        assert name in blocks, f"no generated block named {name!r}"
        return blocks[name]

    @staticmethod
    def marker_names(text: str) -> list[str]:
        return _MARKER_RE.findall(text)

    @staticmethod
    def rows(lines: list[str]) -> list[list[str]]:
        """Parse a GitHub markdown table, dropping the alignment row."""
        parsed = []
        for line in lines:
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
            if all(set(cell) <= {"-", ":"} and cell for cell in cells):
                continue
            parsed.append(cells)
        return parsed


@dataclass
class _EntryDefaults:
    """The schema-valid baseline every synthetic entry starts from."""

    title: str = "Synthetic test entry about example-product"
    tier: int = 3
    attack_class: str = "OTHER"
    target: str = "example-product"
    date: str = FIXED_DATE
    summary: str = (
        "A synthetic catalogue entry written for the test suite. It describes "
        "no real product, person, or event."
    )
    impact: str = (
        "The impact text is invented for tests and describes a hypothetical "
        "outcome only."
    )
    mitigation: str = "Apply the documented mitigation for the synthetic case."
    last_verified: str = field(default_factory=lambda: today().isoformat())


def _ordered(data: dict[str, Any]) -> dict[str, Any]:
    ordered = {key: data[key] for key in _KEY_ORDER if key in data}
    ordered.update({key: data[key] for key in sorted(data) if key not in ordered})
    return ordered


def primary_source(entry_id: str, slug: str = "advisory") -> dict[str, str]:
    """A primary source with a URL unique to ``entry_id``."""
    return {
        "url": f"https://example.invalid/{entry_id}/{slug}",
        "kind": "primary",
        "title": "Example vendor advisory",
    }


def secondary_source(entry_id: str, slug: str = "coverage") -> dict[str, str]:
    return {
        "url": f"https://example.invalid/{entry_id}/{slug}",
        "kind": "secondary",
        "title": "Example news coverage",
    }


@pytest.fixture
def tmp_catalogue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Sandbox:
    """Point every script at a throwaway catalogue and return its paths."""
    root = tmp_path / "catalogue"
    entries_dir = root / "data" / "entries"
    entries_dir.mkdir(parents=True)
    sandbox = Sandbox(
        root=root,
        entries_dir=entries_dir,
        readme_path=root / "README.md",
        dist_path=root / "dist" / "entries.json",
    )
    sandbox.write_readme(README_SKELETON)
    # The docs a generated page links back to must exist in the sandbox, or
    # a test that checks those links resolve would fail for a reason that has
    # nothing to do with the code under test.
    sandbox.docs_dir.mkdir(parents=True, exist_ok=True)
    for doc in ("TIERS.md", "METHODOLOGY.md", "TAXONOMY.md"):
        (sandbox.docs_dir / doc).write_text(f"# {doc}\n", encoding="utf-8")

    for module in (entries_module, LEGACY_ENTRIES_MODULE):
        monkeypatch.setattr(module, "ENTRY_DIR", entries_dir)
        monkeypatch.setattr(module, "REPO_ROOT", root)
    monkeypatch.setattr(validate_module, "ENTRY_DIR", entries_dir)
    monkeypatch.setattr(validate_module, "_REPO_ROOT", str(root))
    monkeypatch.setattr(stats_module, "ENTRY_DIR", entries_dir)
    monkeypatch.setattr(build_module, "README_PATH", sandbox.readme_path)
    monkeypatch.setattr(build_module, "DIST_PATH", sandbox.dist_path)
    # The page and SVG paths derive from build.REPO_ROOT at call time, so
    # redirecting it is what keeps generated pages out of the real docs/.
    monkeypatch.setattr(build_module, "REPO_ROOT", root)
    return sandbox


@pytest.fixture
def entry_factory(tmp_catalogue: Sandbox) -> Callable[..., Path]:
    """Write one synthetic entry YAML and return its path.

    The default entry is schema-valid and clean under every validator rule.
    Keyword arguments override a single field, so a test can perturb exactly
    one thing; ``filename`` and ``comment`` control the file name and leading
    YAML comments. ``last_verified`` defaults to today and ``date`` to a fixed
    past date, never the other way round.
    """
    defaults = _EntryDefaults()

    def make(entry_id: str = "synthetic-entry", **overrides: Any) -> Path:
        data = dict(vars(defaults))
        data["id"] = entry_id
        data["sources"] = [primary_source(entry_id)]

        resolved_id = str(overrides.pop("id", entry_id))
        filename = overrides.pop("filename", None)
        comment = overrides.pop("comment", None)
        data.update(overrides)
        data["id"] = resolved_id

        # A tier 1 entry must clear the evidence lint to be clean, so the
        # baseline impact carries the vocabulary whenever the test did not
        # supply its own impact text.
        if data["tier"] == 1 and "impact" not in overrides:
            data["impact"] = EVIDENCE_IMPACT

        text = yaml.safe_dump(
            _ordered(data),
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=False,
        )
        if comment:
            text = "".join(f"# {line}\n" for line in comment.splitlines()) + text
        path = tmp_catalogue.entries_dir / f"{filename or resolved_id}.yml"
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    return make


@pytest.fixture
def real_entries() -> list[Entry]:
    """The shipped catalogue, loaded from the real entry directory."""
    return [load_entry(path) for path in sorted(REAL_ENTRY_DIR.glob("*.yml"))]


@pytest.fixture
def schema() -> dict[str, Any]:
    """The shipped JSON Schema."""
    return entries_module.load_schema()


@pytest.fixture
def attack_classes(schema: dict[str, Any]) -> list[str]:
    """The attack_class enum in schema order, checked against the pinned copy."""
    enum = list(schema["properties"]["attack_class"]["enum"])
    assert tuple(enum) == ATTACK_CLASSES
    return enum


@pytest.fixture
def run_validate(capsys: pytest.CaptureFixture[str]) -> Callable[..., ValidationRun]:
    """Run ``scripts.validate.main`` and capture both its code and its output."""

    def run(*argv: str, json_output: bool = True) -> ValidationRun:
        args = list(argv)
        if json_output:
            args.insert(0, "--json")
        code = validate_module.main(args)
        out = capsys.readouterr().out
        report = json.loads(out) if json_output else None
        return ValidationRun(code=code, report=report, text=out)

    return run


@pytest.fixture
def run_stats(capsys: pytest.CaptureFixture[str]) -> Callable[..., tuple[int, Any]]:
    """Run ``scripts/stats.main --json`` and return the parsed report."""

    def run(*argv: str) -> tuple[int, Any]:
        code = stats_module.main(["--json", *argv])
        out = capsys.readouterr().out
        return code, json.loads(out)

    return run


@pytest.fixture
def run_build(capsys: pytest.CaptureFixture[str]) -> Callable[..., tuple[int, str]]:
    """Run ``scripts/build.main`` and return its exit code and stdout."""

    def run(*argv: str) -> tuple[int, str]:
        code = build_module.main(list(argv))
        return code, capsys.readouterr().out

    return run


@pytest.fixture
def days_ago() -> Callable[[int], str]:
    """An ISO date ``count`` days before today. Never a hardcoded literal."""

    def shift(count: int) -> str:
        return (today() - timedelta(days=count)).isoformat()

    return shift


@pytest.fixture
def days_ahead() -> Callable[[int], str]:
    """An ISO date ``count`` days after today."""

    def shift(count: int) -> str:
        return (today() + timedelta(days=count)).isoformat()

    return shift


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Read a raw YAML mapping. Used by loader tests, not by fixtures."""
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise ValidationError(f"{path}: not a mapping")
    return parsed
