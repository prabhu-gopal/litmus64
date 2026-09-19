# Non-goals

Said loudly, because a project that cannot say no becomes a project that cannot ship. Each of these
is a deliberate decision, not an unfinished feature, and asking for one is not a bug report.

## We are not

- **A code reviewer.** We emit verifiable artifacts about experiments, not natural language about
  code. If you want opinions on style, use one of the many good tools that provide them.
- **A replacement for CI.** We consume CI. A merge queue is a driver; we are the check it requires.
- **A proof system.** "Evidence, not proof" is in paragraph one of the README and it is literal.
- **A hosted service at 1.0.** Local-first, zero-egress-capable, runs in your own CI.
- **A developer scorecard.** We never score people. Receipts describe changes, not authors. This one
  is permanent and non-negotiable.
- **A live, in-IDE code simulator.** We do not compile, execute, or judge a snippet before it is
  shown to you. Judging code in the moment it is generated is necessarily opinion-shaped — the exact
  thing "not a code reviewer" already rules out. The problem this was meant to solve (architectural
  anti-patterns that compile and pass tests) is handled instead by declared, measurable fitness
  obligations checked in the same batch/CI model as everything else (`DECISIONS.md` D7).
- **A feature-flag or deployment orchestrator.** Wrapping AI-generated functions in flags and gating
  their promotion is a mature, well-funded market (LaunchDarkly, Statsig, GrowthBook). We stay a
  receipt producer; the correct integration, if it ships, is a signed receipt an existing flag
  platform can require before promoting out of staging — not a rollout mechanism of our own
  (`DECISIONS.md` D7).

## We do not verify

- **Visual or UI correctness.** No screenshot diffing, no layout assertions.
- **ML training code.** Nondeterministic by design, and the obligation model does not fit.
- **Whole programs, formally.** Bounded model checking is scoped to changed functions. Whole-program
  verification is intractable, and Dafny/Verus rewrites are not adoptable.
- **Distributed behavior beyond the DST model.** We say so in the receipt rather than guessing.
- **Performance claims, strongly.** We report benchmark deltas with confidence intervals and call the
  correctness high-confidence and the perf claim medium.

## We do not support

- **Non-Git version control.**
- **Repositories with no test harness**, beyond the read-only tier — which still gives you structural
  obligations, contract diffs, blast radius, and an honest `unverified` block. Honest partial value.

## Post-1.0, tracked but not now

WASM as a second plugin transport · additional languages · cross-service contract verification · org
receipt-graph analytics · GitLab/Bitbucket/Buildkite/Jenkins · IDE receipt viewer · federated ledgers
· shared remote cache.
