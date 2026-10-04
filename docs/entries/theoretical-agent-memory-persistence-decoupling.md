# Chronos framing of agent memory injection that separates the attack from the later failure

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-agent-memory-persistence-decoupling` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Training data poisoning |
| Target | Stateful agents with writable, cross-session memory used in enterprise workflows |
| Disclosure date | 2026-07-20 |
| Last verified | 2026-10-04 |

## Summary

A taxonomy paper argues that agents with persistent memory carry a distinct threat, which it calls the Chronos Vulnerability: memory-based attacks such as memory injection and sleeper-agent triggers plant intent in the agent's internal state long before any harmful action, so the vector and the eventual failure are separated in time. It surveys the memory layers it says are exposed and argues that endpoint content filters do not fit this architecture, then organizes proposed defenses into a layered landscape. It is a synthesis over prior work, with no attack of its own run.

## Impact

The claimed consequence is that a compromise written into memory survives past the session that planted it, so the cause is not present when the damage occurs and an investigation focused on the failing step will not find it. The paper's supporting performance numbers come from an existing enterprise workflow benchmark, not from an injection it performed, so the evidence for the attack itself is second-hand. Filed as TRAINING_DATA_POISONING over PROMPT_INJECTION_INDIRECT because the payload is written into durable agent state and keeps working with no attacker content present at inference.

## Mitigation

Filter memory writes with the same care as live inputs and keep provenance on what an agent stores, so a planted belief can be traced to the interaction that wrote it. Assume a persisted memory is untrusted input when read back, and give agents a way to roll back or re-derive stored state rather than treating memory as an authority. The paper points to temporal verification, memory consensus and trusted-execution anchoring as the directions it finds credible.

## Sources

- **PRIMARY** - [The Chronos Vulnerability: A Taxonomy of Temporal Persistence and Memory-Based Deception in Agentic AI](https://arxiv.org/abs/2607.19433)
- **PRIMARY** - [The Chronos Vulnerability: A Taxonomy of Temporal Persistence and Memory-Based Deception in Agentic AI (full text)](https://arxiv.org/html/2607.19433v1)

Generated from `data/entries/theoretical-agent-memory-persistence-decoupling.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-agent-memory-persistence-decoupling.yml).
