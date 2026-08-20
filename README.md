# Litmus64

**Evidence receipts for machine-authored code changes.**

> **Litmus64 does not prove your code is correct. It records what we tried to break, what held, and
> what we could not check.**

That sentence is the first thing you read on purpose, and it is not modesty — it is the product. A
coding agent is not allowed to say "Done." It must produce evidence, and the evidence must survive an
independent attempt to break it.

Your agent says it fixed the bug. Litmus64 tries to prove it didn't, then signs the result.

## Why

> **96%** of developers don't fully trust that AI-generated code is functionally correct.
> Only **48%** always review it before committing.

You don't trust it, and you don't read it. That isn't laziness, it's arithmetic — agents write more
code than anyone can read. So review time rose **441%** while pull requests merged with **no review at
all** rose **31%**, bugs per developer rose **54%**, and the chance a merged change causes a production
incident **more than tripled**.

**The gate didn't get slower. The gate is disappearing.**

And a green checkmark can't replace it: **29.6%** of patches that pass the test suite behave
differently from the known-correct fix, and **7.8%** of correct patches fail it. Your CI cannot tell
you which case you're in.

AI-written defects are *semantically wrong but syntactically plausible* — they look exactly like
correct code. **Syntactic plausibility defeats reading. It does not defeat running things.**

→ **[The plain-language explanation](docs/why.md)** — what this is, what you get, and what it is not.

## Try it

```bash
curl -fsSL https://litmus64.com/install.sh | sh    # or: brew install litmus64
                                                   #     uv tool install litmus64
                                                   #     npm install -g litmus64
lx demo                    # see it work, offline, ~5s
cd your-repo && lx audit   # what did the AI do that nobody checked?
```

One static binary, no runtime to install, and the same executable in every channel. If you are a
Python or TypeScript developer, `uv tool install` and `npm install -g` ship a prebuilt binary — you
never compile anything and never need a Rust toolchain. Full reference: [`docs/cli.md`](docs/cli.md).

`lx audit` reads your git history and reports **verification debt**: changes on critical surfaces with
no evidence behind them, contract drift with no version bump, migrations with no tested rollback, and
the finding reviewers miss most — **the agent also changed something nobody asked about.** No
configuration, no API key, no sandbox, seconds. It cannot report a false violation because the
read-only tier cannot produce one at all.

Then `lx check` on every push (60 s, free, no API key) stops the debt growing.

## Status — nothing works yet

**Design complete; 0% of the product is functional.** 27 crates that compile, every one of them
`unimplemented!()`. See [`STATUS.md`](STATUS.md) for exactly what exists, what doesn't, and the first
testable milestone. A project whose product is honest reporting cannot have a misleading status page.

Built in public, staged by write-access (`DECISIONS.md` D3). No release will ever leak noise into your
pull requests — the read-only tier **cannot emit a violation at all**, by construction rather than by
promise.

| Tier | What it does | State |
|---|---|---|
| T0 · standard | `spec/`, schema, conformance suite, free verifier | in progress |
| T1 · look | reads your code, writes nothing, cannot accuse | planned |
| T2 · run | executes tests in a sandbox, paired against BASE | planned |
| T3 · attack | mutation, property, schedule search, BMC, ledger | planned |

## Read next

- **[`docs/why.md`](docs/why.md) — start here.** What this is in plain language, and how to explain it
- [`docs/cli.md`](docs/cli.md) — every command
- [`docs/enterprise.md`](docs/enterprise.md) — egress, sandboxing, supply chain, licensing, and an
  honest read on what regulations actually require
- [`CODEBASE.md`](CODEBASE.md) — repository design, crate contracts, testing, CI
- [`DECISIONS.md`](DECISIONS.md) — the structural decisions and what they rejected
- [`LICENSING.md`](LICENSING.md) — which tier each path is in (normative)
- [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md) — where we are bad, in writing, before you ask

## We are a conductor, not an orchestra

Semantic diff, symbol graphs, test impact analysis, mutation, property testing, deterministic
simulation, bounded model checking, contract diff, shadow traffic, canary statistics, sandboxing —
all of it already exists and is excellent. Nobody had turned it into one coherent, fast, sandboxed,
signed, open system with a format, a conformance suite, and a governance model. That conversion is
the work.

## License

The **spec, schema, conformance suite, and receipt verifier are Apache-2.0 / CC-BY-4.0** — forever,
because verification that requires our permission is worthless. The **engine is Fair Source
(FSL-1.1-ALv2)**: free for any internal or commercial use of your own code, at any company size,
barred only from being resold as a competing verification service, and it converts to Apache-2.0 two
years after each version ships.

The engine is **not** OSI open source during its FSL term, and we do not call it that. See
[`LICENSING.md`](LICENSING.md).

## One ask

Run it on your last pull request and open an issue with what it got wrong.
