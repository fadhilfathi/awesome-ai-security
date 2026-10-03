# Evidence tiers

The tier answers one question: how well is this attack established by evidence? It
does not answer how bad it is. A hypothetical attack with catastrophic potential is
still Tier 3. A confirmed, minor misconfiguration incident is still Tier 1.

## The three tiers

- **Tier 1 - Confirmed in the wild.** A public postmortem, a CVE or advisory, or a
  vendor disclosure confirms real exploitation or real affected users.
- **Tier 2 - Demonstrated.** A reproducible proof of concept exists, or credible
  research shows the attack works against a named real product or version.
- **Tier 3 - Theoretical.** The attack is described in a paper or a talk, with no
  demonstrated exploit against a real system.

## Minimum evidence per tier

| Tier | Name | Minimum evidence required |
| --- | --- | --- |
| 1 | Confirmed in the wild | A primary source (vendor postmortem, advisory, or CVE record) that states real exploitation occurred or that real users were affected. |
| 2 | Demonstrated | A primary source containing a working proof of concept, or a documented result against a named product or version, with no evidence of real-world exploitation. |
| 3 | Theoretical | A primary source describing the attack, with no implementation run against a real system. |

Tier 1 and Tier 2 entries require at least one source of kind `primary`, as enforced
by `data/schema.json`. Tier 3 entries require at least one source, which may be a
paper or a talk recording.

## The conservative rule

When a candidate sits between two tiers and the evidence does not clearly settle
it, assign the **lower number**. Never raise a tier to make an entry feel more
important.

## The cardinal sin

Inflating a demonstration into "in the wild" destroys reader trust in the entire
list. It is the single most damaging mistake this project can make, because a
reader who catches one false Tier 1 has no reason to trust any other tier either,
including the ones that were correct. A list with a small, honest Tier 1 is useful.
A list with a padded Tier 1 is worse than no list.

The same logic cuts the other way, more subtly: an entry must not be dropped or
quietly downgraded because the evidence was inconvenient. Verify the evidence as it
stands, record it, and move on.

## Worked borderline examples

Each example states the scenario, the call, and the evidence in the source that
drove the call.

### 1. Vendor blog describing a lab demo against the vendor's own product

**Scenario:** A vendor publishes a post describing researchers who reproduced an
attack against the vendor's own product in the vendor's lab, with no affected
customers reported.

**Call: Tier 2.** The evidence shows the attack works against a named real
product, which is the Tier 2 test. No source states that any user outside the lab
was affected, so the Tier 1 condition is not met. The vendor's authorship of the
post does not change the tier: it is the underlying evidence, not the publisher,
that sets it.

### 2. CVE with no evidence of exploitation

**Scenario:** A CVE record describes a flaw in an AI library and names versions, but
the record and the linked advisory do not say that anyone exploited it.

**Call: Tier 2.** An advisory or CVE is the accepted Tier 2 anchor when the flaw is
real and reachable in a named version. Tier 1 additionally requires a statement
about real exploitation or real affected users, and that statement is exactly what
is missing. Absence of a claim of exploitation is not a claim of exploitation.

### 3. Researcher demo on a self-hosted model

**Scenario:** A researcher runs a jailbreak against a model they host themselves, on
weights they downloaded, and writes it up.

**Call: Tier 2.** The Tier 2 test is a reproducible result against a named real
product or version, and a specific released set of weights qualifies. The entry's
`target` must name the model and version, not "LLMs in general", and `impact` must
say that the researcher controlled the deployment. The fact that no vendor ships
this exact configuration does not lower the tier, because the weights are a real
released artefact. Only if the write-up described no run at all would this fall to
Tier 3.

### 4. Real incident disclosed only by the victim, with no technical root cause

**Scenario:** A company states in a public post that its AI-enabled support system
was abused and that customer data was exposed, without publishing a root cause, a
patch analysis or a technical timeline.

**Call: Tier 1 for the incident.** The victim is the primary source and states real
affected users, which satisfies the Tier 1 test on its own terms.

**What this permits:** stating that the incident occurred, who was affected as the
source states, the class, and the date. `impact` must state that the source
confirms real-world exploitation or affected users and cite that source, and must
say plainly that no root cause was published.

**What this forbids:** naming a mechanism, a payload, a vulnerable component or a
fix that the source does not state. `mitigation` may only carry what the source
itself recommends, and `None known` is the correct value when it recommends
nothing. An entry must not infer a mechanism from the shape of the incident, and
an entry in this state is a legitimate candidate for `docs/REJECTED.md` if the
follow-up never arrives.

### 5. Paper with a proof of concept against a specific released version

**Scenario:** An academic paper publishes working exploit code, evaluates it against
a named released version of a product, and reports quantitative results. No one has
been attacked.

**Call: Tier 2.** A working proof of concept against a named released version is
the Tier 2 test, and reporting results in a paper is stronger evidence than a
claim without code. The absence of exploitation is not a gap in the evidence; it is
the definition of Tier 2.

### 6. Purely hypothetical attack with no implementation

**Scenario:** A paper or a talk proposes an attack, gives the mechanism and a cost
estimate, and reports no run against any real system.

**Call: Tier 3.** The Tier 3 test is a description with no demonstrated exploit
against a real system, and that is what the source provides. Stated impact does not
promote a tier. If a later release demonstrates the same mechanism, the entry is
revised and re-tiered with the new evidence cited.

### 7. A vendor hardening advisory with no known attack

**Scenario:** A vendor releases guidance for hardening a configuration it considers
risky, describing what an attacker could do, with no exploit, no affected customer
and no proof of concept.

**Call: Tier 3.** The source describes rather than demonstrates. The reasoning
could be sound and the configuration may genuinely be unsafe, but the evidence
presented does not reach the Tier 2 test. This is the case where the conservative
rule does the most work, because the source is authoritative and the pull is to
treat authority as evidence.

## Tier and attack class are independent

Tier describes evidence. `attack_class` (see `docs/TAXONOMY.md`) describes
mechanism. No combination is disallowed, and the two must not be used as proxies for
each other. In particular:

- A Tier 3 entry can name a class that also appears in Tier 1: same mechanism,
  different evidence.
- A Tier 1 entry can be a mundane class. A confirmed credential leak is not
  intellectually exciting and is still in scope.
