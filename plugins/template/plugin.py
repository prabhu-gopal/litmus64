#!/usr/bin/env python3
"""Litmus64 reference plugin: the contract in the smallest form that runs.

Implements the three subcommands from ../CONTRACT.md (capabilities, plan,
run) over JSON stdio. Deliberately not Rust, and deliberately not a real
language toolchain: it runs a small self-contained fixture (fixtures/suite.py)
so the contract itself -- determinism, honest capability declarations, and
graceful skips -- can be exercised and tested with zero external
dependencies. Copy this file as the starting point for a real plugin.

Design notes (see plugins/template/README.md for the research this is
grounded in):
  - Rule 4 of the contract ("you never spawn a process yourself") is
    enforced structurally here, not just by convention: this file contains
    no subprocess/os.exec call. `plan` only emits a command; the caller
    (the engine, or this repo's conformance tests standing in for it) is
    the one that executes it and hands the captured output to `run`.
  - `plan` and `run` are pure functions of their JSON input, which is what
    makes determinism (rule 1) and idempotency free rather than something
    that has to be carefully maintained.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent
FIXTURE_SUITE = PLUGIN_DIR / "fixtures" / "suite.py"

# Name of an optional, workspace-provided script. Its presence/absence is
# what the graceful-skip conformance test exercises: a plugin must not
# fabricate a task for evidence it cannot actually produce (contract rule 2,
# Law 6), it must report why in `skipped`.
OPTIONAL_FIXTURE_NAME = "litmus_template_checks.py"

# The full, honest capability set for this plugin. Every command emitted by
# `plan` must be drawn from `commands` -- anything else is DENIED by the
# engine's sandbox (see CONTRACT.md rule 4). Mutation is reported as
# unavailable rather than "ready", because this plugin ships no mutator
# (contract rule 3 / Law 14: claiming a capability you lack is not tolerated).
CAPABILITIES: dict[str, Any] = {
    "languages": ["template"],
    "evidence_kinds": ["existing_suite", "generated_test", "mutation"],
    "mechanisms": {
        "differential": "ready",
        "mutation": {
            "no_substrate": "template plugin ships no mutator; add one before claiming mutation"
        },
    },
    "commands": ["python3"],
    "requires_network": False,
    "cost_class": "low",
}


def cmd_capabilities(_request: dict[str, Any]) -> dict[str, Any]:
    return CAPABILITIES


def cmd_plan(request: dict[str, Any]) -> dict[str, Any]:
    """Deterministic: same `request` always yields the same tasks in the
    same order (contract rule 1)."""
    workspace = Path(request.get("workspace", "."))

    tasks = [
        {
            "id": "t1",
            "kind": "existing_suite",
            # Measured empirically (median of 5 runs, see tests/test_contract.py)
            # at ~15ms on a warm interpreter; declared with headroom so the
            # rule-5 2x check tolerates normal machine-to-machine variance.
            "cost_estimate_ms": 25,
            "command": ["python3", str(FIXTURE_SUITE)],
            "cwd": str(PLUGIN_DIR),
        }
    ]
    skipped: list[dict[str, Any]] = []

    optional = workspace / OPTIONAL_FIXTURE_NAME
    if optional.is_file():
        tasks.append(
            {
                "id": "t2",
                "kind": "generated_test",
                "cost_estimate_ms": 50,
                "command": ["python3", str(optional)],
                "cwd": str(workspace),
            }
        )
    else:
        skipped.append(
            {
                "id": "t2",
                "reason": "missing_toolchain",
                "detail": f"{OPTIONAL_FIXTURE_NAME} not found in workspace root",
                "install_hint": (
                    f"add {OPTIONAL_FIXTURE_NAME} to the workspace root to "
                    "enable generated_test evidence"
                ),
            }
        )

    return {"tasks": tasks, "skipped": skipped}


def _env_digest(command: list[str], cwd: str) -> str:
    payload = json.dumps({"command": command, "cwd": cwd}, sort_keys=True).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _seed_for(task_id: str) -> int:
    # Derived, not random: two runs of `run` on the same task must agree.
    return int(hashlib.sha256(task_id.encode()).hexdigest()[:8], 16)


def cmd_run(request: dict[str, Any]) -> dict[str, Any]:
    """Idempotent: same `request` always yields byte-identical output
    (conformance requirement in ../CONTRACT.md). `request` carries the task
    from `plan` plus the *already captured* execution result -- this plugin
    never spawns the process itself (contract rule 4)."""
    task = request["task"]
    execution = request["execution"]
    command = task["command"]
    cwd = task.get("cwd", ".")

    replay = {
        "command": command,
        "env_digest": _env_digest(command, cwd),
        "seed": _seed_for(task["id"]),
    }

    stdout = execution.get("stdout", "")
    exit_code = execution["exit_code"]

    if "RESULT:" not in stdout:
        return {
            "skipped": {
                "reason": "unparseable_output",
                "detail": "expected a 'RESULT: n/m passed' line from the fixture runner",
            }
        }

    result = "pass" if exit_code == 0 else "fail"
    return {
        "result": result,
        "replay": replay,
        "artifacts": [{"kind": "stdout", "content": stdout}],
    }


DISPATCH = {"capabilities": cmd_capabilities, "plan": cmd_plan, "run": cmd_run}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in DISPATCH:
        print("usage: plugin.py {capabilities|plan|run} < request.json", file=sys.stderr)
        return 2

    raw = sys.stdin.read()
    request = json.loads(raw) if raw.strip() else {}
    result = DISPATCH[argv[1]](request)
    json.dump(result, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
