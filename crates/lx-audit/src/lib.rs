//! SPDX-License-Identifier: FSL-1.1-ALv2
//!
//! Retroactive receipts over git history; verification-debt reporting (ADR-0016).
//!
//! **Tier T1.** This is the front door. It replays the last N commits through the
//! read-only tier — no sandbox, no test harness, no API key — and reports what was
//! never verified. Because it never obtains a `ConfirmedEvidence`, it **cannot**
//! emit a violation, so the first command a new user runs has zero false-positive
//! surface by construction.
//!
//! Shares the BASE/HEAD history walk with `bench/mining` (the revert-mining
//! pipeline): same reconstruction, pointed at the user's repository instead of a
//! corpus.
//!
//! Two rules that are easy to violate and expensive to get wrong:
//!
//! 1. **Report what was sampled.** `--max-commits` defaults to 200. A silently
//!    truncated audit breaks Law 6 exactly as badly as a silently skipped stage,
//!    and it is the obvious corner to cut. See `docs/laws.md`.
//! 2. **"Agent-authored" is a claim, not a fact.** It is inferred from commit
//!    trailers, co-author lines, and PR metadata. Report it with its basis shown —
//!    the receipt already treats `authoring_agent` as `trust: unverified_claim`.
//!
//! See `CODEBASE.md` §2 for the dependency laws that constrain this crate, and
//! `docs/cli.md` for the command surface.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

// TODO: implement.
