# Integrations

Each surface lands in its own directory when its tier arrives (`DECISIONS.md` D3). They are absent
rather than stubbed, because an empty directory implies work in progress where none has started.

| Surface | Tier | Note |
|---|---|---|
| `github-app/` | T2 | **Check Runs write access requires an App**, not an Action. Findings are batched to GitHub's 50-annotations-per-request limit and ranked by criticality, so the important annotation is never the one that got truncated |
| `github-action/` | T2 | Thin wrapper, pinned by digest |
| `hooks/claude-code/`, `codex/`, `cursor/`, `git/` | T1 | Self-verification *before* the PR exists is where the leverage is. The default `lx check` profile is LLM-free and ≤ 60 s precisely so a stop-hook can afford it |
| `gh-extension/` | T2 | `gh lx …` |
| `mcp/` | T1 | `lx.check`, `lx.explain`, `lx.replay`, `lx.ledger` — any agent can self-verify mid-task |
| `ci/{gitlab,buildkite,jenkins}/` | post-1.0 | Named in `ROADMAP.md`, not started |

## The rule for every surface

**One artifact, many renderers.** Every integration is a pure projection of the receipt and adds no
information of its own. If a surface needs a fact the receipt does not carry, the fix is the schema —
never a special case in the renderer.

And one PR comment, edited in place, collapsed by default. Never a comment storm: comment-per-finding
is the single most-hated review-bot behaviour and it is not a tradeoff we are willing to make.
