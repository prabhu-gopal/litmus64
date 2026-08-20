# Licensing tiers — this table is NORMATIVE

`cargo xtask license-check` fails CI if a path's SPDX header disagrees with this table. Getting this
wrong once, in public, is a legal mess, so it is a machine check rather than a convention.

## Tier 1 — the standard. Apache-2.0 (code) / CC-BY-4.0 (prose)

A standard competitors cannot implement is not a standard, and **verification must be free to
verify**: if you need our permission to check a receipt, the receipt is worthless.

| Path | License |
|---|---|
| `spec/**` (prose) | CC-BY-4.0 + royalty-free implementation grant |
| `spec/**` (schemas, conformance fixtures) | Apache-2.0 |
| `crates/lx-types/**` | Apache-2.0 |
| `crates/lx-receipt/**` | Apache-2.0 |
| `crates/lx-verdict/**` | Apache-2.0 |
| `crates/lx-sign/**` | Apache-2.0 |
| `crates/lx-verify/**` | Apache-2.0 |
| `crates/lx-conformance/**` | Apache-2.0 |
| `plugins/CONTRACT.md`, plugin schema | Apache-2.0 |
| client SDKs | Apache-2.0 |

**Why `lx-types` and `lx-sign` are in Tier 1, which the first draft got wrong.** The free verifier is
only free if its *entire dependency subgraph* is permissively licensed. `lx-verify` needs
`lx-receipt` (parse + canonicalize), `lx-verdict` (recompute the verdict from the evidence rather
than trusting the stated one), and `lx-sign` (check the DSSE envelope) — and all three need
`lx-types`. An Apache-2.0 verifier sitting on an FSL leaf crate is not independently usable, which
would have quietly broken the central trust promise of the project while appearing to honour it.

The Apache-2.0 subgraph is therefore closed under dependency, and `xtask arch-check` asserts it:
**no Tier 1 crate may depend on a Tier 2 crate.**

## Tier 2 — the engine. FSL-1.1-ALv2

Converts to Apache-2.0 on the second anniversary of each version's release.

`crates/**` (everything not listed above) · `plugins/**` · `integrations/**` · `bench/**` ·
`xtask/**` · `demo/**`

Permitted: any internal or commercial use of your own code, at any company size, forever, with
nothing to buy and nothing to negotiate. Also permitted: non-commercial education and research, and
professional services you provide to a licensee. Barred: reselling the engine as a competing
verification service.

**Do not call the engine "open source."** FSL is not OSI-approved during its term. Say **"Fair
Source,"** and say that the spec, schema, conformance suite, and verifier are Apache-2.0.

## Tier 3 — commercial. Proprietary

Not in this repository. Hosted fleet-scale receipt graph, cross-org analytics, compliance reporting,
managed sandbox capacity, the aggregated cross-org calibration corpus, support and SLAs.

## Never

Paywall receipt verification · telemetry by default · extend a conversion date · move the spec tier
to a more restrictive license · add a CLA.
