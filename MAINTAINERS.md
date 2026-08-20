# Maintainers

Criteria and rights: [`GOVERNANCE.md`](GOVERNANCE.md) Stage 2. Thresholds are numeric and published
on purpose.

| Area | Maintainer | Approvals required |
|---|---|---|
| `spec/`, `lx-receipt`, `lx-verdict` | — | **2** |
| `lx-sandbox`, `lx-llm`, `lx-exec` | — | **2** |
| everything else | — | 1 |

`lx-exec` requires two approvals because it owns the `ConfirmedEvidence` constructor — the single
place where the differential-attribution guarantee (M2) could be silently deleted.

## Recruiting a second organization is a governance milestone

OpenSSF Incubating requires **≥ 3 maintainers across ≥ 2 organizational affiliations**. Until that
exists, this is a person's repository rather than a project, and the specification cannot be donated.
It is tracked as a release-blocking item, not as a hope.
