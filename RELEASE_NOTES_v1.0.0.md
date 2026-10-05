# v1.0.0

The first tagged release of an evidence-graded catalogue of attacks on AI
systems. Every entry states how well the attack is established, so a reader can
tell a documented incident from a researcher's proof of concept from
speculation.

## What is in it

**62 entries**, spanning June 2024 to September 2026:

| Tier | Meaning | Entries |
| --- | --- | ---: |
| 1 | Confirmed in the wild | 7 |
| 2 | Demonstrated against a named product | 41 |
| 3 | Theoretical, described in research | 14 |

Every entry traces to a primary source that was fetched and read: 46 CVE
identifiers, all confirmed published and matched to the product and version
range each entry claims, and 130 distinct primary sources across 15 attack
classes.

Four attack classes have no entries yet: `CODE_ASSISTANT_ABUSE`,
`DENIAL_OF_SERVICE`, `JAILBREAK` and `MODEL_THEFT_EXTRACTION`. They are empty
because nothing was found that met the evidence bar, not because the classes
were forgotten. The matrix in the README shows the gaps.

## Tier 1 is small, and that is the finding

Seven entries are confirmed in the wild. That is fewer than the original target
of fifteen, and it is reported rather than padded.

The bar was kept deliberately strict: an entry qualifies only if a vendor
disclosure, a government catalog, or a vendor postmortem states that the attack
actually happened. Cross-checking the live CISA Known Exploited Vulnerabilities
catalog, which holds 1,733 entries, turned up just two genuinely AI-specific
products, both of which are here alongside the LiteLLM cluster.

Padding Tier 1 to fifteen would have meant admitting vulnerabilities with a CISA
exploitation status of `none`. Those are real and worth recording, but they are
demonstrated attacks, not confirmed ones, and they are filed at Tier 2 instead.
The rejection log in `docs/REJECTED.md` records what was set aside and why,
including several candidates dropped because their research could not be read
rather than because the finding was weak.

## What the catalogue shows

Two classes account for most of the demonstrated entries, and together they are
one finding rather than two buckets. `INSECURE_OUTPUT_HANDLING` and
`PROMPT_INJECTION_INDIRECT` dominate because the recurring failure is not a bug
in a model. It is an agent that is allowed to write a file it should have had to
ask about, which turns a single injected instruction into code execution on a
developer's machine.

## Corrections made before release

The catalogue was audited entry by entry against its own sources, adversarially.
That pass found and fixed:

- An entry citing a CVE identifier that does not exist in the public list.
- Two flagship Tier 1 entries filed under classes their sources contradict: a
  command supplied in a request body is not a poisoned tool definition, and an
  SSRF with no agent involved is not an agent privilege problem.
- A version range that disagreed with the advisory it cited.
- A mitigation attributed to a paper that does not make that recommendation.
- Thirteen entries whose disclosure date was anchored to the wrong event.

Every CVE claim was re-verified against the live CVE record, and every
disclosure date against the publication date of a source the entry actually
cites. All five Tier 1 exploitation claims were confirmed as active in the CISA
enrichment carried inside the CVE record.

## Using the data

`dist/entries.json` is the whole catalogue, machine-readable, with a stable
`_permalink` per entry. It is committed and regenerated from the entry files, so
it cannot drift from them.

Content is CC BY 4.0. The scripts are Apache-2.0.

## Contributing

Report an error on an entry, or propose a new one, through the issue forms. An
entry is only accepted once its primary source has been read, and the curator may
re-tier a submission downward if the evidence is thinner than claimed. That is
the intended behaviour, not a rejection of the contributor.