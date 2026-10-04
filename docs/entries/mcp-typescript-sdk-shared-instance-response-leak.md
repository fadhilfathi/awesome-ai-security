# Reusing one MCP TypeScript SDK transport or server across clients routes one client's tool results to another

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-typescript-sdk-shared-instance-response-leak` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Data exfiltration |
| Target | MCP TypeScript SDK (@modelcontextprotocol/sdk) 1.10.0 through 1.25.3, stateless multi-client servers |
| Disclosure date | 2026-02-04 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-25536 |

## Summary

The TypeScript SDK maps each incoming JSON-RPC message ID to the HTTP stream that carried it, but the SDK's own clients number their messages with an incrementing counter starting at zero. A server that reused one StreamableHTTPServerTransport across client requests, which the advisory says is most common in stateless mode, would therefore see the second client's ID overwrite the first client's mapping entry and deliver the response to the wrong client. A related defect let one McpServer connected to several transports send notifications, sampling and elicitation requests to whichever client connected last. Version 1.26.0 turns both into hard errors.

## Impact

One client receives the tool results, progress notifications, sampling requests or elicitation prompts belonging to another client on the same server, which is DATA_EXFILTRATION because those are the items the source names as reaching the wrong party and none is a credential. It is not AGENT_PRIVILEGE_ABUSE because nothing acquires authority; the servers are misconfigured in a way the advisory says is a common deployment mistake. The advisory scopes the exposure to multi-client servers, so a single-client local development setup is not affected, and states no exploitation.

## Mitigation

Upgrade to @modelcontextprotocol/sdk 1.26.0 or later, which throws on a reused protocol or a reused stateless transport instead of misrouting silently. Before upgrading, create a fresh McpServer and transport per request in stateless mode or per session in stateful mode; the advisory includes reference implementations of both.

## Sources

- **PRIMARY** - [Sharing server/transport instances can leak cross-client response data (GHSA-345p-7cg4-v4c7)](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-345p-7cg4-v4c7)

Generated from `data/entries/mcp-typescript-sdk-shared-instance-response-leak.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-typescript-sdk-shared-instance-response-leak.yml).
