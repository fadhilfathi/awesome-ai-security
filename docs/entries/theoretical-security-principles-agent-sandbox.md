# Position: applying classical information security design principles to LLM agents

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-security-principles-agent-sandbox` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Agent platforms and protocols that hold credentials, call tools and carry context |
| Disclosure date | 2025-05-29 |
| Last verified | 2026-10-04 |

## Summary

A position paper argues that the design principles that have guided systems security for decades, defense in depth, least privilege, complete mediation and psychological acceptability, should be applied deliberately when agents are deployed at scale, since multi-agent interaction and context manipulation create vulnerability classes the principles were written for. It sketches AgentSandbox, a framework placing safeguards across an agent's lifecycle, and reports AgentDojo measurements including a 49.31 percent attack success rate with no defence in place. It contributes a framework, not a new exploit against a deployed product.

## Impact

The claim is that agent deployments that skip these principles lose the containment they would otherwise have, so privacy leakage and system exploitation become design defaults rather than bugs. The paper's own numbers are about its framework's utility and mitigation, not about an attacker gain it demonstrates. Filed as OTHER: the object is a missing set of design principles, a governance mechanism no class tests for, and the impact field names that rather than forcing a mechanism fit.

## Mitigation

Adopt the principles the paper names as acceptance criteria rather than as aspirations: no agent reaches a capability a role does not need, every action a tool can take passes a mediation point that sees it, and layered controls do not share a single failure mode. The paper argues that a control is only followed while it is psychologically acceptable to the person operating it, so usability is treated here as a security property rather than as polish.

## Sources

- **PRIMARY** - [LLM Agents Should Employ Security Principles](https://arxiv.org/abs/2505.24019)
- **PRIMARY** - [LLM Agents Should Employ Security Principles (full text)](https://arxiv.org/html/2505.24019v1)

Generated from `data/entries/theoretical-security-principles-agent-sandbox.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-security-principles-agent-sandbox.yml).
