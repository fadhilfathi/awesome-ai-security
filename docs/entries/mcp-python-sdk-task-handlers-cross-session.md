# MCP Python SDK experimental task handlers let any client read and cancel other clients' tasks

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-python-sdk-task-handlers-cross-session` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Data exfiltration |
| Target | MCP Python SDK 1.23.0 through 1.27.1, servers calling experimental.enable_tasks() |
| Disclosure date | 2026-06-05 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-52870 |

## Summary

The Python SDK's experimental tasks feature installs default handlers for tasks/list, tasks/get, tasks/result and tasks/cancel that acted on a task identifier alone and kept no record of which session created each task. On a server with more than one connected client, any client could enumerate every task, read another task's status and results, take queued messages meant for the task's creator, and cancel it. Version 1.27.2 embeds a per-session marker in generated task IDs and restricts the default handlers to the calling session's own tasks.

## Impact

A connected client reads other clients' task results and elicitation payloads and can destroy their in-flight tasks, so results and messages move to an unintended principal. That is DATA_EXFILTRATION: the sources name task results and elicitation payloads as the items reaching the wrong client, not a credential, and the gain is bounded to tasks rather than a new or persistent capability, so AGENT_PRIVILEGE_ABUSE does not apply. The feature is opt-in, so only servers that call server.experimental.enable_tasks() and serve more than one client are affected; CISA reports exploitation as none.

## Mitigation

Upgrade to mcp 1.27.2 or later. Until then, leave the experimental tasks feature disabled, or register task handlers that validate session ownership themselves; a server that registered its own handlers is affected only if those handlers omit the same check.

## Sources

- **PRIMARY** - [Experimental task handlers allow any client to access and cancel other clients' tasks (GHSA-hvrp-rf83-w775)](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-hvrp-rf83-w775)
- **PRIMARY** - [CVE-2026-52870 CVE record, including the CISA enrichment reporting no exploitation](https://cveawg.mitre.org/api/cve/CVE-2026-52870)

Generated from `data/entries/mcp-python-sdk-task-handlers-cross-session.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-python-sdk-task-handlers-cross-session.yml).
