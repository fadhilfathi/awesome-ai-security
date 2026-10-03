"""Check every source URL in the catalogue over HTTP.

This is the only script in the repository that touches the network. It exists
so that a dead advisory link is caught, not because a link checker proves an
entry true. Results are advisory: the exit code reflects what --fail-on asks
for, and the worst case is classified `unknown` rather than `broken` so that a
flaky network never masquerades as a broken reference.

Usage:
    python scripts/check_links.py
    python scripts/check_links.py --jobs 16 --timeout 30 --fail-on any
    python scripts/check_links.py --json
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from entries import Entry, load_all_entries  # noqa: E402

DEFAULT_USER_AGENT = (
    "awesome-ai-security-linkcheck/1.0 "
    "(+https://github.com/fadhilfathi/awesome-ai-security)"
)
DEFAULT_STATE_PATH = _SCRIPTS_DIR.parent / ".linkcheck-state.json"
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
TRANSIENT_STATUSES = frozenset({429, 500, 502, 503, 504, 507, 509})
# Statuses that mean "the host disliked this request shape", which a ranged
# GET is the right answer to. 403 and 405 are not evidence of a dead link.
RANGE_RETRY_CODES = frozenset({403, 405})
BACKOFF_BASE_SECONDS = 2.0


@dataclass(frozen=True)
class Result:
    """One URL's outcome."""

    url: str
    status: str  # ok | redirect | broken | unknown
    code: int | None = None
    final_url: str | None = None
    detail: str = ""

    @property
    def failed(self) -> bool:
        return self.status in {"broken", "unknown"}


@dataclass
class Checked:
    """A URL paired with the entries that cite it."""

    url: str
    entry_ids: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# entry collection
# --------------------------------------------------------------------------


def collect_targets(entries: list[Entry]) -> list[Checked]:
    """Every source URL, deduplicated, with the entries that cite each."""
    targets: dict[str, Checked] = {}
    for entry in entries:
        for url in entry.source_urls:
            target = targets.setdefault(url, Checked(url=url))
            if entry.id not in target.entry_ids:
                target.entry_ids.append(entry.id)
    return [targets[url] for url in sorted(targets)]


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop at the redirect so the final URL can be recorded, not guessed."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102, ANN001
        raise _Redirect(newurl, code)


class _Redirect(Exception):
    def __init__(self, newurl: str, code: int) -> None:
        super().__init__(newurl)
        self.newurl = newurl
        self.code = code


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_NoRedirect)


def _request(url: str, *, timeout: float, ranged: bool) -> urllib.request.Request:
    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "*/*",
    }
    if ranged:
        headers["Range"] = "bytes=0-0"
    return urllib.request.Request(url, headers=headers, method="GET")


def _describe(exc: BaseException) -> tuple[str, int | None, str]:
    """Map an exception onto (classification, status code, human detail)."""
    if isinstance(exc, urllib.error.HTTPError):
        code = exc.code
        detail = f"{code} {exc.reason or ''}".strip()
        if code in REDIRECT_STATUSES:
            return "redirect", code, detail
        if code in TRANSIENT_STATUSES:
            return "unknown", code, detail
        if code in RANGE_RETRY_CODES:
            # 403 and 405 are a host refusing the request shape, not a
            # vanished document. Believe it only once a ranged GET is
            # refused too; check_url turns that into "broken".
            return "deferred", code, detail
        if 400 <= code < 500:
            return "broken", code, detail
        return "unknown", code, detail
    if isinstance(exc, urllib.error.URLError):
        return "unknown", None, _reason(exc.reason)
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "unknown", None, "timed out"
    return "unknown", None, f"{type(exc).__name__}: {exc}"


def _reason(reason: Any) -> str:
    if isinstance(reason, ssl.SSLError):
        return f"TLS error: {reason}"
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return "timed out"
    return str(reason)


def _absolute(base: str, location: str) -> str:
    return urllib.parse.urljoin(base, location) if location else base


def check_url(url: str, *, timeout: float = 20.0, retries: int = 2) -> Result:
    """Fetch one URL, retrying only failures that could plausibly be transient.

    A plain GET goes first: a large share of advisory hosts answer a request
    they consider too heavy with 403 or 405 while serving the document itself
    perfectly well. Those two get exactly one retry as a ranged GET, which
    asks for a single byte and so costs nothing on a large PDF; if the host
    refuses that too, the link is genuinely broken. Timeouts, TLS, DNS and
    429/5xx are retried with backoff, up to --retries times.
    """
    opener = _opener()
    attempts = max(1, retries + 1)
    result = Result(url=url, status="unknown", detail="not attempted")
    use_range = False

    for attempt in range(attempts):
        try:
            with opener.open(
                _request(url, timeout=timeout, ranged=use_range),
                timeout=timeout,
            ) as response:
                final = response.geturl()
                if final != url:
                    return Result(url, "redirect", response.status, final)
                return Result(url, "ok", response.status, final)
        except _Redirect as exc:
            return Result(url, "redirect", exc.code, _absolute(url, exc.newurl))
        except Exception as exc:  # noqa: BLE001 - every failure is classified
            status, code, detail = _describe(exc)
            if status == "deferred":
                if not use_range:
                    use_range = True
                    continue  # a different request shape, not a different host
                status, detail = "broken", f"{detail} (ranged GET also refused)"
            result = Result(url=url, status=status, code=code, detail=detail)
            if status == "broken" or attempt == attempts - 1:
                return result
            time.sleep(BACKOFF_BASE_SECONDS**attempt)

    return result


def check_all(
    targets: list[Checked], *, jobs: int = 8, timeout: float = 20.0, retries: int = 2
) -> list[tuple[Checked, Result]]:
    """Check every target, bounded concurrency, results in input order."""
    if not targets:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = {
            pool.submit(check_url, t.url, timeout=timeout, retries=retries): t
            for t in targets
        }
        collected: list[tuple[Checked, Result]] = []
        for future in concurrent.futures.as_completed(futures):
            target = futures[future]
            try:
                collected.append((target, future.result()))
            except Exception as exc:  # noqa: BLE001 - a crash is unknown
                failed = Result(target.url, "unknown", detail=str(exc))
                collected.append((target, failed))
    order = {target.url: i for i, target in enumerate(targets)}
    collected.sort(key=lambda pair: order[pair[0].url])
    return collected


# --------------------------------------------------------------------------
# state
# --------------------------------------------------------------------------


def load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(path: Path, results: list[tuple[Checked, Result]]) -> None:
    payload = {
        "results": {
            target.url: {
                "status": result.status,
                "code": result.code,
                "final_url": result.final_url,
            }
            for target, result in results
        }
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        print(f"warning: could not write state file {path}: {exc}")


def was_known_bad(url: str, state: dict[str, Any]) -> bool:
    """True if this URL was already failing last run.

    A link that failed before and still fails is a real problem but not news,
    so it is reported as a repeat rather than a fresh break.
    """
    previous = state.get("results", {})
    if not isinstance(previous, dict):
        return False
    return isinstance(previous.get(url), dict)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def render_text(results: list[tuple[Checked, Result]], state: dict[str, Any]) -> str:
    order = {"ok": 0, "redirect": 1, "broken": 2, "unknown": 3}
    lines = []
    counts = {"ok": 0, "redirect": 0, "broken": 0, "unknown": 0}
    for target, result in sorted(results, key=lambda p: (order[p[1].status], p[0].url)):
        counts[result.status] += 1
        cite = ", ".join(sorted(target.entry_ids))
        note = result.detail
        if result.final_url and result.final_url != result.url:
            note = f"{note} -> {result.final_url}"
        repeat = result.failed and was_known_bad(result.url, state)
        lines.append(
            f"{result.status:<8} {result.url} [{cite}]{(' ; ' + note) if note else ''}"
            f"{' (repeat)' if repeat else ''}"
        )
    summary = "  ".join(f"{k}={v}" for k, v in counts.items())
    lines.append(f"checked {len(results)} url(s): {summary}")
    return "\n".join(lines)


def render_json(results: list[tuple[Checked, Result]], state: dict[str, Any]) -> str:
    payload = {
        "results": [
            {
                "url": target.url,
                "entry_ids": sorted(target.entry_ids),
                "status": result.status,
                "code": result.code,
                "final_url": result.final_url,
                "detail": result.detail,
                "repeat_failure": result.failed and was_known_bad(result.url, state),
            }
            for target, result in results
        ]
    }
    return json.dumps(payload, indent=2, sort_keys=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_links.py",
        description="Check every source URL in the catalogue over HTTP.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="per-request timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--jobs", type=int, default=8, help="concurrent requests (default: 8)"
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="retries for transient failures (default: 2)",
    )
    parser.add_argument(
        "--fail-on",
        choices=("broken", "any"),
        default="broken",
        help=(
            "exit 1 on broken links only, or on any failure including "
            "unknown (default: broken)"
        ),
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--state",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help=(
            "path to the last-known-good state file "
            f"(default: {DEFAULT_STATE_PATH.name})"
        ),
    )
    parser.add_argument(
        "--no-state",
        action="store_true",
        help="do not read or write the state file",
    )
    args = parser.parse_args(argv)

    targets = collect_targets(load_all_entries())
    if not targets:
        print("no source URLs to check.")
        return 0

    state = {} if args.no_state else load_state(args.state)
    results = check_all(
        targets, jobs=args.jobs, timeout=args.timeout, retries=args.retries
    )

    print(render_json(results, state) if args.json else render_text(results, state))
    if not args.no_state:
        save_state(args.state, results)

    failing = [(t, r) for t, r in results if r.failed]
    if args.fail_on == "any" and failing:
        return 1
    if any(r.status == "broken" for _, r in failing):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
