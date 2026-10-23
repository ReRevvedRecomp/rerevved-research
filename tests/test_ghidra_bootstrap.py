from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from java_test_support import JavaFixture, java_method

REPO = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO / "tools" / "bootstrap-ghidra.ps1"


class GhidraBootstrapTests(unittest.TestCase):
    def run_bootstrap(self, *args: str) -> subprocess.CompletedProcess[str]:
        command = [
            shutil.which("pwsh") or shutil.which("powershell") or "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(BOOTSTRAP),
            *args,
        ]
        environment = os.environ.copy()
        environment["REREVVED_GHIDRA_PROJECTS"] = str(REPO / "canonical")
        environment["REREVVED_GHIDRA_PROJECT"] = "canonical"
        return subprocess.run(
            command,
            cwd=REPO,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def plan_args(
        self,
        project_dir: Path | None = None,
        project_name: str = "disposable",
    ) -> tuple[str, ...]:
        disposable = project_dir or (REPO / "disposable-plan")
        return (
            "-Plan",
            "-DisposableProjectDir",
            str(disposable),
            "-DisposableProjectName",
            project_name,
            "-Out",
            str(REPO / "tests" / "plan-result.json"),
            "-LogPath",
            str(REPO / "tests" / "plan-headless.log"),
            "-CanonicalProjectDir",
            str(REPO / "canonical"),
            "-CanonicalProjectName",
            "canonical",
        )

    def test_plan_preserves_repair_order_without_writing(self):
        result = self.run_bootstrap(*self.plan_args())
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["Mode"], "Plan")
        self.assertEqual(
            plan["Scripts"],
            [
                "FixXenonThunks.java",
                "RebuildTruncatedFunctions.java",
                "RecoverSplitConstRefs.java",
            ],
        )
        self.assertFalse((REPO / "tests" / "plan-result.json").exists())
        self.assertFalse((REPO / "tests" / "plan-headless.log").exists())

    def test_plan_refuses_configured_canonical_project(self):
        result = self.run_bootstrap(
            *self.plan_args(project_dir=REPO / "canonical", project_name="canonical")
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("configured canonical project", result.stderr)

    def test_plan_prepends_generated_function_seed(self):
        function_map = REPO / "tests" / "generated-init.cpp"
        result = self.run_bootstrap(
            *self.plan_args(),
            "-FunctionMap",
            str(function_map),
            "-CodeSeedSites",
            "0x8269CAE0,0x8269CAE4",
            "-ConstRefAcceptTarget",
            "0x821B15C0",
            "-ConstRefAcceptSites",
            "0x82DAB144,0x82DAB14C,0x82DAB154",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["Scripts"][2], "SeedGeneratedFunctions.java")
        self.assertEqual(plan["FunctionMap"], str(function_map.resolve()))
        self.assertEqual(plan["CodeSeedSites"], "0x8269CAE0,0x8269CAE4")
        self.assertEqual(plan["ConstRefAcceptTarget"], "0x821B15C0")
        self.assertEqual(
            plan["ConstRefAcceptSites"],
            "0x82DAB144,0x82DAB14C,0x82DAB154",
        )

    def test_disposable_project_must_be_explicit(self):
        result = self.run_bootstrap(
            "-Plan",
            "-DisposableProjectName",
            "disposable",
            "-Out",
            str(REPO / "tests" / "missing-project-result.json"),
            "-LogPath",
            str(REPO / "tests" / "missing-project.log"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Disposable project directory is required", result.stderr)

    def test_code_seeds_require_function_map(self):
        result = self.run_bootstrap(*self.plan_args(), "-CodeSeedSites", "0x8269CAE0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("require a generated function map", result.stderr)

    def test_constref_acceptance_requires_target_and_sites(self):
        result = self.run_bootstrap(
            *self.plan_args(), "-ConstRefAcceptTarget", "0x821B15C0"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires both target and sites", result.stderr)

    def test_execution_log_is_written_as_utf8(self):
        scratch = REPO / "docs" / "ai_agents" / "local" / ".tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temporary:
            root = Path(temporary)
            fake = root / "fake-headless.ps1"
            output = root / "plan.json"
            log = root / "headless.log"
            for label, marker, exit_code, diagnostic in (
                ("exit", "", 7, "exit code 7"),
                ("script", "SCRIPT ERROR", 0, "script failure"),
            ):
                with self.subTest(case=label):
                    fake.write_text(
                        "param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)\n"
                        "$Arguments[-1]\n"
                        "'caf' + [char]0xE9 + [char]0 + '-tail'\n"
                        f"'{marker}'\nexit {exit_code}\n",
                        encoding="ascii",
                    )
                    result = self.run_bootstrap(
                        "-DisposableProjectDir",
                        str(root),
                        "-DisposableProjectName",
                        "disposable",
                        "-Out",
                        str(output),
                        "-LogPath",
                        str(log),
                        "-HeadlessExecutable",
                        str(fake),
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(diagnostic, result.stderr)
                    data = log.read_bytes()
                    self.assertIn(b"caf\xc3\xa9-tail", data)
                    self.assertNotIn(b"\0", data)
                    text = data.decode("utf-8-sig")
                    self.assertIn("FixXenonThunks.java", text)
                    self.assertNotIn("RebuildTruncatedFunctions.java", text)
                    self.assertNotIn("RecoverSplitConstRefs.java", text)
                    self.assertFalse(output.exists())

    def test_plan_rejects_partial_thunk_ranges_and_canonical_configuration(self):
        for option in ("-ThunkRangeStart", "-ThunkRangeEnd"):
            with self.subTest(option=option):
                result = self.run_bootstrap(*self.plan_args(), option, "0x8269CAE0")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Thunk range requires both start and end", result.stderr)
        for option in ("-CanonicalProjectDir", "-CanonicalProjectName"):
            with self.subTest(option=option):
                arguments = list(self.plan_args())
                arguments[arguments.index(option) + 1] = " "
                result = self.run_bootstrap(*arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must provide both directory and name", result.stderr)

    def test_plan_rejects_normalized_output_log_collision(self):
        arguments = list(self.plan_args())
        arguments[arguments.index("-LogPath") + 1] = str(
            Path("tests") / "plan-result.json"
        )
        result = self.run_bootstrap(*arguments)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be different files", result.stderr)

    def test_rebuild_error_helper_propagates_failure(self):
        source = (REPO / "ghidra" / "RebuildTruncatedFunctions.java").read_text(
            encoding="utf-8"
        )
        method = java_method(source, "static void requireNoErrors(")
        fixture = JavaFixture(
            self,
            {
                "RebuildFailureFixture.java": "public class RebuildFailureFixture {\n"
                + method
                + "\n"
                "  public static void main(String[] args) {\n"
                "    try {\n"
                "      requireNoErrors(Integer.parseInt(args[0]));\n"
                '      System.out.println("accepted");\n'
                "    } catch (IllegalStateException expected) {\n"
                '      System.out.println("rejected");\n'
                "    }\n"
                "  }\n"
                "}\n"
            },
        )
        for errors, expected in (("0", "accepted"), ("1", "rejected")):
            with self.subTest(errors=errors):
                result = fixture.run("RebuildFailureFixture", errors)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), expected)


if __name__ == "__main__":
    unittest.main()
