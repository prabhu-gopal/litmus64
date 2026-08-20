# Status — read this before believing anything works

**Nothing works yet. 0% of the product is functional.**

That sentence is the honest answer, and this file exists so nobody — including us in three months —
mistakes a compiling workspace for a working tool.

## What actually exists

| | State |
|---|---|
| **Design** | Complete and reviewed. 10 mechanisms, 14 laws, 6 structural decisions, 9 ADRs |
| **Repository scaffolding** | 27 crates, correct dependency graph, license tiers machine-checkable, `cargo build --workspace` passes with 0 warnings |
| **Functional code** | **None.** Every crate is a doc comment and `unimplemented!()` |
| **Tests** | None |
| **Can it verify anything?** | **No.** `lx check` does not exist. `lx audit` does not exist. There is no binary that does work |

`cargo build` passing means the *shape* is right — dependency laws hold, license subgraph is closed,
tier isolation compiles. It says nothing about behaviour, because there is no behaviour.

## Why there is no code yet, on purpose

The design pass found problems that would have been expensive to discover after implementation:

- Three flagship mechanisms had **zero coverage** across the original 1.0 language set
- The performance budget was **below the median of a strict subset** of the pipeline
- The WASM plugin isolation argument **did not hold** for any plugin that runs tests
- The free verifier's dependency subgraph was **not actually free** (Apache-2.0 crate on an FSL leaf)
- `PinnedSampling` would have **400'd against every current Claude model**
- The golden receipt example **violated our own Law 6**

Each of those is hours of writing now versus weeks of rework later. That trade is done. **From here,
more design is procrastination.**

## First testable slice — the only thing that matters next

The goal is not "start building the engine." It is **one end-to-end path that produces a real
artifact from a real repository**, so every claim after it is measured rather than argued.

### Milestone 1 — `lx audit` read-only on a real repo

Ship order, each step independently checkable:

| # | Deliverable | Done when |
|---|---|---|
| 1 | `lx-types`: `Digest`, ids, `Untrusted<T>`, `ObligationStatus`, `UnverifiedReason`, `ConfirmedEvidence` | `trybuild` proves `Untrusted<T>` has no `Display` and `ConfirmedEvidence` cannot be built outside `lx-exec` |
| 2 | `lx-verdict`: `decide()` + `compute_risk()` | 100% branch coverage; property tests for the 5 invariants; golden fixtures in `spec/conformance/golden-verdicts/` |
| 3 | `spec/receipt-v0.1.schema.json` generated from `lx-receipt`, canonical JSON | `xtask schema-check` passes; round-trip property test |
| 4 | `lx-verify` | Verifies a hand-written receipt, **recomputes** the verdict, rejects a Law 6 violation |
| 5 | `lx-graph`: tree-sitter parse + AST diff, **one language (Rust)** | Correctly classifies 20 hand-labelled commits from this repo |
| 6 | `lx-oblig`: **structural obligations only** | Every public symbol outside the diff yields a `PRESERVE`; migrations yield `CONTRACT` |
| 7 | **`unstated_changes`, deterministic core** (ADR-0019) | Changed symbol not mentioned in PR body / issue / commit message → reported. **This is the demo** |
| 8 | `lx-render` terminal + `lx-audit` history walk | `lx audit` on this repository prints a real verification-debt report |

**The test that ends Milestone 1:** run `lx audit` on a real open-source repository we have never
seen, and have a human confirm that at least one `unstated_changes` finding is real and interesting.

If that works, the thesis is validated with roughly 8 units of work instead of 8 workstreams. If it
doesn't, we learn it now — and step 7 is deliberately the cheapest possible test of the single most
important claim in the product.

**Explicitly not in Milestone 1:** no sandbox, no test execution, no LLM, no mutation, no DST, no BMC,
no ledger, no signing, no GitHub App, no plugins. Those are T2 and T3 (`DECISIONS.md` D3). Milestone 1
is entirely T0 + T1, which is why it can be honest about producing no violations at all.

## Milestones after that

| Milestone | Adds | Unlocks the claim |
|---|---|---|
| **2** | Sigstore signing, DSSE, in-toto predicate, conformance suite | "anyone can verify this without trusting us" |
| **3** | Sandbox tiers, paired BASE/HEAD runner, attribution, discrimination filter | first tier that may say `violated` |
| **4** | Metamorphic relations (M10), mutation, property tests | "we attacked it, here's what survived" |
| **5** | Ledger, `LEDGER_CONFLICT`, supersession | "it compounds on your repo" |
| **6** | Revert-mining, calibration, published reliability curve | "the risk score is empirical" |

## Open action items that are not code

1. **Register `litmus64.com`** before signing lands (Milestone 2) — in progress. ~$15/yr, recorded as
   a governance commitment in `GOVERNANCE.md` because it backs the `predicateType` in every signed
   receipt. ADR-0018. Nothing before Milestone 2 is blocked on it.
2. **Consider moving to a `litmus64` GitHub *organization*.** The repo currently lives at
   `prabhu-gopal/litmus64`, which is fine to start. But an org is free, and moving later breaks every
   bookmarked URL, every `cargo install --git` line, and the `repository` field in published crates.
   Cheapest before the first release; annoying after. Same class of decision as the domain (ADR-0018).
3. **Set up the showcase** at `prabhugopal.com/litmus64`. Free, do it now.
4. ~~Paste the real license texts.~~ **Done** — verbatim FSL-1.1-ALv2 (with the 2026 Change Date and
   licensor filled in), verbatim Apache-2.0, and CC-BY-4.0 plus the royalty-free implementation grant.
   `NOTICE` carries the tier map.
5. **Stand up revert-mining early.** It gates calibration and takes calendar time to accumulate; it is
   the one task where starting late cannot be recovered by working harder.

## The rule for this file

Update it when a milestone completes, and **never let it describe intent as if it were state.** A
project whose entire product is honest reporting of what was and was not verified cannot have a
misleading status page.
