from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

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
        script = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("$stepOutput = @(& $headless @headlessArgs 2>&1)", script)
        self.assertIn("Add-Content -LiteralPath $LogPath -Encoding UTF8", script)
        self.assertIn(".Replace([string][char]0, '')", script)
        self.assertNotIn(">> $LogPath", script)

    def test_rebuild_error_helper_propagates_failure(self):
        source_text = (REPO / "ghidra" / "RebuildTruncatedFunctions.java").read_text(
            encoding="utf-8"
        )
        self.assertIn("requireNoErrors(err);", source_text)
        ghidra_home = os.environ.get("REREVVED_GHIDRA_HOME")
        javac = shutil.which("javac")
        java = shutil.which("java")
        if not ghidra_home or javac is None or java is None:
            self.skipTest("Ghidra and JDK are required for repair failure proof")
        jars = sorted(Path(ghidra_home).rglob("*.jar"))
        if not jars:
            self.skipTest("Ghidra jars are required for repair failure proof")
        scratch = REPO / "docs" / "ai_agents" / "local" / ".tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        fixture = Path(tempfile.mkdtemp(prefix="rebuild-errors-", dir=scratch))
        try:
            source = fixture / "RebuildFailureFixture.java"
            source.write_text(
                "public class RebuildFailureFixture {\n"
                "  public static void main(String[] args) {\n"
                "    try {\n"
                "      RebuildTruncatedFunctions.requireNoErrors(Integer.parseInt(args[0]));\n"
                '      System.out.println("accepted");\n'
                "    } catch (IllegalStateException expected) {\n"
                '      System.out.println("rejected");\n'
                "    }\n"
                "  }\n"
                "}\n",
                encoding="ascii",
            )
            classes = fixture / "classes"
            classes.mkdir()
            classpath = os.pathsep.join(str(path) for path in jars)
            compile_result = subprocess.run(
                [
                    javac,
                    "-proc:none",
                    "-encoding",
                    "UTF-8",
                    "-cp",
                    classpath,
                    "-d",
                    str(classes),
                    str(REPO / "ghidra" / "RebuildTruncatedFunctions.java"),
                    str(source),
                ],
                cwd=fixture,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            for errors, expected in (("0", "accepted"), ("1", "rejected")):
                run_result = subprocess.run(
                    [
                        java,
                        "-cp",
                        os.pathsep.join((str(classes), classpath)),
                        "RebuildFailureFixture",
                        errors,
                    ],
                    cwd=fixture,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(run_result.returncode, 0, run_result.stderr)
                self.assertEqual(run_result.stdout.strip(), expected)
        finally:
            fixture_path = fixture.resolve()
            if fixture_path.parent != scratch.resolve():
                raise AssertionError(
                    "refusing to remove fixture outside Ghidra scratch"
                )
            shutil.rmtree(fixture_path)


if __name__ == "__main__":
    unittest.main()
