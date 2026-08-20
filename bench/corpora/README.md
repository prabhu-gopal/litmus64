# Benchmark corpora

Real repositories are referenced **by URL + commit** and fetched with `cargo xtask corpus sync`.
Nothing third-party is ever vendored. Every fixture carries a license note, and every result records
the model ID used — benchmark numbers without a model ID are meaningless.

Subdirectories are created as their first case lands.

| Corpus | What it is | What it measures |
|---|---|---|
| `revert-mined/` | PRs later reverted, or followed by a "fix the fix" commit | **The unfair advantage.** Real bad changes with real labels, and it doubles as the calibration corpus. Nobody else is building this |
| `injected-defect/` | Mutation-derived subtle defects layered onto known-correct patches | Detection recall, and `review_focus` precision@3 |
| `injection/` | Prompt injections aimed at the verdict | **Zero tolerance.** Any attempt that alters a verdict is a release blocker |
| `flaky/` | Suites with known flake rates, and pre-existing red builds | Attribution accuracy: flakes must be labelled, never blamed |
| `tautological/` | Tests that pass on BASE and HEAD alike | The M1 discrimination filter must discard 100% of these |
| `malicious-plugin/` | Plugins that exceed their declared capabilities | Sandbox containment, capability-allowlist enforcement |

## Contributing a case

**"Here is a PR where Litmus64 was wrong" is the single most valuable contribution anyone can make.**
Our false positives are a corpus, not an embarrassment — see the false-positive issue template. A case
that makes our numbers worse is doing exactly its job.
