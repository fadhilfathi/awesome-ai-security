# GitHub Copilot agent mode remote code execution by turning off its own confirmations

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-copilot-settings-json-yolo-rce` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | GitHub Copilot agent mode in Visual Studio 2022 17.14.0 to 17.14.11 (fixed in 17.14.12) |
| Disclosure date | 2025-08-12 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-53773 |

## Summary

In agent mode the Copilot extension writes file edits straight to disk rather than holding them as a reviewable diff, and Microsoft states that exploitation requires a user to trigger the payload in the application. The researcher's chain starts from instructions hidden in a source file, web page or tool response that make the agent add an auto-approve key to the project settings file, which disables the agent's own confirmation prompts and then lets it run a terminal command with no review. Microsoft assigned CVE-2025-53773 and shipped the fix in the August 2025 patch release; the vendor record reports no exploitation.

## Impact

An attacker who reaches Copilot's context gets command execution on the developer's machine, and the source describes persistence beyond the single command, including committing the injection back into repositories so it spreads. Class choice: INSECURE_OUTPUT_HANDLING, because the source names the editor's treatment of the agent's output as defective: edits were persisted without approval and could rewrite the settings that govern approval. PROMPT_INJECTION_INDIRECT was rejected on the taxonomy tie-break, since the capability is yielded by the unapproved write.

## Mitigation

Update Visual Studio to 17.14.12 or later. Treat project-level .vscode settings committed in a repository as untrusted input, and do not run Copilot agent mode against a project whose configuration files you have not read, since the source shows the agent can change those files itself.

## Sources

- **PRIMARY** - [CVE-2025-53773 GitHub Copilot and Visual Studio Remote Code Execution Vulnerability](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-53773)
- **PRIMARY** - [CVE-2025-53773 record, Visual Studio 2022 17.14.0 before 17.14.12](https://cveawg.mitre.org/api/cve/CVE-2025-53773)
- **PRIMARY** - [GitHub Copilot: Remote Code Execution via Prompt Injection (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection)

Generated from `data/entries/coding-agent-copilot-settings-json-yolo-rce.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-copilot-settings-json-yolo-rce.yml).
