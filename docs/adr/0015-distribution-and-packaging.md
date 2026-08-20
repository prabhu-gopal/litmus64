# ADR-0015 — One binary, every ecosystem's native install command

**Status:** accepted

## Context

The engine is Rust (ADR-0001). Most users are not Rust developers — Python is the largest audience,
followed by TypeScript. The obvious fear is that a Rust tool is hostile to Python users.

**The evidence says the opposite, decisively.** The most loved Python tooling of the last five years
is written in Rust, and Python developers neither know nor care:

| Tool | Written in | Adoption |
|---|---|---|
| **uv** | Rust | **75 million monthly PyPI downloads** (April 2026), past Poetry, becoming the CI default |
| **ruff** | Rust | Replaced flake8 + isort + Black + others with one binary |

They were adopted *because* of what Rust buys, not despite it: **a single static binary, no runtime to
install, no dependency resolution, and 10–100× the speed.** `pip install ruff` works because a
prebuilt wheel ships per platform; nobody compiles anything.

And for this tool specifically, an interpreted implementation is not merely slower — it is
**disqualifying**:

1. **It would install into the environment it analyses.** A Python tool in the user's venv competes
   for dependency versions with the code under test. Our entire premise is isolated, reproducible,
   paired BASE/HEAD execution. A verifier that perturbs the environment it measures is broken at the
   concept level.
2. **It could not be the sandbox.** `lx-sandbox` is the only process spawner and the single security
   boundary (ADR-0012). That needs real process, namespace, and resource control.
3. **Determinism would be a fight.** Byte-identical receipts across runs is a release gate. Hash
   randomisation, GC timing, and dependency drift are the opposite of that.
4. **Install would be the top support cost.** "Which Python version?" is not a question a trust tool
   can afford to ask in its first sixty seconds.

## Decision

**One binary. Every ecosystem's native install command.** A user never learns a new package manager,
and never learns that the tool is written in Rust.

```bash
curl -fsSL https://litmus64.com/install.sh | sh   # primary, auto-updating, no runtime
irm https://litmus64.com/install.ps1 | iex        # Windows
brew install litmus64                             # macOS / Linux
uv tool install litmus64                          # Python users — a prebuilt wheel, like ruff
pip install litmus64                              # same wheel, older workflows
npm install -g litmus64                           # TypeScript users — a binary shim
cargo install litmus64                            # Rust users, from source
docker run ghcr.io/litmus64/lx                    # CI without an install step
```

The native installer is primary and auto-updates in the background — the pattern Claude Code
converged on for the same reason: it removes the runtime question entirely.

Python and npm packages contain **the same binary**, shipped as platform wheels via `maturin` and as
an npm optional-dependency shim. They are distribution channels, not ports. There is exactly one
implementation and one set of receipts, so a receipt produced by `pip`-installed `lx` is
byte-identical to one from `brew`.

## Consequences

**Good.** Install is one command in whichever ecosystem the user already lives in. No runtime
conflicts with the analysed project. Cross-platform matrix is `cargo-dist`'s problem, already solved.
Signed artifacts and SLSA provenance come along the same pipeline.

**Bad.** A release publishes to six channels, so release automation must be genuinely reliable — a
channel that lags is worse than a channel that does not exist. `cargo-dist` plus a wheel job plus an
npm shim job, all tag-triggered, all in `release.yml`, and a smoke test that installs from **every**
channel and runs `lx demo` before the release is marked latest.

## Rejected

- **Write the engine in Python** to match the audience. Fails on all four points above. The audience
  argument is also empirically wrong: uv and ruff prove the audience does not care.
- **Rust only, `cargo install` only.** Would restrict the tool to people who already have a Rust
  toolchain, which is close to none of our users.
- **Per-language reimplementations.** Multiple implementations of the verdict function is the one
  thing that would destroy receipt comparability. Language support belongs in plugins (ADR-0012),
  never in forks of the engine.
