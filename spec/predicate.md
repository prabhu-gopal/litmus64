# Predicate registration

> **Status: draft.** Tier 0 (T0) — ships first and alone. Normative per RFC 2119.
> Prose is CC-BY-4.0; the schema is Apache-2.0.

## Predicate type

```
https://litmus64.com/receipt/v0.1
```

**`v0.1`, not `v1`.** §6.7 requires two independent implementations before any schema feature is
declared stable, and a `predicateType` is immutable in signed history — a receipt signed today must
still verify in a decade. `v1` is earned by the conformance suite passing against a second,
independent implementation. It is not claimed on day one.

`lx verify` MUST accept every version it has ever published, permanently. A receipt never becomes
unverifiable because the schema moved forward.

**The URI MUST resolve.** A `predicateType` that 404s inside a signed attestation is precisely the
unverifiable claim this project exists to oppose. The domain backing it is a maintainer commitment
recorded in `GOVERNANCE.md`, on the same footing as never extending an FSL conversion date. No signed
receipt ships before the URI resolves. (ADR-0018.)

## Envelope

DSSE, Sigstore keyless (OIDC), verifiable **offline**. The verdict object is shaped after the SLSA
Verification Summary Attestation so a consumer that already understands VSA can read our conclusion
without understanding our obligation model.

## Relationship to `test-result/v0.1`

**Subsumption, not competition.** in-toto's registered predicates cover provenance, SBOMs, SCAI,
links, and verification summaries; the nearest neighbour is
`https://in-toto.io/attestation/test-result/v0.1`, whose entire result vocabulary is
`PASSED | WARNED | FAILED` plus a configuration blob. There is no registered predicate for change
correctness, and none anywhere with an obligation model or a declared-unverified set.

A Litmus64 evidence item of kind `existing_suite` MAY embed a `test-result` predicate verbatim, so a
consumer that only understands `test-result` still gets something it can read. State this explicitly
in the ITE-9 registration PR — the in-toto maintainers will ask.

## Registration checklist

- [ ] Schema generated from `lx-receipt` types; `xtask schema-check` green
- [ ] Conformance suite passing, including `law6-skips/` and `forward-compat/`
- [ ] URI resolves to this document
- [ ] Second independent implementation passes conformance *(gates `v1`, not registration)*
- [ ] ITE-9 formatted PR opened against `in-toto/attestation`

TODO: the field-by-field normative definition.
