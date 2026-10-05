# Contributing

## What this project is

`awesome-ai-security` is an evidence-graded catalogue of attacks on AI systems.
Every entry carries a tier that says how well the attack is established: confirmed
in the wild, demonstrated by a researcher, or theoretical. The tier is the
product. A reader should be able to tell a documented incident from a proof of
concept from a plausible mechanism, without reading a single vendor blog.

## The absolute rules

These are not style preferences. An entry that breaks one of them does not ship.

1. **Every entry traces to a primary source you actually fetched and read.** Not
   a source your search results summarised. Fetch it, read it, then write.
2. **Descriptions are in your own words.** Never copy a paragraph from the source
   or from another writeup. Paraphrase, and keep it short.
3. **No affiliate links. No sponsored placements. Ever.** No referral codes, no
   vendor-sponsorship of a position, no "thanks to X for covering this".
4. **No vendor product pages as sources of attack information.** Marketing and
   feature pages are not evidence. A vendor postmortem or security advisory is
   fine; a product landing page is not.
5. **Tier assignment is conservative.** When you are uncertain between two
   tiers, the lower tier wins. Inflating a demonstration into "in the wild" is
   the cardinal sin of this list.
6. **No number in the README is hand-typed.** Counts, tier tallies, and matrices
   are generated from the entry files. If a number appears in the README, a
   script computed it.

## Two-minute contribution path

Open the **Add an incident** issue form (the `Add an incident` template under
Issues -> New issue). Fill in what you know:

- What the attack is, in one or two sentences.
- The system or feature it targets, named precisely (model, product, component,
  version if the source states one).
- The primary source URL: the advisory, postmortem, CVE record, or research
  writeup that states the finding.
- The date the source itself states.
- What the attacker actually gained.

The curator does the rest: fetching and reading the source, writing or editing
the entry file, choosing the tier and attack class, and running the build.

A submission may be re-tiered, split into several entries, merged into an
existing one, or declined. That is normal curation, not a judgement of you. If
the source turns out to support a lower tier than you expected, the entry ships
at the lower tier.

## What makes a submission good

- **A primary source that states the finding.** A security advisory, a vendor
  postmortem, a CVE record, or original research. The finding must be in that
  document, not inferred from its title.
- **A date the source states.** Do not infer a date from a post's relative
  wording ("last week") or from a CVE's assignment window. If the source gives
  no date, say so and leave it for the curator.
- **A precisely named target.** "An LLM chatbot" is not a target.
  "The web search tool in vendor X version Y" is.
- **An impact statement about what was gained.** Data exfiltrated, code
  executed, filter bypassed, cost incurred, user deceived. Not "could lead to
  serious harm".

News coverage alone is not sufficient. Articles are welcome as a secondary
source alongside a primary one, and they often help you find the primary one,
but they never stand in for it.

## Proof-of-concept repositories

A researcher proof-of-concept repository is a **secondary** source. The paper,
advisory, or research blog post that contains the finding is the **primary**
source. Both may be linked; the PoC is added with `kind: secondary`.

If the only artefact you have found is a GitHub repository, keep looking. The
writeup, paper, or advisory behind it is what the entry cites as primary.

## Adding an entry locally

One YAML file per entry, named after the entry id:

```
data/entries/<id>.yml
```

The file must validate against `data/schema.json`. Start from an existing entry
as the shape reference. Required keys: `id`, `title`, `tier`, `attack_class`,
`target`, `date`, `summary`, `impact`, `mitigation`, `sources`,
`last_verified`. `cve` is optional and only for identifiers the source itself
states; omit the key rather than leaving it empty or guessing.

The Makefile targets and the exact commands behind them:

```
make validate    # uv run python scripts/validate.py
make lint        # uv run python -m ruff check .
make test        # uv run python -m pytest
make build       # uv run python scripts/build.py
make gate        # lint, test, validate, and no generated drift
```

`make gate` is what CI enforces. Run it before you open a pull request; if you
have no `make`, run the four commands on the right-hand side in that order.

After `make build`, commit the entry file together with the regenerated
output.

Link checking (`make links`, that is `uv run python scripts/check_links.py`)
reaches out to the network, so CI runs it on a schedule rather than on every
push. Run it yourself when you add or change a source URL.

## Pull requests

`main` is protected. Every change reaches it through a pull request, and three
checks must pass before a change can merge: `validate entries`,
`generated output is current`, and `lint and test`. The branch must also be up
to date with `main`, so merging a second pull request while the first is
waiting means rebasing or merging `main` into your branch first.

There is no required approving review. This repository has one maintainer, and
GitHub does not let an author approve their own pull request, so a
one-approving-review rule would make every change here impossible to merge.
When a second maintainer is added, requiring one review is a settings change,
not a code change.

## Generated files

`dist/entries.json` and every block in `README.md` between
`<!-- BEGIN:GENERATED:... -->` and `<!-- END:GENERATED:... -->` are generated.

- **Never hand-edit them.** Not a count, not a tier table, not a wording fix.
- Run the build command and commit what it produces.
- CI regenerates the output and fails on drift, so a hand-edit is a red build
  with no way to pass.

If a generated section is wrong, the fix belongs in the generator or in the
entry data. Open an issue describing the wrong output if you are not sure
where the bug lives.

## Choosing a tier and a class

- `docs/TIERS.md` defines the three tiers and the evidence each one requires.
- `docs/TAXONOMY.md` defines the attack classes and the enum values accepted by
  `data/schema.json`.

The tier describes the **evidence for the attack**, not the severity of its
impact. A trivially severe impact demonstrated only in a lab is tier 2. A
low-impact bug confirmed against a shipping system is tier 1.

If an entry fits two classes, pick the one that names the mechanism of the
attack itself, not the consequence. For example, an attack that injects
instructions through retrieved documents is classified by how the injection
works, not by what the model did afterwards.

## What gets rejected, and why

Submissions are declined when the source is unreachable, paywalled, or
ambiguous, or when no primary source can be found that states the finding. Dead
links, sources that need a subscription, and a repository with no writeup all
land here.

Rejections are logged in `docs/REJECTED.md` with a short reason. That file is
published on purpose: a catalogue that only shows what passed does not tell you
what to look for next, and a visible rejection log is a quality signal about
how the rest of the list was checked.

## No marketing

This is the rule contributors break most often, so it stands alone.

Do not submit entries because a vendor announced something, because a product
has an interesting name, or because a link earns you something. Do not include
affiliate links, referral URLs, tracking parameters, or sponsored placements in
an entry, in a source URL, or in a pull request description. Do not use a vendor
marketing page as the evidence for an attack. Entries are selected on evidence
alone, and the same standard applies to every vendor equally.

## Attribution

Contributions to this repository are committed under the maintainer's identity.
No co-author trailers are added to commits. This is a repository requirement:
commit history in this project carries the maintainer's identity only.

## No CLA

No Contributor License Agreement is required, and none is offered. No CLA
bot will comment on your pull request.
