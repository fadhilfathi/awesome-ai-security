# Methodology

This is the procedure an entry follows from candidate to published. It is written
to be enforceable, not aspirational: every step names an observable thing the
curator did.

## Per-entry procedure

1. **Fetch the primary source and read it.** Never rely on a search snippet, a
   headline, an aggregator summary, or recollection of a source read earlier in
   the session. If the primary source cannot be fetched and read in full, the entry
   does not proceed (see Exclusion handling).
2. **Confirm the facts against the source text.** Date, affected product, and
   claimed impact are each checked against the wording of the source itself. The
   entry's `date` is the disclosure date as the source states it, never inferred,
   never rounded to a tidier value.
3. **Decide the class** using the inclusion test and tie-break rule for each
   candidate class in `docs/TAXONOMY.md`. Exactly one class is filed. If two fit,
   the entry names the tie-break rule that decided the call.
4. **Decide the tier conservatively** using the evidence table in `docs/TIERS.md`.
   When uncertain between two tiers, take the lower number.
5. **Write the fields in original words.** `summary`, `impact` and `mitigation` are
   written by the curator, not copied and not paraphrased closely enough to
   function as a substitute copy. `impact` for a Tier 1 entry states that the
   source confirms real exploitation or affected users, and cites which source says
   so.
6. **Record `last_verified`** as the date the fetch happened, not the entry's
   disclosure date. `last_verified` is a statement about the curator's own work.
7. **Log exclusions.** Any candidate that fails at any step is recorded in
   `docs/REJECTED.md` with the reason and the source that was checked.

## Rule out fabrication

No incident, CVE number, date, product name, version number or quantity is written
from memory. Every one of those values is transcribed from a source that was
fetched and read in the current session.

Fabrication is the failure mode most likely to occur silently, because a
plausible-looking entry with a plausible-looking advisory URL produces no error and
fails no schema check. A single fabricated incident destroys the value of the
list: it converts a catalogue of evidence into a rumour mill, and it does so in a
way that a reader cannot detect without doing the curator's work themselves. There
is no partial credit for being right about everything else.

If a detail cannot be obtained from a fetched source, the detail is omitted, not
estimated. Omit the `cve` key entirely rather than guessing an identifier; write
`None known` in `mitigation` rather than inventing a remedy.

## Primary sources first

A **primary** source is the advisory, the vendor postmortem, the original research
that states the finding, or the CVE record. A **secondary** source is news
coverage, commentary or an aggregator.

Secondary sources may be linked alongside a primary source, never instead of one.
A secondary source is useful to a reader who wants the human context of an
incident; it is not acceptable support for a fact in the entry.

## Copyright posture

Every description is written in the curator's own words. At most one short quoted
phrase is used per source, and only where the exact wording is load-bearing (for
example, a specific product's own name for a behaviour, or a quoted claim that
cannot be paraphrased without losing precision). Everything else is paraphrased in
original language and linked rather than reproduced. Source paragraphs are never
copied into entry fields.

## No marketing

Vendor product pages are not sources of attack information. A vendor research blog
is acceptable only when it contains the actual technical finding, that is, when it
states the mechanism, the affected version and the reproduction. A vendor post
that is a product announcement, a feature highlight or a roundup of public
research is not a source for an entry that repeats the roundup's claims.

No affiliate links, no sponsored placements, no entries added because a vendor is
a supporter. Where a vendor is both the affected party and the publisher of the
technical finding, that is disclosed in the entry rather than treated as an
independent confirmation.

## Exclusion handling

An unreachable, paywalled or ambiguous source means the entry is not included. The
candidate is logged in `docs/REJECTED.md` with the reason, the source that was
checked, and the date checked. Gaps are never filled from recollection.

**A smaller true list beats a larger doubtful one.** This is the governing
principle of the project and it applies at every level: fewer entries with solid
evidence is the correct outcome when the alternative is more entries with shaky
sourcing. It is also the reason rejections are published rather than hidden.

## Spot-check rule

After each batch of 10 entries, three entries are re-fetched at random and
re-verified against the source text, and the result is reported (in the PR
description or the batch notes). Any failure of a spot-check means the whole batch
is re-verified, not just the three entries that were checked. A spot-check that
cannot be run because a source has since gone offline is reported as
unverifiable rather than counted as a pass.

## Anti-balance rule

Tier criteria are never tuned to make counts look even, and no target in
`docs/ROADMAP.md` is a licence to fill a tier with weaker entries. If Tier 1 is
small, the README says Tier 1 is small. An honest count is a finding about the
field, and publishing it is more useful than a balanced-looking table.

## What the automations enforce, and what they do not

Three automated checks back this procedure. Each has a blind spot, and knowing the
blind spot is part of following the procedure.

- **The validator** (`scripts/validate.py`) checks structure and internal
  consistency: schema conformance, unique ids, kebab-case id and date formats,
  https-only source URLs, the presence of a primary source for Tier 1 and Tier 2
  entries, and agreement between entries and the generated output.
- **The README/dist drift check** (CI, via `scripts/build.py`) fails if the
  committed `README.md` generated blocks or `dist/entries.json` differ from freshly
  generated output. It guarantees the published artefacts match the entry files.
- **The weekly link checker** (`scripts/check_links.py`) reports unreachable sources.

What none of these can do: the validator checks structure and internal
consistency, not the truth of a claim. A fabricated CVE number, a misread impact,
an inflated tier and an invented incident all pass every automated check in this
repository. Only a human or an agent that actually fetched the source can check
those, which is why steps 1 to 5 of the per-entry procedure are not delegable to
CI and why the spot-check exists.
