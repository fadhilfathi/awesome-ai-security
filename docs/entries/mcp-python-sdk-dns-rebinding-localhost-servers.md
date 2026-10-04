# MCP Python and TypeScript SDKs shipped with DNS rebinding protection off by default for localhost servers

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-python-sdk-dns-rebinding-localhost-servers` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Agent privilege abuse |
| Target | MCP Python SDK before 1.23.0 and MCP TypeScript SDK before 1.24.0, HTTP servers on localhost |
| Disclosure date | 2025-12-02 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-66416, CVE-2025-66414 |

## Summary

The reference client and server SDKs for MCP bind to localhost by default, which makes DNS rebinding the natural attack against them: a browser resolves an attacker-controlled hostname to 127.0.0.1 and the page's JavaScript speaks straight to the agent's tool server. Both SDKs shipped with that protection disabled unless the operator opted in, so a developer's local MCP server could be invoked from a web page the developer merely opened. Each project published an advisory and a fix on 2 December 2025, credited to the same outside researcher.

## Impact

A page the developer visits can reach tool servers that were meant to be reachable only from that machine and invoke their tools or resources on the user's behalf, which is an agent exercising authority the operator granted it but did not intend to expose to a web origin, so this is AGENT_PRIVILEGE_ABUSE. INSECURE_OUTPUT_HANDLING was considered and rejected because neither advisory names a defect in how an application consumes model output. Both limit the exposure to HTTP servers run on localhost without authentication and state that stdio servers are unaffected.

## Mitigation

Upgrade to mcp 1.23.0 or later and @modelcontextprotocol/sdk 1.24.0 or later, which enable the protection by default for servers bound to loopback. Code using StreamableHTTPSessionManager or SseServerTransport directly, or a custom Express setup, must configure TransportSecuritySettings or apply the exported hostHeaderValidation() middleware itself, and should authenticate the server rather than rely on rebinding protection alone.

## Sources

- **PRIMARY** - [DNS Rebinding Protection Disabled by Default in Model Context Protocol Python SDK for Servers Running on Localhost (GHSA-9h52-p55h-vw2f)](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-9h52-p55h-vw2f)
- **PRIMARY** - [DNS Rebinding Protection Disabled by Default in Model Context Protocol TypeScript SDK for Servers Running on Localhost (GHSA-w48q-cv73-mx4w)](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-w48q-cv73-mx4w)

Generated from `data/entries/mcp-python-sdk-dns-rebinding-localhost-servers.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-python-sdk-dns-rebinding-localhost-servers.yml).
