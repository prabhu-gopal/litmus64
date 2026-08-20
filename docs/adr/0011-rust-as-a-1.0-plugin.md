# ADR-0011 — Rust is a 1.0 plugin

**Status:** accepted · **Supersedes:** the original 1.0 plugin set (Python, TypeScript, Go, OpenAPI, SQL, Semgrep)

## Context

Three of the nine mechanisms depend on language tooling that was verified, not assumed:

- `schedule_search` (M5): loom, shuttle, madsim, turmoil are **Rust-only**; Fray is JVM-only;
  Python's `blanket` replays one hand-written interleaving; Go has no equivalent.
- Bounded model checking (M4, rung d): Kani is **Rust**, CBMC is **C/C++**.
- Dynamic invariant mining (M3, empirical): Daikon's front ends are Java, C/C++, C#, Eiffel, Perl —
  **none for Python, TypeScript, or Go**.

The original 1.0 plugin set was Python, TypeScript, Go, OpenAPI, SQL, Semgrep. All three mechanisms
had **zero coverage** across it, while the golden receipt and terminal mock both showed
`dst/asyncio-scheduler, 118,402 interleavings` on a Python repository.

## Decision

Ship `lx-rust` at 1.0. Split M5 into `schedule_search` and `schedule_replay` as distinct evidence
kinds. Make the capability matrix (M9) a published, probed, per-receipt artifact.

## Consequences

**Good.** The full escalation ladder exists somewhere real at 1.0, for roughly the cost of one
plugin, in the language the engine is already written in. Our own repository becomes the flagship
dogfood, so the demo is a re-verifiable receipt rather than a screenshot. `cargo-mutants` and
`proptest` come along for free.

**Bad.** One more plugin to maintain. A capability story that takes longer to explain than "it
works" — which we accept, because publishing a matrix of your own gaps requires having no revenue
riding on the gaps being invisible.

## Rejected

- **Ship uniformly, let users discover the gaps.** What everyone in the category does, and the exact
  failure mode this project exists to oppose. Discoverable in an afternoon by a motivated critic.
- **Delay 1.0 until Python has a systematic scheduler.** No viable substrate exists; this makes our
  release date depend on somebody else's research.
