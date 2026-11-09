from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "tools" / "check-cost-audit.py"
SPEC = importlib.util.spec_from_file_location("check_cost_audit", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class CheckModelsTests(unittest.TestCase):
    def test_case_counts_and_differences(self) -> None:
        result = checker.check_models()
        self.assertEqual(result["rush"]["cases"], 1744)
        self.assertEqual(result["rush"]["differencesFromProposedCeilingPolicy"], 210)
        self.assertEqual(result["ai"]["cases"], 1744)
        self.assertEqual(result["ai"]["differencesFromNativeHumanRush"], 1668)
        self.assertEqual(result["fleet"]["cases"], 24)
        self.assertEqual(result["fleet"]["differencesFromPerRecordPolicy"], 8)
        self.assertEqual(result["technology"]["cases"], 836)
        self.assertEqual(result["technology"]["differencesFromLateDivision"], 639)

    def test_controls_have_no_mismatches(self) -> None:
        controls = checker.check_models()["controls"]
        self.assertEqual(controls["roadCases"], 32)
        self.assertEqual(controls["interestCases"], 201)
        self.assertEqual(controls["mismatches"], 0)


class CommandLineTests(unittest.TestCase):
    def run_main(self, out: Path) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = checker.main(["--out", str(out)])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_writes_report_with_source_digests(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "models.json"
            code, _, _ = self.run_main(out)
            self.assertEqual(code, 0)
            report = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(
            set(report["sources"]),
            {f"manifests/{name}" for name in checker.SOURCE_MANIFESTS},
        )

    def test_refuses_to_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "models.json"
            out.write_text("keep", encoding="utf-8")
            code, _, stderr = self.run_main(out)
            self.assertEqual(code, 2)
            self.assertIn("refusing to overwrite", stderr)
            self.assertEqual(out.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
