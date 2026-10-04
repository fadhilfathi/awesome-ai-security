# Hugging Face Transformers executes code while parsing model files for several architectures

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-hf-transformers-model-file-deserialization` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Supply chain (model) |
| Target | Hugging Face Transformers Perceiver, Transformer-XL, megatron_gpt2 and GLM4 model files, release 4.57.1 named for GLM4 |
| Disclosure date | 2025-12-23 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-14920, CVE-2025-14921, CVE-2025-14924, CVE-2025-14930 |

## Summary

The Zero Day Initiative reported and published four related flaws in Hugging Face Transformers, covering the Perceiver, Transformer-XL, megatron_gpt2 and GLM4 model classes. In each case the parser for the corresponding model file, checkpoint or weight set validated no part of the attacker-supplied data before deserializing it, so the file itself carried executable content. The records and advisories state that the target must visit a malicious page or open a malicious file, and that the code then runs as the current user or in the current process. None of the four carries a fixed version.

## Impact

Opening a model file the attacker supplied runs their code on the victim's machine, with the privileges of whoever loaded it. The records assign 7.8 with local attack vector and required user interaction, and the CISA enrichment in each record states no exploitation was seen. A second class was considered and rejected: MODEL_THEFT_EXTRACTION covers artefacts moving out of the owner's control, and here the owner pulls a tampered artefact in, which the direction rule in the taxonomy assigns to SUPPLY_CHAIN_MODEL.

## Mitigation

ZDI states that given the nature of the flaw the only salient mitigation is to restrict interaction with the product, and no fixed version is named for any of the four, so treat every model file from an untrusted source as code rather than as data. Prefer weight formats that do not execute on load, verify provenance and checksums of downloaded checkpoints, and load third-party models in a sandboxed process.

## Sources

- **PRIMARY** - [ZDI-25-1150: Hugging Face Transformers Perceiver model deserialization of untrusted data](https://www.zerodayinitiative.com/advisories/ZDI-25-1150/)
- **PRIMARY** - [ZDI-25-1149: Hugging Face Transformers Transformer-XL model deserialization of untrusted data](https://www.zerodayinitiative.com/advisories/ZDI-25-1149/)
- **PRIMARY** - [ZDI-25-1141: Hugging Face Transformers megatron_gpt2 deserialization of untrusted data](https://www.zerodayinitiative.com/advisories/ZDI-25-1141/)
- **PRIMARY** - [ZDI-25-1145: Hugging Face Transformers GLM4 deserialization of untrusted data](https://www.zerodayinitiative.com/advisories/ZDI-25-1145/)
- **PRIMARY** - [CVE-2025-14930 CVE record, naming release 4.57.1 as affected](https://cveawg.mitre.org/api/cve/CVE-2025-14930)

Generated from `data/entries/ai-infra-hf-transformers-model-file-deserialization.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-hf-transformers-model-file-deserialization.yml).
