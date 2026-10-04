# Position: blockchain execution properties argued to change the threat model for MCP-based agents

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-web3-agent-mcp-attack-surface` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Agents that act on public blockchains through MCP servers, skills or direct tool calls |
| Disclosure date | 2026-08-18 |
| Last verified | 2026-10-04 |

## Summary

A survey argues that the share of deployed MCP tools that modify external state has grown from 27% to 65% of tool use, and that when agents exercise this authority on public blockchains the consequences stop obeying ordinary software assumptions. It names four properties of the execution layer, irreversibility, signing authority, continuous autonomy and sequence-level composition, and argues these turn the recoverable failures of generic agent security into standing irreversible loss. It organizes prior MCP-security work under them and reports no attack.

## Impact

The argued consequence is that the same injection that would be cleaned up in a normal application becomes unrecoverable once an agent has signed and settled a transaction, and that a single compromised component can act repeatedly without a human in the loop. The survey's own contribution is the framework and the framing of prior work, so it evidences no attacker gain of its own. Filed as OTHER: the mechanism is the settlement layer's semantics rather than the payload's channel, which is a property no class tests for.

## Mitigation

Change the deployment rather than the payload: keep an agent's authority over value-bearing actions separate from its authority over ordinary tools, and put a human decision in front of anything a signature commits to. Sequence batching compounds risk, so cap what one agent can settle before it must re-authorize. Treat auditability of the tool and skill supply chain as part of the same problem, since the signing authority is what a poisoned tool inherits.

## Sources

- **PRIMARY** - [When Agents Act on Web3: An Attack-Surface Survey of MCP, Skills, and Tool Calling](https://arxiv.org/abs/2608.17275)
- **PRIMARY** - [When Agents Act on Web3: An Attack-Surface Survey of MCP, Skills, and Tool Calling (full text)](https://arxiv.org/html/2608.17275v1)

Generated from `data/entries/theoretical-web3-agent-mcp-attack-surface.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-web3-agent-mcp-attack-surface.yml).
