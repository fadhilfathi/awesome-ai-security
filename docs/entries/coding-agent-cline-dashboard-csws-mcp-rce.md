# Cline dashboard cross-origin WebSocket hijacking injecting a malicious MCP server

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-cline-dashboard-csws-mcp-rce` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Agent privilege abuse |
| Target | Cline CLI and agent (npm package cline); advisory lists affected versions up to 3.0.24, fixed in 3.0.30 |
| Disclosure date | 2026-06-23 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-59723 |

## Summary

Cline ships a dashboard server that developers start locally, and the advisory shows its browser WebSocket endpoint accepts connections without checking the Origin header. In the default local configuration no room secret is set, so the authorization helper returns true unconditionally and any website the developer visits can connect. From there a page can send command frames that write a new stdio MCP server entry, pointing at an arbitrary shell command, into Cline's settings file, and dashboard-created sessions approve every tool by default. The advisory includes a reproduction that confirmed the write.

## Impact

The injected MCP entry persists in the settings file and Cline runs its command the next time the server is activated, so the attacker gains code execution on the developer's machine that outlives the page visit. Class choice: AGENT_PRIVILEGE_ABUSE, because the source names a persistent new tool binding in the agent's configuration as the gain, which the taxonomy tie-break assigns to this class. TOOL_POISONING and PROMPT_INJECTION_INDIRECT were rejected: the payload is written into the victim's own settings file by a website, not published in a tool definition the tool operator controls.

## Mitigation

Upgrade to Cline 3.0.30 or later. Until then, set a room secret for the dashboard server so the endpoint is not open, do not leave the dashboard running while browsing unrelated sites, and inspect the MCP server list in Cline's settings for stdio entries whose command is a shell you did not add yourself.

## Sources

- **PRIMARY** - [Cross-Origin WebSocket Hijacking in Cline Hub Dashboard (/browser endpoint) (GHSA-3cj3-hqcr-g934)](https://github.com/cline/cline/security/advisories/GHSA-3cj3-hqcr-g934)
- **PRIMARY** - [CVE-2026-59723 record: Cline cross-origin WebSocket hijacking in the Cline Hub dashboard](https://cveawg.mitre.org/api/cve/CVE-2026-59723)

Generated from `data/entries/coding-agent-cline-dashboard-csws-mcp-rce.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-cline-dashboard-csws-mcp-rce.yml).
