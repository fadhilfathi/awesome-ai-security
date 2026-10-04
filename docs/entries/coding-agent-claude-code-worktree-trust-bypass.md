# Claude Code folder trust dialog bypass through a crafted Git worktree commondir file

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-claude-code-worktree-trust-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | Claude Code (npm package @anthropic-ai/claude-code) 2.1.63 through 2.1.83 (fixed in 2.1.84) |
| Disclosure date | 2026-04-24 |
| Last verified | 2026-10-04 |
| CVE | CVE-2026-40068 |

## Summary

Claude Code asks a developer to confirm trust before it works in a folder, and it derived that answer partly from the Git worktree commondir file inside the repository. The advisory reports that the file's contents were never validated, so a repository author could point it at a path the developer had already trusted and have the confirmation dialog skipped. Claude Code then ran the hooks defined in the repository's .claude/settings file straight away. Anthropic published the advisory on 2026-04-24 and fixed it in version 2.1.84.

## Impact

Code defined by the attacker in the repository's settings hooks executes on the developer's machine as soon as Claude Code is started in the cloned directory, without the trust confirmation the product relies on. Class choice: INSECURE_OUTPUT_HANDLING, because the source names Claude Code's own handling of repository-supplied configuration as the defective component, and the hooks are an automated consumer of that configuration. AGENT_PRIVILEGE_ABUSE was rejected on the taxonomy tie-break, since the sources name no gain that outlives the hook execution.

## Mitigation

Upgrade to Claude Code 2.1.84 or later. Users on the standard auto-update channel already have the fix. Treat a repository as untrusted until you have read its .claude directory, and do not rely on the trust dialog alone when cloning code from strangers, since the bypass needs only a path the developer has trusted before.

## Sources

- **PRIMARY** - [Trust Dialog Bypass via Git Worktree Spoofing Allows Arbitrary Code Execution (GHSA-q5hj-mxqh-vv77)](https://github.com/anthropics/claude-code/security/advisories/GHSA-q5hj-mxqh-vv77)
- **PRIMARY** - [CVE-2026-40068 record: Claude Code arbitrary code execution via git worktree commondir trust dialog bypass](https://cveawg.mitre.org/api/cve/CVE-2026-40068)

Generated from `data/entries/coding-agent-claude-code-worktree-trust-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-claude-code-worktree-trust-bypass.yml).
