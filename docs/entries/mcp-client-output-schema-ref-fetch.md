# MCP Python client fetches server-chosen $ref URLs while validating tool results

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-client-output-schema-ref-fetch` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Tool poisoning |
| Target | MCP Python SDK (pip package mcp) 1.29.1 and 2.1.1 and earlier, client-side output schema validation |
| Disclosure date | 2026-09-28 |
| Last verified | 2026-10-04 |

## Summary

When a connected MCP server declares an outputSchema for one of its tools, the Python SDK client validated each call_tool result with jsonschema's default resolver, which opens any $ref it cannot satisfy from the schema itself. A server that put an http, https or file reference in a tool's published output schema could therefore make the client issue that request or read that file on the client's own network position, on every call of the tool, with no setting to switch the validation off. Version 1.30.0 on the 1.x line and 2.2.0 on the 2.x line resolve references only inside the schema document the server sent.

## Impact

The advisory is explicit that the fetched content was used only as a schema and never sent back to the server, so no data crosses to the attacker here; what the attacker gets is that the client's host makes arbitrary outbound requests or reads a local file, which can probe internal services, and that a peer which accepts a connection then goes silent freezes every session in the process, because the fetch runs synchronously on the event loop with no timeout. The payload sits in a schema field the server operator publishes as part of the tool definition, the TOOL_POISONING inclusion test.

## Mitigation

Upgrade to mcp 1.30.0 or 2.2.0 or later. Until then, call tools only on servers you trust, or as a partial stopgap skip any tool whose outputSchema contains an $id or a $ref that does not begin with #.

## Sources

- **PRIMARY** - [Client fetched server-chosen $ref URLs while validating tool results against output schemas (GHSA-rwrf-2pqf-9j8j)](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-rwrf-2pqf-9j8j)

Generated from `data/entries/mcp-client-output-schema-ref-fetch.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-client-output-schema-ref-fetch.yml).
