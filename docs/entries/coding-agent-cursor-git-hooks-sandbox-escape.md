# Cursor sandbox escape through agent writes to Git configuration and hooks

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-cursor-git-hooks-sandbox-escape` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Cursor editor versions prior to 2.5 (fixed in 2.5) |
| Disclosure date | 2026-02-13 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-26268 |

## Summary

Cursor runs its agent inside a sandbox and keeps a list of files that require user approval before the agent may write them. The advisory reports that Git configuration, including the directory Git executes hooks from, was not covered by that protection, so an agent driven by attacker-controlled instructions could write into it. Because Git runs those commands on its own the next time the affected operation fires, the resulting code ran outside the sandbox with no further user interaction. Cursor fixed it in version 2.5 and credited the Novee Security Research Team with researchers at the Nvidia AI Red Team and elsewhere.

## Impact

The advisory rates the issue High, CVSS 3.1 8.0 with scope changed, and states the escape yields out-of-sandbox remote code execution. Class choice: INSECURE_OUTPUT_HANDLING, because the source names the missing write protection on .git settings as the defective component and the attacker gain arrives when Git, an automated consumer, later reads the file the agent wrote; no review sits between the write and execution. AGENT_PRIVILEGE_ABUSE was rejected on the tie-break because the sources name no credential or configuration change that outlives the single execution.

## Mitigation

Upgrade to Cursor 2.5 or later. Until then, do not rely on an editor approval list alone as the boundary: keep repositories that are opened by the agent free of writable .git hooks, and check the .git directory of any repository an agent has worked in for hook files or config keys that were added since the clone.

## Sources

- **PRIMARY** - [Sandbox escape via Git hooks (GHSA-8pcm-8jpx-hv8r)](https://github.com/cursor/cursor/security/advisories/GHSA-8pcm-8jpx-hv8r)
- **PRIMARY** - [CVE-2026-26268 record: Cursor sandbox escape via Git hooks](https://cveawg.mitre.org/api/cve/CVE-2026-26268)

Generated from `data/entries/coding-agent-cursor-git-hooks-sandbox-escape.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-cursor-git-hooks-sandbox-escape.yml).
