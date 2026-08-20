# Command reference

Small, obvious, composable. Three rules govern this surface: **zero config works**, **one artifact
many views**, **never make a human read prose to find the risk**.

## Install

One binary. Use whichever command belongs to the ecosystem you already live in — they all install the
same executable, and none of them requires a Rust toolchain (ADR-0015).

```bash
curl -fsSL https://litmus64.com/install.sh | sh   # primary — auto-updates, no runtime needed
irm https://litmus64.com/install.ps1 | iex        # Windows
brew install litmus64                             # macOS / Linux
uv tool install litmus64                          # Python — a prebuilt wheel, exactly like ruff
pip install litmus64                              # same wheel
npm install -g litmus64                           # TypeScript / Node
cargo install litmus64                            # from source
docker run ghcr.io/litmus64/lx                    # CI, no install step
```

There is one implementation, so a receipt from the `pip` install is byte-identical to one from `brew`.

## Start here — the first five minutes

```bash
lx demo                      # bundled defect fixture, offline, ~5s. See it work before anything else
cd your-repo && lx audit     # what did the AI do that nobody checked? Reads history, no setup
lx init                      # capability score + the one highest-leverage unlock
lx check                     # verify the change you are working on now (60s, free, no API key)
lx check --deep              # full escalation ladder + signed receipt, for the merge gate
```

`lx audit` is the front door and `lx check` is the product. The audit tells you what debt you already
have; `lx check` stops it growing.

## `lx audit` — retroactive receipts over your history

```bash
lx audit                                 # last 200 commits, read-only tier, seconds
lx audit --since 2026-01-01               # or --max-commits N, or --prs
lx audit --html report.html               # one self-contained file. No server, no external requests
lx audit --json                           # machine-readable, for dashboards
lx audit --agent-authored                 # only changes claiming an agent author (a CLAIM, shown as one)
lx audit --write-tests auth/              # generate the discriminating tests that should have existed
lx audit --deep                           # the scheduled whole-repo run: mutation, load, full BMC
```

It reports **verification debt**: changes on critical surfaces with no evidence, `unstated_changes`
(the agent also changed something nobody asked about), contract drift with no version bump, and
migrations with no tested rollback. It names what it sampled — an audit that silently truncates would
break Law 6 as badly as a silently skipped stage.

**`--write-tests` is the honest form of "fix it."** We never edit your code; a verifier that modifies
what it verifies has destroyed its own independence. But the discrimination filter already generates
artifacts that distinguish BASE from HEAD, and the survivors are exactly the tests that should have
existed. Those get committed as plain, readable files that **run without Litmus64 installed.**

## Verifying

```bash
lx verify <receipt|url>      # validate the signature AND RECOMPUTE the verdict from the evidence
                             # — never trusts the stated one. Apache-2.0, no permission needed
lx replay EV-7 [--seed N]    # re-execute one piece of evidence, locally, deterministically
lx explain OB-3              # why this obligation exists, where it came from, how it was attacked
lx receipt diff A B          # obligations gained/lost, risk delta between two receipts
```

## Profiles

| Command | Runs on | Stages | p95 | LLM cost |
|---|---|---|---|---|
| `lx check --read-only` | anything, no setup | structure, contract, intent, blast radius | ≤ 10 s | optional |
| `lx check` *(default)* | every push, agent stop-hook | + paired execution of impacted tests | ≤ 60 s | **$0.00** |
| `lx check --deep` | pre-merge, merge queue | all eleven stages, full attack ladder | ≤ 20 min | ≤ $0.50 |
| `lx audit` | first run, and scheduled | replays history through the read-only tier | ≤ 30 s / 200 commits | **$0.00** |
| `lx audit --deep` | scheduled | whole-repo mutation, load, full BMC | ≤ 90 min | ≤ $5.00 |

The default is free and LLM-less on purpose: the agent feedback loop runs a hundred times a day, so it
cannot cost money or depend on a provider's rate limit.

## Understanding what you did not get

```bash
lx capabilities              # which of the nine mechanisms exist here, and what is missing why
lx explain-nothing           # why this receipt is thin, and the one fix that helps most
lx why-slow                  # per-stage waterfall, cache hits, what the planner cut and why
lx explain-egress            # exactly which bytes would leave, to which provider, for this run
lx doctor                    # toolchain, sandbox, plugin, and permission diagnosis with fixes
lx telemetry show            # the precise payload that would be sent, if you opted in (off by default)
```

## The ledger

```bash
lx ledger list|review|prune       # curate the repo's accumulated invariants
lx ledger supersede <entry>       # this change intentionally replaces a locked-in invariant
```

## Lifecycle

```bash
lx check --fix-loop               # hand violations + minimal reproducers back to the agent, iterate
lx discharge UV-1 --env staging   # satisfy a deferred obligation post-merge; amend the receipt
lx calibrate                      # fit risk weights on this repo's history; print the reliability curve
lx suppress <finding> --reason    # a reviewed, owned, EXPIRING suppression — not a silent ignore-file
lx mcp serve                      # expose the engine to any agent over MCP
```

## Exit codes — part of the public API, and stable

| Code | Meaning |
|---|---|
| `0` | pass |
| `10` | human review required |
| `11` | expert review required |
| `20` | changes requested |
| `30` | blocked |
| `40` | tool error |
| `41` | config error |
| `42` | sandbox unavailable |

**"Found a problem" and "crashed" are never conflated.** CI depends on that distinction, and a tool
that returns 1 for both is unusable in a gate.

## Everywhere

`NO_COLOR` and `--json` honoured · ASCII fallback, no Unicode-only output · `--quiet` for CI logs ·
`--dry-run` prints the plan and cost estimate before spending anything · every error is a diagnostic
with a suggested fix · **no command requires a network or an API key to do something useful.**
