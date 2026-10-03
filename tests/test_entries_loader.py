"""Loader tests: parse one file, expose its fields, keep order deterministic."""

from __future__ import annotations

import dataclasses
import datetime as _dt
import importlib
from pathlib import Path

import pytest
import yaml
from conftest import ATTACK_CLASSES, FIXED_DATE

from scripts import entries as entries_module
from scripts.entries import (
    Entry,
    ValidationError,
    load_all_entries,
    load_entry,
    load_schema,
)

FIXTURES = Path(__file__).parent / "fixtures"
VALID = FIXTURES / "valid-entry.yml"
PRIMARY_URL = "https://example.invalid/fixture-valid-entry/advisory"
SECONDARY_URL = "https://example.invalid/fixture-valid-entry/coverage"


def test_load_entry_parses_a_valid_fixture() -> None:
    entry = load_entry(VALID)
    assert entry.id == "fixture-valid-entry"
    assert entry.tier == 3
    assert entry.attack_class == "OTHER"
    assert entry.title == "Synthetic fixture entry about example-product"
    assert entry.last_verified == FIXED_DATE


def test_load_entry_splits_sources_by_kind() -> None:
    entry = load_entry(VALID)
    assert [s["kind"] for s in entry.primary_sources] == ["primary"]
    assert [s["kind"] for s in entry.secondary_sources] == ["secondary"]
    assert entry.primary_urls == [PRIMARY_URL]
    assert entry.source_urls == [PRIMARY_URL, SECONDARY_URL]


def test_load_entry_exposes_cve_and_lookup() -> None:
    entry = load_entry(VALID)
    assert entry.cve == ["CVE-2026-00000"]
    assert entry["target"] == "example-product"
    assert entry.get("no-such-key", "fallback") == "fallback"
    assert entry.get("no-such-key") is None


@pytest.mark.parametrize(
    ("filename", "expected_fragment"),
    [
        ("empty-entry.yml", "file is empty"),
        ("bare-list-entry.yml", "top level must be a mapping"),
        ("invalid-yaml-entry.yml", "invalid YAML"),
    ],
)
def test_load_entry_rejects_unusable_files(
    filename: str, expected_fragment: str
) -> None:
    with pytest.raises(ValidationError) as caught:
        load_entry(FIXTURES / filename)
    assert expected_fragment in str(caught.value)
    assert str(FIXTURES / filename) in str(caught.value)


def test_load_entry_rejects_a_missing_file() -> None:
    with pytest.raises(ValidationError, match="cannot read file"):
        load_entry(FIXTURES / "no-such-entry.yml")


def test_last_verified_date_parses_iso_and_rejects_junk(tmp_path: Path) -> None:
    good = load_entry(_write(tmp_path, "good", "last_verified: '2024-05-06'"))
    assert good.last_verified_date == _dt.date(2024, 5, 6)

    for index, raw in enumerate(("not-a-date", "2024-13-01", "", "2024-05")):
        bad = load_entry(_write(tmp_path, f"bad-{index}", f"last_verified: '{raw}'"))
        assert bad.last_verified_date is None, raw


def test_last_verified_date_also_accepts_the_basic_format(tmp_path: Path) -> None:
    """date.fromisoformat on 3.11 accepts YYYYMMDD too, so this property is
    laxer than the schema's date pattern. The schema is the enforcing layer;
    pinning the leniency keeps it from changing unnoticed."""
    entry = load_entry(_write(tmp_path, "compact", "last_verified: '20240506'"))
    assert entry.last_verified_date == _dt.date(2024, 5, 6)


def test_entry_properties_tolerate_missing_and_wrong_typed_fields() -> None:
    data = {"id": "x", "tier": "not-an-int", "sources": "not-a-list", "cve": "nope"}
    entry = Entry(path=Path("x.yml"), data=data)
    assert entry.tier == 0
    assert entry.attack_class == ""
    assert entry.sources == []
    assert entry.primary_sources == []
    assert entry.secondary_sources == []
    assert entry.source_urls == []
    assert entry.primary_urls == []
    assert entry.cve == []
    assert entry.last_verified == ""
    assert entry.last_verified_date is None


def test_load_schema_exposes_properties_and_the_full_enum() -> None:
    schema = load_schema()
    assert "properties" in schema
    enum = schema["properties"]["attack_class"]["enum"]
    assert len(enum) == 15
    assert tuple(enum) == ATTACK_CLASSES
    assert set(schema["properties"]["tier"]["enum"]) == {1, 2, 3}


def test_load_all_entries_is_sorted_and_stable(tmp_catalogue) -> None:
    for stem in ("zeta-entry", "alpha-entry", "mid-entry"):
        (tmp_catalogue.entries_dir / f"{stem}.yml").write_text(
            _minimal(stem), encoding="utf-8"
        )

    first = load_all_entries()
    second = load_all_entries()
    assert [e.id for e in first] == ["alpha-entry", "mid-entry", "zeta-entry"]
    assert [e.path for e in first] == [e.path for e in second]
    assert [e.path.name for e in first] == [
        "alpha-entry.yml",
        "mid-entry.yml",
        "zeta-entry.yml",
    ]


def test_entry_files_takes_only_yml(tmp_catalogue) -> None:
    entries_dir = tmp_catalogue.entries_dir
    (entries_dir / "real-entry.yml").write_text(
        _minimal("real-entry"), encoding="utf-8"
    )
    (entries_dir / "notes.md").write_text("ignored", encoding="utf-8")
    (entries_dir / "real-entry.yaml").write_text(_minimal("other"), encoding="utf-8")
    assert [p.name for p in entries_module.entry_files()] == ["real-entry.yml"]


def test_entry_attribute_assignment_raises_frozen_error() -> None:
    entry = load_entry(VALID)
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.id = "renamed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.data = {}  # type: ignore[misc]
    assert entry.id == "fixture-valid-entry"


def test_entry_data_mapping_is_shallowly_mutable() -> None:
    """A frozen dataclass blocks attribute rebinding, not dict mutation.

    Pinned deliberately: the loader promises a read-only *view* of the parsed
    mapping, not a deep-immutable object. If the loader ever starts freezing
    or deep-copying the mapping, this is the test to revisit.
    """
    entry = load_entry(VALID)
    entry.data["extra_key"] = "added-by-test"
    assert entry.get("extra_key") == "added-by-test"


def test_today_is_a_real_date() -> None:
    assert isinstance(entries_module.today(), _dt.date)


def test_build_module_owns_a_separate_entries_module() -> None:
    """Documents the dual-import layout that ``tmp_catalogue`` relies on.

    ``scripts/build.py`` imports the top-level ``entries`` while the other
    scripts import ``scripts.entries``. The two module objects are distinct,
    each with its own ``ENTRY_DIR``, and their ``Entry`` classes are distinct
    too. Patching only one of them would leave the other reading the real
    catalogue, so the fixture patches both.
    """
    legacy = importlib.import_module("entries")
    assert legacy is not entries_module
    assert legacy.Entry is not entries_module.Entry
    assert legacy.ENTRY_DIR is not entries_module.ENTRY_DIR
    legacy_entry = legacy.load_entry(VALID)
    assert isinstance(legacy_entry, legacy.Entry)
    assert not isinstance(legacy_entry, entries_module.Entry)


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / f"{name}.yml"
    path.write_text(body, encoding="utf-8")
    return path


def _minimal(entry_id: str) -> str:
    return yaml.safe_dump({"id": entry_id}, sort_keys=False)
