# sentence-transformers executes model-directory Python despite trust_remote_code=False

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-sentence-transformers-trust-remote-code-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Supply chain (model) |
| Target | Hugging Face sentence-transformers before 5.6.0 (pip package sentence-transformers) |
| Disclosure date | 2026-07-31 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-68770 |

## Summary

sentence-transformers documents trust_remote_code=False as the way to load a model without running the custom code shipped alongside it. The guard that implements the flag in the import_module_class helper also accepted any path that merely existed on the local filesystem, so the check passed for a local model directory regardless of what the caller asked for. An attacker who can place Python modules referenced by a model's modules.json into that directory therefore gets them imported at load time. The advisory was reported through the project's issue tracker and fixed in 5.6.0.

## Impact

Code placed in a model directory runs with the privileges of the loading process, which for a service that loads embeddings for other tenants is the whole service. The attacker needs influence over the contents of a model directory on disk, which is the position a user has after downloading a third-party model, and the safety flag the API offered gave no protection in that case. The artefact carrying the compromise is a model artefact rather than a package from an index, so the taxonomy makes this SUPPLY_CHAIN_MODEL. No source states that exploitation occurred outside the reporting path.

## Mitigation

Upgrade to sentence-transformers 5.6.0 or later. Until then do not treat trust_remote_code=False as a boundary: inspect the model directory before loading it, load third-party models in a sandbox, and keep downloaded model directories out of any location your application imports from.

## Sources

- **PRIMARY** - [CVE-2026-68770 CVE record for the sentence-transformers trust_remote_code bypass](https://cveawg.mitre.org/api/cve/CVE-2026-68770)
- **PRIMARY** - [GitHub Advisory Database entry for CVE-2026-68770, listing the 5.6.0 patch](https://github.com/advisories/GHSA-jhr6-gm9c-rqjv)

Generated from `data/entries/ai-infra-sentence-transformers-trust-remote-code-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-sentence-transformers-trust-remote-code-bypass.yml).
