# A2A protocol specified without context ownership binding or cross-hop identity propagation

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-a2a-context-ownership-absence` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | The Agent2Agent (A2A) protocol specification, for deployments that follow it |
| Disclosure date | 2026-09-09 |
| Last verified | 2026-10-04 |

## Summary

A protocol-analysis paper reconstructs the A2A specification as a finite-state machine of 37 states and 76 transitions, then reasons over it under a full compliance assumption to find gaps a specification-compliant adversary can use. The results are traces validated against the specification text and by expert review, not attacks run against a deployed agent. The paper reports its findings were disclosed to the A2A maintainers under the Linux Foundation.

## Impact

The reported consequences are that an authenticated peer can inject tasks into another client's conversation context and read or poison that client's accumulated state, and that identity established at the transport layer is not carried across delegation hops, so an intermediary can collect forwarded credentials with no party able to verify the original principal. AgentSkill fields are described as self-asserted with no attestation. Filed as OTHER: these are absences in a wire specification, and a context-injection reading would wrongly imply a demonstrated exploit.

## Mitigation

Treat the specification's gaps as design gaps to close rather than implementation bugs: bind ownership and access control to conversation contexts, propagate the original principal's identity across delegation hops, and require attestation for the capability fields a peer advertises. Until the protocol carries those, scope credentials per hop and re-authorize at each delegation rather than forwarding them unchanged.

## Sources

- **PRIMARY** - [A2ABreak: Systematic Security Analysis of the A2A Protocol](https://arxiv.org/abs/2609.10871)
- **PRIMARY** - [A2ABreak: Systematic Security Analysis of the A2A Protocol (full text)](https://arxiv.org/html/2609.10871v1)

Generated from `data/entries/theoretical-a2a-context-ownership-absence.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-a2a-context-ownership-absence.yml).
