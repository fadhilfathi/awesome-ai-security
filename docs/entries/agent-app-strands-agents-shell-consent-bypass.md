# Prompt injection bypasses the shell tool consent gate in Strands Agents Tools

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-strands-agents-shell-consent-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | strands-agents-tools pip package, versions below 0.8.0, shell tool |
| Disclosure date | 2026-08-03 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-18733 |

## Summary

The shell tool in the Strands Agents Tools package asks an operator for consent before running a command, and the advisory says its input schema also exposed a non_interactive parameter the model itself could set. Text an agent reads, such as a web page, a Slack message or a file, can therefore steer the model into setting that flag and skipping the gate; the advisory is GHSA-mqvc-p852-wf8x, CVE-2026-18733. The maintainers released the fix as version 0.8.0.

## Impact

AWS states that anyone who can get crafted text in front of the agent can execute arbitrary operating system commands on the host with the privileges of the agent process, removing the human check the tool was built around. AGENT_PRIVILEGE_ABUSE was considered, since the gain outlives the single request, but the taxonomy resolves it by the step that granted authority, and that is the injection, not a new binding or credential. It is indirect injection rather than tool poisoning because the payload did not arrive in a tool definition.

## Mitigation

Upgrade to strands-agents-tools 0.8.0, where the consent gate can no longer be bypassed through the parameter, and check forks for the same fix. Until then, do not expose the shell tool to an agent that processes untrusted content, and run any agent that keeps the shell tool in an isolated least-privilege environment so executed commands are contained.

## Sources

- **PRIMARY** - [Prompt injection bypasses shell tool consent gate in Strands Agents Tools (GHSA-mqvc-p852-wf8x)](https://github.com/strands-agents/tools/security/advisories/GHSA-mqvc-p852-wf8x)
- **PRIMARY** - [CVE-2026-18733 Strands Agents Tools shell tool record](https://cveawg.mitre.org/api/cve/CVE-2026-18733)

Generated from `data/entries/agent-app-strands-agents-shell-consent-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-strands-agents-shell-consent-bypass.yml).
