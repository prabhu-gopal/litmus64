# What Litmus64 is, in plain language

## One sentence

**Your AI wrote the code and said it works. Litmus64 tries to prove it doesn't — then hands you a
receipt listing what it tried, what survived, and what it could not check.**

That last part is the part nobody else gives you.

---

## The situation you are actually in

Two numbers describe 2026 better than any argument:

> **96%** of developers don't fully trust that AI-generated code is functionally correct.
> Only **48%** always review it before committing.

You don't trust it, and you don't read it. That is not laziness — it is arithmetic. Agents produce
more code than anyone can read, so review time rose **441%** while the number of pull requests merged
with **no review at all** rose **31%**. Over the same period, bugs per developer rose **54%** and the
chance that a merged change causes a production incident **more than tripled**.

The gate didn't get slower. **The gate is disappearing.**

So the question is not "how do I review AI code faster." It is: **what can check the code when nobody
is going to read it?**

---

## Why the obvious answers don't work

**"The tests pass."** A green checkmark is a liar in both directions. Of patches that pass the test
suite, **29.6% behave differently** from the known-correct fix. And **7.8% of correct** patches fail
the suite. Your CI cannot tell you which case you are in.

**"A review bot looks at it."** AI-written defects have a specific shape: *semantically wrong but
syntactically plausible.* The code looks exactly like correct code. That's why it defeats human
review — and a bot reading the same code is reading the same trap. Every reviewer tool, human or AI,
gives you the same thing: **an opinion about code**.

**Syntactic plausibility defeats reading. It does not defeat running things.**

---

## What Litmus64 does instead

It doesn't read your code and form an opinion. It works out what **must be true** if the change is
correct, builds little experiments that would **fail** if it isn't, runs them against the code
**before and after** the change, and records what happened.

Think of a home inspection. You're buying a house; you're not going to inspect it yourself. A bad
inspector says *"looks fine to me."* A good one hands you a report:

- Foundation — checked, solid
- Wiring — **checked, found a problem, here's the photo**
- Roof — **could not access, no ladder. You still don't know about the roof.**

That last line is why you hire an inspector. And it's the line every code tool leaves out.

---

## What you actually get

### Step one: find out what your AI already did

```bash
curl -fsSL https://litmus64.com/install.sh | sh
cd your-repo && lx audit
```

No configuration. No API key. No setup. A few seconds. It reads your git history and tells you what
was never checked:

```
  UNVERIFIED DEBT        61 agent-authored changes · 0 carried evidence

  ⚠ CRITICAL SURFACE, NO EVIDENCE                                  7 changes
     a3f21d9  auth/refresh.py    "fix session refresh race"   no test touched auth/

  ⚠ UNSTATED CHANGES     the agent also changed something nobody asked about
     a3f21d9  token-cache TTL 300s → 60s     not mentioned in the PR body or the issue
     11de882  retry limit 5 → unlimited      not mentioned anywhere

  ⚠ MIGRATIONS           4 forward migrations, 0 with a tested rollback
```

**"The agent also changed something nobody asked about"** is usually the moment people get it. You
asked it to fix a race condition. It also quietly cut a cache timeout from 5 minutes to 1 minute.
Nobody mentioned that. Nobody reviewed it. It's in production.

### Step two: stop the pile growing

```bash
lx check          # on every push. ~60 seconds. Free. No API key.
```

You get one screen. Not a wall of comments:

```
  VERDICT  HUMAN REVIEW REQUIRED    all attempted obligations held; 2 high unverified

  LOOK AT  1  cache invalidation under partition     auth/refresh.py:88-141
           2  down-migration for sessions           migrations/0042_sessions.sql
           3  unstated TTL change                    auth/token_cache.py:31
```

**Three lines.** That's the product. Not "here are 40 comments, good luck" — three places to look, in
priority order, with file and line.

### Step three: it gets better the longer you use it

Every property Litmus64 proves about your code gets saved into your repo as a **plain, readable test
file that runs without Litmus64 installed.** Change #500 gets checked against everything learned from
changes #1–#499.

You are not renting this. It accumulates in your repository, and if you stop using us tomorrow you
keep the tests.

---

## The one thing that makes this different

Every other tool is built to tell you it worked.

**Litmus64 is built to tell you what it couldn't check.** Every report has an `unverified` section,
and it is a *required field* — a report claiming it checked everything is rejected as invalid by our
own validator. If we couldn't test something, you get told, with the reason:

- `capability_unavailable` — no tool exists to test this in your language
- `no_test_harness` — your tests need a live database
- `budget` — we ran out of time; here's how to run it anyway
- `unformalizable` — we couldn't turn this into something executable

Four different messages. A tool that collapsed those into silence would be **more comfortable and
less useful**, and the comfortable version is what everyone else ships.

---

## And it can prove it wasn't lying

Every report is **cryptographically signed**, and anyone can re-check it without trusting us:

```bash
lx verify receipt.json
```

That command doesn't read our conclusion — it **recomputes the verdict from the evidence.** If our
stated answer disagrees with our own data, verification fails. The verifier is Apache-2.0 licensed
and always will be, because **a receipt you need our permission to check is worthless.**

---

## How to explain it in one line, depending on who's asking

| Audience | The line |
|---|---|
| A developer | *"Your agent says it fixed the bug. Litmus64 tries to prove it didn't, then signs the result."* |
| Someone who vibe-codes | *"You're shipping code you didn't read. This checks it for you and tells you the three places to actually look."* |
| A tech lead | *"Every merged change gets a signed receipt showing what was verified and what wasn't. Verification debt becomes visible instead of accumulating silently."* |
| A security or compliance person | *"Tamper-evident, independently verifiable evidence for every machine-authored change, as a signed in-toto attestation."* |
| A skeptic | *"It doesn't prove your code is correct. It records what we tried to break, what held, and what we couldn't check. That's the whole claim."* |

---

## What it is not

- **Not a code reviewer.** No opinions about your style. There are many good tools for that.
- **Not a security scanner.** It uses Semgrep and CodeQL as inputs, but finding vulnerabilities is a
  crowded, solved space. Litmus64 is about **correctness** — does this change do what it claimed, and
  nothing else.
- **Not a replacement for CI.** It consumes CI.
- **Not going to edit your code.** A tool that modifies what it verifies has lost the right to be
  believed. It will *write the tests that were missing*, and hand them to you as normal files.
- **Not proof.** Read the first line of the README again. We say what we tried. That's it.

---

## The honest catch

Some checks don't exist in some languages, and we publish that as a table rather than letting you find
out:

```bash
lx capabilities
```

Rust gets the strongest checking available today, because the tooling for exhaustively exploring
concurrency bugs and mathematically proving properties only exists there. Python, TypeScript, and Go
get everything except those two, and get a weaker-but-real version of the concurrency check: we can
**reproduce** a race on demand, but we can't claim we searched every possibility.

Those are different claims, so they're reported as different things. A tool that blurred them would
look better and be worth less.

---

**Next:** [`docs/cli.md`](cli.md) for every command · [`docs/laws.md`](laws.md) for the rules the code
enforces on itself · [`KNOWN-LIMITATIONS.md`](../KNOWN-LIMITATIONS.md) for where we're bad, written
down before you ask.
