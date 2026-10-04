# Cross-domain query combinability argued to defeat per-request guards in multi-agent LLM deployments

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-cross-domain-query-combinability` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Data exfiltration |
| Target | LLM agents from different organizations whose per-agent guards each see only their own request and response |
| Disclosure date | 2025-05-28 |
| Last verified | 2026-10-04 |

## Summary

A perspective paper argues that when agents owned by different organizations cooperate, no single party holds the whole conversation, so a policy checked per request is judged against too little context. Its worked example has an outside contractor ask one company's payroll agent for a department maximum, then ask the HR agent who earns it, and combine the two answers to recover a specific salary. Each request is ordinary and each answer passes the guard that saw it. This appears as one of seven challenges the paper proposes, with metrics and countermeasures attached; no attack is run.

## Impact

The gain described is a record leaving the boundary: a particular salary the organization meant to keep unrevealed. Because each fragment is individually policy-compliant, the paper argues that per-request filters, turn-by-turn firewalls, and access control over the raw table all miss the composite leak, and it says countermeasures for this remain unexplored. Filed as DATA_EXFILTRATION rather than PROMPT_INJECTION_DIRECT because no attacker-authored instruction rides in retrieved content; the gain comes from combining two legitimate answers across an ownership boundary.

## Mitigation

Evaluate policy over a session and its combined context rather than one request at a time, and write policies knowing that answers are externally combinable. Where the domains can cooperate, keep the composite view inside one owner, and log cross-domain exchanges under a shared identifier so a composite leak can be reconstructed after the fact.

## Sources

- **PRIMARY** - [Seven Security Challenges in Cross-domain Multi-agent LLM Systems](https://arxiv.org/abs/2505.23847)
- **PRIMARY** - [Seven Security Challenges in Cross-domain Multi-agent LLM Systems (full text)](https://arxiv.org/html/2505.23847v5)

Generated from `data/entries/theoretical-cross-domain-query-combinability.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-cross-domain-query-combinability.yml).
