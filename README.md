# awesome-ai-security

An evidence-graded catalogue of attacks on AI systems. Every entry is tagged with
how well the attack is established, so you can tell a documented incident from a
researcher's proof of concept from speculation.

<!-- BEGIN:GENERATED:count -->
**62** entries; last verified **2026-10-05**.
<!-- END:GENERATED:count -->

## Evidence tiers

<!-- BEGIN:GENERATED:tier-legend -->
- **Tier 1 - Confirmed in the wild.** Badge `T1 [===]`. A real system was affected, and a vendor advisory, postmortem, or CVE record states the finding.
- **Tier 2 - Demonstrated.** Badge `T2 [==-]`. The researcher reproduced the attack against a real build or model, but no occurrence outside a controlled setting is on record.
- **Tier 3 - Theoretical.** Badge `T3 [=-]`. The attack is argued from prior work; no working demonstration is published.
<!-- END:GENERATED:tier-legend -->

## Start here: confirmed in the wild

<!-- BEGIN:GENERATED:tier1 -->
| Tier | Entry | Date | Target | Primary source |
| --- | --- | --- | --- | --- |
| `T1 [===]` | [MLflow unauthenticated webhook SSRF via unvalidated redirects and DNS rebinding](docs/entries/mlflow-webhook-ssrf-redirect-dns-rebinding.md) | 2026-08-17 | MLflow 3.3.0 to before 3.15.0 (pip package mlflow) | [cveawg.mitre.org](https://cveawg.mitre.org/api/cve/CVE-2026-64849) |
| `T1 [===]` | [Autonomous AI agent intrusion into Hugging Face production infrastructure](docs/entries/huggingface-autonomous-agent-production-intrusion.md) | 2026-07-16 | Hugging Face production infrastructure, dataset processing pipeline and internal Kubernetes clusters | [huggingface.co](https://huggingface.co/blog/security-incident-july-2026) |
| `T1 [===]` | [LiteLLM MCP endpoint authentication bypass via OAuth2 passthrough fallback](docs/entries/litellm-mcp-auth-bypass-oauth2-passthrough.md) | 2026-07-08 | BerriAI LiteLLM, versions before 1.84.0 (pip package litellm) | [github.com](https://github.com/BerriAI/litellm/security/advisories/GHSA-7488-6r32-c95q) |
| `T1 [===]` | [LiteLLM command execution through MCP stdio test endpoints](docs/entries/litellm-mcp-stdio-test-endpoint-command-injection.md) | 2026-05-08 | BerriAI LiteLLM 1.74.2 to before 1.83.7 (pip package litellm) | [cveawg.mitre.org](https://cveawg.mitre.org/api/cve/CVE-2026-42271) |
| `T1 [===]` | [LiteLLM unauthenticated SQL injection in proxy API key verification](docs/entries/litellm-proxy-api-key-sql-injection.md) | 2026-05-08 | BerriAI LiteLLM 1.81.16 to before 1.83.7 (pip package litellm) | [github.com](https://github.com/BerriAI/litellm/security/advisories/GHSA-r75f-5x8p-qvmc) |
| `T1 [===]` | [LiteLLM malicious PyPI releases published after a compromised CI dependency](docs/entries/litellm-pypi-supply-chain-trivy-compromise.md) | 2026-03-24 | litellm v1.82.7 and v1.82.8 on PyPI, via the project's CircleCI release pipeline | [docs.litellm.ai](https://docs.litellm.ai/blog/security-townhall-updates) |
| `T1 [===]` | [Ray dashboard remote code execution from a developer's browser via DNS rebinding](docs/entries/ray-dashboard-browser-rce-dns-rebinding.md) | 2025-11-26 | Ray before 2.52.0 (pip package ray), dashboard used as a development tool | [cveawg.mitre.org](https://cveawg.mitre.org/api/cve/CVE-2025-62593) |
<!-- END:GENERATED:tier1 -->

## Attack class x evidence tier

<!-- BEGIN:GENERATED:matrix -->
![Attack class by evidence tier](docs/attack-matrix.svg)

Cell colour encodes the evidence tier (darkest is Tier 1, confirmed in the wild); the numeral is how many entries sit there. A dashed empty cell means nothing is filed under that class at that tier yet.

| Attack class | T1 | T2 | T3 | Total |
| --- | --- | --- | --- | --- |
| Prompt injection (direct) | 0 | 3 | 0 | 3 |
| Prompt injection (indirect) | 0 | 6 | 2 | 8 |
| Tool poisoning | 0 | 2 | 0 | 2 |
| Agent privilege abuse | 2 | 3 | 1 | 6 |
| Data exfiltration | 1 | 6 | 2 | 9 |
| Supply chain (package) | 1 | 0 | 0 | 1 |
| Supply chain (model) | 0 | 5 | 0 | 5 |
| Code assistant abuse | 0 | 0 | 0 | 0 |
| Training data poisoning | 0 | 0 | 1 | 1 |
| Model theft and extraction | 0 | 0 | 0 | 0 |
| Jailbreak | 0 | 0 | 0 | 0 |
| Insecure output handling | 1 | 10 | 0 | 11 |
| Credential exposure | 2 | 5 | 0 | 7 |
| Denial of service | 0 | 0 | 0 | 0 |
| Other | 0 | 1 | 8 | 9 |
| **Total** | 7 | 41 | 14 | 62 |
<!-- END:GENERATED:matrix -->

## Full catalogue

<!-- BEGIN:GENERATED:catalogue -->
### Prompt injection (direct)

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | Boolean prompt injection in the 1millionbot Millie chatbot evades chat restrictions | 2026-03-31 | 1millionbot Millie chat chatbot and AI platform, versions prior to 3.6.0 |
| `T2 [==-]` | Prompt injection in the AiDex LLM chatbot executes operating system commands | 2025-04-15 | AiDex LLM chatbot, versions earlier than 1.7, /api/<string-chat>/message endpoint |
| `T2 [==-]` | Direct prompt injection in the EmailGPT service leaks system prompts and runs unwanted prompts | 2024-06-05 | EmailGPT hosted service, revisions through commit eecfaf2cff58793549dd0c1266ac1d62e0c8811d |

### Prompt injection (indirect)

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | Prompt injection bypasses the shell tool consent gate in Strands Agents Tools | 2026-08-03 | strands-agents-tools pip package, versions below 0.8.0, shell tool |
| `T2 [==-]` | Indirect prompt injection exfiltrates data through Markdown images in the Codex desktop app | 2026-07-06 | OpenAI Codex desktop app for macOS, builds before 26.527.31326 |
| `T2 [==-]` | Claude Code reverse shell from a clean repository whose setup script fetches a command from DNS | 2026-06-25 | Claude Code, and agentic coding tools that run shell commands |
| `T3 [=-]` | Impossibility of perfect prompt-injection prevention in shared-embedding sequence models | 2026-06-25 | LLM applications where trusted instructions and untrusted content share one token embedding and one attention pipeline |
| `T2 [==-]` | Indirect prompt injection through workspace file and directory names in Eclipse Theia AI chat | 2026-06-18 | Eclipse Theia AI chat agent, versions prior to 1.71.0 |
| `T3 [=-]` | Position: what system-level defense can and cannot claim against indirect prompt injection | 2026-03-31 | Agent architectures that plan and execute with an explicit policy enforcer, as described in the paper |
| `T2 [==-]` | Zero-click indirect prompt injection through the nanobot email channel | 2026-03-27 | nanobot personal AI assistant, pip package versions <= 0.1.4.post5, email channel |
| `T2 [==-]` | EchoLeak zero-click indirect prompt injection in Microsoft 365 Copilot | 2025-06-11 | Microsoft 365 Copilot, hosted service used from Outlook and Teams |

### Tool poisoning

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | MCP Python client fetches server-chosen $ref URLs while validating tool results | 2026-09-28 | MCP Python SDK (pip package mcp) 1.10.0 through 1.29.1 and 2.0.0 through 2.1.1, client-side output schema validation |
| `T2 [==-]` | Roo Code remote code execution by writing an MCP configuration into the workspace | 2025-06-27 | Roo Code VS Code extension before 3.20.3 (npm package roo-cline) |

### Agent privilege abuse

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T1 [===]` | Autonomous AI agent intrusion into Hugging Face production infrastructure | 2026-07-16 | Hugging Face production infrastructure, dataset processing pipeline and internal Kubernetes clusters |
| `T2 [==-]` | Cline dashboard cross-origin WebSocket hijacking injecting a malicious MCP server | 2026-06-23 | Cline CLI and agent (npm package cline); advisory lists affected versions up to 3.0.24, fixed in 3.0.30 |
| `T3 [=-]` | Authorization-Execution Gap proposed as the unifying failure mode of open-world LLM agents | 2026-05-10 | Tool-using LLM agents acting under a delegated mandate, with persistent state and multi-agent handoffs |
| `T2 [==-]` | Qdrant /logger endpoint writes attacker-supplied log lines to a caller-chosen path | 2026-02-05 | Qdrant 1.9.3 to before 1.15.6 (cargo crate qdrant), the POST /logger endpoint |
| `T2 [==-]` | MCP Python and TypeScript SDKs shipped with DNS rebinding protection off by default for localhost servers | 2025-12-02 | MCP Python SDK before 1.23.0 and MCP TypeScript SDK before 1.24.0, HTTP servers on localhost |
| `T1 [===]` | Ray dashboard remote code execution from a developer's browser via DNS rebinding | 2025-11-26 | Ray before 2.52.0 (pip package ray), dashboard used as a development tool |

### Data exfiltration

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | MLflow CreateModelVersion authorization bypass reads another user's model artifacts | 2026-08-17 | MLflow before 3.15.0 (pip package mlflow) with the built-in basic-auth plugin |
| `T1 [===]` | MLflow unauthenticated webhook SSRF via unvalidated redirects and DNS rebinding | 2026-08-17 | MLflow 3.3.0 to before 3.15.0 (pip package mlflow) |
| `T2 [==-]` | MCP Python SDK serves HTTP session traffic without checking which principal owns the session | 2026-06-05 | MCP Python SDK (pip package mcp) 1.27.1 and earlier, HTTP transports with bearer-token auth |
| `T2 [==-]` | MCP Python SDK experimental task handlers let any client read and cancel other clients' tasks | 2026-06-05 | MCP Python SDK 1.23.0 through 1.27.1, servers calling experimental.enable_tasks() |
| `T2 [==-]` | Stored prompt injection in Kong Konnect MCP analytics data leads to configuration disclosure | 2026-05-15 | Kong Konnect Model Context Protocol server (mcp-konnect), versions below 1.0.0 |
| `T3 [=-]` | Keyless covert channel argued possible between two LLM agents holding no shared secret | 2026-04-06 | Any deployment where two LLM agents converse and a third party reads their transcript |
| `T2 [==-]` | MCP Ruby SDK lets a second connection replace a live SSE stream and take its tool responses | 2026-03-27 | MCP Ruby SDK (RubyGems gem mcp) 0.9.1 and earlier, streamable HTTP transport |
| `T2 [==-]` | Reusing one MCP TypeScript SDK transport or server across clients routes one client's tool results to another | 2026-02-04 | MCP TypeScript SDK (@modelcontextprotocol/sdk) 1.10.0 through 1.25.3, stateless multi-client servers |
| `T3 [=-]` | Cross-domain query combinability argued to defeat per-request guards in multi-agent LLM deployments | 2025-05-28 | LLM agents from different organizations whose per-agent guards each see only their own request and response |

### Supply chain (package)

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T1 [===]` | LiteLLM malicious PyPI releases published after a compromised CI dependency | 2026-03-24 | litellm v1.82.7 and v1.82.8 on PyPI, via the project's CircleCI release pipeline |

### Supply chain (model)

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | MLflow statsmodels flavor loads pickle artifacts despite the deserialization control | 2026-09-01 | MLflow 2.1.0 to before 3.15.0 (pip package mlflow), the statsmodels model flavor |
| `T2 [==-]` | sentence-transformers executes model-directory Python despite trust_remote_code=False | 2026-07-31 | Hugging Face sentence-transformers before 5.6.0 (pip package sentence-transformers) |
| `T2 [==-]` | Ray Data WebDataset reader executes pickle and torch payloads from a supplied tar archive | 2026-07-24 | Ray before 2.56.0 (pip package ray), the ray.data.read_webdataset reader |
| `T2 [==-]` | Hugging Face Accelerate executes code while parsing checkpoints, and the vendor declined to fix it | 2025-12-23 | Hugging Face Accelerate commit 43526c5c089cc831530f42bbbe66a0cb0b0ea461 (pip package accelerate) |
| `T2 [==-]` | Hugging Face Transformers executes code while parsing model files for several architectures | 2025-12-23 | Hugging Face Transformers Perceiver, Transformer-XL, megatron_gpt2 and GLM4 model files, release 4.57.1 named for GLM4 |

### Training data poisoning

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T3 [=-]` | Chronos framing of agent memory injection that separates the attack from the later failure | 2026-07-20 | Stateful agents with writable, cross-session memory used in enterprise workflows |

### Insecure output handling

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | Arbitrary command execution from project configuration files in Language Servers for AWS | 2026-06-23 | Language Servers for AWS before 1.65.0 and the Amazon Q Developer IDE plugins that bundle it |
| `T2 [==-]` | Prompt injection bypasses the read-only guard in the pgAdmin 4 AI Assistant SQL tool | 2026-06-19 | pgAdmin 4 AI Assistant execute_sql_query tool, versions 9.13 to before 9.16 |
| `T2 [==-]` | agentic-flow MCP server tools interpolate tool arguments into shell commands | 2026-06-18 | agentic-flow npm package (and the ruflo / claude-flow CLI wrappers) 2.0.13 and earlier, MCP server tools |
| `T2 [==-]` | LangChain runtime paths revive objects from deserialized run data with a broad allowlist | 2026-05-08 | langchain-core 1 to 1.3.2 and 0 to 0.3.84 (pip package langchain-core) |
| `T1 [===]` | LiteLLM command execution through MCP stdio test endpoints | 2026-05-08 | BerriAI LiteLLM 1.74.2 to before 1.83.7 (pip package litellm) |
| `T2 [==-]` | Claude Code folder trust dialog bypass through a crafted Git worktree commondir file | 2026-04-24 | Claude Code (npm package @anthropic-ai/claude-code) 2.1.63 through 2.1.83 (fixed in 2.1.84) |
| `T2 [==-]` | Claude Code workspace trust bypass through a repository's own settings file | 2026-03-18 | Claude Code (npm package @anthropic-ai/claude-code) before 2.1.53 (fixed in 2.1.53) |
| `T2 [==-]` | Cursor sandbox escape through agent writes to Git configuration and hooks | 2026-02-13 | Cursor editor versions prior to 2.5 (fixed in 2.5) |
| `T2 [==-]` | Cursor remote code execution through agent writes to a VS Code workspace file | 2025-10-02 | Cursor editor versions 1.6 and below (fixed in 1.7) |
| `T2 [==-]` | GitHub Copilot agent mode remote code execution by turning off its own confirmations | 2025-08-12 | GitHub Copilot agent mode in Visual Studio 2022 17.14.0 to 17.14.11 (fixed in 17.14.12) |
| `T2 [==-]` | Roo Code remote code execution through the VS Code settings the agent may write | 2025-07-07 | Roo Code VS Code extension before 3.22.6 |

### Credential exposure

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T2 [==-]` | MCP Python and TypeScript OAuth clients would send credentials to an authorization server the MCP server named | 2026-09-28 | MCP Python SDK before 1.30.0 / 2.2.0 and MCP TypeScript SDK before 1.31.0 / 2.2.0, OAuth client |
| `T2 [==-]` | Azure DevOps token disclosure through GitHub Copilot Chat workspace settings in VS Code | 2026-09-08 | GitHub Copilot Chat extension for Visual Studio Code before 1.136.2 |
| `T2 [==-]` | terraform-mcp-server stateless HTTP mode reuses one tenant's Terraform token for other tenants' tool calls | 2026-07-28 | HashiCorp terraform-mcp-server 0.3.0 through 1.0.0 per the CVE records, or 0.2.1 per vendor bulletin HCSEC-2026-23, stateless streamable-HTTP mode |
| `T2 [==-]` | terraform-mcp-server executes a user's tool calls with another user's cached Terraform credentials | 2026-07-28 | HashiCorp terraform-mcp-server 0.3.0 through 1.0.0 per the CVE records, or 0.2.1 per vendor bulletin HCSEC-2026-23, stateful streamable-HTTP mode |
| `T1 [===]` | LiteLLM MCP endpoint authentication bypass via OAuth2 passthrough fallback | 2026-07-08 | BerriAI LiteLLM, versions before 1.84.0 (pip package litellm) |
| `T1 [===]` | LiteLLM unauthenticated SQL injection in proxy API key verification | 2026-05-08 | BerriAI LiteLLM 1.81.16 to before 1.83.7 (pip package litellm) |
| `T2 [==-]` | Ollama GGUF loader reads past the file buffer and leaks server memory to the caller | 2026-05-04 | Ollama before 0.17.1, the GGUF model loader behind /api/create |

### Other

| Tier | Title | Date | Target |
| --- | --- | --- | --- |
| `T3 [=-]` | A2A protocol specified without context ownership binding or cross-hop identity propagation | 2026-09-09 | The Agent2Agent (A2A) protocol specification, for deployments that follow it |
| `T3 [=-]` | Linguistic illegibility argued to undermine monitors that read an agent's reasoning text | 2026-09-02 | Agents whose sandbox relies on reading the model's reasoning or output text to detect harmful intent |
| `T3 [=-]` | Position: blockchain execution properties argued to change the threat model for MCP-based agents | 2026-08-18 | Agents that act on public blockchains through MCP servers, skills or direct tool calls |
| `T3 [=-]` | Reframing penetration testing for AI systems as violating operational objectives rather than resources | 2026-07-15 | AI-enabled systems in which a learned model materially determines an operational outcome |
| `T3 [=-]` | Position: treating runtime security threats to LLM applications as an operational condition to monitor | 2026-02-23 | Deployed LLM applications that call MCP services, retrieval backends and memory during task execution |
| `T3 [=-]` | Trust-Authorization Mismatch proposed as the root cause shared by prompt injection and tool poisoning | 2025-12-07 | Agent runtimes that grant permissions statically while an agent's trustworthiness varies per step |
| `T3 [=-]` | Irreversibility, anonymity and automaticity proposed as new harm vectors for agents holding crypto and smart contracts | 2025-07-11 | Autonomous agents given direct access to cryptocurrency balances and to deploying smart contracts |
| `T3 [=-]` | Position: applying classical information security design principles to LLM agents | 2025-05-29 | Agent platforms and protocols that hold credentials, call tools and carry context |
| `T2 [==-]` | vLLM unpickles data received on its multi-node ZeroMQ subscription socket | 2025-05-06 | vLLM 0.5.2 to 0.8.5.post1 (pip package vllm), V0 engine with tensor parallelism across hosts |
<!-- END:GENERATED:catalogue -->

## Entry pages

Every entry has a detail page carrying its full summary, impact, mitigation and
its sources. These pages are generated from `data/entries/*.yml`: edit the entry
file and rebuild rather than editing a page.

<!-- BEGIN:GENERATED:entry-index -->
### `T1 [===]` Tier 1 - Confirmed in the wild

- [MLflow unauthenticated webhook SSRF via unvalidated redirects and DNS rebinding](docs/entries/mlflow-webhook-ssrf-redirect-dns-rebinding.md) - Data exfiltration - 2026-08-17
- [Autonomous AI agent intrusion into Hugging Face production infrastructure](docs/entries/huggingface-autonomous-agent-production-intrusion.md) - Agent privilege abuse - 2026-07-16
- [LiteLLM MCP endpoint authentication bypass via OAuth2 passthrough fallback](docs/entries/litellm-mcp-auth-bypass-oauth2-passthrough.md) - Credential exposure - 2026-07-08
- [LiteLLM command execution through MCP stdio test endpoints](docs/entries/litellm-mcp-stdio-test-endpoint-command-injection.md) - Insecure output handling - 2026-05-08
- [LiteLLM unauthenticated SQL injection in proxy API key verification](docs/entries/litellm-proxy-api-key-sql-injection.md) - Credential exposure - 2026-05-08
- [LiteLLM malicious PyPI releases published after a compromised CI dependency](docs/entries/litellm-pypi-supply-chain-trivy-compromise.md) - Supply chain (package) - 2026-03-24
- [Ray dashboard remote code execution from a developer's browser via DNS rebinding](docs/entries/ray-dashboard-browser-rce-dns-rebinding.md) - Agent privilege abuse - 2025-11-26

### `T2 [==-]` Tier 2 - Demonstrated

- [MCP Python and TypeScript OAuth clients would send credentials to an authorization server the MCP server named](docs/entries/mcp-client-oauth-authorization-server-redirect.md) - Credential exposure - 2026-09-28
- [MCP Python client fetches server-chosen $ref URLs while validating tool results](docs/entries/mcp-client-output-schema-ref-fetch.md) - Tool poisoning - 2026-09-28
- [Azure DevOps token disclosure through GitHub Copilot Chat workspace settings in VS Code](docs/entries/coding-agent-copilot-chat-ado-token-disclosure.md) - Credential exposure - 2026-09-08
- [MLflow statsmodels flavor loads pickle artifacts despite the deserialization control](docs/entries/ai-infra-mlflow-statsmodels-pickle-control-bypass.md) - Supply chain (model) - 2026-09-01
- [MLflow CreateModelVersion authorization bypass reads another user's model artifacts](docs/entries/ai-infra-mlflow-model-version-artifact-read-bypass.md) - Data exfiltration - 2026-08-17
- [Prompt injection bypasses the shell tool consent gate in Strands Agents Tools](docs/entries/agent-app-strands-agents-shell-consent-bypass.md) - Prompt injection (indirect) - 2026-08-03
- [sentence-transformers executes model-directory Python despite trust_remote_code=False](docs/entries/ai-infra-sentence-transformers-trust-remote-code-bypass.md) - Supply chain (model) - 2026-07-31
- [terraform-mcp-server stateless HTTP mode reuses one tenant's Terraform token for other tenants' tool calls](docs/entries/mcp-terraform-server-cross-tenant-token-reuse.md) - Credential exposure - 2026-07-28
- [terraform-mcp-server executes a user's tool calls with another user's cached Terraform credentials](docs/entries/mcp-terraform-server-session-credential-inheritance.md) - Credential exposure - 2026-07-28
- [Ray Data WebDataset reader executes pickle and torch payloads from a supplied tar archive](docs/entries/ai-infra-ray-webdataset-pickle-code-execution.md) - Supply chain (model) - 2026-07-24
- [Indirect prompt injection exfiltrates data through Markdown images in the Codex desktop app](docs/entries/agent-app-codex-desktop-markdown-image-exfil.md) - Prompt injection (indirect) - 2026-07-06
- [Claude Code reverse shell from a clean repository whose setup script fetches a command from DNS](docs/entries/coding-agent-claude-code-repo-dns-setup-payload.md) - Prompt injection (indirect) - 2026-06-25
- [Arbitrary command execution from project configuration files in Language Servers for AWS](docs/entries/coding-agent-aws-language-server-workspace-rce.md) - Insecure output handling - 2026-06-23
- [Cline dashboard cross-origin WebSocket hijacking injecting a malicious MCP server](docs/entries/coding-agent-cline-dashboard-csws-mcp-rce.md) - Agent privilege abuse - 2026-06-23
- [Prompt injection bypasses the read-only guard in the pgAdmin 4 AI Assistant SQL tool](docs/entries/agent-app-pgadmin-ai-assistant-sql-readonly-bypass.md) - Insecure output handling - 2026-06-19
- [Indirect prompt injection through workspace file and directory names in Eclipse Theia AI chat](docs/entries/agent-app-theia-workspace-names-prompt-injection.md) - Prompt injection (indirect) - 2026-06-18
- [agentic-flow MCP server tools interpolate tool arguments into shell commands](docs/entries/mcp-agentic-flow-mcp-tool-command-injection.md) - Insecure output handling - 2026-06-18
- [MCP Python SDK serves HTTP session traffic without checking which principal owns the session](docs/entries/mcp-python-sdk-session-hijack.md) - Data exfiltration - 2026-06-05
- [MCP Python SDK experimental task handlers let any client read and cancel other clients' tasks](docs/entries/mcp-python-sdk-task-handlers-cross-session.md) - Data exfiltration - 2026-06-05
- [Stored prompt injection in Kong Konnect MCP analytics data leads to configuration disclosure](docs/entries/agent-app-kong-konnect-mcp-stored-injection.md) - Data exfiltration - 2026-05-15
- [LangChain runtime paths revive objects from deserialized run data with a broad allowlist](docs/entries/ai-infra-langchain-run-data-deserialization.md) - Insecure output handling - 2026-05-08
- [Ollama GGUF loader reads past the file buffer and leaks server memory to the caller](docs/entries/ai-infra-ollama-gguf-loader-memory-leak.md) - Credential exposure - 2026-05-04
- [Claude Code folder trust dialog bypass through a crafted Git worktree commondir file](docs/entries/coding-agent-claude-code-worktree-trust-bypass.md) - Insecure output handling - 2026-04-24
- [Boolean prompt injection in the 1millionbot Millie chatbot evades chat restrictions](docs/entries/agent-app-millie-chatbot-boolean-prompt-injection.md) - Prompt injection (direct) - 2026-03-31
- [Zero-click indirect prompt injection through the nanobot email channel](docs/entries/agent-app-nanobot-email-channel-indirect-injection.md) - Prompt injection (indirect) - 2026-03-27
- [MCP Ruby SDK lets a second connection replace a live SSE stream and take its tool responses](docs/entries/mcp-ruby-sdk-sse-stream-hijack.md) - Data exfiltration - 2026-03-27
- [Claude Code workspace trust bypass through a repository's own settings file](docs/entries/coding-agent-claude-code-repo-settings-trust-bypass.md) - Insecure output handling - 2026-03-18
- [Cursor sandbox escape through agent writes to Git configuration and hooks](docs/entries/coding-agent-cursor-git-hooks-sandbox-escape.md) - Insecure output handling - 2026-02-13
- [Qdrant /logger endpoint writes attacker-supplied log lines to a caller-chosen path](docs/entries/ai-infra-qdrant-logger-file-append.md) - Agent privilege abuse - 2026-02-05
- [Reusing one MCP TypeScript SDK transport or server across clients routes one client's tool results to another](docs/entries/mcp-typescript-sdk-shared-instance-response-leak.md) - Data exfiltration - 2026-02-04
- [Hugging Face Accelerate executes code while parsing checkpoints, and the vendor declined to fix it](docs/entries/ai-infra-hf-accelerate-checkpoint-deserialization.md) - Supply chain (model) - 2025-12-23
- [Hugging Face Transformers executes code while parsing model files for several architectures](docs/entries/ai-infra-hf-transformers-model-file-deserialization.md) - Supply chain (model) - 2025-12-23
- [MCP Python and TypeScript SDKs shipped with DNS rebinding protection off by default for localhost servers](docs/entries/mcp-python-sdk-dns-rebinding-localhost-servers.md) - Agent privilege abuse - 2025-12-02
- [Cursor remote code execution through agent writes to a VS Code workspace file](docs/entries/coding-agent-cursor-workspace-settings-rce.md) - Insecure output handling - 2025-10-02
- [GitHub Copilot agent mode remote code execution by turning off its own confirmations](docs/entries/coding-agent-copilot-settings-json-yolo-rce.md) - Insecure output handling - 2025-08-12
- [Roo Code remote code execution through the VS Code settings the agent may write](docs/entries/coding-agent-roo-code-settings-json-command-execution.md) - Insecure output handling - 2025-07-07
- [Roo Code remote code execution by writing an MCP configuration into the workspace](docs/entries/coding-agent-roo-code-mcp-config-command-execution.md) - Tool poisoning - 2025-06-27
- [EchoLeak zero-click indirect prompt injection in Microsoft 365 Copilot](docs/entries/agent-app-m365-copilot-echoleak-zero-click-injection.md) - Prompt injection (indirect) - 2025-06-11
- [vLLM unpickles data received on its multi-node ZeroMQ subscription socket](docs/entries/ai-infra-vllm-zeromq-pickle-multinode.md) - Other - 2025-05-06
- [Prompt injection in the AiDex LLM chatbot executes operating system commands](docs/entries/agent-app-aidex-chatbot-prompt-injection-command-execution.md) - Prompt injection (direct) - 2025-04-15
- [Direct prompt injection in the EmailGPT service leaks system prompts and runs unwanted prompts](docs/entries/agent-app-emailgpt-direct-prompt-injection.md) - Prompt injection (direct) - 2024-06-05

### `T3 [=-]` Tier 3 - Theoretical

- [A2A protocol specified without context ownership binding or cross-hop identity propagation](docs/entries/theoretical-a2a-context-ownership-absence.md) - Other - 2026-09-09
- [Linguistic illegibility argued to undermine monitors that read an agent's reasoning text](docs/entries/theoretical-llm-sandbox-escape-anomaly-monitor-gap.md) - Other - 2026-09-02
- [Position: blockchain execution properties argued to change the threat model for MCP-based agents](docs/entries/theoretical-web3-agent-mcp-attack-surface.md) - Other - 2026-08-18
- [Chronos framing of agent memory injection that separates the attack from the later failure](docs/entries/theoretical-agent-memory-persistence-decoupling.md) - Training data poisoning - 2026-07-20
- [Reframing penetration testing for AI systems as violating operational objectives rather than resources](docs/entries/theoretical-ai-pentest-objective-violation.md) - Other - 2026-07-15
- [Impossibility of perfect prompt-injection prevention in shared-embedding sequence models](docs/entries/theoretical-prompt-injection-separation-impossibility.md) - Prompt injection (indirect) - 2026-06-25
- [Authorization-Execution Gap proposed as the unifying failure mode of open-world LLM agents](docs/entries/theoretical-authorization-execution-gap.md) - Agent privilege abuse - 2026-05-10
- [Keyless covert channel argued possible between two LLM agents holding no shared secret](docs/entries/theoretical-covert-agent-conversation-keyless.md) - Data exfiltration - 2026-04-06
- [Position: what system-level defense can and cannot claim against indirect prompt injection](docs/entries/theoretical-indirect-injection-defense-position.md) - Prompt injection (indirect) - 2026-03-31
- [Position: treating runtime security threats to LLM applications as an operational condition to monitor](docs/entries/theoretical-runtime-monitoring-threat-taxonomy.md) - Other - 2026-02-23
- [Trust-Authorization Mismatch proposed as the root cause shared by prompt injection and tool poisoning](docs/entries/theoretical-trust-authorization-mismatch-agent.md) - Other - 2025-12-07
- [Irreversibility, anonymity and automaticity proposed as new harm vectors for agents holding crypto and smart contracts](docs/entries/theoretical-crypto-agent-irreversibility.md) - Other - 2025-07-11
- [Position: applying classical information security design principles to LLM agents](docs/entries/theoretical-security-principles-agent-sandbox.md) - Other - 2025-05-29
- [Cross-domain query combinability argued to defeat per-request guards in multi-agent LLM deployments](docs/entries/theoretical-cross-domain-query-combinability.md) - Data exfiltration - 2025-05-28
<!-- END:GENERATED:entry-index -->

## How to read this list

<!-- BEGIN:GENERATED:footer -->
Every entry is graded on the evidence behind it, not on how alarming it sounds.

- [docs/TIERS.md](docs/TIERS.md) - what each tier means and how to disagree with one.
- [docs/METHODOLOGY.md](docs/METHODOLOGY.md) - how a finding is verified before it is filed.
- [docs/TAXONOMY.md](docs/TAXONOMY.md) - the attack classes and the tie-break rule between them.
- [dist/entries.json](dist/entries.json) - the same data, machine readable.
<!-- END:GENERATED:footer -->