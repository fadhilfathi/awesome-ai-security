# Roadmap

Phases are checkable: each acceptance criterion below is a condition that can be
evaluated and either met or not met. Targets for entry counts are goals for
coverage, not quotas, and the anti-balance rule in `docs/METHODOLOGY.md` overrides
them whenever the evidence is not there.

## Branch protection policy

Direct pushes to `main` are permitted until the v1.0.0 phase (P5). At launch,
branch protection switches on and `main` becomes PR-only with required status
checks. This is recorded here as a roadmap item rather than assumed: before v1.0.0
there is no published history to protect, and blocking pushes during scaffolding
would only slow the build.

## P0 - Scaffolding

- Repository created with the agreed layout: `data/entries/`, `data/schema.json`,
  `scripts/`, `tests/`, `docs/`, `dist/`.
- `data/schema.json` defines all entry fields, with `additionalProperties: false`.
- `docs/TAXONOMY.md` defines all fifteen frozen attack classes, each with a
  definition, an inclusion test, a tie-break rule and a confusion boundary.
- `docs/TIERS.md` defines the three tiers with a minimum-evidence table and worked
  borderline examples.
- `docs/METHODOLOGY.md` states the per-entry verification procedure.
- `docs/REJECTED.md` exists with the rejection format established.
- README carries the generated-block markers the build fills.
- CI skeleton in place.
- **No content entries.** P0 ships structure only.

## P1 - Tooling and pipeline proof

- `scripts/validate.py`, `scripts/build.py` and `scripts/stats.py` exist, each
  runnable both as `python scripts/<name>.py` and as an importable `main()`.
- Tests have teeth, verified by mutation: break the validator in a specific way,
  confirm that a test fails for that reason, then revert. A test suite that has not
  been shown to fail is not accepted.
- Seeded with three entries that prove the pipeline end to end: validate, build,
  stats, and a committed `dist/entries.json` that matches generated output.
- README generated blocks fill from the entries and the counts come from script
  output, never from hand-editing.

## P2 - Tier 1 entries

- 15 Tier 1 entries, each verified from a fetched primary source per
  `docs/METHODOLOGY.md`, each with `last_verified` recorded.
- Each entry's `impact` states that the source confirms real exploitation or
  affected users and cites which source says so.
- Rejected candidates from this phase are counted, and the reasons are reported.
  The rejection count is a quality signal and is published, not minimised.
- Tier calls reviewed against the conservative rule; any entry that moved up a tier
  after review is called out.

## P3 - Tier 2 and Tier 3 entries

- 20 Tier 2 entries, verified the same way, each with a working proof of concept or
  a documented result against a named product or version as its basis.
- Then 10 Tier 3 entries, verified the same way, each with a source that describes
  the attack and no claim of a demonstrated exploit.
- Spot-checks run after each batch of 10 and the results reported.

## P4 - Publishing and ongoing verification

- `scripts/check_links.py` runs weekly on a schedule, and dead links produce an
  issue rather than a silent edit.
- README gains the attack class by evidence tier matrix.
- Contribution flow in place via issue forms, so candidates arrive in a shape that
  can be verified.
- `dist/entries.json` generated and committed, so downstream consumers can use the
  catalogue without parsing the repository.

## P5 - Launch hardening

- Branch protection on: `main` is PR-only with required checks (validator, build
  drift check, tests, link checker).
- README polished to the standard of the published catalogue, with the tier legend,
  the Tier 1 section and the matrix all reading clearly on its own.
- `SECURITY.md` published, covering how to report a security problem in the
  catalogue itself.
- Full re-verification pass: every entry's sources re-fetched and every `date`,
  `tier` and `cve` value re-checked against the source text.
- Release v1.0.0 with notes stating the tier counts as computed by the scripts and
  the count of rejections.

## Beyond v1.0

Known deferred work, recorded so it is not rediscovered later:

- Translations of the catalogue, with the same generated-block structure so
  translated sections stay in step with the English source.
- Per-entry detail pages, generated from the same entry files, for entries whose
  detail exceeds what a table row can carry.
- Tooling that tracks CVEs which reference catalogue entries, so a new CVE naming
  an already-listed product can be surfaced automatically.
- A machine-readable schema version field, so consumers can detect a breaking
  change to the entry format.

