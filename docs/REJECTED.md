# Rejected candidates

This file is part of the published dataset on purpose. Rejections are a quality
signal, not a private scratch file: a reader who sees which candidates were checked
and set aside can judge the selection process, and the count of rejections is
evidence about how much unverified material circulates in this field.

Each row records a candidate that was investigated and not published, the reason,
the source that was checked, and the date of that check. Reasons follow
`docs/METHODOLOGY.md`: the primary source could not be fetched and read, the source
did not state what the candidate claimed, the evidence did not reach the tier the
candidate would need, the entry could not name a real product or version, or the
candidate was an aggregator summary with no primary source behind it.

Rejections are not deleted later. If a rejected candidate is later verified
properly, it becomes an entry and the rejection row is removed with a note in the
entry history.

Rows marked `EXAMPLE` are placeholders showing the expected format. They are not
real incidents. Every other row is a real candidate that was investigated and
set aside, which is the point of publishing this file.

| Candidate | Reason rejected | Source checked | Date checked |
| --- | --- | --- | --- |
| EXAMPLE - placeholder, not a real incident | EXAMPLE - primary source could not be fetched, so no fact in the candidate could be confirmed | EXAMPLE - advisory URL | YYYY-MM-DD |
| EXAMPLE - placeholder, not a real incident | EXAMPLE - source describes an attack but states no affected product or version, so the entry cannot be filed | EXAMPLE - research write-up URL | YYYY-MM-DD |
| EchoLeak zero-click prompt injection in Microsoft 365 Copilot | Not filed at the tier the claim would need. The CVE record's CISA enrichment states exploitation is "none", so the evidence is a demonstrated attack against a production system, not a confirmed one in the wild. Held back from the Tier 1 catalogue pending evidence of real exploitation. | https://cveawg.mitre.org/api/cve/CVE-2025-32711 | 2026-10-04 |
| Cursor remote code execution via .code-workspace prompt injection | Not filed. A CVE with a credible reproduction but a CISA exploitation status of "none" is Tier 2 material; held back while the Tier 1 set is being assembled from sources that do confirm exploitation. | https://cveawg.mitre.org/api/cve/CVE-2025-61590 | 2026-10-04 |
| MCP Python SDK session hijack via unverified session id | Not filed. The advisory confirms the vulnerability and a fix, but the CISA enrichment records no exploitation, so it does not meet the Tier 1 bar. | https://cveawg.mitre.org/api/cve/CVE-2026-52869 | 2026-10-04 |
| PromptMink npm campaign attributed to a North Korean group | Not filed. The strongest available account is a JavaScript-rendered vendor page whose article text could not be retrieved, so the campaign's package names, dates, and counts could not be confirmed from the research that made them. A secondary note restating the claim is not a substitute for reading the source. Revisit if the research becomes fetchable. | https://www.reversinglabs.com/blog/claude-promptmink-malware-crypto | 2026-10-04 |
| IronWorm malicious jscrambler npm versions | Not filed. Secondary write-ups describe a real compromise, but no vendor or researcher primary source was reachable that states the affected versions and dates, so the entry could not be written without taking those facts on trust. | https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/07/CSA_research_note_jscrambler_npm_supply_chain_infostealer_20260713-csa-styled.pdf | 2026-10-04 |
| Fake @bitwarden/cli package targeting AI coding agents | Not filed. Secondary coverage describes a short-lived malicious package that hunted agent credentials, but no primary source was reachable to confirm the package identity or the window, and a squatting claim is exactly the kind of fact that must not be written from a summary. | https://pulse.adyog.com/insights/bitwarden-cli-supply-chain-targeted-claude-cursor-codex | 2026-10-04 |
| TrapDoor malware targeting AI coding assistants | Not filed. An aggregator index entry was reachable but not the underlying research, so no product, version, or date could be verified against a primary source. | https://oecd.ai/en/incidents/2026-05-25-2739 | 2026-10-04 |
