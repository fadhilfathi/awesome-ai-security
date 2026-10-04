# Authorization-Execution Gap proposed as the unifying failure mode of open-world LLM agents

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-authorization-execution-gap` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Agent privilege abuse |
| Target | Tool-using LLM agents acting under a delegated mandate, with persistent state and multi-agent handoffs |
| Disclosure date | 2026-05-10 |
| Last verified | 2026-10-04 |

## Summary

A position paper argues that many agent failures share one shape: what an agent ends up doing diverges from what the principal meant to authorize. It traces that divergence to three structural sources: incomplete delegation of the mandate, corruption through execution channels such as tool output or web content, and fragmentation of authorization across stages and agents. A worked travel-booking trace carries the argument, and the paper closes by asking for authorization-integrity checks during execution rather than one-shot filtering. Nothing is run against a deployed system.

## Impact

The paper asserts rather than demonstrates a harm: an agent takes actions, writes state, or hands off work outside the authorization the user granted, and because such actions may be irreversible the divergence is costly to undo. It explicitly excludes harmful-task and compromised-infrastructure cases and leans on previously documented agent failures only as stakes evidence. Filed as AGENT_PRIVILEGE_ABUSE rather than JAILBREAK or prompt injection because the step that yields the gain is the agent exercising authority beyond the mandate, not a refusal being bypassed.

## Mitigation

Carry authorization as an explicit, machine-checkable scope and evaluate it during execution rather than once at the start. Treat tool output, web content, stored state and upstream agent output as environmental content that never carries delegated authority, and re-check scope after every handoff. Diagnose by structural source, since the same symptom calls for different fixes depending on which of the three sources is responsible.

## Sources

- **PRIMARY** - [The Authorization-Execution Gap Is a Major Safety and Security Problem in Open-World Agents](https://arxiv.org/abs/2605.11003)
- **PRIMARY** - [The Authorization-Execution Gap Is a Major Safety and Security Problem in Open-World Agents (full text)](https://arxiv.org/html/2605.11003v1)

Generated from `data/entries/theoretical-authorization-execution-gap.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-authorization-execution-gap.yml).
