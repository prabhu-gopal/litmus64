# Examples — committed receipts you can read

Every merged Litmus64 pull request lands a signed receipt here. **That is the proof**, and it is worth
more than any blog post: anyone can read the artifacts, re-verify them with the Apache-2.0 verifier,
and check whether we hold ourselves to the standard we describe.

```
lx verify examples/<lang>/<sha>.json      # recomputes the verdict from the evidence,
                                          # rather than trusting the stated one
```

Per-language directories appear as each plugin ships. They are deliberately **unequal**, and the
inequality is the point: the Rust receipts carry `schedule_search` and bounded model checking, while
the Python, TypeScript, and Go receipts carry `schedule_replay` and a larger `unverified[]` block.
Publishing the narrower ones next to the strongest one is how the capability matrix stays honest
instead of becoming marketing.
