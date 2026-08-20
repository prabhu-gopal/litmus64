## What and why

<!-- One paragraph. Link the issue or RFC. -->

## Which law of the system does this touch?

<!-- docs/laws.md lists fourteen. If none, write "none" — but check first, because
     most pipeline changes touch at least one. Law tests are named law_<n>_<what>. -->

## Definition of done

- [ ] Unit + property tests
- [ ] Snapshot updated (`cargo insta review`)
- [ ] Conformance case added if the schema moved
- [ ] Determinism test passes (`cargo xtask determinism`)
- [ ] Capability matrix still accurate (`cargo xtask capability-check`)
- [ ] Benchmark delta reported if this could move FP rate or detection
- [ ] Docs updated · CHANGELOG entry · `Signed-off-by:` present

## New dependencies

<!-- One line of justification each, or "none". Prefer boring and maintained. -->
