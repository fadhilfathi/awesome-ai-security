# Impossibility of perfect prompt-injection prevention in shared-embedding sequence models

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-prompt-injection-separation-impossibility` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Prompt injection (indirect) |
| Target | LLM applications where trusted instructions and untrusted content share one token embedding and one attention pipeline |
| Disclosure date | 2026-06-25 |
| Last verified | 2026-10-04 |

## Summary

A theory paper argues that the failure of prompt-injection defenses is not bad luck. It models a prompted LLM as a Prompted Action Model whose outputs include control decisions such as refusals, tool authorization and memory writes, and defines Semantic-Faithful Control: that behavior depends on what untrusted input means, not on how it is encoded. It then proves that property cannot be held inside a shared pipeline, via a provenance-recovery impossibility result plus an argument that untrusted content reaches control-relevant computation through the same value pathway, plus a finite-coverage invariance argument.

## Impact

The consequence is a ceiling on what any in-pipeline defense can promise: in architectures that do not separate control from data, some input will be treated as authoritative rather than as data, so the attacker eventually gets a control-authoritative action. The authors compare this to code-data confusion on von Neumann machines and read it as a claim about architecture, not about today's models. The result is a proof, not an attack run against a system.

## Mitigation

Take the paper's architectural implication rather than another classifier: complete protection needs a mechanism that enforces separation between trusted control and untrusted content, so move control decisions out of the shared embedding pipeline and into a component the untrusted text cannot reach. The authors explicitly note this does not mean useful systems must ignore user input, nor that all defenses are equally ineffective in practice.

## Sources

- **PRIMARY** - [On the Inseparability of Instructions and Data in Shared-Embedding Sequence Models](https://arxiv.org/abs/2606.27567)
- **PRIMARY** - [On the Inseparability of Instructions and Data in Shared-Embedding Sequence Models (full text)](https://arxiv.org/html/2606.27567v1)

Generated from `data/entries/theoretical-prompt-injection-separation-impossibility.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-prompt-injection-separation-impossibility.yml).
