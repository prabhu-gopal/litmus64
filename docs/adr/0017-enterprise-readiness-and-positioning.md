# ADR-0017 — Positioning is "the receipt," and enterprise readiness is a T0 concern

**Status:** accepted

## Context

Two related problems, both discovered by trying to explain the product to a non-author.

**1. There was no simple explanation.** The documentation could describe nine mechanisms, an eleven-stage
pipeline, and a verdict algebra, but not answer *"what is this, in one sentence, for someone who
vibe-codes?"* A product that cannot be explained in one sentence does not get adopted regardless of how
good it is, and the sentence has to survive being repeated by someone who does not work here.

**2. Enterprise-readiness was scattered and late.** Sandbox tiering, SLSA provenance, and zero-egress
mode all existed in the plan, but as engineering details rather than as an answerable procurement
position. Meanwhile 2026 procurement has converged on a specific question — *which claim can this vendor
prove, at what point in the lifecycle, with what tamper resistance?* — which is, word for word, what we
do for code changes. Failing to answer it about ourselves would be indefensible.

## Decision

### The positioning: the receipt, and specifically the part that says "I don't know"

Every competitor is built to tell you it worked. **The differentiator is the `unverified` block** — a
*required* schema field, such that a report claiming total coverage is rejected as malformed by our own
validator.

That is the one thing no closed vendor can copy, because it is not a feature, it is a business decision:
publishing what you failed to check requires having no revenue riding on the gaps being invisible.

The public explanation lives in `docs/why.md`, structured as one sentence → the situation → why the
obvious answers fail → what you get → what it is not → the honest catch. Two research findings anchor it:

- **96% of developers don't fully trust AI-generated code; only 48% always review it.** The trust
  paradox in one line — they don't trust it *and* they don't read it. This is the sharpest available
  statement of the gap, better than any review-time metric, because it describes a situation no faster
  reviewer can fix.
- **PRs merged without review +31.3%**, while incidents per merged change more than tripled.

The lead framing is therefore **"the gate is disappearing,"** not "review is slow." *Review is slow*
invites *build a faster reviewer* — the crowded, commoditized category. *Nobody is checking and
incidents tripled* invites *build evidence*, which is us.

Per-audience one-liners are specified in `docs/why.md` so that the message does not drift as other
people repeat it.

**The analogy is a home inspection**, because it carries the differentiator for free: a good inspector's
report says *"could not access the roof — you still don't know about the roof,"* and that line is why
you hired them.

### Enterprise readiness is T0, not T3

Moved forward, because these are cheap while the repo is small and expensive to retrofit, and because
several are gates on being taken seriously at all:

- **OpenSSF Scorecard** published in the README and tracked as a regression. A verification project with
  a mediocre Scorecard is self-refuting.
- **SBOM (CycloneDX + SPDX), signed and attached to every release artifact.** Previously we only
  *consumed* SBOM formats as evidence sources; we now emit them for ourselves.
- **SLSA Build L3 provenance** on every artifact — the current federal-procurement bar.
- **Published vulnerability-response SLA**, not just a disclosure address.
- **`docs/enterprise.md`** as a single procurement-facing page, including a list of questions we cannot
  dodge.

### Regulatory claims: deliberately smaller than the market's

Researching this produced a finding that argues *against* an easy sales angle, and we take the finding:
**the EU AI Act does not generally make AI-assisted coding high-risk.** Annex III covers specific use
cases, not developer assistance. Vendors currently implying "AI Act compliance requires our code tool"
are overclaiming.

So the honest positions, all stated in `docs/enterprise.md`:

- If the software *you ship* is high-risk under Annex III, then from 2 August 2026 you owe traceability
  and demonstrable human oversight over how it was built — and a receipt is strong evidence where "an
  agent wrote it and a human clicked merge" is weak. **We are the evidence layer, not the compliance
  product.**
- The **EU Cyber Resilience Act** is the more directly relevant regime for most teams.
- A receipt is **SOC 2 CC8.1 change-management evidence** — but the open-source project carries no SOC 2
  report, because there is no service to audit. Saying this unprompted is worth more than the claim we
  are declining to make.
- **We will never claim Litmus64 makes anyone compliant with anything.** It produces evidence; an auditor
  decides what it is worth.

## Consequences

**Good.** There is now a canonical explanation that a developer, a lead, and a procurement reviewer can
each read, and one that survives repetition. The supply-chain commitments are the same ones we ask users
to care about, so dogfooding covers them. And declining the AI Act pitch costs a talking point but
protects the only asset that matters — if one compliance claim fails counsel's reading, every other
claim on the page gets re-examined.

**Bad.** T0 grew: Scorecard, dual SBOM, and provenance now block the first release rather than the third.
Accepted, because they are days of CI work now versus a retrofit under procurement pressure later.

## Rejected

- **Leading with the compliance angle.** Bigger near-term pipeline, and it breaks the first time a
  lawyer reads Annex III.
- **Leading with "AI code review, but better."** Puts us in the commoditized category (§3.1) and invites
  comparison on recall against tools optimising for a different thing.
- **A security-scanning headline.** Users say "vulnerabilities" because that is the vocabulary they were
  taught, but that space is crowded and solved. Correctness is ours (ADR-0016).
- **Waiting on Scorecard/SBOM until enterprises ask.** By then it is a blocker in someone's procurement
  cycle rather than a line in a README.
