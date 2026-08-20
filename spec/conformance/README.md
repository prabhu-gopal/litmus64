# Conformance suite

Tier 0. **Anyone may claim "Litmus64-conformant" and prove it** — `cargo run -p lx-conformance`, or the
released `lx-conformance` binary. Apache-2.0, so no permission is needed to verify anything.

Directories are created as the first case in each lands. Each fixture is a single JSON file, named
for what it tests, and every invalid fixture names the clause it violates.

| Directory | Contains | Assertion |
|---|---|---|
| `valid/` | Well-formed receipts, one per interesting shape | MUST validate against `spec/receipt-v0.1.schema.json` |
| `invalid/` | Malformed receipts, each paired with the spec clause it violates | MUST be rejected, **and rejected for the stated reason** — a validator that rejects for the wrong reason has a bug |
| `golden-verdicts/` | `(obligations, coverage, risk, policy) → expected verdict` | `lx-verdict::decide` MUST return exactly this. The verdict is ~50 lines of pure code; these fixtures are why you can trust that claim |
| `golden-risk/` | `(features, weights) → expected score` | `lx-verdict::compute_risk` MUST match to full float precision |
| `law6-skips/` | Receipts where a stage is not `ok` | Every non-`ok` stage MUST have a matching `unverified[]` entry. A receipt that skips work silently is **malformed** — silent truncation reads as coverage, which is a lie |
| `forward-compat/` | Receipts containing unknown fields | Consumers MUST preserve unknown fields. This is what lets the schema evolve without orphaning signed history |

## The bar for a new case

A conformance case is a **normative claim**, so adding one is a spec change: it needs an RFC link if
it constrains behaviour that the prose does not already require. If the prose is ambiguous enough that
two reasonable implementers disagree, the fix is the prose, not the fixture.
