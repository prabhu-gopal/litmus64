# Known limitations

Written before the first release, while we are still honest and unattached. Being visibly harder on
ourselves than our critics are is the entire brand.

## Mechanisms that do not exist in your language

Verified, not estimated. `lx capabilities` prints the resolved matrix for your install; every receipt
carries the capability set that produced it; a missing mechanism appears as `unverified` with
`reason: capability_unavailable`.

| Mechanism | Available | Missing because |
|---|---|---|
| `schedule_search` | Rust (loom, shuttle); JVM post-1.0 (Fray) | Python, TypeScript, and Go have no systematic scheduler. Python's `blanket` replays one hand-written interleaving; Go has no loom equivalent |
| Bounded model checking | Rust (Kani); C/C++ (CBMC) | Nothing comparable exists elsewhere |
| Invariant mining | Python first (PEP 669); TS and Go planned | Daikon has front ends only for Java/C/C++/C#/Eiffel/Perl, so we build our own trace adapters per language |

Python, TypeScript, and Go get `schedule_replay` instead of `schedule_search`: we can reproduce a
race deterministically from a recorded schedule, but **we cannot claim to have searched the space.**
Those are separate evidence kinds precisely so the weaker one can never masquerade as the stronger.

## Change classes we handle badly

- **`config`** — infra, CI, and env changes get policy evaluation and blast radius only. Confidence is
  low and the receipt says so.
- **Generated code** where we cannot reproduce the generator input.
- **Perf regressions** — benchmark deltas with intervals, not a verdict.
- **Migrations without a rollback harness** — recorded as explicitly `unverified`, never assumed safe.

## Structural assumptions we make

- **BASE is a control, not an oracle.** Law 13 exists because the literature we build on assumes the
  base version is correct and we decline to: a `CHANGE`-class intent that contradicts a `PRESERVE`
  resolves in favour of the stated intent. But we can still be wrong about which is which, and when
  we are, a correct change gets routed to review it did not need.
- **Diff-scoped by default.** A defect whose cause lies outside the blast radius is reported as an
  observation, never as a violation of this change — which means we can miss it entirely.
- **Obligation inference from natural language is ~0.62 precision** in the published literature. Two
  of our three sources need no model at all, which raises the floor, and low-confidence inferences
  route to `unverified` rather than asserting. It is still the hardest unsolved part of the system.

## Operational limits

- **Repos with no usable tests** — the long tail, and it is most repositories. You get the read-only
  tier and a large, honest `unverified` block.
- **Tests requiring live infrastructure** — differential execution is unavailable until a devcontainer
  service exists. `lx init --fix-devcontainer` will write one; if it cannot, it says so.
- **Flake floor.** ~25% of large-scale CI failures are flakes. We measure and label rather than blame,
  but a test that is flaky on BASE is excluded from attribution entirely, so it cannot support any
  conclusion at all.

## Send us the ones we missed

"Here is a PR where Litmus64 was wrong" is the single most valuable contribution anyone can make, and
`bench/corpora/` is where it lands. Our false positives are a corpus, not an embarrassment.
