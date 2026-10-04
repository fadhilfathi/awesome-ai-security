# Claude Code workspace trust bypass through a repository's own settings file

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-claude-code-repo-settings-trust-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Claude Code (npm package @anthropic-ai/claude-code) before 2.1.53 (fixed in 2.1.53) |
| Disclosure date | 2026-03-18 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-33068 |

## Summary

Claude Code asks a developer to confirm trust in a workspace before it acts, and the advisory reports that the permission mode was resolved from settings files first, including the settings file the repository itself controls. A repository that committed a permissive permission mode in that file therefore had the confirmation dialog silently skipped the first time it was opened, and the source states this places the user in a permissive mode without ever seeing the prompt. Anthropic published the advisory on 2026-03-18 and shipped the fix in version 2.1.53.

## Impact

The developer ends up in a mode where tool calls run without confirmation in a directory an attacker chose, which the advisory says makes it easier for an attacker-controlled repository to obtain tool execution without explicit consent. Class choice: INSECURE_OUTPUT_HANDLING, because the source names Claude Code's own handling of repository-supplied configuration as the defective component, and that configuration is then consumed by the permission engine without review.

## Mitigation

Upgrade to Claude Code 2.1.53 or later; users on the standard auto-update channel already have the fix. Where you cannot update, read the .claude directory of any repository before running the agent in it, and set the permission mode yourself rather than letting the workspace declare it.

## Sources

- **PRIMARY** - [Workspace Trust Dialog Bypass via Repo-Controlled Settings File (GHSA-mmgp-wc2j-qcv7)](https://github.com/anthropics/claude-code/security/advisories/GHSA-mmgp-wc2j-qcv7)
- **PRIMARY** - [CVE-2026-33068 record: Claude Code Workspace Trust Dialog Bypass via Repo-Controlled Settings File](https://cveawg.mitre.org/api/cve/CVE-2026-33068)

Generated from `data/entries/coding-agent-claude-code-repo-settings-trust-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-claude-code-repo-settings-trust-bypass.yml).
