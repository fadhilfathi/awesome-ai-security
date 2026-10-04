# Ollama GGUF loader reads past the file buffer and leaks server memory to the caller

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `ai-infra-ollama-gguf-loader-memory-leak` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Credential exposure |
| Target | Ollama before 0.17.1, the GGUF model loader behind /api/create |
| Disclosure date | 2026-05-04 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-7482 |

## Summary

The record describes a crafted GGUF file whose declared tensor offset and size exceed the file's real length. Quantizing that tensor in the GGUF loader reads past the allocated heap buffer, so the bytes that follow it in memory end up inside the model artifact the server produces. Because /api/create and /api/push carry no authentication in the upstream distribution, the caller who uploaded the file can push the resulting artifact to a registry they control and read the leaked memory out of it. The fix landed in 0.17.1.

## Impact

The record names what the overread can disclose as environment variables, API keys, system prompts and other users' concurrent conversation data, so the taxonomy tie-break on the item set classifies this CREDENTIAL_EXPOSURE rather than DATA_EXFILTRATION. It scores 9.1 with no privileges required and no user interaction, and its enrichment states that the documented OLLAMA_HOST=0.0.0.0 configuration is widely used and that large public exposure was observed. No source states that any specific deployment was exploited.

## Mitigation

Upgrade to Ollama 0.17.1 or later. The record gives three interim steps: keep the server bound to a trusted interface rather than 0.0.0.0, put an authenticating reverse proxy in front of /api/create and /api/push, and restrict outbound egress from the host so a push cannot reach an attacker-controlled registry.

## Sources

- **PRIMARY** - [CVE-2026-7482 CVE record for the Ollama GGUF loader out-of-bounds read](https://cveawg.mitre.org/api/cve/CVE-2026-7482)
- **PRIMARY** - [GitHub Advisory Database entry for the Ollama GGUF loader heap overread](https://github.com/advisories/GHSA-x8qc-fggm-mpqg)

Generated from `data/entries/ai-infra-ollama-gguf-loader-memory-leak.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/ai-infra-ollama-gguf-loader-memory-leak.yml).
