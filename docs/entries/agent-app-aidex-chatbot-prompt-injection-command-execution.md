# Prompt injection in the AiDex LLM chatbot executes operating system commands

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-aidex-chatbot-prompt-injection-command-execution` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (direct) |
| Target | AiDex LLM chatbot, versions earlier than 1.7, /api/<string-chat>/message endpoint |
| Disclosure date | 2025-04-15 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-3579 |

## Summary

Spain's INCIBE coordinated the publication of two critical findings in the AiDex chatbot, one of which covers prompt injection on the message endpoint of an open chat registry. The advisory states that an authenticated user manipulating the content parameter could make the chatbot run commands the product never intended, and that this was assigned CVE-2025-3579. The vendor fixed both findings in AiDex 1.7.

## Impact

The advisory states the attacker can run Unix commands, talk to internal services such as PHP or MySQL, and invoke native functions of the framework behind the product, so the gain is command execution as the application rather than a refused answer. CISA recorded Exploitation: none and no source reports affected users, so this is demonstrated rather than confirmed. INSECURE_OUTPUT_HANDLING was considered and rejected: the taxonomy keys the class on the defective component, and the defect here is a model obeying text that arrived on the normal user input channel.

## Mitigation

Upgrade to AiDex 1.7 or later, which the advisory names as the fix. Do not let a chat endpoint reach shell, interpreter or framework internals on the strength of model output alone: put an explicit allowlist of callable operations between the model and the host, and require an operator decision for anything outside it.

## Sources

- **PRIMARY** - [Multiple vulnerabilities in AiDex (INCIBE-2025-0185)](https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-aidex)
- **PRIMARY** - [CVE-2025-3579 Code Injection Vulnerability in AiDex record](https://cveawg.mitre.org/api/cve/CVE-2025-3579)

Generated from `data/entries/agent-app-aidex-chatbot-prompt-injection-command-execution.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-aidex-chatbot-prompt-injection-command-execution.yml).
