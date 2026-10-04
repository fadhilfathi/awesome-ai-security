# Position: treating runtime security threats to LLM applications as an operational condition to monitor

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-runtime-monitoring-threat-taxonomy` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Deployed LLM applications that call MCP services, retrieval backends and memory during task execution |
| Disclosure date | 2026-02-23 |
| Last verified | 2026-10-04 |

## Summary

A position paper argues that the reliability problems of LLM applications are not exceptional events to be engineered away but expected operating conditions, and that the missing piece is system-level monitoring after deployment rather than better models. It walks a representative application from user prompt through MCP tool discovery, orchestration, retrieval and tool execution, and tabulates threat categories it says monitoring must cover, running from prompt injection and adversarial inputs through response manipulation, denial of service, live data poisoning and sensitive data exposure. It reports no attack and no monitoring results.

## Impact

The claim is organizational: without runtime detection and an incident-response discipline, an attack that succeeds against a deployed agent is discovered by its user rather than by its operator, and the loss is whatever the agent reached. The paper's threat table is its own enumeration rather than evidence of a gain, and it deliberately excludes training-stage attacks. Filed as OTHER: the object is the absence of a detection and response capability, which is not an attack mechanism any class tests for.

## Mitigation

Instrument the runtime rather than only the model: log the prompt, the tool list retrieved at call time, the arguments, the results and the state writes for each step, and alert on anomalies in that trace. The paper's argument is that this monitoring, treated as a standing operation with its own runbooks, is a prerequisite for deploying agents at all, and that guardrails and testing do not cover what happens after release.

## Sources

- **PRIMARY** - [LLM-enabled Applications Require System-Level Threat Monitoring](https://arxiv.org/abs/2602.19844)
- **PRIMARY** - [LLM-enabled Applications Require System-Level Threat Monitoring (full text)](https://arxiv.org/html/2602.19844v1)

Generated from `data/entries/theoretical-runtime-monitoring-threat-taxonomy.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-runtime-monitoring-threat-taxonomy.yml).
