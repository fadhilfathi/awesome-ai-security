# Trust-Authorization Mismatch proposed as the root cause shared by prompt injection and tool poisoning

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-trust-authorization-mismatch-agent` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Agent runtimes that grant permissions statically while an agent's trustworthiness varies per step |
| Disclosure date | 2025-12-07 |
| Last verified | 2026-10-04 |

## Summary

A systematization of more than 200 papers argues that agent runtimes hand an agent a fixed permission set while the agent's trustworthiness at any given step is not a fixed property, and that this mismatch is the shared root under attacks that otherwise look unrelated. It decomposes agent execution into belief formation, intent generation and permission grant, and shows across the surveyed work that prompt injection and tool poisoning are different expressions of one structural problem. The paper systematizes and frames; it runs no attack.

## Impact

The consequence claimed is that a permission granted at deployment stays granted no matter what changed the agent's belief, so a permission check that passes is not evidence the action was authorized by anything the user intended. Because the paper's unit is the mismatch rather than an incident, it reports no attacker gain of its own and rests on surveyed case results. Filed as OTHER: the object is a runtime property, the decoupling of static permission from per-step trustworthiness, which none of the named classes tests for.

## Mitigation

Make authorization track the state of the agent rather than a fixed grant: re-evaluate permission at the point of use, against the belief and intent the run actually holds, and let permission narrow as confidence about provenance falls. Pair that with provenance on tool definitions and results so a permission grant can name the content it was based on.

## Sources

- **PRIMARY** - [SoK: Trust-Authorization Mismatch in LLM Agent Interactions](https://arxiv.org/abs/2512.06914)
- **PRIMARY** - [SoK: Trust-Authorization Mismatch in LLM Agent Interactions (full text)](https://arxiv.org/html/2512.06914v2)

Generated from `data/entries/theoretical-trust-authorization-mismatch-agent.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-trust-authorization-mismatch-agent.yml).
