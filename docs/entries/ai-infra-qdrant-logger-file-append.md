# Qdrant /logger endpoint writes attacker-supplied log lines to a caller-chosen path

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-qdrant-logger-file-append` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Agent privilege abuse |
| Target | Qdrant 1.9.3 to before 1.15.6 (cargo crate qdrant), the POST /logger endpoint |
| Disclosure date | 2026-02-05 |
| Last verified | 2026-10-05 |
| CVE | CVE-2026-25628 |

## Summary

The Qdrant logging endpoint takes an on-disk log file path from the request body. In affected releases nothing constrained that path, and the endpoint needed only read-level access, so a low-privilege caller could point logging at a file the service can write and then inject content into it through any other request whose parameters get logged. The advisory works the attack through by setting the path to the service's configuration file and requesting a collection whose name carries newlines and YAML. The advisory shipped a fix in 1.15.6; the CVE record states the affected range as up to but excluding 1.16.0, so the sources differ on the ceiling and both are recorded rather than reconciled.

## Impact

The advisory demonstrates the injected content becoming valid configuration that takes precedence after a restart, redirecting the static content directory so that files including the password file become readable through the web UI, and notes that overriding configuration may also let the caller set a master key. The gain outlives the single request and is an authority the caller granted itself, which the taxonomy tie-break on persistence settles as AGENT_PRIVILEGE_ABUSE over DATA_EXFILTRATION. The advisory tested 1.15.5 and reports no exploitation outside its own reproduction.

## Mitigation

Upgrade to Qdrant 1.15.6 or later, the version the advisory names as patched. The advisory's own two mitigations apply regardless: restrict the /logger endpoint to users holding management privileges or disable it outright, and constrain the log file path to a dedicated logs directory. Keep the configuration directory non-writable by the service, which is also why Qdrant Cloud is unaffected.

## Sources

- **PRIMARY** - [Arbitrary file write via /logger endpoint (GHSA-f632-vm87-2m2f)](https://github.com/qdrant/qdrant/security/advisories/GHSA-f632-vm87-2m2f)
- **PRIMARY** - [CVE-2026-25628 CVE record for the Qdrant logger file write](https://cveawg.mitre.org/api/cve/CVE-2026-25628)

Generated from `data/entries/ai-infra-qdrant-logger-file-append.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-qdrant-logger-file-append.yml).
