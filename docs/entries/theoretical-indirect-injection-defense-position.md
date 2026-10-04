# Position: what system-level defense can and cannot claim against indirect prompt injection

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-indirect-injection-defense-position` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Prompt injection (indirect) |
| Target | Agent architectures that plan and execute with an explicit policy enforcer, as described in the paper |
| Disclosure date | 2026-03-31 |
| Last verified | 2026-10-04 |

## Summary

A position paper takes the position that indirect prompt injection, where instructions hidden in retrieved emails, pages or tool output drive agent actions, is not fixable by a filter on the input. It argues for an agent skeleton of orchestrator, plan and policy approver, plan, executor, policy and policy enforcer, then states three positions: that dynamic replanning and policy updates are necessary for real tasks, that a learned model is sometimes needed for security decisions but only inside a design that strictly limits what it sees and decides, and that ambiguity such as what counts as urgent needs the user rather than more model robustness. It reports no attack.

## Impact

The consequence argued is a limit on what a defense team may claim: a benchmark number from a static-payload harness does not tell you what happens when the attacker adapts to the defense or when the policy itself is updated from untrusted data. The paper also states that isolating one piece of data can make the task impossible, so tightening the boundary costs utility. What the attacker gains is left unspecified, which is why this is filed as a framing of the mechanism rather than a demonstrated gain.

## Mitigation

Build the skeleton the paper describes and keep the policy enforcer outside the model. When a learned model must judge, give it structured inputs and a narrow decision rather than arbitrary environmental text. Plan for human input on genuinely ambiguous instructions instead of resolving them by inference, and test against an adaptive attacker rather than a fixed payload set.

## Sources

- **PRIMARY** - [Architecting Secure AI Agents: Perspectives on System-Level Defenses Against Indirect Prompt Injection Attacks](https://arxiv.org/abs/2603.30016)
- **PRIMARY** - [Architecting Secure AI Agents: Perspectives on System-Level Defenses Against Indirect Prompt Injection Attacks (full text)](https://arxiv.org/html/2603.30016v1)

Generated from `data/entries/theoretical-indirect-injection-defense-position.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-indirect-injection-defense-position.yml).
