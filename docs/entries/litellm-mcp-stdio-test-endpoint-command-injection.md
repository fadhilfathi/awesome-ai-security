# LiteLLM command execution through MCP stdio test endpoints

`T1 [===]` **Tier 1 - Confirmed in the wild**

| Field | Value |
| --- | --- |
| Id | `litellm-mcp-stdio-test-endpoint-command-injection` |
| Tier | `T1 [===]` **Tier 1 - Confirmed in the wild** |
| Attack class | Insecure output handling |
| Target | BerriAI LiteLLM 1.74.2 to before 1.83.7 (pip package litellm) |
| Disclosure date | 2026-05-08 |
| Last verified | 2026-10-05 |
| CVE | CVE-2026-42271 |

## Summary

LiteLLM exposes endpoints that let an operator preview an MCP server configuration before saving it. Those endpoints accepted a full server definition in the request body, including the command, arguments, and environment used by the stdio transport, and attempting to connect to the previewed server spawned that command as a subprocess on the proxy host. The endpoints were reachable with any valid proxy API key and performed no role check, so a holder of a low-privilege internal key could run arbitrary commands with the privileges of the proxy process. The project shipped a fix in 1.83.7.

## Impact

An authenticated user with a low-privilege internal key obtained arbitrary command execution on the proxy host, inheriting whatever that process could reach: configuration and credentials for every tenant the proxy fronts. This is INSECURE_OUTPUT_HANDLING rather than TOOL_POISONING because the command arrives in the body of a request to a preview endpoint, not in a definition the server operator publishes. CISA lists this CVE in the Known Exploited Vulnerabilities catalog and the enrichment in the CVE record states exploitation is active.

## Mitigation

Upgrade to LiteLLM 1.83.7 or later. Restrict the MCP preview endpoints to administrative roles so an ordinary internal key cannot reach them, and treat any host running an affected proxy as potentially compromised until its credentials are rotated.

## Sources

- **PRIMARY** - [CVE-2026-42271 CVE record, including the CISA exploitation enrichment](https://cveawg.mitre.org/api/cve/CVE-2026-42271)
- **PRIMARY** - [LiteLLM: authenticated command execution via MCP stdio test endpoints (GHSA-v4p8-mg3p-g94g)](https://github.com/BerriAI/litellm/security/advisories/GHSA-v4p8-mg3p-g94g)
- **PRIMARY** - [CISA Known Exploited Vulnerabilities catalog entry for CVE-2026-42271](https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-42271)

Generated from `data/entries/litellm-mcp-stdio-test-endpoint-command-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/litellm-mcp-stdio-test-endpoint-command-injection.yml).
