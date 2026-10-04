# MCP Ruby SDK lets a second connection replace a live SSE stream and take its tool responses

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-ruby-sdk-sse-stream-hijack` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Data exfiltration |
| Target | MCP Ruby SDK (RubyGems gem mcp) 0.9.1 and earlier, streamable HTTP transport |
| Disclosure date | 2026-03-27 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-33946 |

## Summary

The Ruby implementation of MCP keeps one Server-Sent Events stream per session ID, and when a second client presents the same session ID it silently overwrites the stored stream with its own instead of rejecting the connection or checking who owns the session. The reporter attached two Python client scripts demonstrating the takeover against the SDK's own example server: the legitimate client's notifications stop and the second client begins receiving all of them. The transport also records no user identity against a session. Version 0.9.2 carries the patch.

## Impact

Anyone who learns a session ID can take over that session's event stream and receive every subsequent tool response the server sends, which the advisory describes as sensitive, while the legitimate user receives nothing and gets no indication of the hijack. The advisory records that of the ten official MCP SDKs, only the C# and Go SDKs bound session IDs to user identity at the time of the report. This is DATA_EXFILTRATION rather than CREDENTIAL_EXPOSURE because the item the source names as reaching the wrong party is the tool responses. CISA reports exploitation as a proof of concept.

## Mitigation

Upgrade to mcp 0.9.2 or later. The advisory's stated guidance for SDK maintainers is to bind session IDs to authenticated user identity where possible and to reject a second simultaneous connection for the same session, and it notes that SDK documentation gave operators no secure session management guidance. Operators should enforce that binding themselves and treat session IDs as values that must not be logged or exposed in URLs.

## Sources

- **PRIMARY** - [Lack of Session Hijacking protection in ruby-sdk - Stream Replacement Vulnerability (GHSA-qvqr-5cv7-wh35)](https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-qvqr-5cv7-wh35)
- **PRIMARY** - [CVE-2026-33946 CVE record, including the CISA enrichment reporting proof-of-concept exploitation](https://cveawg.mitre.org/api/cve/CVE-2026-33946)

Generated from `data/entries/mcp-ruby-sdk-sse-stream-hijack.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-ruby-sdk-sse-stream-hijack.yml).
