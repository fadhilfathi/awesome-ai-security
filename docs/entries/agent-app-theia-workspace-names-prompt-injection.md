# Indirect prompt injection through workspace file and directory names in Eclipse Theia AI chat

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-theia-workspace-names-prompt-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | Eclipse Theia AI chat agent, versions prior to 1.71.0 |
| Disclosure date | 2026-06-18 |
| Last verified | 2026-10-05 |
| CVE | CVE-2026-44688 |

## Summary

The CVE record for Eclipse Theia states that before 1.71.0 the AI chat agent processed workspace file and directory names as part of its prompt context without distinguishing them from system instructions. A repository whose names are chosen by an attacker therefore instructs the agent as soon as the agent analyses that workspace. The record assigns CVE-2026-44688 to the flaw and cites an Eclipse Foundation work item.

## Impact

The CVE record states the injected names enable attack chains leading to data exfiltration through Markdown image rendering, or to arbitrary command execution through task definitions, so the attacker gains session data or code execution from a repository the developer merely opened. The record names no credential as the item reaching the attacker, so this is not CREDENTIAL_EXPOSURE, and TOOL_POISONING and INSECURE_OUTPUT_HANDLING were both rejected because the payload arrived in neither a tool definition nor an output handler. CISA recorded no exploitation for this CVE.

## Mitigation

Upgrade to 1.71.0 or later. Until then, do not run AI features over an untrusted clone, and grant workspace trust deliberately. Treat a repository name as untrusted input in the same way as any other retrieved content, because the agent cannot tell the difference once the name is in its context.

## Sources

- **PRIMARY** - [CVE-2026-44688 Eclipse Theia AI chat record](https://cveawg.mitre.org/api/cve/CVE-2026-44688)
- **PRIMARY** - [Eclipse Foundation CVE assignment work item 113](https://gitlab.eclipse.org/security/cve-assignment/-/work_items/113)

Generated from `data/entries/agent-app-theia-workspace-names-prompt-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-theia-workspace-names-prompt-injection.yml).
