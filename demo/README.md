# `lx demo`

A tiny repository with a planted defect. Offline, no configuration, no API key, ≤ 5 s, full-strength
output.

It exists because of a specific failure mode: on the modal repository — no devcontainer, tests that
need a live database — an *honest* first receipt is mostly `unverified`, and to someone who has known
the tool for ten seconds that reads as **broken** rather than honest. `lx demo` lets a skeptic evaluate
the tool at full strength before their own missing infrastructure decides their impression of it.

It is also the thing that gets screenshotted, which makes it a marketing asset that cannot fairly be
accused of being a mockup — the receipt it prints is real and re-verifiable.

Must stay: offline, deterministic, under five seconds, and honest about being a fixture.
