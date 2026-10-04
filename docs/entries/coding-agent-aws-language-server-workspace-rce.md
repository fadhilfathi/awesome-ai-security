# Arbitrary command execution from project configuration files in Language Servers for AWS

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-aws-language-server-workspace-rce` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Language Servers for AWS before 1.65.0 and the Amazon Q Developer IDE plugins that bundle it |
| Disclosure date | 2026-06-23 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-12957 |

## Summary

Language Servers for AWS is the runtime behind Amazon Q Developer's IDE plugins, and AWS describes an improper trust boundary enforcement problem in it: when a developer opens a crafted workspace and trusts it, commands defined in the project's configuration files run automatically. The vendor states the affected products are Language Servers for AWS below 1.65.0 and the Amazon Q Developer plugins that bundle it, and published the bulletin with the advisory on 2026-06-23 crediting Wiz. Both sources state no workarounds and give an upgrade as the remedy.

## Impact

Commands chosen by whoever authored the workspace run under the developer's account with no further interaction, which AWS rates 8.5 under CVSS 4.0 with high confidentiality, integrity and availability impact. Class choice: INSECURE_OUTPUT_HANDLING, because the source names the runtime's handling of project configuration files as the defective component: it trusted a file inside the workspace to define commands to execute, with no review step. SUPPLY_CHAIN_PACKAGE was rejected because the source describes no package index resolving an attacker-authored artefact. No source states exploitation.

## Mitigation

Upgrade the Amazon Q Developer IDE plugin to a release bundling Language Servers for AWS 1.65.0 or later, or 1.69.0 as AWS recommends. AWS states no workarounds are available. Do not open workspaces from untrusted senders in an IDE with the Amazon Q plugins installed until upgraded, and review a workspace's project configuration files first.

## Sources

- **PRIMARY** - [CVE-2026-12957 and CVE-2026-12958 - Issues in Language Servers for AWS and Amazon Q Developer Plugins](https://aws.amazon.com/security/security-bulletins/2026-047-aws/)
- **PRIMARY** - [Arbitrary Code Execution in Language Servers for AWS (GHSA-xhcr-j4j9-3gh7)](https://github.com/aws/language-servers/security/advisories/GHSA-xhcr-j4j9-3gh7)
- **PRIMARY** - [CVE-2026-12957 record: improper trust boundary enforcement in Language Servers for AWS](https://cveawg.mitre.org/api/cve/CVE-2026-12957)

Generated from `data/entries/coding-agent-aws-language-server-workspace-rce.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-aws-language-server-workspace-rce.yml).
