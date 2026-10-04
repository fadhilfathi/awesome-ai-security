# Direct prompt injection in the EmailGPT service leaks system prompts and runs unwanted prompts

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-emailgpt-direct-prompt-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (direct) |
| Target | EmailGPT hosted service, revisions through commit eecfaf2cff58793549dd0c1266ac1d62e0c8811d |
| Disclosure date | 2024-06-05 |
| Last verified | 2026-10-04 |
| CVE | CVE-2024-5184 |

## Summary

Synopsys's CyRC assigned CVE-2024-5184 to a prompt injection in the EmailGPT email assistant service, and the record states that the service accepts an injected prompt through its API and lets it take over the service logic. The stated outcomes are two: the attacker can force the assistant to leak its hard-coded system prompt, and can make it run prompts it was never meant to run, answering requests that should have been refused. The record lists Mohammed Alshehri as finder and does not name a fixed version.

## Impact

The CVE states any individual with access to the service can trigger the issue, and that the system responds with the requested data rather than declining. That is the PROMPT_INJECTION_DIRECT tie-break outcome, an action the service would not otherwise take, rather than JAILBREAK. INSECURE_OUTPUT_HANDLING was considered and rejected because the record does not describe a component consuming the output unsafely. CISA recorded Exploitation: none, so this is demonstrated rather than confirmed in the wild.

## Mitigation

No fix version is named in the record. Treat an assistant that fronts user-controlled text with a fixed system prompt as a service that needs the same controls as any other injection surface: separate system instructions from user content, never let user text alone decide what actions run, and scope the assistant's credentials so a successful takeover is bounded.

## Sources

- **PRIMARY** - [CVE-2024-5184 Prompt Injection in EmailGPT record](https://cveawg.mitre.org/api/cve/CVE-2024-5184)

Generated from `data/entries/agent-app-emailgpt-direct-prompt-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-emailgpt-direct-prompt-injection.yml).
