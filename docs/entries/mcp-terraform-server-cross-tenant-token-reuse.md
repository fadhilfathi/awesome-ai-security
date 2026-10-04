# terraform-mcp-server stateless HTTP mode reuses one tenant's Terraform token for other tenants' tool calls

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `mcp-terraform-server-cross-tenant-token-reuse` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Credential exposure |
| Target | HashiCorp terraform-mcp-server 0.2.1 through 1.0.0, stateless streamable-HTTP mode |
| Disclosure date | 2026-07-28 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-16498 |

## Summary

When terraform-mcp-server is configured for stateless streamable HTTP, the underlying MCP library assigns no unique session identifiers to requests. The server's per-session Terraform client cache still relied on those identifiers to tell callers apart, so the tenant who arrived first had their Terraform token used to execute tool calls on behalf of every tenant after them, whatever credentials those later callers supplied. HashiCorp found the issue internally and fixed it in 1.1.0 alongside two related flaws in the same transport.

## Impact

A caller who supplies their own Terraform token can have tool calls executed under a different tenant's identity instead of their own, so reads and writes land on the wrong organization's state. The item the sources name as crossing tenants is the Terraform token, which makes this CREDENTIAL_EXPOSURE rather than DATA_EXFILTRATION even though organization data is also at stake. HashiCorp scored it 10.0 but reported no exploitation; the defect requires that an operator explicitly opted into stateless mode.

## Mitigation

Upgrade to terraform-mcp-server 1.1.0. Until then, do not run terraform-mcp-server in stateless streamable-HTTP mode for a multi-tenant deployment, and restrict network access to the streamable-HTTP listener to trusted users.

## Sources

- **PRIMARY** - [HCSEC-2026-23 - Multiple vulnerabilities impacting HashiCorp Terraform MCP Server](https://discuss.hashicorp.com/t/hcsec-2026-23-multiple-vulnerabilities-impacting-hashicorp-terraform-mcp-server/77606)
- **PRIMARY** - [CVE-2026-16498 CVE record, including the CISA enrichment reporting no exploitation](https://cveawg.mitre.org/api/cve/CVE-2026-16498)

Generated from `data/entries/mcp-terraform-server-cross-tenant-token-reuse.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/mcp-terraform-server-cross-tenant-token-reuse.yml).
