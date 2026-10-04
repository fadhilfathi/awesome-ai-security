# Ray dashboard remote code execution from a developer's browser via DNS rebinding

`T1 [===]` **Tier 1 - Confirmed in the wild**

| Field | Value |
| --- | --- |
| Id | `ray-dashboard-browser-rce-dns-rebinding` |
| Tier | `T1 [===]` **Tier 1 - Confirmed in the wild** |
| Attack class | Agent privilege abuse |
| Target | Ray before 2.52.0 (pip package ray), dashboard used as a development tool |
| Disclosure date | 2025-11-26 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-62593 |

## Summary

Ray is a distributed compute engine widely used to run AI and machine learning workloads, and its dashboard is normally reachable only from the developer's own machine during development. The dashboard relied on the User-Agent header starting with the string Mozilla as its browser-origin defence. Because the fetch specification lets a page set that header, the check could not distinguish a real browser navigation from a scripted request. Combined with a DNS rebinding attack against the browser, a developer who visited an attacker-controlled page, or loaded a malicious advertisement, could have code run on the machine serving Ray. The project shipped a fix in 2.52.0.

## Impact

The advisory describes remote code execution on the developer workstation with confidentiality, integrity, and availability impact all high. In practice that workstation holds source access, cloud credentials, and often the credentials for the cluster the dashboard is driving. CISA lists this CVE in the Known Exploited Vulnerabilities catalog, added 2026-08-17, and the enrichment in the CVE record states exploitation is active, so it is filed here as an attack with confirmed real-world use. The sources do not state how many victims were affected.

## Mitigation

Upgrade to Ray 2.52.0 or later. Until then, do not expose the Ray dashboard beyond localhost, and do not rely on a User-Agent check as an origin control; a header a page can set is not evidence that a request came from a browser address bar.

## Sources

- **PRIMARY** - [CVE-2025-62593 CVE record, including the CISA exploitation enrichment](https://cveawg.mitre.org/api/cve/CVE-2025-62593)
- **PRIMARY** - [Ray remote code execution via Safari and Firefox browsers through DNS rebinding (GHSA-q279-jhrf-cc6v)](https://github.com/ray-project/ray/security/advisories/GHSA-q279-jhrf-cc6v)
- **PRIMARY** - [CISA Known Exploited Vulnerabilities catalog entry for CVE-2025-62593](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-62593)
- **SECONDARY** - [RondoDox infrastructure analysis cited by the CISA enrichment](https://www.bitsight.com/blog/rondodox-botnet-infrastructure-analysis)

Generated from `data/entries/ray-dashboard-browser-rce-dns-rebinding.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ray-dashboard-browser-rce-dns-rebinding.yml).
