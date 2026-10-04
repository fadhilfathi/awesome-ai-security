# Azure DevOps token disclosure through GitHub Copilot Chat workspace settings in VS Code

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-copilot-chat-ado-token-disclosure` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Credential exposure |
| Target | GitHub Copilot Chat extension for Visual Studio Code before 1.136.2 |
| Disclosure date | 2026-09-08 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-81381 |

## Summary

The Copilot Chat extension's Azure DevOps code search integration let its endpoint be overridden through workspace configuration. Microsoft states that a repository could carry a settings file redirecting those requests to a server the attacker controls, so that when the signed-in developer used code search the extension would send the request, and the user's access token with it, to the attacker's endpoint. The fix in Visual Studio Code 1.136.2 removes the workspace-controlled endpoint override, including its legacy setting name. The vendor record reports no exploitation.

## Impact

The disclosed item is a sign-in access token for the user's work account, which Microsoft states could allow access to data and services the user is authorized to use, potentially including sensitive organizational information. Class choice: CREDENTIAL_EXPOSURE, because the source names a token as the exposed item and the taxonomy keys that class on the item. DATA_EXFILTRATION and PROMPT_INJECTION_INDIRECT were both rejected: the repository settings file is ordinary retrieved content rather than a prompt aimed at the model, and the item set named by the source is a credential.

## Mitigation

Update to Visual Studio Code 1.136.2 or later; Microsoft states there are no known workarounds. Review any repository you open for a .vscode settings.json that sets the code search endpoint override or its legacy equivalent, and treat Azure DevOps and GitHub tokens on a workstation as rotatable if the repository was not trusted.

## Sources

- **PRIMARY** - [Azure DevOps access token disclosure through GitHub Copilot Chat workspace settings (GHSA-rvgr-2w56-2j67)](https://github.com/microsoft/vscode/security/advisories/GHSA-rvgr-2w56-2j67)
- **PRIMARY** - [CVE-2026-81381 record: GitHub Copilot and Visual Studio Code Information Disclosure Vulnerability](https://cveawg.mitre.org/api/cve/CVE-2026-81381)

Generated from `data/entries/coding-agent-copilot-chat-ado-token-disclosure.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-copilot-chat-ado-token-disclosure.yml).
