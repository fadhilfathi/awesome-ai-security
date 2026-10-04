# Boolean prompt injection in the 1millionbot Millie chatbot evades chat restrictions

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-millie-chatbot-boolean-prompt-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (direct) |
| Target | 1millionbot Millie chat chatbot and AI platform, versions prior to 3.6.0 |
| Disclosure date | 2026-03-31 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-4399 |

## Summary

INCIBE coordinated the publication of a high severity finding in the Millie chatbot by 1millionbot. The mechanism is a Boolean form of prompt injection: a question is framed so that an affirmative answer causes the model to run the instruction that follows it, and the restriction evasion was assigned CVE-2026-4399. The advisory lists the product as fixed in version 3.6.0.

## Impact

A remote user can make the chatbot answer questions it was meant to refuse and spend the vendor's resources, including the OpenAI API key behind the service, on tasks outside its purpose. That is abuse of an existing entitlement, so AGENT_PRIVILEGE_ABUSE was considered and rejected. JAILBREAK was also considered and rejected, because the taxonomy sends it to injection when success is an action rather than a refused-content bypass, and the advisory names out-of-context tasks and API key use rather than a bare refusal. CISA recorded Exploitation: none, so this is not Tier 1.

## Mitigation

Upgrade to 3.6.0 or later, which the advisory names as the fix. Treat prompt content controls as a single gate that blocks both direct attempts and affirmative-answer constructions, put per-user and per-session spend and rate limits on model calls, and scope the API credential to the minimum the service needs so abuse is bounded.

## Sources

- **PRIMARY** - [Multiple vulnerabilities in 1millionbot Millie chatbot (INCIBE-2026-243)](https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-1millionbot-millie-chatbot)
- **PRIMARY** - [CVE-2026-4399 Multiple vulnerabilities in 1millionbot Millie chatbot record](https://cveawg.mitre.org/api/cve/CVE-2026-4399)

Generated from `data/entries/agent-app-millie-chatbot-boolean-prompt-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-millie-chatbot-boolean-prompt-injection.yml).
