# Enterprise readiness

Written for the person who has to approve this, not for the developer who wants it. Every claim here is
either already true or has a named gate in `DECISIONS.md` D3 — nothing on this page is aspirational
marketing.

## The short version

| Question | Answer |
|---|---|
| Does our source code leave the building? | **No.** `llm.enabled: false` gives full deterministic function with zero network egress. `lx explain-egress` prints exactly which bytes would leave, for which provider, before you run anything |
| Can it run in an air-gapped network? | **Yes**, at reduced capability, and the report says which capabilities were lost and why |
| Does it phone home? | **No.** Telemetry is off by default, opt-in only, aggregate-only, and `lx telemetry show` prints the exact payload before you enable it |
| Does it execute untrusted code? | **Yes, deliberately** — that is the product. Tiered isolation: container for your own repo, gVisor for forked PRs, Firecracker microVM for untrusted diffs. Network denied by default, no secrets mounted |
| Can we verify its output ourselves? | **Yes**, with an Apache-2.0 tool that has no dependency on our Fair Source code. `lx verify` recomputes the verdict from the evidence rather than trusting it |
| Can we self-host everything? | **Yes.** There is no hosted component in the open-source product |
| What happens if you disappear? | Your accumulated invariants are plain test files in **your** repository that run without Litmus64. Our engine converts to Apache-2.0 two years after each release, automatically, and that date can never be extended |

## Supply-chain posture

Procurement in 2026 has converged on a single useful question: *which claim can this vendor prove, at
what point in the lifecycle, with what tamper resistance?* That is, word for word, what Litmus64 does
for code changes — so it would be indefensible not to hold ourselves to it.

| Control | Commitment | Gate |
|---|---|---|
| **SLSA Build L3 provenance** | Every release artifact, via `actions/attest-build-provenance`. Hardened builder, non-falsifiable provenance — the current bar for federal procurement | T0 |
| **Signed releases** | Sigstore keyless, verifiable offline, no key management | T0 |
| **SBOM** | CycloneDX **and** SPDX, signed and attached to every release artifact | T0 |
| **OpenSSF Scorecard** | Published in the README and tracked as a regression. A verification project with a mediocre Scorecard is not credible | T0 |
| **Reproducible builds** | Pinned toolchain (`rust-toolchain.toml`), committed lockfile, pinned and vendored dependencies | T0 |
| **Dependency audit** | `cargo-deny` and OSV in CI on every PR; `cargo-audit` daily | T0 |
| **Vulnerability disclosure** | `SECURITY.md` with a private channel and a **published response SLA** — 48h acknowledgement, 14 days to fix for critical | T0 |
| **`#![forbid(unsafe_code)]`** | Every crate except `lx-sandbox`, where each `unsafe` block carries a safety comment and a test | continuous |
| **Third-party sandbox review** | External review of untrusted-diff execution, as a release gate | T2 |
| **We dogfood in public** | Every Litmus64 pull request has a committed, signed Litmus64 receipt in `examples/`. Anyone can read them | continuous |

The last row is the one that should carry the most weight. A supply-chain tool that cannot produce its
own evidence is asking you to take its word for it.

## Regulatory alignment — the honest version

Vendors are currently overclaiming here, and it is worth being precise, because a compliance claim that
does not survive your counsel's reading costs more trust than it buys.

**The EU AI Act does not generally make AI-assisted coding high-risk.** Annex III covers specific use
cases — worker management, regulated safety components, and similar — not ordinary developer
assistance. If someone tells you their code tool is "required for AI Act compliance," they are selling
you something.

Where receipts genuinely matter:

- **If the software you ship is itself high-risk under Annex III**, then from **2 August 2026** you owe
  technical documentation, traceability, and demonstrable human oversight over how it was built.
  "An agent wrote this module and a human clicked merge" is a weak answer to that. A signed receipt
  showing what was verified, what wasn't, and who reviewed it is a strong one. We are the evidence
  layer, not the compliance product.
- **EU Cyber Resilience Act** (applying through 2026–2027) is the more directly relevant regime for
  most teams: traceability and vulnerability-handling obligations across the product lifecycle.
  Receipts, SBOMs, and provenance are the artifacts it asks for.
- **SOC 2 Type II** — for *your* audit, a receipt is evidence for change-management controls (CC8.1):
  tamper-evident proof that a change was verified before merge, with the verification recomputable by
  the auditor rather than asserted by you. Note clearly: **the open-source project does not carry a
  SOC 2 report**, because there is no service to audit. SOC 2 applies only to the commercial hosted
  tier, if and when you use it.
- **Machine-readable AI marking** (AI Act Art. 50) applies to AI *output* marking, not to development
  tooling. A receipt does record a self-reported `authoring_agent` — and marks it
  `trust: unverified_claim`, because we cannot verify who wrote a diff and will not pretend otherwise.

**What we will never do:** claim Litmus64 makes you compliant with anything. It produces evidence. Your
auditor decides what the evidence is worth. Any vendor telling you otherwise about a code tool is
describing a product that does not exist.

## Licensing, for your legal team

Full detail in [`LICENSING.md`](../LICENSING.md), which is normative and machine-enforced in CI.

- **Apache-2.0 forever:** the specification, the JSON Schema, the conformance suite, and the **receipt
  verifier**. You can verify receipts, permanently, without our permission or our code.
- **Fair Source (FSL-1.1-ALv2)** for the engine: **any internal or commercial use of your own code is
  permitted**, at any company size, with nothing to buy and nothing to negotiate. Professional services
  to a licensee are explicitly permitted. The only barred activity is reselling the engine as a
  competing verification service. **Each version converts to Apache-2.0 on its second anniversary**, and
  we have publicly committed that conversion dates are never extended.
- **We do not call the engine "open source"** during its FSL term, because it is not OSI-approved. We
  say Fair Source. If your policy requires OSI licenses for all dependencies, say so and we will
  provide a written exception letter — that is a known and documented friction, not a surprise.
- **No CLA**, ever. DCO only. Contributors keep their copyright and we never acquire the right to
  relicense.

## What to ask us that we cannot dodge

A short list, offered because a vendor page that only contains flattering questions is not useful:

1. *Show me your last 20 false positives.* They are in `bench/corpora/`, as committed test cases.
2. *What is your published false-positive rate, and how is the denominator defined?* Two rates, both
   gated, both defined normatively in `spec/metrics.md`.
3. *Show me your calibration curve, including the bad releases.* Published per release, with the command
   to reproduce it.
4. *What can't it check in my language?* `lx capabilities`, printed from probed toolchains.
5. *Show me a receipt for one of your own commits, and let me verify it myself.* `examples/`, then
   `lx verify`.
