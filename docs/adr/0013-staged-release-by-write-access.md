# ADR-0013 — Releases are staged by write-access, not by maturity

**Status:** accepted · **Replaces:** "there is no MVP; 1.0 is the first public release"

## Context

The original stance kept one thing that must never change — **no release leaks noise into somebody's
pull requests** — and one thing that would have killed the project: applied to the entire engine, it
meant *years* before any public artifact, and therefore years of zero external signal on the one
component that cannot be verified internally, namely **whether the obligations we derive are useful
to a human being**.

Solo-maintainer burnout is the most common actual cause of death for a project this size. A multi-year unpublished build is how that happens. Revision 1 even contained the
antidote and mislabelled it: §18.1 said to validate the falsification loop on 30 real PRs — "*not a
public milestone*."

## Decision

Four tiers, staged by the write-access each requests. Every tier is production-grade at what it
claims, ships publicly, and is honest about the tier above it.

- **T0 · standard** — `spec/`, schema, conformance suite, `lx verify`, predicate registration. Asks
  for no access at all. Ships **first and alone**.
- **T1 · look** — `--read-only`, `lx demo`, `lx init`, `lx capabilities`, renderers. Reads code,
  writes nothing, and **cannot emit `violated`**: it never obtains a `ConfirmedEvidence`.
- **T2 · run** — sandbox, paired runner, discrimination, attribution, `lx-rust` + `lx-python`,
  signing, GitHub App. First tier that can accuse, and only with a BASE control.
- **T3 · attack & compound** — attack ladder, ledger, discharge, calibration, merge gating.

## Consequences

**Good.** The no-noise promise becomes *structural* rather than temporal: the type that authorises an
accusation is unreachable from T1, which is a stronger guarantee than "we waited." The riskiest
unknown gets external feedback first and cheapest. T0 alone starts the moat compounding in weeks
rather than years — and AgentPlane already publishes an MIT-licensed competing schema, so that head
start is contested.

**Bad.** Four launch narratives instead of one. Tier discipline must be enforced in the build graph
(`xtask arch-check`: no T1 crate may depend on a T2+ crate) or T1 silently acquires T2's
requirements and stops being installable without a sandbox.

## Rejected

- **Single all-at-once 1.0.** Maximises time-to-feedback on the riskiest unknown and maximises
  burnout risk, in exchange for a launch-day narrative.
- **A conventional beta.** Emitting low-confidence violations into real pull requests is precisely
  the noise that kills tools in this category. T1 is not a beta; it is a complete product with a
  narrow, honestly-stated scope.
