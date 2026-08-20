# Revert-mining pipeline

Walks a repository's history for PRs that were later reverted, or followed by a "fix the fix" commit,
and emits labelled `(change, outcome)` pairs.

This produces the **calibration corpus**, which gates the empirical risk model: risk weights are *fit*
on real outcomes, not guessed, and the reliability curve and Brier score are published per release. A
risk number nobody validated is astrology.

**Stand this up early.** It takes real calendar time to accumulate, and it blocks the calibration
work, the evaluation gates, and the launch essay. It is the one task where starting late cannot be
recovered by working harder.

The mining pipeline is public. The *aggregated cross-org corpus* is the commercial tier — that
boundary is stated in `GOVERNANCE.md` and does not move.
