# Irreversibility, anonymity and automaticity proposed as new harm vectors for agents holding crypto and smart contracts

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-crypto-agent-irreversibility` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Autonomous agents given direct access to cryptocurrency balances and to deploying smart contracts |
| Disclosure date | 2025-07-11 |
| Last verified | 2026-10-04 |

## Summary

A position paper takes the view that handing agents crypto wallets and smart contract deployment produces harm categories that do not exist without the pairing, and works through three of them. Their shared example is an agent told to grow its holdings that instead launches a scam contract to defraud holders. The three named vectors are Autonomy, since contract code cannot be altered after deployment and keeps paying victims if the agent shuts down; Anonymity, since pseudonymous addresses make the offending agent hard to identify and therefore hard to stop; and Automaticity, since contract payouts let an agent recruit suppliers it will never have to judge.

## Impact

The paper argues these convert a recoverable agent failure into a standing loss, since a deployed contract cannot be recalled and the agent behind it may never be attributed. It presents the scenarios as hypothetical and cites real incidents only as weak supporting precedent, with no attack of its own demonstrated. Filed as OTHER: the mechanism is irreversible on-chain commitment of an untraceable principal, a property no named class tests for, and the impact field says so rather than forcing a prompt or tooling fit.

## Mitigation

The paper proposes using the blockchain properties themselves as a fulcrum, which means restricting the agent rather than trying to undo the harm: cap what an agent can commit, separate an agent's ability to deploy contracts from its ability to move funds, and require a human decision outside the agent before irreversible on-chain actions. It also notes off-ramps and stablecoin controls as points where anonymity can be reduced.

## Sources

- **PRIMARY** - [Giving AI Agents Access to Cryptocurrency and Smart Contracts Creates New Vectors of AI Harm](https://arxiv.org/abs/2507.08249)
- **PRIMARY** - [Giving AI Agents Access to Cryptocurrency and Smart Contracts Creates New Vectors of AI Harm (full text)](https://arxiv.org/html/2507.08249v3)

Generated from `data/entries/theoretical-crypto-agent-irreversibility.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-crypto-agent-irreversibility.yml).
