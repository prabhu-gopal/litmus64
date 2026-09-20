"""Conformance tests for plugins/template, mirroring the checklist in
../../CONTRACT.md: capabilities are honest, `plan` is deterministic, `run`
is idempotent, no writes outside the workspace, declared cost is within 2x
of measured, and a missing toolchain is skipped rather than panicking.

Stdlib only (subprocess + unittest) -- a plugin author copying this template
should not need to `pip install` anything to verify their fork still
conforms.

Run with: python3 -m unittest discover -s plugins/template/tests
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
PLUGIN = PLUGIN_DIR / "plugin.py"


def invoke(subcommand: str, request: dict | None = None) -> dict:
    proc = subprocess.run(
        [sys.executable, str(PLUGIN), subcommand],
        input=json.dumps(request or {}),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def invoke_raw(subcommand: str, request: dict | None = None) -> str:
    proc = subprocess.run(
        [sys.executable, str(PLUGIN), subcommand],
        input=json.dumps(request or {}),
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


class TestCapabilitiesHonesty(unittest.TestCase):
    def test_shape_and_required_fields(self):
        caps = invoke("capabilities")
        for key in ("languages", "evidence_kinds", "mechanisms", "commands",
                    "requires_network", "cost_class"):
            self.assertIn(key, caps)
        self.assertIn(caps["cost_class"], {"low", "medium", "high"})
        self.assertIsInstance(caps["requires_network"], bool)

    def test_unready_mechanisms_carry_a_reason_not_a_lie(self):
        # Law 14: a mechanism that isn't "ready" must explain why, not be
        # silently omitted or falsely marked ready.
        caps = invoke("capabilities")
        mutation = caps["mechanisms"]["mutation"]
        self.assertNotEqual(mutation, "ready")
        self.assertIn("no_substrate", mutation)

    def test_every_planned_command_is_in_the_allowlist(self):
        caps = invoke("capabilities")
        allowlist = set(caps["commands"])
        with tempfile.TemporaryDirectory() as workspace:
            plan = invoke("plan", {"workspace": workspace})
        for task in plan["tasks"]:
            self.assertIn(task["command"][0], allowlist)


class TestPlanDeterminism(unittest.TestCase):
    def test_same_input_same_output_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as workspace:
            request = {"workspace": workspace}
            first = invoke_raw("plan", request)
            second = invoke_raw("plan", request)
        self.assertEqual(first, second)

    def test_task_order_is_stable(self):
        with tempfile.TemporaryDirectory() as workspace:
            plan = invoke("plan", {"workspace": workspace})
        ids = [t["id"] for t in plan["tasks"]]
        self.assertEqual(ids, sorted(ids))


class TestGracefulSkip(unittest.TestCase):
    def test_missing_optional_fixture_is_skipped_not_crashed(self):
        with tempfile.TemporaryDirectory() as workspace:
            plan = invoke("plan", {"workspace": workspace})
        self.assertEqual(len(plan["skipped"]), 1)
        skip = plan["skipped"][0]
        self.assertEqual(skip["reason"], "missing_toolchain")
        self.assertIn("detail", skip)
        self.assertIn("install_hint", skip)

    def test_present_optional_fixture_is_planned_not_skipped(self):
        with tempfile.TemporaryDirectory() as workspace:
            (Path(workspace) / "litmus_template_checks.py").write_text(
                "print('RESULT: 0/0 passed')\n"
            )
            plan = invoke("plan", {"workspace": workspace})
        self.assertEqual(plan["skipped"], [])
        self.assertEqual({t["id"] for t in plan["tasks"]}, {"t1", "t2"})


class TestRunIdempotency(unittest.TestCase):
    def _task_and_execution(self):
        with tempfile.TemporaryDirectory() as workspace:
            plan = invoke("plan", {"workspace": workspace})
        task = plan["tasks"][0]
        proc = subprocess.run(task["command"], capture_output=True, text=True)
        execution = {"exit_code": proc.returncode, "stdout": proc.stdout}
        return task, execution

    def test_same_input_same_output(self):
        task, execution = self._task_and_execution()
        request = {"task": task, "execution": execution}
        first = invoke_raw("run", request)
        second = invoke_raw("run", request)
        self.assertEqual(first, second)

    def test_passing_fixture_reports_pass_with_replay(self):
        task, execution = self._task_and_execution()
        result = invoke("run", {"task": task, "execution": execution})
        self.assertEqual(result["result"], "pass")
        self.assertTrue(result["replay"]["env_digest"].startswith("sha256:"))
        self.assertIsInstance(result["replay"]["seed"], int)

    def test_unparseable_output_is_skipped_not_misreported(self):
        task, _ = self._task_and_execution()
        execution = {"exit_code": 0, "stdout": "nothing structured here"}
        result = invoke("run", {"task": task, "execution": execution})
        self.assertIn("skipped", result)
        self.assertEqual(result["skipped"]["reason"], "unparseable_output")


class TestNeverSpawnsItself(unittest.TestCase):
    def test_source_contains_no_subprocess_call(self):
        # Structural enforcement of contract rule 4: the engine spawns the
        # sandboxed process, never the plugin. Only scans code lines (not
        # comments/docstrings, which are free to discuss the rule by name).
        code_lines = [
            line for line in (PLUGIN_DIR / "plugin.py").read_text().splitlines()
            if not line.strip().startswith("#")
        ]
        code = "\n".join(code_lines)
        for forbidden in ("subprocess.", "os.system(", "os.popen(", "os.spawn"):
            self.assertNotIn(forbidden, code)


class TestNoWritesOutsideWorkspace(unittest.TestCase):
    def test_plugin_directory_untouched_by_any_subcommand(self):
        before = {
            p: p.stat().st_mtime_ns
            for p in PLUGIN_DIR.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
        with tempfile.TemporaryDirectory() as workspace:
            invoke("capabilities")
            invoke("plan", {"workspace": workspace})
        after = {
            p: p.stat().st_mtime_ns
            for p in PLUGIN_DIR.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }
        self.assertEqual(before, after)


class TestCostClassWithinTolerance(unittest.TestCase):
    def test_declared_estimate_within_2x_of_measured(self):
        with tempfile.TemporaryDirectory() as workspace:
            plan = invoke("plan", {"workspace": workspace})
        task = plan["tasks"][0]

        samples = []
        for _ in range(5):
            start = time.monotonic()
            subprocess.run(task["command"], capture_output=True, text=True, check=True)
            samples.append((time.monotonic() - start) * 1000)
        samples.sort()
        measured_ms = max(samples[len(samples) // 2], 1.0)  # median, damps outliers
        declared_ms = max(task["cost_estimate_ms"], 1.0)

        ratio = max(measured_ms, declared_ms) / min(measured_ms, declared_ms)
        self.assertLessEqual(
            ratio, 2.0,
            f"declared {declared_ms}ms vs measured {measured_ms:.1f}ms exceeds 2x (contract rule 5)",
        )


if __name__ == "__main__":
    unittest.main()
