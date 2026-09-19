# ADR-0020 — Test-surface integrity and architecture fitness join the obligation model; live IDE simulation and deployment orchestration do not

**Status:** accepted

## Context

Four adjacent problems were evaluated together, because treating them as one undifferentiated "AI
safety" bucket is exactly the kind of uniform claim D1–D3 already rejected once. Each is checked
against the same bar: **is this a falsifiable fact we can hash, diff, or re-run — or is it an
opinion?** Only the former belongs in a receipt (`NON-GOALS.md`: "not a code reviewer").

**1. Agents tamper with the tests meant to check them.** SWE-bench's evaluator trusts test output
produced inside the same container the agent's patch can modify — a named design flaw, not a rare
exploit. It is the reason reward-hacking benchmarks exist at all (EvilGenie: agents hardcode answers
or edit testing infrastructure; SpecBench: every frontier model can saturate a visible suite while
reward-hacking scales underneath it). Litmus64 already runs paired BASE/HEAD sandboxed execution
(D3, T2) but currently takes the test files themselves on trust. That is the same class of gap as
`unstated_changes` (ADR-0019) — an agent-authored change nobody checked — just applied to the harness
instead of the source.

**2. Agents introduce architectural anti-patterns that compile and pass tests.** Independent of
functional correctness, published studies describe AI-assisted code churn rising and unresolved
technical debt compounding by two orders of magnitude within a year, with architectural debt singled
out as harder to detect than file-level debt because it sits *between* files. Litmus64's obligation
model (`lx-oblig`) currently reasons per-symbol (`PRESERVE`, `CONTRACT`); it has no notion of
cross-file structural health. This is a real gap, not a duplicate of Mechanism 1's or the existing
engine's semantic-correctness coverage.

**3. The proposed fix for #2 was a live, in-IDE simulator** — "compiles, executes, and logically
stress-tests AI snippets... before presenting them in the IDE." This is a different species of tool:
real-time, pre-display, and necessarily opinionated about what counts as an anti-pattern in the
moment a snippet is generated. It is closer to an inline linter/copilot layer than to a receipt.

**4. Unreviewed AI commits reaching production caused real outages** (Amazon, two separate incidents
in a single week, one with a 99% order-volume drop). The proposed fix was a deployment orchestrator
wrapping AI-generated functions in feature flags gated on staging approval. That category already has
a funded incumbent (LaunchDarkly "CodeControl": progressive rollout, guardrails, kill switches,
45 trillion flag evaluations/day) plus Statsig and GrowthBook. Amazon's own published remediation was
procedural (two-person review, formal approval, stricter automated checks) — not a novel mechanism.

## Decision

**Mechanisms 1 and 2 join the obligation model as new, evidence-shaped obligation families.
Mechanisms 3 and 4 do not enter Litmus64 at all**, for two different reasons: 3 fails the
falsifiable-fact bar this project is built around, and 4 is a solved, competitive market that a
receipt should *feed*, not replace.

### Test & Fixture Integrity Ledger (Mechanism 1)

- A content hash over the sorted file tree of everything the verdict depends on trusting — test
  files, fixtures, golden files, CI config, the harness — taken **before** the agent runs and
  recomputed **after**.
- Any file inside that tree that changed becomes a new obligation kind, `TEST_SURFACE_MODIFIED`,
  alongside `PRESERVE`/`CONTRACT` in `lx-oblig`. It is never an automatic violation — legitimate test
  fixes are common — but it is never silent either: it requires `ConfirmedEvidence` that the paired
  BASE run justified the change (BASE failed the way the stated intent claims), or it is reported as
  `unverified`/`violated` per the existing verdict rules.
- `lx-verdict::decide()` gains an invariant: a verdict cannot be `HELD` while an unresolved
  `TEST_SURFACE_MODIFIED` obligation exists with no evidence behind it.
- Receipt schema (post `v0.1`, tracked as a `v0.2` field addition, not a break — `predicate.md`'s
  forward-compat rule applies): a `test_surface` block carrying pre-hash, post-hash, per-file diff,
  and justification status.

### Architecture Fitness Obligations (Mechanism 2)

- A new obligation family, `STRUCTURAL`, built from declared, checkable rules — the same pattern as
  ArchUnit/NetArchTest "fitness functions": dependency cycles, layering violations against a declared
  module graph, public-API/symbol-surface churn outside the diff's stated scope, coupling delta
  before vs. after. Every one of these is a boolean or a number, never a style verdict.
- Rules are declared once per repository (a `fitness.toml`, mirroring how obligation config already
  works), not invented by Litmus64. A repo with no declared rules gets `unverified: unformalizable`
  for this obligation family — the same honest-gap pattern already used for capability limits
  (`docs/why.md`, `lx capabilities`). Litmus64 never decides what good architecture is; it decides
  whether the declared architecture held.
- Built on `lx-graph`'s existing tree-sitter AST diff, extended from symbol-level diff to a
  module-level dependency graph. Rust-first, matching the existing capability tiering (D1); other
  languages arrive through the existing plugin contract (`plugins/CONTRACT.md`), not a new subsystem.
- Checked at the same points `lx check`/`lx audit` already run — batch, CI-time, evidence-only.
  **No code runs, and no opinion is shown, inside an editor.**

### What does not ship

- **No live IDE simulator.** It would judge code before a human or a paired run ever sees it, which
  makes it opinion by construction — the exact thing `NON-GOALS.md` already rules out. The problem it
  targeted is still solved, by Architecture Fitness Obligations, checked in the same batch/CI model as
  everything else Litmus64 does.
- **No feature-flag orchestrator.** Litmus64 stays a receipt producer. The correct integration, if and
  when it is built, is a thin webhook so an existing flag platform can require a valid signed receipt
  before promoting a flag out of staging — an integration, not a product, and not part of this ADR's
  scope.

## Consequences

**Good.** Mechanism 1 is close to free: it reuses the sandbox and obligation machinery D3/ADR-0019
already specified, adding one digest type and one obligation kind. It closes the exact gap that made
SWE-bench's evaluator exploitable, strengthening the project's core claim rather than diluting it.
Mechanism 2 gives Litmus64 a cross-file dimension it currently lacks, using a formulation
(declared, measurable fitness rules) that is industry-precedented and survives the "not a code
reviewer" bar without exception.

**Bad.** Mechanism 2 is real new work, not a free extension — someone has to build the module
dependency graph and write a credible default `fitness.toml`, or day-one users get zero rules and
zero value. It is Rust-first on day one, same honest gap as every other mechanism in the capability
matrix. Mechanism 1 adds a second content-hash type that must be kept in sync with whatever the
sandbox already hashes for reproducibility, or the two can silently disagree.

## Rejected

- **Treating all four problems as one bundled feature.** The live-IDE-simulator framing and the
  deployment-orchestrator framing both fail the same test (opinion, or already-solved-elsewhere) that
  the other two pass. Forcing them in would have diluted the one sentence that makes Litmus64
  legible: every claim in the receipt is a hash, a diff, or a re-run.
- **Building a feature-flag/deployment orchestrator in-house.** Duplicates a funded, mature market
  (LaunchDarkly CodeControl, Statsig, GrowthBook) for no differentiated benefit; the leverage is in
  making the receipt a gate condition those tools can consume, not in re-implementing rollout
  mechanics.
- **A live in-editor stress-test simulator.** Conflicts with `NON-GOALS.md` ("not a code reviewer");
  real-time, pre-display judgment is a different product category (inline linter/copilot-style tool),
  not a receipt.
- **Hard-blocking any test-file modification outright.** Legitimate test fixes are routine; a blanket
  lock would generate exactly the false-positive noise D3/T1 was designed to make structurally
  impossible.
