# terraform-mcp-server executes a user's tool calls with another user's cached Terraform credentials

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-terraform-server-session-credential-inheritance` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Credential exposure |
| Target | HashiCorp terraform-mcp-server 0.3.0 through 1.0.0 per the CVE records, or 0.2.1 per vendor bulletin HCSEC-2026-23, stateful streamable-HTTP mode |
| Disclosure date | 2026-07-28 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-16496 |

## Summary

HashiCorp's terraform-mcp-server is meant for centralised multi-user deployments in which each caller supplies their own Terraform Cloud or Enterprise token so that RBAC applies to their actions. In stateful streamable-HTTP mode the server cached a Terraform API client per MCP session, keyed on the session ID alone and never bound to the token that created it, so a caller who obtained another user's session ID had their tool calls run against that user's cached client and bearer token. HashiCorp identified the issue internally and published it as part of a three-CVE bulletin; it was reported by Juan Pablo Martinez Kuhn of Coinspect and fixed in 1.1.0.

## Impact

The attacker's tool calls execute with the victim's Terraform bearer token, so they reach the victim's organizations, workspaces and variables to the extent that token's permissions allow, and they can write as well as read. This is CREDENTIAL_EXPOSURE because the item the sources name as reaching an unintended principal is a bearer token and the access it authorises; it is not merely DATA_EXFILTRATION. The CISA enrichment reports exploitation as none. It affected only stateful streamable HTTP, the default for central deployments.

## Mitigation

Upgrade to terraform-mcp-server 1.1.0. Operators who cannot upgrade should restrict network access to the streamable-HTTP listener to trusted users and treat MCP session IDs as sensitive values, since the cache lookup is keyed on the session ID and nothing else.

## Sources

- **PRIMARY** - [HCSEC-2026-23 - Multiple vulnerabilities impacting HashiCorp Terraform MCP Server](https://discuss.hashicorp.com/t/hcsec-2026-23-multiple-vulnerabilities-impacting-hashicorp-terraform-mcp-server/77606)
- **PRIMARY** - [CVE-2026-16496 CVE record, including the CISA enrichment reporting no exploitation](https://cveawg.mitre.org/api/cve/CVE-2026-16496)
- **PRIMARY** - [Security Bulletin: terraform-mcp-server vulnerable to cross-user credential inheritance if an MCP session ID is obtained by another user](https://www.ibm.com/support/pages/security-bulletin-terraform-mcp-server-vulnerable-cross-user-credential-inheritance-if-mcp-session-id-obtained-another-user)

Generated from `data/entries/mcp-terraform-server-session-credential-inheritance.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-terraform-server-session-credential-inheritance.yml).
