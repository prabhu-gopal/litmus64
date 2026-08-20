# Workspace-level tests

Per-crate tests live next to their crate. This directory is for tests that span the whole system.

`e2e/` (created with its first case): cold install → receipt, on Linux and macOS, with and without
network, on pinned real repositories.

The end-to-end suite is also where the onboarding budgets are enforced as regressions rather than
aspirations: `lx demo` ≤ 5 s · `lx check --read-only` ≤ 10 s on an unseen repo with no configuration ·
time to first executed receipt ≤ 5 min. Those numbers are product promises, so they are tests.
