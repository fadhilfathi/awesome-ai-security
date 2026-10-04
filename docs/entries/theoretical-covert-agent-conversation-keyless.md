# Keyless covert channel argued possible between two LLM agents holding no shared secret

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-covert-agent-conversation-keyless` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Data exfiltration |
| Target | Any deployment where two LLM agents converse and a third party reads their transcript |
| Disclosure date | 2026-04-06 |
| Last verified | 2026-10-04 |

## Summary

A cryptography paper asks whether two agents operated by different entities can hold a private side conversation while their visible transcript stays computationally indistinguishable from an honest exchange, even for an auditor who knows the models, the protocol, and each side's context. It proves covert conversation is possible in the shared-key case, then works the harder keyless case where the two agents begin with no shared secret, introducing a primitive it calls pseudorandom noise-resilient key exchange for that setting. The results are constructive and negative; the authors report no system attacked.

## Impact

The gain argued for is a hidden channel: content that a transcript reader, including a monitoring service, cannot distinguish from ordinary output, which turns monitoring of agent-to-agent traffic into a losing position for the defender. The paper's assumptions are stated tightly, that honest messages carry at least constant min-entropy and the protocol is adaptive, and its negative results also warn that weaker key-exchange variants admit efficient attacks. No third party is shown to be fooled in practice.

## Mitigation

Treat a text transcript of an agent conversation as unverified and do not treat readability as evidence of absence of covert content. Where the two agents belong to different principals, gate inter-agent messaging on an attested policy rather than on inspection of the text. The paper's negative results argue against rolling your own covert-resistant key exchange.

## Sources

- **PRIMARY** - [Undetectable Conversations Between AI Agents via Pseudorandom Noise-Resilient Key Exchange](https://arxiv.org/abs/2604.04757)
- **PRIMARY** - [Undetectable Conversations Between AI Agents via Pseudorandom Noise-Resilient Key Exchange (full text)](https://arxiv.org/html/2604.04757v1)

Generated from `data/entries/theoretical-covert-agent-conversation-keyless.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-covert-agent-conversation-keyless.yml).
