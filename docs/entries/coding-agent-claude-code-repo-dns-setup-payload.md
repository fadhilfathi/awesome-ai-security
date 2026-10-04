# Claude Code reverse shell from a clean repository whose setup script fetches a command from DNS

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-claude-code-repo-dns-setup-payload` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Prompt injection (indirect) |
| Target | Claude Code, and agentic coding tools that run shell commands |
| Disclosure date | 2026-06-25 |
| Last verified | 2026-10-04 |

## Summary

Mozilla's 0DIN group published a worked demonstration against agentic coding tools in which a repository contains no malicious code at all. A package in the repo refuses to work until an init step is run, so the coding agent treats that error as routine recovery, and the init script reads a value from a DNS TXT record and executes it. The authors report the value decoded to a reverse shell and ran as the developer's own user, with the developer's terminal showing only two ordinary-looking setup lines. Because the payload is fetched at run time, the source states no scanner, reviewer or the agent itself ever sees it. No specific vulnerable product version is named or affected range stated.

## Impact

The attacker gains an interactive shell as the developer's user, plus every secret in the environment such as API keys, and can install persistence first. Class choice: PROMPT_INJECTION_INDIRECT, because the instructions travel in retrieved repository content the agent read on its own initiative and the payload is fetched from DNS at run time. INSECURE_OUTPUT_HANDLING and TOOL_POISONING were rejected: the repository is ordinary content and the payload is not a tool definition.

## Mitigation

Treat setup instructions and scripts in unfamiliar repositories as untrusted code, as the source recommends, whatever the coding tool advises. Read what a setup command will actually run, including the contents of any script it invokes and anything that script fetches at run time, and alert on shell constructs such as command substitution and piping a fetched value into a shell.

## Sources

- **PRIMARY** - [Clone This Repo and I Own Your Machine (0DIN)](https://0din.ai/blog/clone-this-repo-and-i-own-your-machine)
- **SECONDARY** - [Clean GitHub repo tricks AI coding agents into running malware](https://www.bleepingcomputer.com/news/security/clean-github-repo-tricks-ai-coding-agents-into-running-malware)

Generated from `data/entries/coding-agent-claude-code-repo-dns-setup-payload.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-claude-code-repo-dns-setup-payload.yml).
