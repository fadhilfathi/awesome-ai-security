# EchoLeak zero-click indirect prompt injection in Microsoft 365 Copilot

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-m365-copilot-echoleak-zero-click-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | Microsoft 365 Copilot, hosted service used from Outlook and Teams |
| Disclosure date | 2025-06-11 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-32711 |

## Summary

Aim Labs found that an external attacker could plant instructions in an ordinary email and have Microsoft 365 Copilot carry them out, without the recipient doing anything. The email was retrieved during normal Copilot work, the hidden instructions told Copilot to fold context data into a link, and reference-style Markdown and an auto-fetched image tag got past the output filter and the page's content security policy, the last step using an allow-listed Microsoft Teams URL as the fetcher. Microsoft shipped a server-side fix and assigned CVE-2025-32711; a later academic paper analyses the chain rather than reproducing it.

## Impact

The attacker obtains whatever the victim's Copilot could read, which the CVE describes as information disclosure over a network and the research describes as internal files and message content pulled out of the user's context. The record carries CISA's Exploitation: none and the paper states Microsoft reported no evidence of in-the-wild exploitation, so this is not Tier 1. DATA_EXFILTRATION was considered because data is what leaves, but the taxonomy classifies by the step that yielded capability, and that step is the retrieved email whose instructions the model obeyed.

## Mitigation

Microsoft states the fix was server-side with no customer action required. The research recommends partitioning the prompt so external mail is tagged as non-authoritative and never concatenated inline with a user's internal query, resolving retrieval by provenance so external sources are excluded by default, gating model output through a format and URL allowlist before rendering, and applying a strict content security policy so any permitted fetch goes through an internal proxy.

## Sources

- **PRIMARY** - [CVE-2025-32711 M365 Copilot Information Disclosure Vulnerability record](https://cveawg.mitre.org/api/cve/CVE-2025-32711)
- **PRIMARY** - [EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System](https://arxiv.org/abs/2509.10540)
- **PRIMARY** - [EchoLeak paper, full PDF](https://arxiv.org/pdf/2509.10540v1)

Generated from `data/entries/agent-app-m365-copilot-echoleak-zero-click-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-m365-copilot-echoleak-zero-click-injection.yml).
