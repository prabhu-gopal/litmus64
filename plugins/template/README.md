# template

Subprocess plugin: `capabilities` | `plan` | `run` over JSON on stdio.
Contract: [`../CONTRACT.md`](../CONTRACT.md), schema: `spec/plugin-v0.1.schema.json`
(not generated yet — this plugin follows the shapes documented in
`CONTRACT.md` §"Three subcommands" until the Rust-generated schema lands).

This is the **reference implementation** of the plugin contract, not a real
language toolchain. It exists so a new plugin author has something to copy
and a contributor can verify the contract itself — determinism, honest
capability declarations, graceful skips — without installing anything beyond
Python 3's standard library.

## Run it

```bash
echo '{}' | python3 plugin.py capabilities
echo '{"workspace":"."}' | python3 plugin.py plan
```

`run` expects the task from `plan` plus an already-captured execution
result, since a plugin never spawns its own process (contract rule 4):

```bash
python3 - <<'PY'
import json, subprocess
task = json.loads(subprocess.run(
    ["python3", "plugin.py", "plan"], input="{}", capture_output=True, text=True
).stdout)["tasks"][0]
proc = subprocess.run(task["command"], capture_output=True, text=True)
execution = {"exit_code": proc.returncode, "stdout": proc.stdout}
print(subprocess.run(
    ["python3", "plugin.py", "run"],
    input=json.dumps({"task": task, "execution": execution}),
    capture_output=True, text=True,
).stdout)
PY
```

## Conformance tests

```bash
python3 -m unittest discover -s tests
```

Covers the checklist from `CONTRACT.md`: capabilities are honest, `plan` is
deterministic, `run` is idempotent, no writes outside the workspace, a
missing toolchain is skipped rather than crashed, and the declared cost
class is within 2x of measured wall time. `TestNeverSpawnsItself` enforces
contract rule 4 structurally by scanning the source for subprocess calls,
not just by convention.

## Design notes and the research behind them

- **Host owns execution, plugin owns interpretation.** `plan` only emits a
  command; the engine runs it (in its sandbox, at its trust tier) and hands
  the captured stdout/exit code back to `run` for interpretation. This
  mirrors how the [Language Server
  Protocol](https://microsoft.github.io/language-server-protocol/) separates
  a language server (owns semantic knowledge) from the client that manages
  the actual process lifecycle — keeping subprocess management in one
  trusted place avoids every plugin having to reimplement sandboxing
  correctly, and is why contract rule 4 exists.
- **Never let interpretation output collide with transport.** LSP implementers
  learned this the hard way: a stray `print()` on stdout corrupts the
  message stream for whoever is parsing it. This plugin writes exactly one
  JSON object to stdout per invocation and nothing else; anything
  diagnostic belongs on stderr.
- **`plan`/`run` as pure functions.** Determinism (contract rule 1) and
  idempotency (the conformance checklist) fall out for free when both
  subcommands are pure functions of their JSON input — no wall-clock reads,
  no randomness, no filesystem state beyond what's in the request. The
  `seed` in `run`'s replay block is derived from the task id via SHA-256
  rather than sampled, for the same reason.
- **Honest capability declarations, not aspirational ones.** Mutation
  testing is reported as unavailable (`no_substrate`) rather than "ready",
  because this plugin ships no mutator. The empirical literature on mutation
  testing (e.g. Zhu et al., *"A systematic literature review of how mutation
  testing supports quality assurance processes,"* STVR 2018) treats mutation
  score as a genuinely useful but imperfect adequacy signal — which is
  exactly why a plugin claiming it without a real mutator would corrupt the
  one thing this project promises not to fabricate (Law 14: claiming a
  capability you lack is the one thing this project cannot tolerate).
