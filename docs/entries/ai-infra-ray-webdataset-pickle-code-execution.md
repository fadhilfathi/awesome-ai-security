# Ray Data WebDataset reader executes pickle and torch payloads from a supplied tar archive

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-ray-webdataset-pickle-code-execution` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Supply chain (model) |
| Target | Ray before 2.56.0 (pip package ray), the ray.data.read_webdataset reader |
| Disclosure date | 2026-07-24 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-57516 |

## Summary

Ray's WebDataset reader dispatches on each sample key's file extension and, for .pkl and .pickle members, calls pickle.loads() on the raw bytes, and for .pt and .pth members calls torch.load() with the safer default disabled. The decoder is on by default with no opt-in and no environment variable, so supplying a crafted tar archive to the reader runs the attacker's code inside the Ray workers that process it, at sample time and before any row data is read. The advisory reproduces this end to end and the project patched the reader in 2.56.0.

## Impact

A tar archive delivered from a shared object store, an HTTP URL, a model hub mirror or a model-zoo tarball executes attacker-chosen commands with the privileges of the calling Ray process and its workers, which on a training cluster usually means access to the dataset credentials and the cluster itself. The artefact the victim pulls in is a model or dataset artefact rather than a package resolved from an index, so the taxonomy makes this SUPPLY_CHAIN_MODEL rather than SUPPLY_CHAIN_PACKAGE. The advisory's reproduction ran on Ray 2.55.1 and reports no in-the-wild exploitation.

## Mitigation

Upgrade to Ray 2.56.0 or later. On earlier versions pass a custom decoder or decoder=None to read_webdataset instead of relying on the default, and treat every dataset shard as untrusted code until it has been read by something that does not unpickle.

## Sources

- **PRIMARY** - [Arbitrary code execution via ray.data.read_webdataset default decoder (GHSA-hhrp-gw25-jr43)](https://github.com/ray-project/ray/security/advisories/GHSA-hhrp-gw25-jr43)
- **PRIMARY** - [CVE-2026-57516 CVE record for the Ray WebDataset reader deserialization flaw](https://cveawg.mitre.org/api/cve/CVE-2026-57516)

Generated from `data/entries/ai-infra-ray-webdataset-pickle-code-execution.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-ray-webdataset-pickle-code-execution.yml).
