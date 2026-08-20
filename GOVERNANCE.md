# Governance

## Stage 1 — BDFL with written promises

Decisions rest with the maintainer. These promises are public and binding, and exist because a
project whose pitch is neutrality has to bind itself before anyone will believe it:

1. **The spec tier never becomes less permissive.** Apache-2.0 / CC-BY-4.0, permanently.
2. **FSL conversion dates are never extended.** Each version converts to Apache-2.0 on its second
   anniversary. No exceptions, no renegotiation.
3. **No CLA is ever added.** DCO only. A CLA would reserve the right to relicense, and reserving that
   right contradicts the neutrality claim. Node.js moved CLA → DCO for exactly this reason.
4. **Verification is never paywalled and never crippled.**
5. **No telemetry without opt-in**, aggregate-only, with the payload published and inspectable via
   `lx telemetry show`.
6. **Spec changes require an RFC** with a time-boxed comment period; decisions recorded in
   `rfcs/accepted/` **including rejected alternatives**.
7. **Benchmark and calibration results are published even when unflattering.** Especially then.
8. **The predicate URI domain is held, renewed, and never repointed.** `litmus64.com` backs the
   `predicateType` embedded in every signed receipt, and a receipt signed today must still resolve in
   a decade. This is the only promise on this list whose breach would silently invalidate artifacts
   other people rely on, so it is recorded here rather than treated as an expense line. (ADR-0018.)

## Stage 2 — maintainer ladder, with numeric criteria

Vague criteria are how projects quietly stay one-person forever, so the thresholds are published:

| Role | Criteria | Rights |
|---|---|---|
| Contributor | one merged PR | — |
| Reviewer | 5 merged non-trivial PRs in an area + nomination | triage, approve in that area |
| Maintainer | 10 merged non-trivial PRs + 3 months + nomination + lazy consensus | merge rights, area ownership |
| Steering | maintainer + 12 months + majority vote of maintainers | roadmap, RFC arbitration |

Two maintainer approvals are required for `spec/`, `lx-verdict/`, `lx-sandbox/`, `lx-llm/`, and
`lx-exec/` — the last because it owns the `ConfirmedEvidence` constructor, which is where the
differential-attribution guarantee could be silently deleted.

## Stage 3 — donate the specification, keep the engine

MCP's arc (vendor-internal → open spec → foundation in about a year) is the template, and neutrality
is *why* competing giants adopted it. Because the engine is FSL and foundations require OSI licenses,
**only Tier 1 is donatable — which is exactly the tier where neutrality matters.**

**OpenSSF is the right home** rather than plain LF: in-toto, SLSA, Sigstore, and the AI/ML security
work already live there, so the receipt predicate sits beside its natural neighbours. Sandbox is the
entry stage; **Incubating requires ≥ 3 maintainers across ≥ 2 organizational affiliations**, which
makes recruiting a second-org maintainer a **governance milestone rather than a nice-to-have.**

## Decision records

- **ADRs** in `docs/adr/` for architecture. Public reasoning attracts contributors who reason.
- **RFCs** for anything touching the schema, verdict algebra, risk model, or ledger semantics.
- [`DECISIONS.md`](DECISIONS.md) is the readable summary of the structural decisions and what they
  rejected.

## Never

Paywall verification · telemetry by default · extend a conversion date · restrict the spec tier ·
add a CLA · score individual developers.
