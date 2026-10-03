# awesome-ai-security -- developer entry points.
#
# POSIX make. Recipe lines are indented with real tabs. Every script is
# invoked the same way: `uv run python scripts/<name>.py`.

PYTHON := uv run python

.DEFAULT_GOAL := all
.PHONY: all sync validate build stats links test lint format gate clean

## all: install deps, then run the full gate.
all: sync gate

## sync: install runtime + dev dependencies into .venv.
sync:
	uv sync --group dev

## validate: check every entry against the schema and the tier rules.
validate:
	$(PYTHON) scripts/validate.py

## build: regenerate dist/entries.json and the README generated blocks.
build:
	$(PYTHON) scripts/build.py

## stats: print catalogue statistics.
stats:
	$(PYTHON) scripts/stats.py

## links: check every source URL (uses the network).
links:
	$(PYTHON) scripts/check_links.py

## test: run the test suite.
test:
	$(PYTHON) -m pytest

## lint: ruff lint.
lint:
	$(PYTHON) -m ruff check .

## format: ruff format in place.
format:
	$(PYTHON) -m ruff format .

## gate: what CI enforces -- lint, test, validate, and no generated drift.
# `build` deliberately does NOT run here: it writes files, which would make the
# drift check below vacuously true. `gate` is a gate, so it only reads.
gate: lint test validate check-generated

## check-generated: fail if the committed generated output is stale.
check-generated:
	$(PYTHON) scripts/build.py --check

## clean: remove local caches.
clean:
	rm -rf .pytest_cache .ruff_cache