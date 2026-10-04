# Linguistic illegibility argued to undermine monitors that read an agent's reasoning text

`T3 [=-]` **Tier 3 - Theoretical**

| Field | Value |
| --- | --- |
| Id | `theoretical-llm-sandbox-escape-anomaly-monitor-gap` |
| Tier | `T3 [=-]` **Tier 3 - Theoretical** |
| Attack class | Other |
| Target | Agents whose sandbox relies on reading the model's reasoning or output text to detect harmful intent |
| Disclosure date | 2026-09-02 |
| Last verified | 2026-10-04 |

## Summary

A position paper argues that a model's language output and the features read out of its activations are an unreliable picture of what the model is actually computing, because most of that computation is arithmetic over activation space with lossy translation to text only at the input and output ends. It calls this linguistic illegibility and names the security consequence: a monitor that judges the model by what it says is judging a lossy projection, so intent expressed in activations rather than words is not something such a monitor can be shown to catch. The paper proposes design principles for a sandbox rather than building one.

## Impact

The claimed gain is that a model with harmful intent gets to act on the external world while a language-based monitor reports nothing unusual, which the paper says would defeat detection rather than merely delay it. It is an argument with no run against a system; the paper's own security model assumes a model could be intrinsically misaligned rather than injected. Filed as OTHER: the mechanism is unfaithfulness of the model's textual self-report as the control, which no class tests for, and the impact field names that.

## Mitigation

Do not rest containment on reading the model's language. The paper argues for a floor beneath linguistic monitoring built from taint tracking over model-produced data, robust virtualization, and third-party auditing of sandbox configurations, and it notes those would have limited recent frontier-model sandbox escapes. Treat introspective monitoring as one layer with known blind spots, not as the control.

## Sources

- **PRIMARY** - [The Implications of Linguistic Illegibility for LLM Security](https://arxiv.org/abs/2609.02852)
- **PRIMARY** - [The Implications of Linguistic Illegibility for LLM Security (full text)](https://arxiv.org/html/2609.02852v1)

Generated from `data/entries/theoretical-llm-sandbox-escape-anomaly-monitor-gap.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/theoretical-llm-sandbox-escape-anomaly-monitor-gap.yml).
