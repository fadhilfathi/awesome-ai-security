# Roo Code remote code execution by writing an MCP configuration into the workspace

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `coding-agent-roo-code-mcp-config-command-execution` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Tool poisoning |
| Target | Roo Code VS Code extension before 3.20.3 (npm package roo-cline) |
| Disclosure date | 2025-06-27 |
| Last verified | 2026-10-04 |
| CVE | CVE-2025-53098 |

## Summary

Roo Code keeps its project-specific MCP server configuration in a workspace file whose format allows arbitrary commands to be launched. The advisory reports that an attacker able to submit prompts to the agent could ask it to write a malicious command into that configuration, and that a user who had opted in to auto-approving file writes would then have that command run. The vendor fixed it in 3.20.3 by adding an extra opt-in layer for writes to the agent's own configuration files. The vendor record reports no exploitation.

## Impact

The attacker gains arbitrary command execution on the developer's machine through an MCP server the agent itself wrote on the attacker's behalf. Class choice: TOOL_POISONING, because the source names the MCP configuration file the tool operator's agent consults as the defective artefact, and the taxonomy tie-break assigns a payload in a tool definition that caused the agent to act to this class even though the resulting act ran a command. PROMPT_INJECTION_INDIRECT was considered and rejected because the delivery channel is the tool definition itself, not ordinary retrieved content.

## Mitigation

Upgrade to Roo Code 3.20.3 or later. Leave auto-approve for file writes off, since the vendor lists it as off by default and the advisory says the chain needs it, and review any .roo directory an agent has touched for entries whose command line is not what you expect.

## Sources

- **PRIMARY** - [Potential Remote Code Execution via Model Context Protocol in the Roo Code extension (GHSA-5x8h-m52g-5v54)](https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-5x8h-m52g-5v54)
- **PRIMARY** - [CVE-2025-53098 record: Roo Code remote code execution via the workspace MCP configuration file](https://cveawg.mitre.org/api/cve/CVE-2025-53098)

Generated from `data/entries/coding-agent-roo-code-mcp-config-command-execution.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/coding-agent-roo-code-mcp-config-command-execution.yml).
