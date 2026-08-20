//! SPDX-License-Identifier: Apache-2.0
//!
//! The free, independent receipt verifier. Apache-2.0 subgraph root.
//!
//! **Tier T0.** This crate is a **library first** and a binary second, deliberately:
//! anyone — including a competitor — must be able to embed receipt verification
//! without our permission and without linking any Fair Source code. If verifying a
//! receipt required our permission, the receipt would be worthless.
//!
//! Its entire dependency subgraph is Apache-2.0 (`lx-types`, `lx-receipt`,
//! `lx-verdict`, `lx-sign`), and `xtask arch-check` asserts that no Tier 1 crate
//! depends on a Tier 2 crate. See `LICENSING.md`, which is normative.
//!
//! The load-bearing property: verification **recomputes** the verdict from the
//! evidence rather than trusting the value stated in the receipt. A receipt whose
//! stated verdict disagrees with its own evidence is invalid. That is what makes a
//! receipt checkable by someone who does not trust its producer — the trust anchor
//! of the entire project.

#![forbid(unsafe_code)]
#![warn(missing_docs)]

// TODO: implement.
//
// pub fn verify(receipt: &[u8], opts: &VerifyOptions) -> Result<Report, VerifyError>;
//
// The report distinguishes, and must never conflate:
//   - signature valid / invalid / absent
//   - stated verdict == recomputed verdict
//   - Law 5: `unverified[]` present (absent ⇒ malformed, not merely suspicious)
//   - Law 6: every non-ok stage has a matching `unverified[]` entry
//   - execution mode: CI-signed vs locally self-signed (receipt laundering, THREATS.md)
//   - amendment chain validity, and the CURRENT risk after discharges
