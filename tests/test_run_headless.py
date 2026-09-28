from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DRIVER = REPO / "tools" / "run-headless.ps1"
SCRATCH = REPO / "docs" / "ai_agents" / "local" / ".tmp"


class RunHeadlessReadOnlyTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.work = Path(self.temporary.name)
        self.project = self.work / "project"
        self.project.mkdir()
        self.capture = self.work / "headless-args.json"
        self.fake = self.work / "fake-headless.ps1"
        self.fake.write_text(
            "param(\n"
            "  [Parameter(ValueFromRemainingArguments = $true)]\n"
            "  [string[]]$Arguments\n"
            ")\n"
            "$Arguments | ConvertTo-Json -Compress | Set-Content -LiteralPath "
            "$env:FAKE_ARGS_PATH -Encoding UTF8\n"
            "exit 0\n",
            encoding="ascii",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def run_driver(
        self,
        *extra_args: str,
        out_path: Path | None = None,
        log_path: Path | None = None,
        omit_log: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["FAKE_ARGS_PATH"] = str(self.capture)
        out_path = out_path or (self.work / "query.out")
        arguments = [
            "pwsh",
            "-NoProfile",
            "-File",
            str(DRIVER),
            "-Script",
            "DumpFunctions.java",
            "-ScriptPath",
            str(REPO / "ghidra"),
            "-HeadlessExecutable",
            str(self.fake),
            "-ProjectDir",
            str(self.project),
            "-ProjectName",
            "fixture",
        ]
        arguments.extend(("-Out", str(out_path)))
        if not omit_log:
            arguments.extend(("-LogPath", str(log_path or (self.work / "query.log"))))
        arguments.extend(extra_args)
        return subprocess.run(
            arguments,
            cwd=REPO,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_read_only(self, *extra_args: str) -> None:
        result = self.run_driver(*extra_args)
        log = self.work / "query.log"
        details = (
            result.stdout
            + result.stderr
            + (log.read_text(encoding="utf-8") if log.exists() else "")
        )
        self.assertEqual(result.returncode, 0, details)
        arguments = json.loads(self.capture.read_text(encoding="utf-8"))
        self.assertEqual(
            [argument.lower() for argument in arguments].count("-readonly"), 1
        )

    def test_omitted_read_only_switch_is_forwarded(self):
        self.assert_read_only()

    def test_explicit_read_only_switch_is_forwarded(self):
        self.assert_read_only("-ReadOnly")

    def test_explicit_false_read_only_switch_is_rejected(self):
        result = self.run_driver("-ReadOnly:$false")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be false", result.stderr)
        self.assertFalse(self.capture.exists())

    def test_equal_output_and_log_paths_are_rejected_before_invocation(self):
        output = self.work / "same.out"
        output.write_text("keep", encoding="ascii")
        result = self.run_driver(out_path=output, log_path=output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distinct paths", result.stderr)
        self.assertFalse(self.capture.exists())
        self.assertEqual(output.read_text(encoding="ascii"), "keep")

    def test_normalized_relative_and_absolute_collision_is_rejected(self):
        output = self.work / "nested" / "same.out"
        output.parent.mkdir()
        output.write_text("keep", encoding="ascii")
        relative = Path(os.path.relpath(output, REPO))
        result = self.run_driver(out_path=relative, log_path=output.resolve())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distinct paths", result.stderr)
        self.assertFalse(self.capture.exists())
        self.assertEqual(output.read_text(encoding="ascii"), "keep")

    def test_case_variant_collision_is_rejected_on_windows(self):
        output = self.work / "CaseVariant.out"
        output.write_text("keep", encoding="ascii")
        result = self.run_driver(
            out_path=output,
            log_path=Path(str(output).lower()),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("distinct paths", result.stderr)
        self.assertFalse(self.capture.exists())
        self.assertEqual(output.read_text(encoding="ascii"), "keep")

    def test_default_headless_log_derivation_remains_distinct(self):
        output = self.work / "query.headless.log"
        output.write_text("keep", encoding="ascii")
        result = self.run_driver(out_path=output, omit_log=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.capture.exists())
        self.assertTrue((self.work / "query.headless.headless.log").exists())
        self.assertEqual(output.read_text(encoding="ascii"), "keep")


if __name__ == "__main__":
    unittest.main()
