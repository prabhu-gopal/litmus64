# ADR-0012 — Subprocess plugin ABI; WASM is a post-1.0 second transport

**Status:** accepted · **Supersedes:** ADR-0003 (WASM plugins)

## Context

ADR-0003 made WASM components (WASI 0.2, wasmtime) the primary plugin ABI with a subprocess "escape
hatch," justified by: *a third-party plugin cannot exfiltrate your source even if malicious — that is
what makes it safe to open the ecosystem wide.*

**A WASI 0.2 component cannot run `pytest`, `vitest`, `go test`, or `cargo test`.** Every
evidence-producing plugin — `lx-rust`, `lx-python`, `lx-typescript`, `lx-go` — would have taken the
escape hatch. The isolation boundary justifying an open ecosystem would have protected only the
plugins that never execute code, while wasmtime, WIT, and the Component Model stayed as a permanent
audit surface and a learning curve in front of our highest-leverage contribution path.

## Decision

One transport-neutral contract (`spec/plugin-v0.1.schema.json`, generated from the receipt types).
One transport at 1.0: subprocess, JSON over stdio. Isolation is `lx-sandbox`, which already has the
harder job of containing the untrusted diff; a plugin inherits the trust tier of its run and can
never obtain a weaker one. WASM returns post-1.0 as a second transport for pure-analysis plugins.

## Consequences

**Good.** One security boundary, audited once. wasmtime leaves the dependency graph. Plugin authoring
becomes "read JSON on stdin, write JSON on stdout" — an afternoon, in any language. Enforced
mechanically: `xtask arch-check` forbids `std::process` and `tokio::process` outside `lx-sandbox`.

**Bad.** Process-spawn overhead per invocation — irrelevant at our granularity, which is once per
task, not once per function call.

## Rejected

- **WASM-first with subprocess fallback** (ADR-0003). The security claim does not hold for the
  plugins that matter, and a claim that holds only in cases you do not ship is worse than none,
  because it manufactures false confidence.
- **Both transports at 1.0.** Two boundaries, two audit surfaces, twice the sandbox-escape exposure,
  for latency we do not need.
