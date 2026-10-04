# Stored prompt injection in Kong Konnect MCP analytics data leads to credential disclosure

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-kong-konnect-mcp-stored-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | Kong Konnect Model Context Protocol server (mcp-konnect), versions below 1.0.0 |
| Disclosure date | 2026-05-15 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-13341 |

## Summary

Kong's security advisory for the Konnect MCP server describes an attacker who can send traffic to a gateway planting instructions in request metadata such as the User-Agent. That metadata is stored in Konnect analytics and later returned to an AI assistant by the server's analytics tools without neutralisation, so the assistant reads attacker text as instructions; the advisory is GHSA-7767-3m3w-2p44, CVE-2026-13341. Kong prepared the fixes in release 1.0.0.

## Impact

Kong states that in client environments which fetch remote resources from model output, this could disclose sensitive information to an attacker-controlled URL, exposing secrets or configuration values other MCP tools return, including plugin configuration data, plus internal hostnames. A separate path manipulation flaw let the server request unintended Konnect API endpoints with the user's token. CREDENTIAL_EXPOSURE and DATA_EXFILTRATION were both considered, but the step that yielded capability here was the stored request data the agent read back, so the entry is filed as indirect injection.

## Mitigation

Upgrade to 1.0.0 or later, where Kong neutralises untrusted analytics fields before returning them, validates identifiers as UUIDs and encodes path segments. Leave raw plugin configuration output disabled unless it is strictly required. Sand-box the agent so tool output cannot trigger automatic remote fetches, block automatic rendering of remote content and model-generated links, and apply egress controls to keep agent runtimes off untrusted external hosts.

## Sources

- **PRIMARY** - [Stored Prompt Injection and Credential Exposure via Untrusted Analytics Data in Kong Konnect MCP (GHSA-7767-3m3w-2p44)](https://github.com/Kong/mcp-konnect/security/advisories/GHSA-7767-3m3w-2p44)
- **PRIMARY** - [CVE-2026-13341 Kong Konnect MCP server record](https://cveawg.mitre.org/api/cve/CVE-2026-13341)

Generated from `data/entries/agent-app-kong-konnect-mcp-stored-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-kong-konnect-mcp-stored-injection.yml).
