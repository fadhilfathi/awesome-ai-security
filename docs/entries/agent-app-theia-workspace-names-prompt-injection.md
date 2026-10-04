# Indirect prompt injection through workspace file and directory names in Eclipse Theia AI chat

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-theia-workspace-names-prompt-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | Eclipse Theia AI chat agent, versions prior to 1.71.0 |
| Disclosure date | 2026-06-18 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-44688 |

## Summary

The Eclipse Foundation's CVE record states that before 1.71.0 the Theia AI chat agent folded workspace file and directory names into its prompt context without distinguishing them from system instructions. A repository whose names are chosen by an attacker therefore instructs the agent as soon as the agent analyses that workspace, and the record assigns CVE-2026-44688 to it. The Foundation states that the workspace trust enforcement added in 1.71.0 disables the AI features in untrusted workspaces and closes the chain.

## Impact

The Foundation states the injected names enable attack chains leading to data exfiltration through Markdown image rendering or arbitrary command execution through task definitions, so the attacker obtains session data or code execution from a repository the developer merely opened. INSECURE_OUTPUT_HANDLING and TOOL_POISONING were both considered and rejected: the payload arrived neither in output handling nor in a tool definition. The step that yielded capability was the attacker-chosen workspace names entering the prompt. CISA recorded Exploitation: none.

## Mitigation

Upgrade to 1.71.0 or later, which disables AI chat, inline suggestions and code actions, and stops loading workspace prompt templates and resolving workspace file variables, while a workspace is in Restricted Mode. Until then, do not run AI features over an untrusted clone; grant workspace trust deliberately, and treat a repository name as untrusted input the same way any other retrieved content is treated.

## Sources

- **PRIMARY** - [CVE-2026-44688 Eclipse Theia AI chat record](https://cveawg.mitre.org/api/cve/CVE-2026-44688)
- **PRIMARY** - [Hook workspace trust into AI features (issue 16892)](https://github.com/eclipse-theia/theia/issues/16892)

Generated from `data/entries/agent-app-theia-workspace-names-prompt-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-theia-workspace-names-prompt-injection.yml).
