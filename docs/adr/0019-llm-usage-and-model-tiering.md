# ADR-0019 — What the LLM is for, which models, and a bug this uncovered

**Status:** accepted

## Context

"Do we even need an LLM?" is the right question, and the answer is **mostly no** — which is unusual
for a 2026 developer tool and is worth being precise about, because it is a competitive advantage
rather than a limitation.

Three of our four obligation sources need no model at all (structural, ledger, policy), and the
default `lx check` profile is LLM-free and costs **$0.00** (ADR-0015, D4). `lx audit`, the front door,
runs at the read-only tier. So a user can install Litmus64, audit their history, and gate every push
without ever configuring an API key.

The LLM earns its place in exactly three stages.

## Decision

### Where a model is genuinely used

| Stage | Job | Deterministic alternative? | Profile |
|---|---|---|---|
| **`reconstruct`** (intent) | Describe what the diff does *without seeing the stated intent*, then compare → `intent_agreement`, `unstated_changes` | **Partially** — see below | `--deep` |
| **`derive`** (inferred obligations) | PatchGuru-style oracle inference from PR body, issues, commit trailers | No | `--deep` |
| **`triage`** (self-review) | Classify each violation TP/FP with a written rationale and a minimal reproducer | No. **Non-optional** — PatchGuru's ablation shows precision collapsing 0.62 → 0.13 without it | `--deep` |

Everything else — the discrimination filter, differential attribution, mutation, property testing,
schedule search/replay, BMC, contract diff, coverage, risk, and the verdict itself — is deterministic
and unreachable from model output (Law 1).

### `unstated_changes` should be mostly deterministic, and currently isn't

Our single most quotable finding — *"the agent also changed something nobody asked about"* — was
specified as an LLM output. Most of it does not need to be:

1. The AST diff already knows, exactly and for free, that `TOKEN_CACHE_TTL` changed from `300` to `60`.
2. Whether anyone *asked* for it is largely a **symbol-mention test**: does the PR body, any linked
   issue, or any commit message mention that symbol, its identifier fragments (`token`, `cache`,
   `ttl`), or its file? That is deterministic string and token matching over the intent bundle.

So `unstated_changes` splits: a **deterministic core** (changed symbol, not mentioned anywhere in the
stated intent) that ships in the **read-only tier at zero cost**, plus an **LLM refinement** in
`--deep` that catches paraphrase ("reduced the cache lifetime" without naming the constant) and
suppresses false alarms.

This matters disproportionately: the killer demo becomes free, works with no API key, works
air-gapped, and works in `lx audit` over hundreds of commits without a token bill.

### Models

Reference default is **`claude-opus-5`**, with documented tiers so cost is the operator's choice and
not ours:

| Stage | Model | Config | Rationale |
|---|---|---|---|
| `reconstruct`, `derive` | `claude-opus-5` | `output_config: {effort: "high"}`, adaptive thinking, structured outputs | Reasoning quality directly sets obligation precision — the hardest number in §12 |
| `triage` | `claude-opus-5` at `effort: "low"`, or `claude-haiku-4-5` for cost-capped runs | structured outputs, `strict: true` | Bounded classification with a rationale. High volume, so it is where cost actually accumulates |

Pricing at time of writing (per MTok in/out): Opus 5 **$5 / $25**; Sonnet 5 **$3 / $15**; Haiku 4.5
**$1 / $5**. Published in `spec/budgets.md` alongside the token arithmetic so the `--deep` ≤ $0.50
budget is checkable rather than asserted.

Provider abstraction stays one trait (`ChatProvider`) with Anthropic as the reference, an
OpenAI-compatible implementation, and local via Ollama/llama.cpp. `no_egress: true` restricts the
registry to local providers **at construction time** — there is no runtime branch that could leak.
A "neutral standard" whose reference implementation hard-codes one vendor is not neutral.

### Three API facts that change the design

1. **Structured outputs are the quarantine boundary.** `output_config: {format: {...}}` plus
   `strict: true` on tool definitions means the quarantined channel's "output MUST deserialize into a
   caller-supplied schema or the call fails" is enforced by the API, not by our parser. This is
   exactly the CaMeL typed-data channel, and we should use the platform feature rather than
   post-hoc validation.
2. **The Batch API is a 50% discount, and `lx audit` is its ideal workload.** Auditing 200 commits of
   history is not latency-sensitive. `lx audit --deep` should submit as a batch.
3. **Token counting is a real endpoint.** `lx check --dry-run` promises a cost estimate before
   spending anything; that estimate must come from `messages.count_tokens`, never from a local
   tokenizer approximation, or the promise is a guess wearing a number.

### The bug this uncovered

`CODEBASE.md` specified:

> `PinnedSampling` forbids unspecified temperature — reproducibility requires that the sampling
> parameters are part of the record.

**`temperature`, `top_p`, and `top_k` are removed on Claude Opus 5, Sonnet 5, and Fable 5 — sending
any of them returns a 400.** As specified, `PinnedSampling` would have failed against every current
Claude model, and the reproducibility record would have pinned parameters that no longer exist.

The reasoning-quality knob is now `output_config.effort` (`low`…`max`) plus the thinking mode. So the
reproducibility record is:

```rust
pub struct PinnedGeneration {
    model: ModelId,            // exact id, never a date-suffixed guess
    effort: Effort,            // low | medium | high | xhigh | max
    thinking: ThinkingMode,    // adaptive | disabled (where the model permits)
    format_digest: Digest,     // digest of the output schema — part of the contract
}
```

Note what this means honestly: **LLM stages are not bit-reproducible even with everything pinned.**
That is why Law 8 requires every model call to be followed by a deterministic filter, and why the
byte-identical-receipt gate applies to the deterministic core. The receipt records what was pinned so
a reader knows *what varied*, not so they can replay the sampling. Claiming otherwise would be the
kind of overclaim we reject elsewhere.

## Consequences

**Good.** The free tier gets stronger: the flagship finding moves from `--deep` to read-only. The cost
ceiling becomes defensible with published arithmetic. And a bug that would have 400'd on first contact
with the API is fixed before any code exists.

**Bad.** Two implementations of `unstated_changes` (deterministic core plus LLM refinement) that must
agree, needing a test asserting the LLM layer only ever *adds* findings or *suppresses* with a
recorded rationale — never silently contradicts the deterministic layer.

## Rejected

- **No LLM at all.** Loses intent reconstruction, inferred obligations, and triage — and dropping
  triage collapses precision 0.62 → 0.13 by the literature's own ablation.
- **LLM everywhere, including the verdict.** Law 1. Non-negotiable and architecturally prevented.
- **Pinning `temperature: 0` for reproducibility.** Returns a 400 on every current model, and would
  have implied a reproducibility guarantee we cannot make anyway.
- **A local model as the reference.** Quality on obligation inference is the constraint; local stays
  fully supported for zero-egress deployments and is measured separately in §12.
