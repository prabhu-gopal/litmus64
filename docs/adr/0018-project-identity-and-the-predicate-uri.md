# ADR-0018 — Project identity: three surfaces, three homes

**Status:** accepted · **Action item:** register `litmus64.com` before the first signed receipt ships

## Context

The receipt is published as an in-toto predicate, and its `predicateType` is a URI **embedded in
every signed attestation, permanently**. A receipt signed in 2026 is still being verified in 2036, and
a verifier resolves that URI to learn what the receipt means. It cannot change later without
orphaning every receipt already signed.

`SLSA` uses `https://slsa.dev/...`; in-toto uses `https://in-toto.io/attestation/...`. A
domain-shaped predicate URI is the convention, and the convention exists because the URI is an
identity that has to outlive the person who registered it.

## Decision

Three surfaces, three homes, chosen by how long each identifier has to survive.

| Surface | Home | Why |
|---|---|---|
| **Code, issues, releases, spec, docs** | **GitHub** (`github.com/prabhu-gopal/litmus64`) | Where developers already are. Free CI, Pages, and release hosting. Needs no domain |
| **Showcase, landing page, launch essay** | **`prabhugopal.com/litmus64`** | Free, already owned, and a project subpage on a maintainer's site is completely normal in open source. Nobody has declined a tool over a landing-page path |
| **The predicate URI** | **`litmus64.com`** | The one identifier that cannot be a subpath or a personal domain |

### Why the predicate URI needs its own domain

1. **It is a one-way door.** If the project later gets its own domain — or is donated to OpenSSF,
   which is the stated Stage 3 governance goal — a predicate URI rooted anywhere else cannot follow it
   without breaking every signed receipt in existence.
2. **It is where the neutrality claim is either true or false.** The argument for an open format is
   neutrality: *no agent vendor will trust another vendor's verdict, so the format must be neutral and
   unownable.* A predicate URI rooted in one person's personal domain says the opposite in the most
   durable place available — inside every signed artifact. Asking a competing vendor to emit
   `someone-personal-site.com/...` receipts asks them to endorse a person rather than adopt a
   standard. That is a cheap way to lose the only strategic advantage the project has.

### Sequencing, so nothing is blocked

- **Now:** GitHub organization created, repository public, spec drafted, showcase at
  `prabhugopal.com/litmus64`. **None of this needs the domain** — T0 is prose, schema, and a verifier.
- **Before signing lands (the T0→T2 boundary):** `litmus64.com` registered and pointed at GitHub
  Pages, with the predicate definition published at `https://litmus64.com/receipt/v0.1`.
- **Never:** ship a signed receipt whose `predicateType` does not resolve. A dangling predicate URI
  inside a signed attestation is exactly the kind of unverifiable claim this project exists to oppose,
  and it would be ours.

Register `@litmus64` on GitHub as an **organization**, not a personal repo, from the first commit.
Moving a repository later breaks every bookmarked URL, and the org is free.

### The domain is a maintainer commitment, not an expense line

Holding `litmus64.com` for a decade belongs in `GOVERNANCE.md` alongside the promise never to extend
an FSL conversion date and never to add a CLA. Those promises cost nothing and are worth more than a
CLA; this one costs about $15 a year and is worth more than all of them, because it is the only one
whose breach silently invalidates artifacts other people are relying on.

Registering `litmus64.dev` defensively as well is worth the second $15 — but only one becomes the
predicate URI, and that one can never lapse.

## Consequences

**Good.** Nothing is blocked today. The neutrality argument stays intact, the project stays donatable
to OpenSSF, and the predicate URI is stable from the first signed receipt onward.

**Bad.** A hard dependency on holding one domain for a decade, which is a real obligation and is
therefore recorded as a governance commitment rather than left implicit.

## Rejected

- **A personal domain as the predicate URI.** Fine for the website, wrong for the identity — see above.
- **`https://github.com/prabhu-gopal/litmus64/spec/receipt/v0.1`.** Works, and in-toto permits any URI, so
  it is the genuine fallback if a domain ever became impossible. Rejected because it hard-codes a
  platform we do not control into every signed artifact, and it reads as a repository path rather than
  a standard. Not needed: the domain arrives before signing does.
- **Deferring the decision to launch.** Cheap now, expensive after the first signed receipt exists.
  Decided early precisely because it is boring.
