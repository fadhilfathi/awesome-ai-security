"""Statistics tests.

Expectations here are hand-computed from the fixture contents written in each
test, not recomputed by calling the production code under test. A test that
derives its own expectation with the same function it is checking proves
nothing.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from conftest import ATTACK_CLASSES, EVIDENCE_IMPACT, Sandbox

from scripts.build import ATTACK_CLASS_LABELS
from scripts.stats import DEFAULT_MAX_AGE_DAYS, TIERS, attack_classes

Factory = Callable[..., Path]

#: build.py's ATTACK_CLASS_LABELS map is written in taxonomy order, which is a
#: different sequence from the schema enum. stats.py reports schema order.
BUILD_LABEL_ORDER = tuple(ATTACK_CLASS_LABELS)

StatsRun = Callable[..., tuple[int, Any]]

REPORT_KEYS = {
    "total_entries",
    "by_tier",
    "by_attack_class",
    "matrix_attack_class_by_tier",
    "attack_class_order",
    "tier_order",
    "distinct_cve_ids",
    "entries_with_cve",
    "distinct_primary_source_urls",
    "oldest_date",
    "newest_date",
    "oldest_last_verified",
    "newest_last_verified",
    "stale_entries",
    "max_age_days",
    "generated_on",
}


def source(url: str, kind: str = "primary", title: str = "Synthetic source") -> dict:
    return {"url": url, "kind": kind, "title": title}


# --------------------------------------------------------------------------
# empty catalogue
# --------------------------------------------------------------------------


def test_empty_catalogue_produces_zeros_not_a_crash(
    tmp_catalogue: Sandbox, run_stats: StatsRun
) -> None:
    code, stats = run_stats()
    assert code == 0
    assert set(stats) == REPORT_KEYS
    assert stats["total_entries"] == 0
    assert stats["by_tier"] == {"1": 0, "2": 0, "3": 0}
    assert stats["by_attack_class"] == {name: 0 for name in ATTACK_CLASSES}
    assert stats["matrix_attack_class_by_tier"] == {
        name: {"1": 0, "2": 0, "3": 0} for name in ATTACK_CLASSES
    }
    assert stats["distinct_cve_ids"] == 0
    assert stats["entries_with_cve"] == 0
    assert stats["distinct_primary_source_urls"] == 0
    assert stats["stale_entries"] == 0
    assert stats["max_age_days"] == DEFAULT_MAX_AGE_DAYS


def test_empty_catalogue_date_fields_are_none_not_zero(
    tmp_catalogue: Sandbox, run_stats: StatsRun
) -> None:
    """A zero would be a wrong type for a date field, not merely a wrong value."""
    _, stats = run_stats()
    for key in (
        "oldest_date",
        "newest_date",
        "oldest_last_verified",
        "newest_last_verified",
    ):
        assert stats[key] is None, key
        assert not isinstance(stats[key], int), key


def test_empty_catalogue_text_report_renders(run_stats: StatsRun) -> None:
    from scripts.stats import render_text

    _, stats = run_stats()
    text = render_text(stats)
    assert "total entries" in text
    assert "oldest disclosure date" in text
    # A None date renders as a dash, never as "None".
    assert "None" not in text


# --------------------------------------------------------------------------
# hand-computed expectations over a known fixture
# --------------------------------------------------------------------------


def test_counts_match_a_hand_computed_fixture(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    """Six entries, every field written out by hand below.

    id              tier  class                    cve           date
    --------------  ----  -----------------------  ------------  ---------
    alpha-entry     1     PROMPT_INJECTION_DIRECT  00000, 00001  2020-01-05
    beta-entry      1     PROMPT_INJECTION_DIRECT  00001         2021-03-09
    gamma-entry     2     TOOL_POISONING           none          2020-07
    delta-entry     2     TOOL_POISONING           none          2019-11-20
    epsilon-entry   3     OTHER                    00002         2022-01-31
    zeta-entry      3     JAILBREAK                none          2020-01-01

    Totals: 6 entries; tiers 1=2 2=2 3=2; distinct CVE ids 3; entries
    carrying a CVE 3; distinct primary URLs 6. Every entry declares an
    explicit date, so the extremes are unambiguous.
    """
    entry_factory(
        "alpha-entry",
        tier=1,
        attack_class="PROMPT_INJECTION_DIRECT",
        cve=["CVE-2026-00000", "CVE-2026-00001"],
        date="2020-01-05",
    )
    entry_factory(
        "beta-entry",
        tier=1,
        attack_class="PROMPT_INJECTION_DIRECT",
        cve=["CVE-2026-00001"],
        date="2021-03-09",
    )
    entry_factory(
        "gamma-entry",
        tier=2,
        attack_class="TOOL_POISONING",
        date="2020-07",
    )
    entry_factory(
        "delta-entry",
        tier=2,
        attack_class="TOOL_POISONING",
        date="2019-11-20",
    )
    entry_factory(
        "epsilon-entry",
        tier=3,
        attack_class="OTHER",
        cve=["CVE-2026-00002"],
        date="2022-01-31",
    )
    entry_factory("zeta-entry", tier=3, attack_class="JAILBREAK", date="2020-01-01")

    _, stats = run_stats()

    assert stats["total_entries"] == 6
    assert stats["by_tier"] == {"1": 2, "2": 2, "3": 2}
    assert stats["by_attack_class"]["PROMPT_INJECTION_DIRECT"] == 2
    assert stats["by_attack_class"]["TOOL_POISONING"] == 2
    assert stats["by_attack_class"]["OTHER"] == 1
    assert stats["by_attack_class"]["JAILBREAK"] == 1
    assert stats["by_attack_class"]["DENIAL_OF_SERVICE"] == 0

    assert stats["distinct_cve_ids"] == 3
    assert stats["entries_with_cve"] == 3
    assert stats["distinct_primary_source_urls"] == 6

    # String comparison, so month-only values order by their own text.
    assert stats["oldest_date"] == "2019-11-20"
    assert stats["newest_date"] == "2022-01-31"


def test_matrix_counts_match_the_hand_computed_fixture(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", tier=1, attack_class="PROMPT_INJECTION_DIRECT")
    entry_factory("beta-entry", tier=1, attack_class="PROMPT_INJECTION_DIRECT")
    entry_factory("gamma-entry", tier=2, attack_class="PROMPT_INJECTION_DIRECT")
    entry_factory("delta-entry", tier=2, attack_class="TOOL_POISONING")
    entry_factory("epsilon-entry", tier=3, attack_class="TOOL_POISONING")
    entry_factory("zeta-entry", tier=3, attack_class="TOOL_POISONING")

    _, stats = run_stats()
    matrix = stats["matrix_attack_class_by_tier"]
    assert matrix["PROMPT_INJECTION_DIRECT"] == {"1": 2, "2": 1, "3": 0}
    assert matrix["TOOL_POISONING"] == {"1": 0, "2": 1, "3": 2}
    assert matrix["JAILBREAK"] == {"1": 0, "2": 0, "3": 0}


# --------------------------------------------------------------------------
# structural invariants
# --------------------------------------------------------------------------


def test_every_attack_class_appears_with_zero_when_absent(
    tmp_catalogue: Sandbox, run_stats: StatsRun
) -> None:
    _, stats = run_stats()
    assert stats["by_attack_class"] == {name: 0 for name in ATTACK_CLASSES}
    assert len(stats["by_attack_class"]) == 15
    assert set(stats["by_attack_class"].values()) == {0}
    assert set(stats["matrix_attack_class_by_tier"]) == set(ATTACK_CLASSES)
    assert all(
        cells == {"1": 0, "2": 0, "3": 0}
        for cells in stats["matrix_attack_class_by_tier"].values()
    )


def test_class_and_tier_order_come_from_the_schema(run_stats: StatsRun) -> None:
    _, stats = run_stats()
    assert stats["attack_class_order"] == list(ATTACK_CLASSES)
    assert stats["attack_class_order"] == attack_classes()
    assert stats["tier_order"] == [str(tier) for tier in TIERS]
    assert stats["tier_order"] == ["1", "2", "3"]
    # --json is emitted with sort_keys=True, so key order in the serialised
    # object is alphabetical. attack_class_order exists precisely so a
    # consumer can recover the schema sequence without relying on that.
    # Pinned so the difference is never mistaken for an accident.
    assert list(stats["by_attack_class"]) == sorted(ATTACK_CLASSES)
    assert list(stats["matrix_attack_class_by_tier"]) == sorted(ATTACK_CLASSES)
    assert list(stats["by_attack_class"]) != stats["attack_class_order"]
    assert set(stats["by_attack_class"]) == set(stats["attack_class_order"])


def test_matrix_row_sums_equal_the_per_class_totals(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", tier=1, attack_class="PROMPT_INJECTION_DIRECT")
    entry_factory("beta-entry", tier=2, attack_class="PROMPT_INJECTION_DIRECT")
    entry_factory("gamma-entry", tier=3, attack_class="OTHER")
    _, stats = run_stats()
    for name, cells in stats["matrix_attack_class_by_tier"].items():
        assert sum(cells.values()) == stats["by_attack_class"][name], name


def test_every_count_sums_to_the_total(
    tmp_catalogue, entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", tier=1, attack_class="JAILBREAK")
    entry_factory("beta-entry", tier=1, attack_class="JAILBREAK")
    entry_factory("gamma-entry", tier=2, attack_class="OTHER")
    entry_factory("delta-entry", tier=3, attack_class="CREDENTIAL_EXPOSURE")
    _, stats = run_stats()
    assert sum(stats["by_tier"].values()) == stats["total_entries"] == 4
    assert sum(stats["by_attack_class"].values()) == stats["total_entries"]
    assert (
        sum(
            sum(cells.values())
            for cells in stats["matrix_attack_class_by_tier"].values()
        )
        == stats["total_entries"]
    )
    for tier in stats["tier_order"]:
        assert (
            sum(cells[tier] for cells in stats["matrix_attack_class_by_tier"].values())
            == stats["by_tier"][tier]
        )


def test_an_unlisted_attack_class_is_counted_in_the_total_only(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    """A class outside the enum cannot be labelled, so it drops out of the
    per-class map but not the headline total. Pinned so the discrepancy is
    never mistaken for a correct report."""
    entry_factory("alpha-entry", tier=2, attack_class="NOT_IN_THE_ENUM")
    _, stats = run_stats()
    assert stats["total_entries"] == 1
    assert sum(stats["by_attack_class"].values()) == 0
    assert stats["by_tier"]["2"] == 1


def test_an_out_of_range_tier_is_counted_in_the_total_only(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", tier=9)
    _, stats = run_stats()
    assert stats["total_entries"] == 1
    assert sum(stats["by_tier"].values()) == 0


# --------------------------------------------------------------------------
# CVE accounting
# --------------------------------------------------------------------------


def test_distinct_cve_ids_and_entries_with_cve_are_different_numbers(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", cve=["CVE-2026-00000"])
    entry_factory("beta-entry", cve=["CVE-2026-00000"])
    entry_factory("gamma-entry", cve=["CVE-2026-00001"])
    entry_factory("delta-entry")

    _, stats = run_stats()
    # Four entries, three carry at least one CVE...
    assert stats["entries_with_cve"] == 3
    # ...but those CVEs name only two distinct identifiers, because alpha
    # and beta both cite CVE-2026-00000.
    assert stats["distinct_cve_ids"] == 2
    assert stats["entries_with_cve"] != stats["distinct_cve_ids"]


def test_entries_with_cve_ignores_an_empty_cve_list(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", cve=[])
    _, stats = run_stats()
    assert stats["entries_with_cve"] == 0
    assert stats["distinct_cve_ids"] == 0


def test_distinct_primary_urls_ignores_secondary_urls(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory(
        "alpha-entry", sources=[source("https://example.invalid/alpha/primary")]
    )
    entry_factory(
        "beta-entry",
        sources=[
            source("https://example.invalid/beta/primary"),
            source("https://example.invalid/beta/secondary", "secondary"),
        ],
    )
    _, stats = run_stats()
    assert stats["distinct_primary_source_urls"] == 2


def test_distinct_primary_urls_deduplicates_shared_urls(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", sources=[source("https://example.invalid/shared")])
    entry_factory("beta-entry", sources=[source("https://example.invalid/shared")])
    _, stats = run_stats()
    assert stats["total_entries"] == 2
    assert stats["distinct_primary_source_urls"] == 1


# --------------------------------------------------------------------------
# dates
# --------------------------------------------------------------------------


def test_oldest_and_newest_dates_are_min_and_max_over_the_data(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    for index, date in enumerate(
        ["2020-01-05", "2019-11-20", "2022-01-31", "2021-03-09"]
    ):
        entry_factory(f"entry-{index}", date=date)
    _, stats = run_stats()
    assert stats["oldest_date"] == "2019-11-20"
    assert stats["newest_date"] == "2022-01-31"


def test_a_month_only_date_is_accepted_without_crashing(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("month-only-entry", date="2020-07")
    _, stats = run_stats()
    assert stats["newest_date"] == "2020-07"
    assert stats["oldest_date"] == "2020-07"


def test_a_month_only_date_mixes_with_full_dates(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    """min/max run over the raw strings; "2020-07" sorts after "2020-06-30"
    and before "2020-07-15", which is the documented text ordering."""
    entry_factory("a", date="2020-06-30")
    entry_factory("b", date="2020-07")
    entry_factory("c", date="2020-07-15")
    _, stats = run_stats()
    assert stats["oldest_date"] == "2020-06-30"
    assert stats["newest_date"] == "2020-07-15"


def test_an_absent_date_key_is_excluded_from_the_extremes(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    """The default factory always writes a date, so the key is deleted to
    model an entry that genuinely has none."""
    import yaml

    path = entry_factory("undated-entry")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    del data["date"]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    entry_factory("dated-entry", date="2019-11-20")
    _, stats = run_stats()
    assert stats["total_entries"] == 2
    assert stats["oldest_date"] == "2019-11-20"
    assert stats["newest_date"] == "2019-11-20"


def test_last_verified_extremes_ignore_unparseable_values(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", last_verified="2019-11-20")
    entry_factory("beta-entry", last_verified="2022-01-31")
    entry_factory("gamma-entry", last_verified="not-a-date")
    _, stats = run_stats()
    assert stats["oldest_last_verified"] == "2019-11-20"
    assert stats["newest_last_verified"] == "2022-01-31"


def test_an_unparseable_last_verified_is_never_counted_stale(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("alpha-entry", last_verified="not-a-date")
    _, stats = run_stats("--max-age-days", "1")
    assert stats["stale_entries"] == 0
    assert stats["oldest_last_verified"] is None


# --------------------------------------------------------------------------
# staleness
# --------------------------------------------------------------------------


def test_stale_entries_counts_only_past_the_horizon(
    entry_factory: Factory, run_stats: StatsRun, days_ago
) -> None:
    entry_factory("fresh-entry", last_verified=days_ago(10))
    entry_factory("stale-one", last_verified=days_ago(400))
    entry_factory("stale-two", last_verified=days_ago(1000))
    entry_factory("undated-entry", last_verified="not-a-date")

    _, default_horizon = run_stats()
    assert default_horizon["stale_entries"] == 2
    assert default_horizon["max_age_days"] == 365

    _, narrow = run_stats("--max-age-days", "30")
    assert narrow["stale_entries"] == 2
    assert narrow["max_age_days"] == 30

    _, wide = run_stats("--max-age-days", "5000")
    assert wide["stale_entries"] == 0


def test_the_staleness_horizon_boundary_is_inclusive(
    entry_factory: Factory, run_stats: StatsRun, days_ago
) -> None:
    entry_factory("boundary-entry", last_verified=days_ago(100))
    _, exact = run_stats("--max-age-days", "100")
    assert exact["stale_entries"] == 0
    _, tighter = run_stats("--max-age-days", "99")
    assert tighter["stale_entries"] == 1


# --------------------------------------------------------------------------
# report shape
# --------------------------------------------------------------------------


def test_generated_on_is_todays_date(
    tmp_catalogue, entry_factory: Factory, run_stats: StatsRun
) -> None:
    from scripts.entries import today

    entry_factory("synthetic-entry")
    _, stats = run_stats()
    assert stats["generated_on"] == today().isoformat()


def test_json_output_is_the_documented_shape(
    entry_factory: Factory, run_stats: StatsRun
) -> None:
    entry_factory("synthetic-entry", tier=1, impact=EVIDENCE_IMPACT)
    _, stats = run_stats()
    assert set(stats) == REPORT_KEYS
    json.dumps(stats)


def test_text_report_names_every_section(run_stats: StatsRun) -> None:
    import scripts.stats as stats_module

    _, stats = run_stats()
    text = stats_module.render_text(stats)
    for heading in (
        "awesome-ai-security catalogue statistics",
        "Totals",
        "Entries per evidence tier",
        "Entries per attack class",
        "Attack class x evidence tier",
        "Date coverage",
    ):
        assert heading in text


def test_attack_classes_reads_the_schema_enum(schema: dict) -> None:
    assert attack_classes() == list(schema["properties"]["attack_class"]["enum"])
    assert len(attack_classes()) == 15


# --------------------------------------------------------------------------
# real catalogue
# --------------------------------------------------------------------------


def test_the_real_catalogue_reports_consistently(real_entries: list[Any]) -> None:
    import scripts.stats as stats_module

    stats = stats_module.compute_stats()
    assert stats["total_entries"] == len(real_entries)
    assert sum(stats["by_tier"].values()) == stats["total_entries"]
    assert sum(stats["by_attack_class"].values()) == stats["total_entries"]
    # The tier keys are fixed by the schema, not by whatever happens to be
    # filed, so every tier is represented even when it holds zero entries.
    assert set(stats["by_tier"]) == {"1", "2", "3"}
    # Invariants that must hold for any catalogue, however small or large.
    assert stats["entries_with_cve"] <= stats["total_entries"]
    assert stats["distinct_cve_ids"] >= 0
    if stats["total_entries"] == 0:
        assert stats["oldest_date"] is None
