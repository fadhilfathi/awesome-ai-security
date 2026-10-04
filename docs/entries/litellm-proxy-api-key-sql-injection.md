# LiteLLM unauthenticated SQL injection in proxy API key verification

`T1 [===]` **Tier 1 - Confirmed in the wild**

| Field | Value |
| --- | --- |
| Id | `litellm-proxy-api-key-sql-injection` |
| Tier | `T1 [===]` **Tier 1 - Confirmed in the wild** |
| Attack class | Credential exposure |
| Target | BerriAI LiteLLM 1.81.16 to before 1.83.7 (pip package litellm) |
| Disclosure date | 2026-05-08 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-42208 |

## Summary

LiteLLM validates the API keys presented to its proxy routes against a database. In the affected releases the lookup query interpolated the caller-supplied key value into the query text instead of binding it as a separate parameter. An attacker could therefore send a crafted Authorization header to any proxied model route and reach the vulnerable query through the proxy's error-handling path. The project shipped a fix in 1.83.7.

## Impact

The flaw was reachable without authentication, and the advisory states an attacker could read from the proxy's database and may also be able to modify it, which exposes the API keys the proxy manages for its tenants. CISA lists this CVE in the Known Exploited Vulnerabilities catalog, added 2026-05-08, and the enrichment in the CVE record states exploitation is active, so it is filed here as an attack with confirmed real-world use. The sources do not state how many victims were affected.

## Mitigation

Upgrade to LiteLLM 1.83.7 or later, and rotate any API keys the affected proxy held, since an attacker able to read the key database may have taken them. Where an upgrade is not immediate, the advisory gives one workaround: set disable_error_logs to true under general_settings, which removes the error-handling path through which unauthenticated input reaches the vulnerable query.

## Sources

- **PRIMARY** - [SQL injection in Proxy API key verification (GHSA-r75f-5x8p-qvmc)](https://github.com/BerriAI/litellm/security/advisories/GHSA-r75f-5x8p-qvmc)
- **PRIMARY** - [CVE-2026-42208 CVE record, including the CISA exploitation enrichment](https://cveawg.mitre.org/api/cve/CVE-2026-42208)
- **PRIMARY** - [CISA Known Exploited Vulnerabilities catalog entry for CVE-2026-42208](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-42208)

Generated from `data/entries/litellm-proxy-api-key-sql-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/litellm-proxy-api-key-sql-injection.yml).
