# Security Policy

## Reporting a vulnerability

Report vulnerabilities through **GitHub Security Advisories only**.

1. Open the repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Fill in the report form.

No email address is published for this project, and none should be used. If you
receive an email claiming to be from the maintainer about a vulnerability in
this repository, treat it as a phishing attempt and report it through the same
Security tab.

## Scope

**In scope:**

- A vulnerability in the scripts under `scripts/` or in the CI workflows under
  `.github/workflows/`: code execution during a build, unsafe deserialisation,
  command injection, credential exposure, or a workflow that runs untrusted
  input with write permissions.
- A data-integrity problem in the catalogue: an entry that states something its
  source does not, a fabricated identifier or date, a mis-tiered entry, an
  unreachable or substituted source, or a generated figure that does not match
  the entry data.

**Out of scope:**

- **Attacking AI systems in the wild is the subject of this repository, not a
  vulnerability in it.** Exploits, advisories, and postmortems about AI products
  are content. If you have found a new attack technique, the contribution path
  in `CONTRIBUTING.md` is where it belongs.
- Security questions about products listed in the catalogue. Those go to the
  vendors, through their own disclosure channels.
- Missing or inaccurate `last_verified` dates with no evidence of a wrong
  finding. Those are maintenance issues; open an issue or a pull request.
- Style, wording, and formatting.

If you are unsure whether something is in scope, submit it through the Security
tab anyway and say what you found. It will be classified, not discarded.

## What to include

- The affected file path, or the entry `id` for a data-integrity report.
- Steps to reproduce, for code and workflow issues. For a data-integrity issue,
  the URL of the source that contradicts the entry, and the passage in the
  entry that it contradicts.
- The impact, stated concretely: what an attacker gains, or what a reader of
  the catalogue would be misled into believing.

Screenshots and log output help. Proof-of-concept code is welcome for code
issues.

## Response

- The report will be acknowledged within a few business days. Beyond that there
  is no service-level promise, and none is implied.
- Confirmed issues are fixed, and the fix is referenced in the report so the
  reporter can verify it.
- Credit is offered in the fix or release notes if you want it, and omitted if
  you would rather not be named.

The maintainer is a single person. Responses can take time, and triage competes
with curation work. That is a fact about resourcing rather than a statement
about how seriously reports are taken.
