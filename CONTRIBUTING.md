# Contributing

```bash
git clone https://github.com/prabhu-gopal/litmus64 && cd litmus64
make dev              # devcontainer: toolchain, grammars, fixtures, sandbox check. One command.
cargo xtask check     # everything CI runs, locally, in the same order
cargo run -p lx-cli -- demo    # see the whole thing work, offline, in 5s
```

If `make dev` does not work first try, that is a **bug and a P1** — broken onboarding is the
number-one killer of contributor funnels.

## Sign-off, not paperwork

**DCO, no CLA.** Add `Signed-off-by:` with `git commit -s`. You keep your copyright; we never gain the
right to relicense your work. See [`GOVERNANCE.md`](GOVERNANCE.md).

## Where to start, by interest

| Interest | Where | Why it matters |
|---|---|---|
| **A language plugin** | `plugins/template/`, [`plugins/CONTRACT.md`](plugins/CONTRACT.md) | **Highest leverage.** Read JSON on stdin, write JSON on stdout — an afternoon, in any language. Each new language is a community we did not have to recruit |
| **Benchmark corpus** | `bench/corpora/` | "Here is a PR where Litmus64 was wrong" is the single most valuable PR anyone can send. Our false positives are a corpus, not an embarrassment |
| Renderers, docs | `crates/lx-render/`, `docs/` | The receipt is the product; every surface is a projection of it |
| Obligation inference | `crates/lx-oblig/`, `crates/lx-invariant/` | The hardest open problem in the system |
| Trace adapters | `crates/lx-invariant/` | Unlocks a whole mechanism for a whole language (M9) |
| The hard core | `lx-sandbox`, `lx-attack`, `lx-verdict` calibration | Two maintainer approvals required |

## The bar

**Definition of done** for a pipeline change: unit + property tests · snapshot updated · conformance
case if the schema moved · determinism test passes · benchmark delta reported · docs updated ·
CHANGELOG entry · law tests still green.

Every test that encodes one of the fourteen laws is named `law_<n>_<what>`, so a reviewer can grep the
laws and see them enforced. If your change touches a law, the PR template asks which one — answer it.

**Errors before features.** A new evidence kind is not done until it has a `Skipped` path, a replay
recipe, and a snapshot test.

New dependencies need a one-line justification in the PR. Prefer boring and maintained.

## What we promise you

Fast, honest review. Docs fixes merged same-day. A clear no with reasons beats silence. Credit
loudly — all-contributors, and humans named in release notes.
