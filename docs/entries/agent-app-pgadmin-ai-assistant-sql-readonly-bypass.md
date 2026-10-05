# Prompt injection bypasses the read-only guard in the pgAdmin 4 AI Assistant SQL tool

`T2 [==-]` **Tier 2 - Demonstrated**

| Field | Value |
| --- | --- |
| Id | `agent-app-pgadmin-ai-assistant-sql-readonly-bypass` |
| Tier | `T2 [==-]` **Tier 2 - Demonstrated** |
| Attack class | Insecure output handling |
| Target | pgAdmin 4 AI Assistant execute_sql_query tool, versions 9.13 to before 9.16 |
| Disclosure date | 2026-06-19 |
| Last verified | 2026-10-05 |
| CVE | CVE-2026-12045 |

## Summary

The PostgreSQL CNA's record for pgAdmin 4 states that the AI Assistant's execute_sql_query tool wrapped model-generated SQL in a read-only transaction but forwarded the statement to the driver unrestricted, so a payload led by COMMIT, END, ROLLBACK or ABORT closed that wrapper and ran the rest in autocommit mode. The record names prompt injection through database content the assistant reads as the delivery route and assigns CVE-2026-12045; the fix shipped in pgAdmin 4 9.16.

## Impact

Anyone who can write into an object the AI Assistant inspects can obtain unauthorised data modification with the pgAdmin user's privileges, and when that role is a superuser or holds pg_execute_server_program the chain extends to code execution on the database host via COPY TO PROGRAM. PROMPT_INJECTION_INDIRECT was considered and rejected: the delivery is retrieved content, but the taxonomy classifies by the step that yielded capability, and here the tool behaved as designed while the application consumed its output without validation.

## Mitigation

Upgrade to 9.16 or later, where the fix rejects any query that parses to more than one statement and requires the leading real token to be one of SELECT, WITH, EXPLAIN, SHOW, VALUES or TABLE, with the read-only transaction left as the runtime backstop. Do not connect the assistant with a superuser role or pg_execute_server_program, and do not grant the assistant's role more than the reads it needs.

## Sources

- **PRIMARY** - [GitHub Advisory Database entry for CVE-2026-12045, published 2026-06-19](https://github.com/advisories/GHSA-95q2-vx3p-f723)
- **PRIMARY** - [CVE-2026-12045 pgAdmin 4 AI Assistant read-only transaction bypass record](https://cveawg.mitre.org/api/cve/CVE-2026-12045)
- **PRIMARY** - [fix(llm): reject multi-statement and non-read-only AI assistant queries](https://github.com/pgadmin-org/pgadmin4/commit/bf4792444446f0e7ab721d23cbd6bfe6afaa7a8b)

Generated from `data/entries/agent-app-pgadmin-ai-assistant-sql-readonly-bypass.yml` by `scripts/build.py`. Never hand-edit this page: change the entry file and rebuild.

Back to the [catalogue](../../README.md#full-catalogue), to [what the tiers mean](../TIERS.md), or to the [entry file](../../data/entries/agent-app-pgadmin-ai-assistant-sql-readonly-bypass.yml).
