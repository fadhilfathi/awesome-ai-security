# Hugging Face Accelerate executes code while parsing checkpoints, and the vendor declined to fix it

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-hf-accelerate-checkpoint-deserialization` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Supply chain (model) |
| Target | Hugging Face Accelerate commit 43526c5c089cc831530f42bbbe66a0cb0b0ea461 (pip package accelerate) |
| Disclosure date | 2025-12-23 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-14925 |

## Summary

The Zero Day Initiative found that the checkpoint parser in Hugging Face Accelerate validated no part of the attacker-supplied data before deserializing it, so a checkpoint file could carry executable content. ZDI reported the issue in September 2025; the bug bounty rejected it as out of scope, and on 14 October 2025 the vendor confirmed no changes would be made and closed the report as informative. ZDI published it as a zero-day advisory on 18 December 2025, and the CVE record names the affected Accelerate commit.

## Impact

Loading a checkpoint the attacker supplied runs their code in the context of the current process, which for the training and inference launcher is the job that has access to the training data and the cluster. The record scores it 7.8 with required user interaction, and the CISA enrichment in the record states no exploitation was seen. The artefact that carries the compromise is a checkpoint the victim pulls in, not a package resolved in an index, so the direction rule in the taxonomy makes this SUPPLY_CHAIN_MODEL rather than SUPPLY_CHAIN_PACKAGE.

## Mitigation

No fix is available: the vendor closed the report with no change. ZDI's stated mitigation is to restrict interaction with the product. Verify the provenance of every checkpoint before handing it to Accelerate, keep training and inference launchers isolated from credentials they do not need, and convert checkpoints to a format that does not execute on load where the pipeline allows it.

## Sources

- **PRIMARY** - [ZDI-25-1140: Hugging Face Accelerate deserialization of untrusted data](https://www.zerodayinitiative.com/advisories/ZDI-25-1140/)
- **PRIMARY** - [CVE-2025-14925 CVE record, naming the affected Accelerate commit](https://cveawg.mitre.org/api/cve/CVE-2025-14925)

Generated from `data/entries/ai-infra-hf-accelerate-checkpoint-deserialization.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-hf-accelerate-checkpoint-deserialization.yml).
