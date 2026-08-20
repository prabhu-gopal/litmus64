# Litmus64 — Structural decisions

Companion to [`CODEBASE.md`](CODEBASE.md) and [`docs/laws.md`](docs/laws.md). Those describe the system
as it is now. **This file records the decisions that shaped it, the evidence that forced them, and
what was rejected** — so nobody has to reverse-engineer intent from code, and so anyone proposing a
reversal has to engage with the reason rather than the outcome.

Full ADRs live in `docs/adr/`. This is the readable summary.

---

## The six decisions of revision 2

Revision 1 of the plan was strategically sound — the in-toto/DSSE choice, the discrimination filter
(M1), the differential attribution law (M2), the required `unverified[]` field, and the free
Apache-2.0 verifier all survive untouched. Three things did not survive review, all of them the same
mistake in different clothing: **a claim stated uniformly that is only true conditionally.**

---

### D1 — Rust is a 1.0 plugin, and the marquee examples are Rust

**ADR-0011.** Supersedes the original 1.0 plugin set of Python, TypeScript, Go, OpenAPI, SQL,
Semgrep.

**The evidence.** Three of the nine mechanisms depend on language tooling that does not exist for
most languages, and this was verified rather than assumed:

| Mechanism | Substrate | Reality |
|---|---|---|
| M5 `schedule_search` | loom, shuttle, madsim, turmoil | **Rust-only.** Fray is JVM-only. Python's `blanket` replays *one* hand-written interleaving. Go has no equivalent |
| M4 BMC rung | Kani, CBMC | **Rust** and **C/C++** only |
| M3 empirical (invariant mining) | Daikon front ends | Chicory (Java), Kvasir (C/C++), C#/Eiffel/Perl. **No Python, no TypeScript, no Go** |

Every one of those has **zero coverage** across revision 1's plugin set. Meanwhile the golden receipt
and the terminal mock both showed `dst/asyncio-scheduler, 118,402 interleavings` on a *Python*
repository — a screenshot the shipping product could not have produced.

For a project whose first README paragraph is an honesty clause, shipping an unproducible flagship
demo was the single most dangerous thing in the plan. It would not have been caught by a user; it
would have been caught by a critic.

**The decision, in three parts.**

1. **`lx-rust` ships at 1.0.** The engine is written in Rust, so this hands us loom, shuttle,
   cargo-mutants, *and* Kani — the complete escalation ladder — for approximately the cost of writing
   one plugin. Our own repository becomes the flagship dogfood, so the demo is a receipt anyone can
   re-verify rather than a screenshot they have to trust.
2. **M5 splits into two honestly-named levels.** `schedule_search` (explore the interleaving space)
   and `schedule_replay` (reproduce a recorded schedule deterministically) are **separate
   `EvidenceKind` variants**, not one variant with a confidence score. Python/TS/Go get
   `schedule_replay`, which is genuinely valuable — it converts *"it failed once in CI and never
   again"* into `lx replay EV-7 --seed 8412331` — and is never allowed to look like the stronger claim.
3. **M9, the capability matrix, becomes a mechanism in its own right.** `lx capabilities` prints what
   this install can actually do, every receipt carries the capability set that produced it, and a
   missing mechanism is `unverified` with `reason: capability_unavailable` — never a silently
   narrower receipt.

**Rejected: ship uniformly and let users discover the gaps.** This is what every tool in the category
does. It is also the exact failure mode we exist to oppose, and the gaps are discoverable in an
afternoon by anyone motivated to embarrass us.

**Rejected: delay 1.0 until Python has a systematic scheduler.** No viable substrate exists. This
would have made the release date depend on someone else's research.

**Cost we accept.** One more plugin to maintain, and a capability story that is more complicated to
explain than "it works." The second one is a feature: publishing a matrix of your own gaps is a move
that requires having no revenue riding on the gaps being invisible.

---

### D2 — The plugin ABI is subprocess JSON-over-stdio; WASM is a post-1.0 second transport

**ADR-0012**, superseding ADR-0003.

**The evidence.** Revision 1 made WASM components (WASI 0.2, wasmtime) the primary plugin ABI, with
a subprocess ABI as "the escape hatch for tools that must drive Docker or native runners," and
justified it with: *a third-party plugin cannot exfiltrate your source even if malicious — that is
what makes it safe to open the ecosystem wide.*

**A WASI 0.2 component cannot run `pytest`, `vitest`, `go test`, or `cargo test`.** So `lx-rust`,
`lx-python`, `lx-typescript`, and `lx-go` — which produce essentially all of our evidence — would
every one of them have taken the escape hatch. The isolation boundary used to justify opening the
ecosystem would have protected only the plugins that never execute code, while wasmtime, WIT, and the
Component Model remained a permanent audit surface and a learning curve sitting in front of our
single highest-leverage contribution path.

**The decision.**

- **The contract is transport-neutral** — `spec/plugin-v0.1.schema.json`, generated from the same Rust
  types as the receipt, so it cannot drift.
- **At 1.0 there is one transport: subprocess, JSON over stdio.** The entire contract is "read JSON on
  stdin, write JSON on stdout, exit 0," with three subcommands: `capabilities`, `plan`, `run`.
- **Isolation is the sandbox**, which already has the strictly harder job of containing the untrusted
  *diff*. A plugin inherits the trust tier of the run it executes inside and can never obtain a
  weaker one — enforced by `xtask arch-check` forbidding `std::process` outside `lx-sandbox`.
- **WASM returns post-1.0** as a second transport for pure-analysis plugins, where sub-5ms in-process
  invocation is a genuine win. Because the contract is transport-neutral, it lands without breaking a
  single existing plugin.

**Rejected: WASM-first with a subprocess fallback** (revision 1). The security claim does not hold for
the plugins that matter, and a security claim that holds only in the cases you do not ship is worse
than no claim, because it produces false confidence.

**Rejected: both transports at 1.0.** Two boundaries means two audit surfaces and twice the
opportunity for a sandbox-escape CVE, in exchange for latency we do not yet need.

**What this buys.** One security boundary, audited once. One fewer heavy dependency. And a plugin
contract that someone can implement in an afternoon in any language — which matters because plugins
are the highest-leverage contribution surface in the project, and "learn the Component Model" is a
filter, not a funnel.

**Cost we accept.** Higher per-invocation overhead (process spawn vs. in-process call), which is
irrelevant at the granularity we invoke plugins — once per task, not once per function.

---

### D3 — Releases are staged by write-access, not by maturity

**ADR-0013.** Replaces "there is no MVP; 1.0 is the first public release."

**The evidence.** Half the original stance was right and is kept verbatim: **no release of ours ever
leaks noise into somebody's pull requests.** A tool whose entire value proposition is trust cannot
earn trust with a prototype.

Applied to the whole engine, though, it had a cost that would have killed the project. Counting what
had to land before *any* public artifact: semantic AST diff for four languages, SCIP integration, a
salsa-shaped incremental engine, a content-addressed cache, four sandbox tiers including Firecracker,
a determinism harness, an invariant miner built from scratch (D1), the obligation engine, the
discrimination filter, a paired runner with flake statistics, mutation orchestration for four
ecosystems, DST, BMC, the dual-LLM layer, triage, risk fitting, Sigstore/DSSE/in-toto, the ledger
with its full lifecycle, seven plugins, a GitHub App plus Action plus `gh` extension plus MCP server
plus four agent hooks, six renderers, a benchmark harness with six corpora and a revert-mining
pipeline, a docs site, and a conformance suite.

That is years, and it means **years of zero external signal on the one component that cannot be
verified internally: whether the obligations we derive are actually useful to a human being.**
Solo-maintainer burnout is the most common actual cause of death for a project this size, and a
multi-year unpublished build is precisely how that happens. The original plan even contained the
antidote and mislabelled it: it called for validating the falsification loop on 30 real PRs, but
specified "*not a public milestone*." It should be one."

**The decision.** Stage on write-access. Each tier is production-grade *at what it claims*, ships
publicly, and is honest about the tier above it.

| Tier | Ships | Write-access requested | Why it is safe |
|---|---|---|---|
| **T0 · The standard** | `spec/`, JSON Schema, conformance suite, `lx verify`, predicate registration | **none** | A document and a validator. Weeks of work, and it is the only durable moat |
| **T1 · Look** | `lx check --read-only`, `lx demo`, `lx init`, `lx capabilities`, renderers, MCP reads | reads code, writes nothing | **Cannot emit `violated` at all** — it never obtains a `ConfirmedEvidence`. Zero false-positive surface, by construction |
| **T2 · Run** | sandbox, paired runner, discrimination, attribution, `lx-rust` + `lx-python`, signing, GitHub App | executes tests in a sandbox | First tier that can say `violated`, and only with a BASE control. Gated on FP ≤ 0.05 **and** precision ≥ 0.85 |
| **T3 · Attack & compound** | mutation, property, schedule search/replay, BMC, triage, ledger, discharge, calibration | may gate merges | Needs the calibration corpus, which needs T2 receipts to exist |

**The promise is now kept structurally rather than by delay.** T1 cannot produce a false accusation
because the type that authorises an accusation is unreachable from it. That is a stronger guarantee
than "we waited until it was good."

**Rejected: single all-at-once 1.0** (revision 1). Maximises time-to-feedback on the riskiest
unknown and maximises burnout risk, in exchange for a launch-day narrative.

**Rejected: a conventional beta.** A beta that emits low-confidence violations into real pull
requests is exactly the noise that kills tools in this category. The read-only tier is not a beta —
it is a complete product with a narrow, honestly-stated scope.

**Sequencing note.** T0 ships **first and alone**. If the format is the moat, every month it exists
unopposed compounds, and it costs weeks rather than years. AgentPlane already publishes an
MIT-licensed Agent Change Record schema; the answer to a competing format is not a better license but
a better institution — a conformance suite, an independently runnable verifier, and a registered
in-toto predicate, none of which a bare JSON schema has.

---

### D4 — One binary, every ecosystem's native install command

**ADR-0015.**

**The question, asked plainly:** most of our users write Python. The engine is Rust. Does that hurt
them?

**No — it is the single best thing we can do for them, and the evidence is not close.** The most
widely adopted Python tooling of the last five years is written in Rust and its users neither know nor
care: **uv** does **75 million monthly PyPI downloads** (April 2026), past Poetry and becoming the CI
default; **ruff** replaced flake8, isort, and Black with one binary. They won *because* of what Rust
buys — a single static binary, no runtime to install, no dependency resolution, 10–100× the speed —
and `pip install ruff` works because a prebuilt wheel ships per platform. Nobody compiles anything.

For this tool an interpreted implementation would be **disqualifying**, not merely slower: a Python
verifier installs into the environment it analyses and competes for dependency versions with the code
under test, which breaks isolated paired BASE/HEAD execution at the concept level. It also could not
be the sandbox, and byte-identical receipts would become a fight against hash randomisation and GC
timing rather than a release gate we simply meet.

**Decision:** one binary, published to every ecosystem's native channel — `curl | sh` (primary,
auto-updating), Homebrew, `uv tool install` / `pip` (platform wheels via maturin), `npm` (binary shim),
`cargo`, and a container image. Same executable everywhere, so a receipt from the `pip` install is
byte-identical to one from `brew`. **The user never learns a new package manager and never learns the
tool is written in Rust.**

**Cost we accept:** six release channels to keep reliable, with an install-and-run smoke test on every
one before a release is marked latest. A lagging channel is worse than an absent one.

**Rejected:** writing the engine in Python to match the audience (fails on all four points above, and
uv/ruff prove the audience does not care) · `cargo install` only (restricts the tool to people who
already have a Rust toolchain, which is almost none of our users) · per-language reimplementations
(multiple implementations of the verdict function would destroy receipt comparability — language
support belongs in plugins).

---

### D5 — `lx audit` is the front door; per-change verification is the product

**ADR-0016.**

**The gap, found by describing the product as a user rather than as its author:** *"install it, audit
my codebase, get the report, fix the issues."* The design offered none of that. It offered diff-scoped
per-change verification, with `audit` demoted to a scheduled job — so a new user pointing the tool at a
repository with a year of agent-authored commits in it got **nothing**, because there was no change to
verify. That is the gap at precisely the moment someone decides whether the tool is worth their time.

**But the naive reading is a trap.** "Scan my codebase and list what's wrong" is the most crowded
category in the market (SlopCop, Sherlock Forensics, CodeRabbit, Sonar, Greptile), and they all do it
by **static pattern matching** — the exact technique that loses to a defect profile that is
*semantically wrong but syntactically plausible*. Building a better pattern matcher means competing
where we have no advantage, on defects our differentiator cannot see.

**Decision: keep our mechanism, change the unit of work.** `lx audit` replays the last N commits
through the **real engine** at the read-only tier — no sandbox, no harness, no API key, and unable to
produce a false accusation by construction. Output is a **verification-debt ledger**: critical-surface
changes with no evidence, `unstated_changes`, contract drift with no version bump, migrations with no
tested rollback. Plus a single self-contained HTML report a human can open and forward.

Three reasons this is the right front door: it answers the question users actually ask ("what did the
AI do that nobody checked?"); it costs nothing to try; and it reuses machinery already required — the
revert-mining pipeline already walks history reconstructing BASE/HEAD pairs for the calibration corpus,
so this is that walk pointed at the user's repo.

And it **converts**: the audit ends by naming the debt and offering the two things that stop it
accumulating — `lx check` on every push, and `--write-tests` to discharge the backlog. Audit is the
wedge, per-change verification is the product, the ledger (M6) is the retention.

**`--write-tests` is the honest reading of "fix the issues."** We never edit the code we verify —
independence is the asset, and that boundary is permanent. But the discrimination filter already
generates artifacts that distinguish BASE from HEAD, and the survivors are exactly the tests that
should have existed. They get committed as plain files that **run without Litmus64 installed.**

**Cost we accept:** history replay is unbounded, so it needs hard defaults (`--max-commits 200`,
`--since`) and must report what it sampled — a silently truncated audit breaks Law 6 as badly as a
silently skipped stage. "Agent-authored" detection is heuristic (trailers, co-author lines, PR
metadata) and is reported as a claim with its basis shown, never as a fact.

**Rejected:** a whole-codebase static score ("your repo is 62% slop") — crowded, undifferentiated, and
a number with no falsification behind it is the astrology we criticise elsewhere · security scanning as
a headline — we consume Semgrep and CodeQL as evidence sources, but security-shaped analysis is a
solved, crowded space and correctness is ours · auto-fixing code — permanently out of scope.

---

### D6 — Positioning is "the receipt," and enterprise readiness moves to T0

**ADR-0017.**

**The gap:** the documentation could describe nine mechanisms and an eleven-stage pipeline, but could
not answer *"what is this, in one sentence, for someone who vibe-codes?"* A product that cannot be
explained in one sentence does not get adopted however good it is — and the sentence has to survive
being repeated by someone who does not work here.

**The positioning, decided:** the differentiator is **the part of the receipt that says "I don't
know."** `unverified[]` is a *required* schema field, so a report claiming total coverage is rejected as
malformed by our own validator. That is not a feature a competitor can ship next quarter, because it
is not a feature — it is a business decision. Publishing what you failed to check requires having no
revenue riding on the gaps being invisible.

Two research findings anchor the pitch, and the first is the sharpest statement of the problem available
anywhere: **96% of developers don't fully trust AI-generated code, and only 48% always review it.**
They don't trust it *and* they don't read it. No faster reviewer fixes that. Paired with **PRs merged
without review +31.3%**, the lead framing is **"the gate is disappearing"** — because *review is slow*
invites "build a faster reviewer" (the commoditized category), while *nobody is checking and incidents
tripled* invites "build evidence," which is us.

The analogy is a **home inspection**, chosen because it carries the differentiator for free: a good
inspector's report says *"could not access the roof — you still don't know about the roof,"* and that
line is why you hired them. Public explanation and per-audience one-liners live in `docs/why.md` so the
message does not drift as other people repeat it.

**Enterprise readiness moves to T0** — cheap now, expensive to retrofit, and several items are gates on
being taken seriously at all: OpenSSF Scorecard published and tracked as a regression · SBOM in
**both** CycloneDX and SPDX, signed and attached to every artifact (previously we only *consumed* these
formats) · SLSA Build L3 provenance · a published vulnerability-response SLA rather than just an address
· `docs/enterprise.md` as one procurement-facing page, including the questions we cannot dodge.

**And we decline the easy compliance pitch.** Research produced a finding that argues against our own
sales angle, and we take it: **the EU AI Act does not generally make AI-assisted coding high-risk** —
Annex III covers specific use cases, not developer assistance. Vendors implying otherwise are
overclaiming. Our honest positions: if the software *you ship* is high-risk, receipts are strong
traceability evidence where "an agent wrote it and a human clicked merge" is weak; the **Cyber
Resilience Act** is more directly relevant for most teams; a receipt is **SOC 2 CC8.1** change-management
evidence, though the open-source project carries no SOC 2 report because there is no service to audit.
**We will never claim Litmus64 makes anyone compliant with anything.** It produces evidence; an auditor
decides what it is worth.

Saying that unprompted is worth more than the claim we are declining to make. If one compliance claim
fails counsel's reading, every other claim on the page gets re-examined — and our other claims are true.

**Cost we accept:** T0 grew by several CI days, and we give up a talking point that would have generated
near-term interest.

**Rejected:** leading with compliance (breaks the first time a lawyer reads Annex III) · leading with
"AI code review, but better" (commoditized category, invites recall comparisons against tools optimising
for something else) · a security-scanning headline (crowded and solved; correctness is ours) · waiting on
Scorecard and SBOM until an enterprise asks (by then it is a blocker in someone's procurement cycle).

---

## Smaller corrections made in the same revision

| # | Was | Now | Why |
|---|---|---|---|
| C1 | `p95 < 5 min`, `< $0.25`, one profile | Three profiles: `check` ≤ 60 s/$0, `--deep` ≤ 20 min/$0.50, `audit` ≤ 90 min | PatchGuru reports **8.9 min** for a strict *subset* of our pipeline, and M2 multiplies every execution by 2 sides × N reps. The old budget was below the median of a subset of the work. Arithmetic now published in `spec/budgets.md` |
| C2 | One FP metric (`≤ 0.05`) | Per-change FP ≤ 0.05 **and** finding-level precision ≥ 0.85 | Different denominators. By the per-change measure, PatchGuru's published results are *already inside* our gate (~15 FP warnings / 400 PRs ≈ 3.75%), so one number would have let us claim an advance we had not made |
| C3 | `predicate/v1` at launch | `predicate/v0.1` until a second implementation passes conformance | §6.7 requires two implementations before stability, and a predicate URI is immutable in signed history forever. `v1` is earned |
| C4 | Golden receipt showed `bmc: skipped` with no `unverified` entry | Every non-`ok` stage has a matching entry; `lx verify` rejects receipts where it does not | Our own flagship example violated Law 6. The conformance corpus would have been seeded from it |
| C5 | `Attribution::NotAttributed` "may never support a Violated status" — a comment | `ConfirmedEvidence`, mintable only inside `lx-exec` | The doc claimed "Law 2, in the type system" while the code checked at runtime. Now deleting the guarantee requires deleting a type |
| C6 | Ledger failure ⇒ `violated` | `LEDGER_CONFLICT` + `lx ledger supersede` | The dominant failure mode is a *correct* change invalidating a locked-in invariant. Treating that as a violation is how the strongest feature becomes the reason `.litmus64/ledger/` gets deleted |
| C7 | "64-byte digest that anchors every receipt" | "the **64 hexadecimal characters** of the SHA-256 digest" | SHA-256 is 32 bytes and 64 hex chars. The `Digest` type said 32; the naming story said 64 bytes. Being wrong about a hash length in a receipt project is not survivable |
| C8 | §2 led with review-time increases | §2 leads with incidents tripling and **PRs merged without review +31.3%** | "Review takes longer" invites *build a faster reviewer* — the commoditized category. "The gate is disappearing and incidents tripled" invites *build evidence*, which is us |
| C9 | Metrics measured only correctness | Added `review_focus` precision@3 and a published human time-to-locate study | §2 states the problem in hours per week; nothing measured hours. A tool can be perfectly calibrated and still help nobody |
| C10 | 12 laws | 14 laws — added **stated intent outranks the control** and **a capability we lack is a gap we print** | The literature assumes BASE is correct; we decline to inherit that, because "the change that fixes a long-standing bug gets blocked" is the most infuriating possible false positive |
| C11 | `litmus64-policy` / `lx-policy` used interchangeably | `lx-policy` throughout | Two names for one crate in the founding document is how a codebase starts drifting |
| C12 | Law 9 cross-referenced §11 | §9.1 | Wrong pointer |

---

## Standing promises these decisions must not break

Any future decision that contradicts one of these needs an RFC and a very good reason:

- Verification is **never** paywalled and never crippled. The spec, schema, conformance suite, and
  receipt verifier stay Apache-2.0 / CC-BY-4.0, forever.
- The spec tier never becomes less permissive. FSL conversion dates are never extended. No CLA is
  ever added.
- No telemetry without opt-in.
- Benchmark and calibration results are published **including** the unflattering ones.
- The verdict function never gains a dependency on model output.
- `unverified[]` stays a required field. A receipt claiming total coverage is malformed.
- The tool never claims a capability it does not have.
