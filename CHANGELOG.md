# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: SemVer, with the
receipt schema versioned independently in `spec/receipt-v0.1.md`.

## [Unreleased]

### Added
- Workspace scaffolding: 27 crates across four release tiers (`DECISIONS.md` D3).
- `lx-verify` — the free, independent receipt verifier as a closed Apache-2.0 dependency subgraph.
- `lx-capability` — probes toolchains and produces the M9 capability matrix.
- `lx-rust` plugin (ADR-0011): the only 1.0 language with the full escalation ladder.
- `LEDGER_CONFLICT` obligation status and `lx ledger supersede` (M6).
- `ConfirmedEvidence` — the M2 guarantee as a type rather than a runtime check.
- `DECISIONS.md`, ADR-0011/0012/0013, `LICENSING.md`, `THREATS.md`, `NON-GOALS.md`,
  `KNOWN-LIMITATIONS.md`.

- `lx-audit` — retroactive receipts over git history; the front door (ADR-0016).
- `packaging/` — one binary published to six ecosystem channels (ADR-0015).
- `docs/cli.md`, `docs/laws.md` — tracked, public-safe extractions.
- `TEST_SURFACE_MODIFIED` obligation kind and a `test_surface` receipt block — the test/fixture/harness
  tree is hashed before and after the agent runs, and any change needs `ConfirmedEvidence` from the
  paired BASE run (ADR-0020). Planned for the `v0.2` schema as a forward-compatible field addition.
- `STRUCTURAL` obligation family — architecture fitness rules declared per repo in `fitness.toml`
  (cycles, layering, API-surface churn, coupling delta). Undeclared repos get
  `unverified: unformalizable` (ADR-0020).
- `DECISIONS.md` D7 and ADR-0020.

### Changed
- Plugin ABI is subprocess JSON-over-stdio; WASM demoted to a post-1.0 transport (ADR-0012).
- Three execution profiles with separately derived budgets, replacing one unachievable target.
- Predicate type is `receipt/v0.1`; `v1` is earned by a second implementation.
- Two false-positive metrics (per-change and per-finding) with normative denominators.
- `lx audit` promoted from a scheduled job to the primary onboarding surface; the scheduled
  whole-repo run is now `lx audit --deep`.
- `lx-verify` is a library first and a binary second, so the verifier can be embedded by anyone
  without linking Fair Source code.
