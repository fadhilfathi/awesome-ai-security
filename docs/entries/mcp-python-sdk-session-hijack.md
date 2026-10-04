# MCP Python SDK serves HTTP session traffic without checking which principal owns the session

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-python-sdk-session-hijack` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Data exfiltration |
| Target | MCP Python SDK (pip package mcp) 1.27.1 and earlier, HTTP transports with bearer-token auth |
| Disclosure date | 2026-06-05 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-52869 |

## Summary

The MCP Python SDK routed HTTP requests to an existing MCP session using only the session identifier, supplied as a query parameter on the SSE transport and as the Mcp-Session-Id header on stateful streamable HTTP. It never compared the request's authentication context with the credentials that created the session, so any client holding a valid bearer token for the same server could send JSON-RPC messages into another client's session if it learned the session ID. Version 1.27.2 records the principal that created each session and answers a mismatched request with the same 404 it gives for an unknown session.

## Impact

A client authenticated to the same server could inject tool calls into another user's session and, on streamable HTTP, read the results back in its own request response; on SSE the results are pushed to the original client's event stream. That is tool results moving to an unintended principal, so the entry is DATA_EXFILTRATION and not CREDENTIAL_EXPOSURE, because the advisory names no credential as the exposed item. Session IDs are randomly generated UUIDs, so obtaining one out of band, through logs or network observation, is a prerequisite.

## Mitigation

Upgrade to mcp 1.27.2 or later. Deployments where many end users share a single OAuth client, such as hosted clients and gateways, should ensure their token verifier populates AccessToken.subject so sessions are isolated per user rather than per client. Deployments using a custom authentication backend rather than the built-in BearerAuthBackend should enforce the same principal check themselves.

## Sources

- **PRIMARY** - [HTTP transports serve session requests without verifying the authenticated principal (GHSA-jpw9-pfvf-9f58)](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-jpw9-pfvf-9f58)
- **PRIMARY** - [CVE-2026-52869 CVE record, including the CISA enrichment reporting no exploitation](https://cveawg.mitre.org/api/cve/CVE-2026-52869)

Generated from `data/entries/mcp-python-sdk-session-hijack.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-python-sdk-session-hijack.yml).
