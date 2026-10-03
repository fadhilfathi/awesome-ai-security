# Pull request

One entry per PR, or a tooling-only change. A PR that adds several entries
gets split  -  one entry is easier to verify against one primary source.

## Before you open it

```bash
uv sync --group dev --locked
uv run python scripts/validate.py
uv run python scripts/build.py          # regenerates README sections + dist/entries.json
uv run pytest -q
```

## Checklist

- [ ] `data/entries/<id>.yml` validates against `data/schema.json`
      (`scripts/validate.py` passes), or the change is tooling-only and touches
      no entry.
- [ ] I read the primary source for every entry in this PR. No entry was added
      from memory, from a summary, or from a secondary source alone.
- [ ] Entry text is in my own words. No paragraph was copied from a source.
- [ ] CVE ids, product names, dates, and counts come from the source. Nothing
      was inferred or rounded.
- [ ] Generated files were rebuilt and committed: `dist/entries.json` and the
      marked sections of `README.md` match what `scripts/build.py` produces.
      Nothing inside a `<!-- BEGIN/END:GENERATED -->` block was hand edited.
- [ ] Tier is the lowest the evidence supports, and a Tier 1 entry cites a
      source that states real exploitation or affected users.
- [ ] If `uv.lock` changed, it is committed alongside `pyproject.toml`.
- [ ] No `Co-Authored-By` trailer, no tool attribution, no generated-by footer
      in the commit message or in the files.

CI must be green before merge: schema validation, generated-output drift,
ruff lint, ruff format, and tests all run as required checks and none of them
are allowed to fail soft.
