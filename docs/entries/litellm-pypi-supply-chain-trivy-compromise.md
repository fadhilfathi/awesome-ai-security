# LiteLLM malicious PyPI releases published after a compromised CI dependency

`T1 [===]` **Tier 1 - Confirmed in the wild**

| Field | Value |
| --- | --- |
| Id | `litellm-pypi-supply-chain-trivy-compromise` |
| Tier | `T1 [===]` **Tier 1 - Confirmed in the wild** |
| Attack class | Supply chain (package) |
| Target | litellm v1.82.7 and v1.82.8 on PyPI, via the project's CircleCI release pipeline |
| Disclosure date | 2026-03-24 |
| Last verified | 2026-10-04 |

## Summary

LiteLLM publishes itself to PyPI from an automated pipeline. On 2026-03-24 the project pushed v1.82.7 and then v1.82.8, and both were malicious: they were live for roughly forty minutes before PyPI quarantined them, and the project worked with PyPI to delete them. The vendor's own account is that an unpinned Trivy security-scanner dependency in the pipeline had itself been compromised, ran during a scan, read the release credentials from the environment, and used them to publish the bad versions. The vendor named three contributing factors: a shared CI environment, long-lived static release secrets, and the unpinned scanner.

## Impact

Malicious code was published to a public package index under the project's own name and release path, so users who installed either version during the exposure window were affected by running attacker code on their own machines. The vendor reports rotating the PyPI, GitHub, and Docker credentials and maintainer accounts, removing roughly six thousand open branches, and pausing releases, and states it found no evidence of lateral movement into its own systems. It also states the last twenty releases show no indicators of compromise.

## Mitigation

Pin every dependency and action in a release pipeline to a verified digest or commit, including security scanners, and add a cooldown before adopting a new version of a package. Move release credentials to ephemeral identity, such as PyPI Trusted Publisher, rather than long-lived static secrets. Give each pipeline stage its own isolated environment so one compromised component cannot reach the release path. Sign releases so consumers can verify them; the vendor now signs its images with cosign. Anyone who installed v1.82.7 or v1.82.8 should rotate secrets present in that environment.

## Sources

- **PRIMARY** - [Security Townhall Updates (vendor incident report, 2026-03-27)](https://docs.litellm.ai/blog/security-townhall-updates)
- **PRIMARY** - [Security Update: Suspected Supply Chain Incident (vendor notice, 2026-03-24)](https://docs.litellm.ai/blog/security-update-march-2026)
- **SECONDARY** - [Trivy supply chain attack, the upstream scanner compromise the vendor cites](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/)

Generated from `data/entries/litellm-pypi-supply-chain-trivy-compromise.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/litellm-pypi-supply-chain-trivy-compromise.yml).
