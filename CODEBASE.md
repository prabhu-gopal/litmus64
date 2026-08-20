# Litmus64 — Production Codebase Design

Companion to [`DECISIONS.md`](DECISIONS.md) and [`docs/laws.md`](docs/laws.md). Those cover *why*; this one is
*how it is built*. It is written to be handed to an engineer on day one and to survive fifty
contributors.

**Non-negotiables this structure enforces mechanically:**

1. The verdict function cannot reach model output. *(Enforced by a dependency-graph test.)*
2. Nothing enters a receipt without a replay recipe. *(Enforced by the type system.)*
3. Determinism is asserted, not assumed. *(Enforced by CI running every fixture twice.)*
4. Untrusted text cannot become an instruction. *(Enforced by a newtype that cannot be formatted
   into a privileged prompt.)*
5. An obligation cannot be `held` or `violated` without differentially-confirmed evidence.
   *(Enforced by a token type that only the attribution engine can mint.)*
6. A stage that skips, fails, or finds a mechanism unavailable becomes an `unverified` entry with a
   typed reason. *(Enforced by `StageOutcome` having no variant that discards information.)*
7. A capability the install does not have cannot be claimed. *(Enforced by `lx capabilities` being
   computed from probed toolchains, and by a CI test asserting the published matrix matches.)*

Structural decisions taken in revision 2 and recorded in `DECISIONS.md` + ADRs 0011–0013:
**Rust is a 1.0 plugin** (it is the only language where the full escalation ladder exists, and it
makes our own repo the flagship dogfood); **the plugin ABI is subprocess JSON-over-stdio**, with WASM
demoted to a post-1.0 second transport; and **releases are staged by write-access** (T0 standard →
T1 read-only → T2 execution → T3 attack), so crates below carry the tier that first needs them.

---

## 1. Repository layout

```
litmus64/
├── README.md                     honest, one screenshot, one ask, benchmark-linked
├── DECISIONS.md                  the three structural decisions + rejected alternatives
├── LICENSE                       FSL-1.1-ALv2 — the engine (converts to Apache-2.0 in 2y)
├── LICENSE-APACHE                Apache-2.0 — spec/, schema, conformance/, verifier, SDKs, plugin ABI
├── LICENSE-SPEC                  CC-BY-4.0 + royalty-free implementation grant (spec prose & docs)
├── LICENSING.md                  which tier each path is in; the table is NORMATIVE
├── TRADEMARK.md                  Litmus64 wordmark policy; "Litmus64-compatible" grant terms
├── NOTICE  CODEOWNERS  CHANGELOG.md
├── GOVERNANCE.md  CONTRIBUTING.md  CODE_OF_CONDUCT.md  MAINTAINERS.md
├── SECURITY.md  THREATS.md  NON-GOALS.md  KNOWN-LIMITATIONS.md  ROADMAP.md
├── Cargo.toml                    workspace root; [workspace.dependencies] pins EVERYTHING
├── Cargo.lock                    committed
├── rust-toolchain.toml           pinned toolchain — reproducibility starts here
├── deny.toml                     cargo-deny: licenses, advisories, bans, duplicate versions
├── dist-workspace.toml           cargo-dist release matrix
├── .devcontainer/                one-command contributor environment
├── .github/
│   ├── workflows/                ci · security · bench · release · dogfood · calibrate
│   ├── ISSUE_TEMPLATE/           bug · false-positive · missed-defect · plugin · rfc
│   └── PULL_REQUEST_TEMPLATE.md  includes "which law of the system does this touch?"
│
├── spec/                                        ── THE NORMATIVE ARTIFACT ──
│   ├── receipt-v0.1.md                          RFC 2119 prose. v1 is EARNED (two impls), not claimed
│   ├── receipt-v0.1.schema.json                 GENERATED from lx-receipt types; CI asserts match
│   ├── plugin-v0.1.schema.json                  GENERATED; transport-neutral plugin contract
│   ├── predicate.md                             in-toto registration + test-result subsumption
│   ├── verdict.md                               the algebra, normatively
│   ├── risk.md                                  the model, weights, calibration protocol
│   ├── ledger.md                                promotion / application / retirement / SUPERSESSION
│   ├── amendment.md                             append-only discharge chain
│   ├── capability.md                            the M9 matrix; what each mechanism requires
│   ├── budgets.md                               per-stage cost arithmetic for the three profiles
│   ├── metrics.md                               NORMATIVE metric denominators (per-change vs per-finding)
│   └── unverified-reasons.md                    the reason enum; why flattening it is a lie
│   └── conformance/
│       ├── valid/*.json                         must validate
│       ├── invalid/*.json                       each paired with the clause it violates
│       ├── golden-verdicts/*.json               (evidence, policy) → expected verdict
│       ├── golden-risk/*.json                   (features, weights) → expected score
│       ├── law6-skips/*.json                    every skipped stage HAS an unverified entry
│       └── forward-compat/*.json                unknown fields MUST be preserved
│
├── crates/
│   ├── lx-types/          leaf types, newtypes, ids, digests, Untrusted<T>, Capability
│   ├── lx-receipt/        schema types (schemars) · canonical JSON · validation · amendments
│   ├── lx-verdict/        PURE. verdict algebra + risk scoring. deps: lx-types only
│   ├── lx-verify/         THE FREE VERIFIER. Apache-2.0 subgraph root; closed under deps.
│   │                      Library FIRST, binary second — anyone may embed it
│   ├── lx-policy/         litmus64.yaml → typed policy; Cedar evaluation
│   ├── lx-graph/          tree-sitter parse · AST diff (GumTree-class) · SCIP · blast radius
│   ├── lx-classify/       change taxonomy (M4) → recipe selection
│   ├── lx-oblig/          obligation derivation: structural · empirical · ledger · inferred
│   ├── lx-invariant/      dynamic invariant mining: grammar + FP filter (language-independent)
│   │                      + trace adapters (python first; see M3 — Daikon has NO front end
│   │                      for python/ts/go, so this is built, not vendored)
│   ├── lx-ledger/         promote · apply · prune · curate; on-disk format
│   ├── lx-plan/           budget knapsack · escalation ladder · task DAG
│   ├── lx-sandbox/        OCI / gVisor / Firecracker / bubblewrap tiers; determinism harness
│   ├── lx-exec/           paired BASE|HEAD runner · attribution (M2) · flake statistics
│   ├── lx-discriminate/   the M1 filter
│   ├── lx-attack/         mutation · property · DST orchestration · BMC escalation
│   ├── lx-llm/            provider trait · quarantined/privileged channels · structured output
│   ├── lx-triage/         self-review, suppression records
│   ├── lx-cache/          content-addressed store; salsa-style query layer
│   ├── lx-sign/           DSSE · Sigstore · in-toto · transparency log · offline verify
│   ├── lx-plugin/         subprocess host · JSON contract · capability gating · probe & registry
│   │                      (no wasmtime at 1.0 — ADR-0012)
│   ├── lx-capability/     probe toolchains → the M9 matrix; backs `lx capabilities`
│   ├── lx-audit/          retroactive receipts over git history; verification debt (ADR-0016).
│   │                      THE FRONT DOOR — read-only tier, so it cannot accuse anyone
│   ├── lx-render/         terminal · markdown · HTML · SARIF · JUnit · annotations
│   ├── lx-engine/         orchestration: the 11 stages wired together
│   ├── lx-cli/            `lx` binary (clap) — thin; all logic lives in lx-engine
│   ├── lx-mcp/            MCP server
│   └── lx-conformance/    `lx-conformance` binary; runs spec/conformance/**
│
├── packaging/              one binary, six channels (ADR-0015); wrappers land per channel
│
├── plugins/                shipped at 1.0 — subprocess ABI, any language
│   ├── lx-rust/            THE FLAGSHIP: loom + shuttle + cargo-mutants + Kani = full ladder
│   ├── lx-python/  lx-typescript/  lx-go/  lx-openapi/  lx-sql/  lx-semgrep/
│   ├── CONTRACT.md         "read JSON on stdin, write JSON on stdout, exit 0" — the whole thing
│   └── template/           starting point; also a non-Rust example, to prove the ABI is neutral
│
├── integrations/
│   ├── github-app/         Checks write requires an App
│   ├── github-action/      thin wrapper; pinned digest
│   ├── gh-extension/  hooks/{claude-code,codex,cursor,git}/  mcp/
│   └── ci/{gitlab,buildkite,jenkins}/          post-1.0
│
├── bench/
│   ├── lx-bench/          harness (corpora, runners, statistics, CIs)
│   ├── corpora/            manifests + fetchers (no vendored third-party code)
│   ├── mining/             revert-mining pipeline → calibration corpus
│   └── RESULTS.md          dated, commit-pinned, model-pinned, reproduction commands
│
├── demo/                   `lx demo` fixture: tiny repo, planted defect, offline, <=5s
├── examples/               real repos + COMMITTED RECEIPTS you can read (rust, python, ts, go —
│                           the narrower ones included ON PURPOSE, per M9)
├── docs/                   docusaurus; spec pages generated; adr/ decision log
├── xtask/                  cargo xtask: schema-gen, conformance, dogfood, corpus, audit-deps
└── fuzz/                   cargo-fuzz targets: receipt parse, canonical JSON, diff, policy
```

---

## 2. Crate dependency law

```
                       lx-types  ← leaf: no deps beyond std/serde
                          │
      ┌───────────────────┼─────────────────────────┬──────────────┐
      ▼                   ▼                         ▼              ▼
 lx-receipt         lx-verdict               lx-policy     lx-cache
      │             (PURE — types only)             │              │
      │                                             │              │
      ├──────────────┬───────────┬──────────────┬───┴──────┬───────┴──────┐
      ▼              ▼           ▼              ▼          ▼              ▼
  lx-graph    lx-invariant  lx-ledger   lx-sandbox  lx-sign   lx-plugin
                                              │
                                        lx-capability
      │              │           │              │
      ▼              ▼           ▼              ▼
 lx-classify ──→ lx-oblig ←────┘         lx-exec ──→ lx-discriminate ──→ lx-attack
                     │                                                            │
                  lx-llm ──→ lx-triage                                          │
                     │            │                                              │
                     └────────────┴──────────────→ lx-plan ──────────────────────┘
                                                       │
                                                  lx-engine ──→ lx-render
                                                       │
                                        ┌──────────────┼──────────────┐
                                     lx-cli       lx-mcp     lx-conformance
```

**Hard rules, enforced by `xtask arch-check` in CI:**

| Rule | Rationale |
|---|---|
| `lx-verdict` may depend **only** on `lx-types`. | Law 1. The verdict is unreachable from model output, provably, at the build-graph level. |
| `lx-llm` may **not** be a dependency of `lx-verdict`, `lx-receipt`, `lx-policy`, or `lx-sign`. | Injection containment. |
| Nothing may depend on `lx-cli`. | The binary is a shell; all logic is testable without it. |
| `lx-types` has no I/O, no async, no filesystem. | Keeps the domain model portable and fast to test. |
| Every crate that produces evidence depends on `lx-sandbox`. | No unsandboxed execution path can exist. |
| No crate spawns a process except through `lx-sandbox`, including `lx-plugin`. | Law 6 of the codebase: a plugin inherits the trust tier of the run it executes inside and can never obtain a weaker one. This is the rule that replaces the WASM boundary (ADR-0012), so it is enforced by `xtask arch-check` scanning for `std::process` and `tokio::process` outside `lx-sandbox`. |
| `ConfirmedEvidence` may only be constructed inside `lx-exec`. | An obligation cannot be `held` or `violated` without a BASE control (M2), by construction rather than by check. |
| Tier discipline: no T1 crate may depend on a T2+ crate. | `lx check --read-only` must run with no sandbox, no runner, no model, no plugin host present — the tier that everyone meets first cannot be broken by the tiers above it. |

---

## 3. Core domain model

`lx-types` is where correctness is designed in. The type system carries the invariants so reviewers
don't have to remember them.

```rust
// ── Identity & integrity ─────────────────────────────────────────────────────
/// SHA-256: 32 bytes, and exactly **64 hexadecimal characters** in serde —
/// which is where the name Litmus64 comes from. (An earlier draft said
/// "64-byte digest"; that was wrong, and being wrong about a hash length in
/// the origin story of a receipt project is not survivable.)
pub struct Digest(pub [u8; 32]);
pub struct ReceiptId(Ulid);
pub struct ObligationId(SmolStr);             // "OB-1"
pub struct EvidenceId(SmolStr);               // "EV-7"
pub struct Seed(pub u64);                     // every stochastic step records one

// ── Law 4: untrusted text can never be formatted into a privileged prompt ────
/// Wraps any bytes that came from a human or an agent: PR bodies, issue text,
/// code comments, commit messages, test output, agent transcripts.
/// Deliberately implements NEITHER Display NOR Serialize-as-string.
/// The ONLY way out is `quarantine()`, which routes through lx-llm's
/// quarantined channel and returns typed, schema-validated data.
pub struct Untrusted<T>(T, Provenance);

impl<T: AsRef<str>> Untrusted<T> {
    pub fn provenance(&self) -> &Provenance { &self.1 }
    pub fn redacted_preview(&self, n: usize) -> String { /* for logs only */ }
    // NO `fn as_str()`. NO `impl Display`. This is the whole point.
}

pub enum Provenance { PrBody, Issue(u64), CommitMessage, CodeComment(FileSpan),
                      AgentTranscript, TestOutput, ExternalDoc(Url) }

// ── Obligations ──────────────────────────────────────────────────────────────
pub struct Obligation {
    pub id: ObligationId,
    pub class: ObligationClass,          // PRESERVE CHANGE INTRODUCE INVARIANT CONTRACT NON_GOAL
    pub statement: String,               // human-readable; marked by source in every renderer
    pub source: ObligationSource,        // Structural | Empirical | Ledger | Issue | PrBody
                                         // | Policy | Human | Inferred
    pub confidence: Confidence,          // 1.0 only for Structural/Policy
    pub criticality: Criticality,        // Low Medium High Critical
    pub formalization: Option<Formalization>,
    pub status: ObligationStatus,
    pub evidence: Vec<EvidenceId>,
    pub ledger_ref: Option<LedgerRef>,
}

/// The six terminal states. `LedgerConflict` is NOT a violation: it means a
/// ledger-sourced invariant failed while its own symbols are in this diff, i.e.
/// the change probably supersedes it (M6). Conflating the two is how the
/// compounding asset turns into a nag and gets deleted.
pub enum ObligationStatus {
    Held        (NonEmpty<ConfirmedEvidence>),
    Violated    (NonEmpty<ConfirmedEvidence>),
    Inconclusive{ evidence: Vec<EvidenceId>, why: InconclusiveReason },
    PreExisting { base_fail_rate: f64 },
    LedgerConflict { entry: LedgerRef, locked_by: ReceiptId, supersede_hint: String },
    Unverified  { reason: UnverifiedReason },
}

/// Law 5 + Law 6 + Law 14: `unverified` is not one thing, and flattening these
/// into a single word is a lie of omission. "We ran out of budget" is a knob the
/// user can turn; "no such verifier exists for this language" is a limit they
/// must plan around. Normative in `spec/unverified-reasons.md`.
pub enum UnverifiedReason {
    Budget            { stage: StageName, estimated: CostEstimate },
    CapabilityUnavailable { mechanism: Mechanism, language: Language, detail: String },
    MissingToolchain  { tool: String, install_hint: String },
    NoTestHarness     { detail: String },
    Unformalizable    { detail: String },
    PolicyDisabled    { setting: String },
    NotRunInFastProfile,                    // the read-only / `check` profile — never an accusation
}

/// ── The M2 token ────────────────────────────────────────────────────────────
/// A receipt for a *differentially confirmed* observation. Its constructor is
/// `pub(crate)` in `lx-exec` and reachable only from the attribution engine, so
/// no other crate — including a future contributor's — can mint one. This is
/// what makes "no attribution without a BASE control" a compile-time property
/// instead of a runtime `if`.
pub struct ConfirmedEvidence { id: EvidenceId, base_runs: u32, base_fail: u32,
                               head_runs: u32, head_fail: u32 }

impl ConfirmedEvidence {
    pub fn id(&self) -> &EvidenceId { &self.id }
    // NO pub fn new(). NO From<EvidenceId>. That absence IS the mechanism.
}

/// Construction is fallible-by-design: an obligation with no formalization
/// CANNOT be constructed in a verified state. Law 2, in the type system.
impl Obligation {
    pub fn hold(self, ev: NonEmpty<ConfirmedEvidence>) -> Result<Self, HoldError> {
        if self.formalization.is_none() { return Err(HoldError::NotFormalized) }
        // The attribution requirement is now discharged by the TYPE of `ev`,
        // not by a check that a future refactor could delete.
    }
}

// ── Capability (M9): the tool's own limits are typed domain data ─────────────
pub enum Mechanism { Structural, Contract, Differential, Mutation, Property,
                     InvariantMining, ScheduleReplay, ScheduleSearch, Bmc }

pub enum Availability { Ready, Planned { tracking: String },
                        NoSubstrate { detail: String }, NotApplicable }

/// Probed from the environment, never hardcoded, and asserted in CI to match
/// the published matrix in `spec/capability.md`. Every receipt carries one.
pub struct CapabilitySet { pub language: Language,
                           pub matrix: BTreeMap<Mechanism, Availability> }

// ── Evidence: no evidence without a replay recipe ─────────────────────────────
pub struct Evidence {
    pub id: EvidenceId,
    pub kind: EvidenceKind,
    pub claim: String,
    pub result: EvidenceResult,           // Pass | Fail | Warn | Inconclusive | Skipped { reason }
    pub attribution: Attribution,         // M2
    pub detail: EvidenceDetail,           // strongly typed per kind — never a JSON blob
    pub replay: ReplayRecipe,             // REQUIRED. Law 3.
    pub artifacts: Vec<ArtifactRef>,
    pub duration: Duration,
    pub cost: Cost,
}

pub enum Attribution {
    DifferentialConfirmed { base_runs: u32, base_fail: u32, head_runs: u32, head_fail: u32 },
    PreExisting  { base_fail_rate: f64 },
    Environmental{ detail: String },
    Flaky        { rate: f64, runs: u32 },
    NotAttributed,
}
// `NotAttributed` cannot support a `Violated` status — and that is no longer a
// comment, which is all it used to be. `ObligationStatus::Violated` requires
// `ConfirmedEvidence`, which only the attribution engine can mint, and only from
// `DifferentialConfirmed`. Deleting the guarantee now requires deleting a type.

/// M5 ships as two distinct kinds, never one kind with a confidence score,
/// because "we explored 118k interleavings" and "we can reproduce this race on
/// demand" are different claims and only one of them is available in Python.
pub enum EvidenceKind {
    ExistingSuite, GeneratedTest, DifferentialExecution, RegressionReproduction,
    PropertyTest, Mutation, ContractDiff, MigrationAnalysis, InvariantMining,
    ScheduleReplay { seed: Seed, recorded_decisions: u32 },
    ScheduleSearch { engine: SearchEngine, seeds: u32, interleavings: u64 },
    BoundedModelCheck { engine: BmcEngine, harnesses: u32, unwind: u32 },
    ShadowDiff, Canary, StaticAnalysis, PerfSmoke,
}

pub struct ReplayRecipe {
    pub command: Vec<String>,
    pub env_digest: Digest,
    pub seed: Option<Seed>,
    pub workspace: WorkspaceSpec,          // BASE | HEAD | Paired
}

// ── Verdict: pure, total, auditable ──────────────────────────────────────────
pub enum Verdict { AutoMergeable, HumanReviewRequired, ExpertReviewRequired,
                   ChangesRequested, Blocked }
```

`lx-verdict` exposes exactly two pure functions. Both are property-tested and golden-tested against
`spec/conformance/`:

```rust
pub fn compute_risk(f: &RiskFeatures, w: &Weights) -> RiskScore;
pub fn decide(obligations: &[Obligation], coverage: &Coverage,
              risk: RiskScore, policy: &VerdictPolicy) -> VerdictOutcome;
```

Properties asserted in `lx-verdict/tests/props.rs`:

- Monotonicity: adding an `unverified` high-criticality obligation never *loosens* the verdict.
- No `Held` obligation may reference evidence whose attribution is not `DifferentialConfirmed`
  (now unrepresentable rather than merely asserted — kept as a property test anyway, because the
  test documents the intent for the next person who touches the type).
- `LedgerConflict` never blocks, under any policy, and never satisfies an `auto_merge` gate.
- A `CHANGE`-class obligation from stated intent that contradicts a `PRESERVE` resolves to
  `LedgerConflict`/review, never `Violated` (Law 13 — BASE is a control, not an oracle).
- `Inconclusive` never satisfies an `auto_merge` gate, under any policy.
- Any `Violated { criticality >= High }` ⇒ `Blocked`, for every policy.
- Determinism: `decide` is a pure function of its arguments (no clock, no env, no I/O — the crate
  cannot even reach them).

---

## 4. Engine orchestration

`lx-engine` wires the eleven stages. Every stage implements one trait, which is what makes the
pipeline testable, cacheable, resumable, and honest about skips.

```rust
#[async_trait]
pub trait Stage: Send + Sync {
    fn name(&self) -> StageName;
    fn cache_key(&self, ctx: &Ctx) -> Option<Digest>;      // None ⇒ never cached
    fn cost_estimate(&self, ctx: &Ctx) -> CostEstimate;    // feeds the knapsack planner
    async fn run(&self, ctx: &mut Ctx) -> StageOutcome;
}

pub enum StageOutcome {
    Ok(StageReport),
    Skipped { reason: SkipReason },   // Budget | MissingToolchain | PolicyDisabled
                                      // | UnsupportedLanguage | NoTestHarness
    Failed  { error: StageError, partial: Option<StageReport> },
}
```

**`SkipReason` is a domain type, not a string** — because Law 6 says skips must be reported, and
`lx-engine` mechanically converts every `Skipped` and every `Failed` into an `unverified[]` entry
with that reason. A stage cannot vanish quietly; the code path does not exist.

Stage registry, in order, with cache and criticality gating:

| # | Stage | Cached | Runs when |
|---|---|---|---|
| 1 | `ingest` | by tree digest | always |
| 2 | `understand` (graph + classify + blast radius) | ✓ | always |
| 3 | `reconstruct` (intent, diff-only) | by diff digest + model id | `llm.enabled` |
| 4 | `derive` (obligations, 4 sources) | partially | always |
| 5 | `formalize` | ✓ | always |
| 6 | `harness` (paired BASE\|HEAD env) | by env digest | always |
| 7 | `discriminate` | by artifact digest | always |
| 8 | `attack` (mutation → property → DST → BMC) | per rung | ladder gated by criticality + budget |
| 9 | `triage` | by finding digest | when any violation exists |
| 10 | `score` (coverage, risk, verdict, routing) | never | always |
| 11 | `emit` (canonicalize, sign, ledger, defer, calibrate) | never | always |

**Profiles select stages; they never weaken claims.** `lx check` (default) runs 1, 2, 4, 5, 6, 7, 10,
11 with no model and no attack ladder; `--read-only` runs 1, 2, 4, 10, 11 with no execution at all
and **cannot construct `ObligationStatus::Violated`**, because it never obtains a
`ConfirmedEvidence`; `--deep` runs everything. Stages a profile omits produce
`UnverifiedReason::NotRunInFastProfile` entries — visible, typed, and never phrased as a finding
against the author.

| Profile | Stages | Wall clock p95 | LLM |
|---|---|---|---|
| `--read-only` | 1 2 4 10 11 | ≤ 10 s | optional (intent only) |
| `check` (default) | 1 2 4 5 6 7 10 11 | ≤ 60 s | none |
| `--deep` | all 11 | ≤ 20 min | yes |
| `audit` | all 11, whole-repo scope | ≤ 90 min | yes |

The planner (`lx-plan`) does a cost×information-gain knapsack over the tasks each stage proposes,
subject to the policy budget. Its output is deterministic given the same inputs and budget — asserted
in tests, because a nondeterministic planner makes receipts non-reproducible.

---

## 5. The model layer: CaMeL in code

`lx-llm` has two channels and they are different types. Confusing them is a compile error, not a
review comment.

```rust
/// Reads untrusted content. No tools. No history. Output MUST deserialize into
/// a caller-supplied schema type or the call fails.
pub struct Quarantined { model: ModelId, params: PinnedSampling }
impl Quarantined {
    pub async fn extract<T: DeserializeOwned + JsonSchema>(
        &self, task: &'static str, input: Untrusted<String>,
    ) -> Result<T, LlmError>;                  // ← the only exit from Untrusted<T>
}

/// Plans and drafts. NEVER receives Untrusted<T>. Enforced by the signature:
/// there is no overload that accepts one.
pub struct Privileged { model: ModelId, params: PinnedSampling }
impl Privileged {
    pub async fn draft<T: DeserializeOwned + JsonSchema>(
        &self, task: &'static str, facts: &TypedFacts,
    ) -> Result<T, LlmError>;
}
```

Every call records `{ model_id, prompt_digest, generation_digest, tokens, usd, latency }` into the
receipt's `stages[]`.

**`PinnedGeneration`, not `PinnedSampling` — and this was a bug.** The original spec said
"`PinnedSampling` forbids unspecified temperature." But `temperature`, `top_p`, and `top_k` are
**removed on Claude Opus 5, Sonnet 5, and Fable 5 — sending any of them returns a 400.** As written,
this type would have failed against every current model, and would have pinned parameters that no
longer exist. The knob is now `output_config.effort` plus the thinking mode (ADR-0019):

```rust
pub struct PinnedGeneration {
    model: ModelId,            // exact id from the models list — NEVER a date-suffixed guess
    effort: Effort,            // low | medium | high | xhigh | max
    thinking: ThinkingMode,    // adaptive | disabled, where the model permits it
    format_digest: Digest,     // digest of the structured-output schema; part of the contract
}
```

And the honest consequence, stated in the receipt rather than glossed: **LLM stages are not
bit-reproducible even fully pinned.** That is exactly why Law 8 requires every model call to be
followed by a deterministic filter, and why the byte-identical-receipt gate applies to the
deterministic core. `PinnedGeneration` records what was fixed so a reader knows *what varied* — it is
not a replay guarantee, and calling it one would be the sort of overclaim we reject elsewhere.

**Structured outputs are the quarantine boundary, enforced by the API.** `Quarantined::extract` uses
`output_config: {format: ...}` with `strict: true`, so "output MUST deserialize into a caller-supplied
schema or the call fails" is a platform guarantee rather than our parser's opinion. This is the CaMeL
typed-data channel implemented with the platform feature instead of around it.

Provider abstraction is one trait (`ChatProvider`) with implementations for Anthropic (reference),
OpenAI-compatible, and local (Ollama/llama.cpp). `no_egress: true` restricts the registry to local
providers at construction time; there is no runtime branch that could leak.

**Tests that must exist:**
- `tests/injection_corpus.rs` — every entry in `bench/corpora/injection/` is fed through the real
  pipeline; the assertion is that **no verdict changes**. Zero tolerance, release-gating.
- `tests/untrusted_leak.rs` — a compile-fail test suite (trybuild) asserting that
  `Privileged::draft` cannot be called with `Untrusted<T>`, and that `Untrusted<T>` has no
  `Display`/`as_str`.

---

## 6. Sandbox and determinism

`lx-sandbox` presents one interface over four backends and picks the tier from trust, not from
convenience.

```rust
pub enum Tier { Process, Container, Gvisor, MicroVm }

pub fn tier_for(trust: TrustContext) -> Tier {
    match trust {
        TrustContext::OwnRepoLocal            => Tier::Container,
        TrustContext::OwnRepoCi               => Tier::Container,
        TrustContext::ForkedPr                => Tier::Gvisor,
        TrustContext::UntrustedDiff           => Tier::MicroVm,
        TrustContext::UntrustedPlugin         => unreachable!("plugins run in wasmtime"),
    }
}

pub struct Limits { cpu_ms: u64, mem_bytes: u64, wall_ms: u64, pids: u32,
                    net: NetPolicy /* Denied | Allowlist(..) */, fs: FsPolicy }
```

The **determinism harness** applied to every execution: pinned `TZ`, `LC_ALL`, `PYTHONHASHSEED`,
`SOURCE_DATE_EPOCH`, faked clock where the runtime allows, seeded RNG, stable hostname, network
denied, `/tmp` fresh per run, environment sorted and digested. The digest of that entire
configuration is `environment_digest` in the receipt — it is what makes `lx replay` meaningful on
someone else's machine.

`lx-exec` owns the **paired** execution primitive, which is the physical embodiment of M2:

```rust
pub async fn run_paired(spec: &TaskSpec, reps: u32) -> PairedOutcome;
// Runs on BASE and HEAD, `reps` times each, interleaved to cancel out machine drift.
// Returns per-side pass/fail counts, timings, and a computed Attribution.
// There is no `run_head_only`. The API does not permit unattributed claims.
```

---

## 7. Plugin host

**One contract, one transport at 1.0** (ADR-0012). `spec/plugin-v0.1.schema.json` is generated from
the same Rust types as the receipt, so the contract cannot drift from the engine. The transport is a
subprocess speaking JSON over stdio, and the complete plugin surface is three subcommands:

```
$ lx-python capabilities          # → { languages, evidence_kinds, mechanisms, commands, cost_class }
$ lx-python plan  < request.json  # → { tasks: [ … ] }              deterministic; asserted in tests
$ lx-python run   < task.json     # → { result, replay, artifacts } or { skipped: { reason } }
```

**Why not WASM at 1.0.** A WASI 0.2 component cannot run `pytest`, `vitest`, `go test`, or
`cargo test`, so all five evidence-producing plugins would have taken the subprocess "escape hatch"
anyway — leaving wasmtime, WIT, and the Component Model as a permanent audit surface and a learning
curve protecting only the plugins that never execute code. Isolation belongs to the sandbox, which
already has the strictly harder job of containing the untrusted *diff*. WASM returns post-1.0 as a
second transport for pure-analysis plugins, where sub-5ms in-process invocation is a real win; the
contract is transport-neutral precisely so that lands without breaking a single existing plugin.

Host capabilities are gated identically to before, but by `lx-plugin` over `lx-sandbox` rather than
by a wasmtime host:

| Capability | Gate |
|---|---|
| process execution | Only commands matching the plugin's declared `capabilities().commands` allowlist, spawned **through `lx-sandbox`** in the current trust tier. A plugin can never spawn a process directly; `xtask arch-check` forbids `std::process` outside `lx-sandbox` |
| filesystem | Workspace-scoped; BASE mounted read-only; no path escape; enforced by the sandbox, not by cooperation |
| network | Denied unless the plugin declares `requires_network` **and** policy allows it |
| logging | Always; structured, redacted, secret-scanned |

Every receipt records which plugin produced which evidence, at which version, so a plugin that
starts producing bad evidence is attributable after the fact — the accountability layer that
replaces ambient distrust.

Plugin conformance suite (`plugins/template/tests/`) that every plugin must pass:
capabilities are honest · `plan` is deterministic · `run` is idempotent for the same input ·
no writes outside the workspace · declared cost class matches measured cost within 2× ·
graceful `Skipped` on a missing toolchain rather than a panic.

Third-party plugins require an allowlist entry in `litmus64.yaml` naming the plugin and its pinned
digest — trust is explicit and versioned, never ambient. `plugins/template/` ships in a language
*other* than Rust, deliberately: if the reference template were Rust, the ABI's language-neutrality
would be a claim rather than a demonstration.

---

## 8. Ledger on disk

The ledger lives in the *user's* repository and must be readable by a human with no tooling. That is
both the anti-lock-in guarantee and the reason it can be reviewed in a normal PR.

```
.litmus64/
├── policy.yaml
├── receipts/<short-sha>.json           signed receipts (or an external store)
├── ledger/
│   ├── manifest.toml                   index: id, version, symbols, status, provenance
│   ├── auth/no-duplicate-sessions@1/   RETIRED — superseded by @2
│   │   ├── invariant.toml              statement, class, criticality, symbols, seeds
│   │   ├── test_no_duplicate_sessions.py   ← plain, readable, runnable WITHOUT litmus64
│   │   ├── provenance.json             PR, issue, incident, promoting receipt id
│   │   └── superseded_by.json          → @2, the receipt that changed it, and WHY
│   ├── auth/no-duplicate-sessions@2/   active
│   └── cache/invalidation-order@4/…
└── suppressions.toml                   reviewed, owned, EXPIRING suppressions
```

`manifest.toml` entries carry a lifecycle: `active` → `nondiscriminating(n)` → `retired{reason}`.
Retirement is deterministic (an entry that fails to discriminate on N consecutive runs where its
symbols still exist is flagged for review; an entry whose symbols are gone is retired
automatically), and every transition is recorded with the receipt that caused it.

**Ledger entries can require review; they can never silently block.** A ledger obligation that fails
routes to `HUMAN_REVIEW_REQUIRED` with the provenance attached, so a stale invariant costs a
conversation, never a false wall.

**Supersession is the path that keeps the ledger from becoming a liability.** The dominant failure
mode is not a stale entry — it is a *correct* change that legitimately invalidates a locked-in
invariant. When a failing ledger entry's own symbols appear in the current diff, the status is
`LedgerConflict`, not `Violated`, and the remedy is one command:

```
$ lx ledger supersede auth/no-duplicate-sessions --receipt lx_01JB3K7X9QW2
  @1 retired  → @2 promoted   reason recorded, provenance chained, both kept on disk
```

Versioned, append-only, and never destructive — the same shape as receipt amendments. Directories
are never deleted, because over a few years this history *is* the repository's decision log, mined
automatically from its own verification runs. That artifact is worth more than the current invariant
set, and it is the part no competitor can retroactively acquire.

---

## 9. Testing strategy

A verification tool with weak tests is a joke. Eight layers, all in CI.

| Layer | Where | What it guarantees |
|---|---|---|
| **Unit** | per crate | Ordinary correctness |
| **Property** (proptest) | `lx-verdict`, `lx-receipt`, `lx-graph`, `lx-plan` | Verdict monotonicity, canonical-JSON round-trip, AST-diff invariants, planner determinism |
| **Snapshot** (insta) | `lx-render`, `lx-receipt` | Terminal/markdown/SARIF output and schema stay reviewable; diffs are visible in PRs |
| **Golden / conformance** | `lx-conformance` over `spec/conformance/**` | The spec and the implementation cannot drift |
| **Compile-fail** (trybuild) | `lx-llm`, `lx-types` | `Untrusted<T>` cannot leak into a privileged path; `Obligation::hold` cannot be called without formalization; **`ConfirmedEvidence` cannot be constructed outside `lx-exec`** (the M2 guarantee, as a compile error) |
| **Architecture** | `xtask arch-check` | The §2 dependency laws: verdict ⊥ llm · no `std::process` outside `lx-sandbox` · no T1 crate depends on a T2+ crate |
| **Capability honesty** | `xtask capability-check` | `lx capabilities` output matches `spec/capability.md` for every language; no mechanism is claimed `Ready` without a passing end-to-end fixture that uses it (Law 14) |
| **Law 6 completeness** | `lx-conformance` + `spec/conformance/law6-skips/` | Every `stages[]` entry that is not `ok` has a matching `unverified[]` entry. A receipt that skips a stage silently is **rejected as malformed** — including our own examples, which is how this was caught |
| **Determinism** | `xtask determinism` | Every fixture run twice → byte-identical receipts modulo timestamps |
| **Adversarial** | `bench/corpora/injection`, `…/flaky`, `…/tautological`, `…/malicious-plugin` | Zero verdict changes under injection; flakes labelled not blamed; tautological tests discarded; malicious plugins contained |
| **End-to-end** | `tests/e2e/` on pinned real repos | Cold install → receipt, on Linux and macOS, with and without network |
| **Fuzz** (cargo-fuzz) | `fuzz/` | Receipt parsing, canonical JSON, diff engine, policy evaluation never panic |
| **Performance** (criterion + budgets) | `benches/` | The §8 non-functional budgets are regressions, not vibes |
| **Benchmark** | `bench/lx-bench` | FP rate, detection, calibration — release-gating |

**Per-path license headers.** Every file carries an SPDX identifier, and `cargo xtask license-check`
fails CI if a path's header disagrees with the tier table in `LICENSING.md`, which is normative.
Getting this wrong once, in public, is a legal mess — so it is a machine check, not a convention.

**The Tier 1 set is larger than first drafted, and the reason is load-bearing.** The free verifier is
only free if its **entire dependency subgraph** is permissively licensed. `lx verify` must parse and
canonicalize a receipt (`lx-receipt`), check the DSSE envelope (`lx-sign`), and — critically —
**recompute** the verdict from the evidence rather than trusting the stated one (`lx-verdict`), and
all three rest on `lx-types`. An Apache-2.0 verifier sitting on an FSL leaf crate is not
independently usable: it would have broken the central trust promise of the project while appearing
to honour it.

So Tier 1 (Apache-2.0) is `lx-types`, `lx-receipt`, `lx-verdict`, `lx-sign`, **`lx-verify`**, and
`lx-conformance`, plus `spec/` and the plugin contract. `lx-verify` exists as its own crate and
binary precisely so the permissive subgraph has a root that does not drag in the FSL engine —
`lx-cli` (FSL) simply calls it. `xtask arch-check` asserts the subgraph is closed:
**no Tier 1 crate may depend on a Tier 2 crate.**

**Fixture policy.** Real repositories are referenced by URL + commit and fetched by
`xtask corpus sync`; never vendored. Every fixture carries a license note. Benchmark corpora record
the model ID used, because results are meaningless without it.

**Test naming.** Every test that encodes one of the **fourteen** laws is named `law_<n>_<what>` so a
reviewer can grep the laws and see them enforced. The two newest are the easiest to forget and the
most embarrassing to get wrong:

- `law_13_stated_intent_outranks_base_control` — a change that fixes long-standing wrong behavior on
  BASE must not be reported as a `PRESERVE` violation. BASE is our control, not our oracle, and the
  literature we build on assumes otherwise.
- `law_14_capability_gap_is_printed` — for each mechanism, remove its toolchain from the fixture
  environment and assert the receipt contains `capability_unavailable` with a usable detail string,
  rather than a narrower receipt that looks complete.

---

## 10. CI/CD

```
.github/workflows/
├── ci.yml           on every PR:
│                      fmt · clippy -D warnings · cargo test --workspace --all-features
│                      · trybuild · xtask arch-check · xtask schema-check (schema matches types)
│                      · xtask capability-check · lx-conformance · xtask determinism · insta --check
│                      · cargo-deny (licenses, advisories, bans) · typos · docs build
│                      · e2e on ubuntu + macos · criterion budget check (per-profile, §7.3)
│                      · tier-isolation build: `cargo build -p lx-cli --no-default-features
│                        --features read-only` must compile with NO sandbox/runner/llm crates
├── security.yml     daily: cargo-audit / OSV · dependency review · injection corpus
│                      · sandbox escape suite · CodeQL + Semgrep on our own source
├── bench.yml        nightly + on demand: Litmus64-Bench subset; full corpus weekly;
│                      posts FP / detection / calibration deltas to the PR or an issue
├── calibrate.yml    weekly: refit risk weights on the calibration corpus; publish the
│                      reliability curve; FAIL if Brier regresses beyond the budget
├── dogfood.yml      runs `lx check` on this repository's own PRs and commits the receipt
│                      to examples/ — the marketing is the dogfooding
└── release.yml      tag-triggered cargo-dist matrix → signed multi-platform artifacts,
                      SLSA 3 provenance via actions/attest-build-provenance, Homebrew tap,
                      shell installer, crates.io publish, Docker image, Action version bump
```

**Merge requirements:** DCO sign-off · all CI green · one maintainer approval (two for `spec/`,
`lx-verdict/`, `lx-sandbox/`, `lx-llm/`, and `lx-exec/` — which now owns the `ConfirmedEvidence`
constructor and is therefore where the M2 guarantee could be silently deleted) · an RFC link for any change to schema, verdict, risk, or
ledger semantics · CHANGELOG entry · benchmark deltas attached when the change could move FP rate or
detection.

**Release engineering:** SemVer, with the schema versioned independently and documented in
`spec/receipt-v0.1.md`. `cargo-dist` handles the platform matrix (macOS x86_64+aarch64, Linux
glibc+musl, Windows) with signed artifacts and installers — the same pipeline Zed, rustfmt, and
starship use. Every release publishes: binaries, checksums, SLSA provenance, the JSON Schema, the
conformance suite tarball, the fitted policy weights, and `RESULTS.md`.

---

## 11. Observability

`tracing` throughout, one span per stage and per task, exported via `tracing-opentelemetry`.
Span attributes: stage name, cache hit, cost, sandbox tier, model ID, digests. **No source content,
ever, in a span** — asserted by a redaction test.

Field debuggability commands, because a verification tool that can't explain itself is unusable:

```
lx why-slow           per-stage timing waterfall + cache hit/miss + what the planner cut and why
lx explain-egress     exactly which bytes would leave, to which provider, for this run
lx doctor             toolchain, sandbox, plugin, and permission diagnosis with fixes
lx receipt diff A B   what changed between two receipts (obligations gained/lost, risk delta)
lx telemetry show     the precise payload that would be sent, if opted in
```

Telemetry is **off by default**, opt-in, aggregate-only, with the schema published in
`docs/telemetry.md`. One surprise phone-home permanently ends a trust project.

---

## 12. Error handling

`thiserror` for library errors, `miette` for anything a human reads. Every user-facing error carries
a code, the source span when applicable, and a suggested fix:

```
litmus64::exec::no_test_harness

  × cannot run differential execution for OB-2
   ╭─[litmus64.yaml:14:3]
14 │   recipes: { concurrency: { dst: { seeds: 4096 } } }
   ·            ────────┬───────
   ·                    ╰── this recipe needs a runnable test harness
   ╰────
  help: your tests require a live PostgreSQL instance. Add a devcontainer
        service (docs.litmus64.com/harness#db) or set
        recipes.concurrency.differential: false to record this as unverified.
  → OB-2 recorded as unverified (reason: missing_test_harness)
```

Note the last line: **a tool failure still produces an honest receipt entry.** Errors degrade the
receipt; they never fabricate a pass and never silently drop an obligation.

Exit codes are part of the public API and are stable: `0` pass · `10` human review · `11` expert
review · `20` changes requested · `30` blocked · `40` tool error · `41` config error · `42` sandbox
unavailable. "Found a problem" and "crashed" are never conflated — CI depends on that distinction.

---

## 13. Engineering standards

- **Rust edition and toolchain pinned** in `rust-toolchain.toml`; MSRV documented and CI-checked.
- `#![forbid(unsafe_code)]` in every crate except `lx-sandbox` (where each `unsafe` block carries a
  safety comment and a test) — and that exception is documented in `THREATS.md`.
- `clippy::pedantic` on, with allow-lists justified inline.
- **No `unwrap`/`expect` outside tests and `main`**, enforced by clippy.
- All public items documented; `#![warn(missing_docs)]`; `cargo doc` builds clean in CI.
- Dependencies: pinned in `[workspace.dependencies]`, license-checked by `cargo-deny`, and each new
  dependency needs a one-line justification in the PR. Prefer boring and maintained.
- **Errors before features.** A new evidence kind is not done until it has a `Skipped` path, a
  replay recipe, and a snapshot test.
- **Definition of done** for any change to the pipeline: unit + property tests · snapshot updated ·
  conformance case if the schema moved · determinism test passes · benchmark delta reported ·
  docs updated · CHANGELOG entry · law tests still green.
- **ADRs** in `docs/adr/` for architecture decisions. Seed set: 0001 Rust · 0002 in-toto predicate ·
  0003 *superseded by 0012* · 0004 Cedar over OPA · 0005 salsa-style incrementality · 0006 CaMeL
  dual-LLM · 0007 sandbox tiering · 0008 ledger on disk in the user's repo · 0009 DCO over CLA ·
  0010 Apache-2.0 + CC-BY spec split · **0011 Rust as a 1.0 plugin** · **0012 subprocess plugin ABI,
  WASM post-1.0** (supersedes 0003) · **0013 staged release by write-access** · **0014 `v0.1`
  predicate until a second implementation exists**.
  ADRs 0011–0013 are the three decisions a future contributor is most likely to try to reverse
  without knowing why they were made, so each states its rejected alternative and the evidence that
  decided it. `DECISIONS.md` is the readable summary.

---

## 14. Getting started as a contributor

```bash
git clone https://github.com/prabhu-gopal/litmus64 && cd litmus64
make dev                    # devcontainer: rust toolchain, tree-sitter grammars, python/node
                            # fixtures, sandbox check — one command, no README archaeology
cargo xtask check           # everything CI runs, locally, in the same order
cargo run -p lx-cli -- demo                    # see the whole thing work, offline, in 5s
cargo run -p lx-cli -- check --base HEAD~1     # a receipt for your own last commit

cargo xtask schema-gen      # regenerate spec/receipt-v0.1.schema.json + plugin schema from types
cargo xtask conformance     # run the spec conformance suite
cargo xtask determinism     # prove receipts are byte-identical across runs
cargo xtask capability-check# assert the published capability matrix matches reality
cargo xtask bench --subset smoke
cargo xtask new-plugin my-lang     # scaffold a plugin from plugins/template (any language)
```

**Start with `lx demo` and read the receipt it prints.** The receipt is the product; every other
surface in this repository is a pure projection of it, so the fastest way to understand the codebase
is to read one artifact and then find the code that produced each of its fields.

**Where to start, by interest:** renderers and docs (`lx-render`, `docs/`) · a new language plugin
(`plugins/template` — the highest-leverage contribution) · benchmark corpus cases
(`bench/corpora/` — "here is a PR where Litmus64 was wrong" is the single most valuable PR anyone can
send) · obligation inference (`lx-oblig`, `lx-invariant`) · the hard core (`lx-sandbox`,
`lx-attack` DST, `lx-verdict` calibration).
