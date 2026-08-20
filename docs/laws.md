# The fourteen laws

Enforced in code and in review, not aspirational. **Every test that encodes a law is named
`law_<n>_<what>`**, so a reviewer can grep the laws and see them enforced:

```bash
cargo test law_          # all of them
cargo test law_3_        # no attribution without a BASE control
```

If your change touches a law, the pull-request template asks which one. Answer it.

---

1. **The model proposes; the machine disposes.** An LLM may write obligations, mutants, tests, and
   prose. An LLM may **never** decide a verdict. The verdict is a pure function over evidence and is
   unreachable from any model output path. Enforced architecturally: `lx-verdict` has no dependency on
   `lx-llm`, and CI fails if that edge appears.
2. **No claim without a falsification attempt.** An obligation with no executed attempt is
   `unverified`, never `held`.
3. **No attribution without a BASE control.** Nothing is blamed on the change until it has been shown
   to behave differently on BASE than on HEAD, across N repetitions. Enforced by the type system:
   `Held` and `Violated` require `ConfirmedEvidence`, which only `lx-exec`'s attribution engine can
   mint.
4. **No evidence without replay.** Every evidence item carries the exact command, environment digest,
   and seed needed to reproduce it. `lx replay <EV>` must reproduce, or the receipt is invalid.
5. **Report the dark matter.** `unverified[]` is a required field. A receipt claiming total coverage is
   malformed and is rejected by the validator.
6. **Skips are recorded, never silent.** Budget cuts, crashes, timeouts, and missing toolchains appear
   as skipped stages with typed reasons, each with a matching `unverified[]` entry. Silent truncation
   reads as coverage, which is a lie.
7. **Diff-scoped by default.** Whole-repo anything is a scheduled job, never a pull-request job.
8. **Deterministic core, quarantined edge.** All analysis, diffing, mutation, and execution is
   deterministic and content-addressed. Model calls are isolated, logged with model ID, prompt digest,
   and pinned sampling parameters, and always followed by a deterministic filter.
9. **Untrusted text is data, never instruction.** `Untrusted<T>` implements neither `Display` nor
   `Serialize`-as-string and has no `as_str()`. The only exit is `quarantine()`. Asserted by a
   compile-fail suite.
10. **Local-first.** Full function with zero network egress, degraded honestly — which means more
    `unverified`, never a fabricated pass.
11. **One artifact, many renderers.** The receipt is the product. Every human surface is a
    reimplementable projection of it. If a surface needs a fact the receipt lacks, fix the schema.
12. **Never punish the user for our uncertainty.** When confidence is low, prefer `unverified` over a
    wrong `violated`. False positives are this category's cause of death.
13. **Stated intent outranks the control.** BASE is our control, not our oracle. `PRESERVE`
    obligations derived structurally or empirically are *hypotheses* that BASE's behaviour was
    intended; a `CHANGE`-class intent that contradicts one resolves **in favour of the stated
    intent**, and the contradiction is surfaced for confirmation rather than reported as a violation.
    The literature we build on assumes the base version is correct; we decline to inherit that,
    because "the change that fixes a long-standing bug gets blocked" is the most infuriating possible
    false positive.
14. **A capability we lack is a gap we print.** Missing toolchains, unsupported languages, and
    unavailable mechanisms are recorded as `capability_unavailable` in `unverified[]` and reflected in
    `lx capabilities`. The tool's own limits obey Laws 5 and 6.

---

## The two that are easiest to forget

Laws 13 and 14 are the newest and the most embarrassing to get wrong, so they have dedicated tests:

- `law_13_stated_intent_outranks_base_control` — a change that fixes long-standing wrong behaviour on
  BASE must not be reported as a `PRESERVE` violation.
- `law_14_capability_gap_is_printed` — for each mechanism, remove its toolchain from the fixture
  environment and assert the receipt contains `capability_unavailable` with a usable detail string,
  rather than a narrower receipt that merely *looks* complete.
