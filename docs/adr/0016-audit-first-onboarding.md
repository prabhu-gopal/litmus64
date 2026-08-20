# ADR-0016 — `lx audit` is the front door: retroactive receipts and verification debt

**Status:** accepted

## Context

Stated plainly by someone describing what they want as a user:

> *"Simply install it in the CLI, run an audit on my codebase, get the report, and fix the issues.
> Running that gives me everything — so I know what mistakes the AI made."*

The design did not offer that. It offered **per-change verification**: diff-scoped by default (Law 7),
`lx check` on a pull request, `lx audit` demoted to a scheduled whole-repo job. A new user pointing
the tool at an existing repository with a year of agent-authored commits in it got **nothing**, because
there was no change to verify.

That is a real gap, and it is the gap at the exact moment a user decides whether the tool is worth
their time.

**But the naive reading of the request is a trap.** "Scan my whole codebase and list what is wrong" is
the most crowded category in the market — SlopCop, Sherlock Forensics, CodeRabbit, Sonar, Semgrep,
Greptile — and they all do it by **static pattern matching**, which is precisely the technique that
loses to the AI defect profile: *semantically wrong but syntactically plausible*. Building a better
pattern matcher means competing on the axis where we have no advantage and where the defects we care
about are invisible.

So: the requested **shape** is right and the requested **mechanism** is wrong. The synthesis is to keep
our mechanism and change the unit of work from "this pull request" to "this repository's history."

## Decision

**`lx audit` becomes a first-class front door, and it works by replaying history through the real
engine.** For each of the last N commits or merged PRs, reconstruct BASE and HEAD and run the
read-only tier — which needs no sandbox, no test harness, no API key, and cannot produce a false
accusation because it never obtains a `ConfirmedEvidence` (ADR-0013).

What comes out is not a lint report. It is a **verification-debt ledger**:

```
  litmus64 audit   github.com/acme/api        184 commits · 61 agent-authored · 12.4s

  UNVERIFIED DEBT        61 agent-authored changes · 0 carried evidence

  ⚠ CRITICAL SURFACE, NO EVIDENCE                                     7 changes
     a3f21d9  auth/refresh.py         "fix session refresh race"       no test touched auth/
     8b2c04e  billing/charge.py       "handle partial refunds"         no test touched billing/

  ⚠ UNSTATED CHANGES     the agent also changed something nobody asked about
     a3f21d9  token-cache TTL 300s → 60s          not mentioned in the PR body or issue
     11de882  retry limit 5 → unlimited           not mentioned anywhere

  ⚠ CONTRACT DRIFT       public surface changed without a version bump      3 changes
  ⚠ MIGRATIONS           4 forward migrations, 0 with a tested rollback

  REPORT   lx-audit-2026-08-20.html      shareable, self-contained, no server

  → Highest leverage: 7 critical-surface changes have no evidence at all.
    `lx audit --write-tests auth/` generates discriminating tests for them.
  → To stop the debt growing: `lx check` on every push (60s, free, no API key).
```

Three properties make this the right front door:

1. **It answers the actual question.** "What did the AI do that nobody checked?" — with
   `unstated_changes` as the headline finding, which is the one thing reviewers miss most and which
   requires no execution at all to detect.
2. **It costs nothing to try.** Read-only tier, no setup, no key, seconds. There is no configuration
   cliff between installing and getting value.
3. **It reuses machinery we already need.** The revert-mining pipeline (`bench/mining/`) already walks
   history reconstructing BASE/HEAD pairs for the calibration corpus. `lx audit` is that walk pointed
   at the user's repo instead of ours. This is close to free.

**And it converts into the real product.** The audit ends by naming the debt and offering the two
things that stop it accumulating: `lx check` on every push, and `--write-tests` to discharge the
existing backlog. Audit is the wedge; per-change verification is the product; the ledger (M6) is the
retention.

### `--write-tests`: the honest form of "fix the issues"

We do not fix code. We never will — a verifier that edits the thing it verifies has destroyed its own
independence, and that boundary is permanent.

But the discrimination filter (M1) already generates artifacts that *distinguish BASE from HEAD*, and
the ones that survive are exactly the tests that should have existed. `lx audit --write-tests` commits
them as plain, readable test files that run **without Litmus64 installed**. That is the useful and
honest reading of "fix the issues": we do not repair the change, we build the evidence that was
missing, and we hand it over in a form that outlives us.

## Consequences

**Good.** A first run produces real findings on any repository with git history, with zero setup. The
positioning stays differentiated — evidence and honest gaps, not a pattern-matching score. `lx audit`
gets a legitimate second job beyond the scheduled deep run.

**Bad.** History replay is unbounded work, so it needs hard defaults (`--since`, `--max-commits`,
default 200) and honest reporting of what it sampled. Silent truncation of an audit would violate Law
6 as surely as a silent stage skip. Detecting "agent-authored" is heuristic — commit trailers,
co-author lines, PR metadata — so it is reported as a *claim* with its basis shown, never as a fact
(the receipt already treats `authoring_agent` as `trust: unverified_claim`; the same rule applies
here).

**Also bad, and worth stating:** this raises the stakes on the HTML report. "Get a report" means a
file a human can open and send to their lead. It must be one self-contained file with no server and no
external requests — which is also the only form that works inside an enterprise network.

## Rejected

- **A whole-codebase static score** ("your repo is 62% slop"). Crowded, undifferentiated, and it loses
  to the defect profile we exist to catch. A number with no falsification behind it is exactly the
  astrology we criticise elsewhere.
- **Security scanning as a headline.** Users say "vulnerabilities" because that is the vocabulary the
  market taught them. We consume Semgrep and CodeQL as evidence sources, but security-shaped analysis
  is a solved, crowded space and correctness is ours. Say so plainly rather than half-competing.
- **Auto-fixing code.** Permanently out of scope. Independence is the asset.
