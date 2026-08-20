# The Litmus64 plugin contract

**The whole contract: read JSON on stdin, write JSON on stdout, exit 0.**

Any language. No SDK required. No WebAssembly, no Component Model, no IDL toolchain — see
[`DECISIONS.md`](../DECISIONS.md) D2 for why that was removed rather than added.

Normative schema: `spec/plugin-v0.1.schema.json`, generated from the same Rust types as the receipt,
so the contract cannot drift from the engine.

## Three subcommands

```
$ my-plugin capabilities
{ "languages": ["ruby"],
  "evidence_kinds": ["existing_suite", "generated_test", "mutation"],
  "mechanisms": { "differential": "ready", "mutation": "ready",
                  "schedule_search": { "no_substrate": "no systematic scheduler for ruby" } },
  "commands": ["rspec", "ruby"],          // host-exec allowlist. Anything else is DENIED
  "requires_network": false,
  "cost_class": "medium" }

$ my-plugin plan < plan-request.json
{ "tasks": [ { "id": "t1", "kind": "existing_suite", "cost_estimate_ms": 4200, ... } ] }

$ my-plugin run < task.json
{ "result": "pass", "replay": { "command": [...], "env_digest": "sha256:...", "seed": 1337 },
  "artifacts": [ ... ] }
```

## Five rules, all of them load-bearing

1. **`plan` MUST be deterministic.** Same input, same tasks, same order. A nondeterministic planner
   makes receipts non-reproducible, and reproducibility is the product.
2. **Never fake a pass.** A task you cannot perform returns
   `{ "skipped": { "reason": "missing_toolchain", "detail": "rspec not found",
   "install_hint": "gem install rspec" } }`. The engine converts every skip into an `unverified[]`
   entry — a code path that silently drops work does not exist. This is Law 6.
3. **Declare your capabilities honestly.** `xtask capability-check` verifies that every mechanism you
   report `ready` has a passing end-to-end fixture that actually uses it. Claiming a capability you
   lack is the one thing this project cannot tolerate (Law 14).
4. **You never spawn a process yourself.** Emit the command; the engine runs it through the sandbox
   at the current trust tier. A plugin cannot obtain a weaker tier than the run it lives in.
5. **Declared cost class must match measured cost within 2×.** The budget planner is a knapsack; a
   plugin that lies about cost corrupts everybody's budget.

## Conformance

`cargo xtask new-plugin my-lang` scaffolds a plugin plus the conformance tests every plugin must
pass: capabilities are honest · `plan` is deterministic · `run` is idempotent for identical input ·
no writes outside the workspace · declared cost class within 2× of measured · graceful `skipped` on
a missing toolchain rather than a panic.

`plugins/template/` is deliberately **not** written in Rust. If the reference template were Rust,
the ABI's language-neutrality would be a claim rather than a demonstration.
