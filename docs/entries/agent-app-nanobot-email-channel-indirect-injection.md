# Zero-click indirect prompt injection through the nanobot email channel

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-nanobot-email-channel-indirect-injection` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | nanobot personal AI assistant, pip package versions <= 0.1.4.post5, email channel |
| Disclosure date | 2026-03-27 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-33654 |

## Summary

Bitslab reported that nanobot's email channel decides who is allowed to command it by reading the From header of raw mail and trusting it against an allowlist, with no SPF, DKIM or DMARC evaluation. An unauthenticated attacker can therefore forge the header, send a message to the polled inbox, and have the body ingested as a trusted instruction set; the advisory is GHSA-4gmr-2vc8-7qh3, CVE-2026-33654. The maintainers released the patch as version 0.1.6.

## Impact

The advisory states the injected text can drive the agent's tools with no interaction from the bot owner: reading its own config, including the API keys, posting it to an attacker URL, or running a reverse shell through the execution tool if that tool is enabled. CREDENTIAL_EXPOSURE and AGENT_PRIVILEGE_ABUSE were both considered; the taxonomy keys the class on the step that yielded capability, and that step is the retrieved email body, which any remote sender can write, so the entry is filed as indirect injection.

## Mitigation

Upgrade to 0.1.6 or later. Until then, or for forks, stop deriving identity from the From header and instead parse the Authentication-Results header and require spf=pass and dkim=pass; keep email polling off by default; tag mail as external context and run it through a restricted tool set rather than the main agent loop.

## Sources

- **PRIMARY** - [Zero-Click Indirect Prompt Injection and Authentication Bypass via Email Polling (GHSA-4gmr-2vc8-7qh3)](https://github.com/HKUDS/nanobot/security/advisories/GHSA-4gmr-2vc8-7qh3)
- **PRIMARY** - [CVE-2026-33654 nanobot email channel record](https://cveawg.mitre.org/api/cve/CVE-2026-33654)

Generated from `data/entries/agent-app-nanobot-email-channel-indirect-injection.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-nanobot-email-channel-indirect-injection.yml).
