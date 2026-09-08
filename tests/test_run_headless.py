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

    def run_driver(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["FAKE_ARGS_PATH"] = str(self.capture)
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
            "-Out",
            str(self.work / "query.out"),
            "-LogPath",
            str(self.work / "query.log"),
            *extra_args,
        ]
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
        details = result.stdout + result.stderr + (
            log.read_text(encoding="utf-8") if log.exists() else ""
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


if __name__ == "__main__":
    unittest.main()
