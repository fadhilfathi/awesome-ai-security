# LiteLLM MCP endpoint authentication bypass via OAuth2 passthrough fallback

`T1 [===]` **Tier 1 - Confirmed in the wild**

| Field | Value |
| --- | --- |
| Id | `litellm-mcp-auth-bypass-oauth2-passthrough` |
| Tier | `T1 [===]` **Tier 1 - Confirmed in the wild** |
| Attack class | Credential exposure |
| Target | BerriAI LiteLLM, versions before 1.84.0 (pip package litellm) |
| Disclosure date | 2026-07-08 |
| Last verified | 2026-10-05 |
| CVE | CVE-2026-59822 |

## Summary

LiteLLM is a proxy that fronts several model providers behind one OpenAI-compatible interface, and it also brokers Model Context Protocol servers for its users. Its MCP auth handler supported an OAuth2 passthrough mode, and the fallback branch of that handler substituted an empty authentication object when key validation failed instead of rejecting the request. A caller presenting a fabricated Authorization header was therefore treated as authenticated and could enumerate and invoke the MCP tools the proxy was configured to reach. A fix shipped in 1.84.0.

## Impact

An unauthenticated attacker could list and call every configured MCP tool behind the proxy, reaching whatever those tools are wired to. The advisory names the reachable items as the configured MCP tools and the services exposed through them, and does not name a credential as the item reaching the attacker; this class rests on such integrations typically holding tokens, a judgement about deployment rather than a claim the advisory makes. CISA lists this CVE in the Known Exploited Vulnerabilities catalog and the enrichment in the CVE record states exploitation is active.

## Mitigation

Upgrade to LiteLLM 1.84.0 or later. Where an upgrade cannot happen immediately, disable the MCP routes or block the /mcp/ paths at the reverse proxy or API gateway, so an unvalidated Authorization header cannot reach the MCP tooling at all.

## Sources

- **PRIMARY** - [MCP Authentication Bypass via OAuth2 Passthrough Fallback (GHSA-7488-6r32-c95q)](https://github.com/BerriAI/litellm/security/advisories/GHSA-7488-6r32-c95q)
- **PRIMARY** - [CVE-2026-59822 CVE record, including the CISA exploitation enrichment](https://cveawg.mitre.org/api/cve/CVE-2026-59822)
- **PRIMARY** - [CISA Known Exploited Vulnerabilities catalog entry for CVE-2026-59822](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-59822)
- **SECONDARY** - [AI infrastructure honeypot report cited by the CISA enrichment](https://www.wiz.io/blog/ai-infrastructure-honeypot)

Generated from `data/entries/litellm-mcp-auth-bypass-oauth2-passthrough.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/litellm-mcp-auth-bypass-oauth2-passthrough.yml).
