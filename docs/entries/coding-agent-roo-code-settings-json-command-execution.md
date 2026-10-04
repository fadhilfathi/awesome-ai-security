# Roo Code remote code execution through the VS Code settings the agent may write

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-roo-code-settings-json-command-execution` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Roo Code VS Code extension before 3.22.6 |
| Disclosure date | 2025-07-07 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-53536 |

## Summary

Roo Code guards writes with an auto-approve setting that is off by default, and the advisory reports that when a developer had switched file writes to auto-approve, an attacker able to submit prompts to the agent could have it write to the editor's settings files. Because settings can name the program to run for a language service, the advisory gives a concrete route: point the PHP validator at an arbitrary command, then create a PHP file that makes the editor run it. The vendor fixed it in 3.22.6 by requiring an extra layer of opt-in for writes to that folder. The vendor record reports no exploitation.

## Impact

The attacker gains arbitrary code execution on the developer's machine. Class choice: INSECURE_OUTPUT_HANDLING, because the source names the extension's handling of the agent's own writes as the defective component and the editor, not a human, later consumed the setting. PROMPT_INJECTION_INDIRECT and TOOL_POISONING were rejected on the taxonomy tie-break: the record names prompt submission only as the entry point and the capability is yielded by the unapproved settings write.

## Mitigation

Upgrade to Roo Code 3.22.6 or later. Leave auto-approve for file writes off, since the vendor lists it as off by default and the advisory says the chain needs it, and do not let an agent write into an editor's settings folder, where a single key can decide what program the editor runs.

## Sources

- **PRIMARY** - [Potential Remote Code Execution via .vscode/settings.json in the Roo Code extension (GHSA-3765-5vjr-qjgm)](https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-3765-5vjr-qjgm)
- **PRIMARY** - [CVE-2025-53536 record: Roo Code remote code execution via .vscode/settings.json](https://cveawg.mitre.org/api/cve/CVE-2025-53536)

Generated from `data/entries/coding-agent-roo-code-settings-json-command-execution.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-roo-code-settings-json-command-execution.yml).
