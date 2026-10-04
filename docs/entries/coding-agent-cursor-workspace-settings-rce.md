# Cursor remote code execution through agent writes to a VS Code workspace file

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-cursor-workspace-settings-rce` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Cursor editor versions 1.6 and below (fixed in 1.7) |
| Disclosure date | 2025-10-02 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-61590 |

## Summary

Cursor inherits Visual Studio Code workspace files, the JSON documents that hold per-project settings and can be created automatically by the editor as an untitled workspace. The reporter found the agent's write-protection list covered ordinary settings files but not the workspace file, so an attacker who could steer the victim's chat context, for example through a compromised MCP server, could instruct the agent to write attacker-chosen workspace settings. The advisory describes this as a bypass of the earlier Cursor fix CVE-2025-54130, turning an unapproved agent edit into code execution. Cursor fixed it in 1.7 by requiring approval for that file.

## Impact

The advisory rates the issue High at CVSS 3.1 7.5 and states the outcome could be remote code execution on the victim with no user approval. Class choice: INSECURE_OUTPUT_HANDLING, because the source names Cursor's handling of the agent's own edit as the defective component and the fix adds an approval gate on that file. PROMPT_INJECTION_INDIRECT and TOOL_POISONING were rejected on the taxonomy tie-break, since the advisory names the hijacked chat context only as a way in. No source states any exploitation.

## Mitigation

Upgrade to Cursor 1.7 or later. Where an upgrade is not yet possible, treat any MCP server connected to the editor as capable of running code, since the advisory names a compromised MCP server as the injection entry point, and do not run an agent against a workspace whose .code-workspace file is not already under version control and review.

## Sources

- **PRIMARY** - [RCE via .code-workspace files using Prompt Injection (GHSA-xg6w-rmh5-r77r)](https://github.com/cursor/cursor/security/advisories/GHSA-xg6w-rmh5-r77r)
- **PRIMARY** - [CVE-2025-61590 record: Cursor is vulnerable to RCE via .code-workspace files using Prompt Injection](https://cveawg.mitre.org/api/cve/CVE-2025-61590)

Generated from `data/entries/coding-agent-cursor-workspace-settings-rce.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-cursor-workspace-settings-rce.yml).
