# Indirect prompt injection exfiltrates data through Markdown images in the Codex desktop app

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-codex-desktop-markdown-image-exfil` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | OpenAI Codex desktop app for macOS, builds before 26.527.31326 |
| Disclosure date | 2026-07-06 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-14898 |

## Summary

OpenAI's own CVE record for the Codex desktop app on macOS states that the app rendered remote images from Markdown in model responses without restriction. An attacker who can place an indirect prompt injection in content the app processes, such as a connected-tool result, can induce the model to build a remote image URL that encodes session data, and the app fetches it while rendering, with no separate click; the record is CVE-2026-14898 and the affected builds end at 26.527.31326.

## Impact

OpenAI states successful exploitation could exfiltrate secrets and other information accessible in the Codex session, naming API keys, source code and data returned by connected tools. INSECURE_OUTPUT_HANDLING was considered, since the Markdown renderer performs the fetch, but OpenAI names the induced model as the failing step. CREDENTIAL_EXPOSURE was also considered, since API keys are named, but the taxonomy routes by the step that yielded capability, here the injected instruction. The record states no integrity or availability impact was shown and no exploitation in the wild is known.

## Mitigation

Update to a build at or above 26.527.31326. Do not let model output drive automatic network fetches: block external image loads in the renderer, allow only data URIs for locally attached images, require explicit user approval before any remote fetch, and constrain the app's egress so a rendered response cannot reach an arbitrary host.

## Sources

- **PRIMARY** - [CVE-2026-14898 OpenAI Codex desktop app for macOS record](https://cveawg.mitre.org/api/cve/CVE-2026-14898)

Generated from `data/entries/agent-app-codex-desktop-markdown-image-exfil.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-codex-desktop-markdown-image-exfil.yml).
