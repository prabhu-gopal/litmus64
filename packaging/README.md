# Packaging — one binary, six channels

`cargo-dist` builds the platform matrix; these directories hold the per-ecosystem wrappers that
publish **the same executable** under each ecosystem's native install command (ADR-0015).

| Directory | Channel | Mechanism |
|---|---|---|
| `pypi/` | `uv tool install litmus64` · `pip install litmus64` | `maturin` platform wheels — a prebuilt binary, exactly how `ruff` ships. No compiler, no Rust toolchain, no Python version constraint |
| `npm/` | `npm install -g litmus64` | Thin shim resolving a platform-specific optional dependency to the binary |
| `homebrew/` | `brew install litmus64` | Formula/cask, published to the tap by `release.yml` |

`curl | sh`, PowerShell, `cargo install`, and the container image need no wrapper.

## The rule that matters

**These are distribution channels, not ports.** There is exactly one implementation of the engine and
one implementation of the verdict function, so a receipt produced by the `pip`-installed binary is
byte-identical to one from `brew`. A second implementation of the verdict would destroy receipt
comparability, which is the whole product — language support belongs in plugins, never in a fork of
the engine.

## Release gate

`release.yml` must **install from every channel and run `lx demo`** before marking a release latest. A
lagging channel is worse than an absent one: a user who follows our own README and gets a stale binary
has learned that our tooling is unreliable, on the one dimension where that is unaffordable.
