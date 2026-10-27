from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "tools" / "reference_data.py"
SPEC = importlib.util.spec_from_file_location("reference_data", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
reference_data = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = reference_data
SPEC.loader.exec_module(reference_data)


class ReferenceDataTests(unittest.TestCase):
    def prepare_repository(self, *, markdown: bool = False) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        (self.repo / "data").mkdir()
        (self.repo / "manifests").mkdir()
        inputs = [
            "data/civilizations.csv",
            "data/era-bonus-definitions.csv",
            "data/achievements.json",
            "manifests/civilization-bonus-storage.json",
        ]
        if markdown:
            (self.repo / "docs" / "reference").mkdir(parents=True)
            inputs.extend(
                (
                    "docs/reference/civilization-bonuses.md",
                    "docs/reference/achievements.md",
                )
            )
        for relative in inputs:
            source = REPO / relative
            destination = self.repo / relative
            shutil.copyfile(source, destination)

    def _replace(self, relative: str, old: str, new: str) -> None:
        path = self.repo / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_repository_data_and_markdown_are_synchronized(self) -> None:
        data = reference_data.check_repository(REPO)
        self.assertEqual(len(data.civilizations), 16)
        self.assertEqual(len(data.bonus_effects), 45)
        self.assertEqual(
            tuple(row.achievement_id for row in data.achievements), tuple(range(5, 55))
        )
        self.assertEqual(
            data.achievements[43].unachieved_description,
            "Win 20 battles with one unit.\r\n",
        )

    def test_csv_field_guards(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.csv"
            for label, contents, diagnostic in (
                ("header", "wrong,value\n1,valid\n", "expected headers id,value"),
                ("extra", "id,value\n1,valid,extra\n", "extra CSV field"),
                ("missing", "id,value\n1\n", "value is required"),
                ("empty", "id,value\n1,\n", "value is required"),
                ("whitespace", "id,value\n1, padded\n", "outer whitespace"),
                ("pipe", "id,value\n1,a|b\n", "not Markdown-safe"),
                ("newline", 'id,value\n1,"a\nb"\n', "not Markdown-safe"),
            ):
                with self.subTest(case=label):
                    path.write_text(contents, encoding="utf-8")
                    with self.assertRaisesRegex(
                        reference_data.ReferenceDataError, diagnostic
                    ):
                        reference_data._read_csv(path, ("id", "value"))

    def test_rewrite_preserves_prose_and_then_returns_unchanged(self) -> None:
        self.prepare_repository(markdown=True)
        path = self.repo / "docs" / "reference" / "civilization-bonuses.md"
        expected = (
            "Before the tables.\n"
            + path.read_text(encoding="utf-8")
            + "After the tables.\n"
        )
        path.write_text(
            expected.replace("Factories provide triple Production", "stale effect"),
            encoding="utf-8",
        )
        _, changed = reference_data.write_repository(self.repo)
        self.assertTrue(changed)
        self.assertEqual(path.read_text(encoding="utf-8"), expected)
        before = path.read_bytes()
        _, changed = reference_data.write_repository(self.repo)
        self.assertFalse(changed)
        self.assertEqual(path.read_bytes(), before)

    def test_duplicate_civilization_id_is_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/civilizations.csv",
            "1,Egyptian,Egyptian",
            "0,Egyptian,Egyptian",
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "unique and ordered"
        ):
            reference_data.load_reference_data(self.repo)

    def test_populated_starting_bonus_id_is_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/civilizations.csv",
            "Julius Caesar,,Code of Laws",
            "Julius Caesar,99,Code of Laws",
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "starting_bonus_id must remain blank"
        ):
            reference_data.load_reference_data(self.repo)

    def test_malformed_csv_is_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/civilizations.csv",
            "0,Roman,Roman,Julius Caesar",
            '0,"Roman,Roman,Julius Caesar',
        )
        with self.assertRaisesRegex(reference_data.ReferenceDataError, "malformed CSV"):
            reference_data.load_reference_data(self.repo)

    def test_generated_marker_in_csv_is_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/civilizations.csv",
            "An Ancient Wonder",
            reference_data.BONUS_TABLE_END,
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "contains a generated marker"
        ):
            reference_data.write_repository(self.repo)

    def test_conflicting_duplicate_bonus_definition_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "data" / "era-bonus-definitions.csv"
        with path.open("a", encoding="utf-8", newline="") as stream:
            stream.write("1,Conflicting road effect\n")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "duplicate bonus_id 1"
        ):
            reference_data.load_reference_data(self.repo)

    def test_out_of_order_bonus_definitions_are_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/era-bonus-definitions.csv",
            "1,Roads cost half as much\n2,Factories provide triple Production\n",
            "2,Factories provide triple Production\n1,Roads cost half as much\n",
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError,
            "bonus_id values must be numerically ordered",
        ):
            reference_data.load_reference_data(self.repo)

    def test_missing_assigned_bonus_definition_is_rejected(self) -> None:
        self.prepare_repository()
        self._replace(
            "data/era-bonus-definitions.csv",
            "61,Longbow Archers gain +1 defense\n",
            "",
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "missing assigned IDs 61"
        ):
            reference_data.load_reference_data(self.repo)

    def test_unused_bonus_definition_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "data" / "era-bonus-definitions.csv"
        with path.open("a", encoding="utf-8", newline="") as stream:
            stream.write("62,Unused effect\n")
        with self.assertRaisesRegex(reference_data.ReferenceDataError, "unused IDs 62"):
            reference_data.load_reference_data(self.repo)

    def test_manifest_name_disagreement_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["rows"][13]["name"] = "Zulu"
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "internal name.*disagrees"
        ):
            reference_data.load_reference_data(self.repo)

    def test_manifest_shape_disagreement_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["shape"]["civilizations"] = 15
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "unexpected storage.shape"
        ):
            reference_data.load_reference_data(self.repo)

    def test_manifest_rows_must_be_a_list(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["rows"] = {}
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "storage.rows must be a list"
        ):
            reference_data.load_reference_data(self.repo)

    def test_manifest_boolean_index_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["rows"][0]["index"] = False
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "invalid row index"
        ):
            reference_data.load_reference_data(self.repo)

    def test_manifest_row_order_is_rejected_by_loader(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["rows"][1]["index"] = 0
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "row indexes must be unique and ordered"
        ):
            reference_data.load_reference_data(self.repo)

    def test_manifest_boolean_bonus_id_is_rejected(self) -> None:
        self.prepare_repository()
        path = self.repo / "manifests" / "civilization-bonus-storage.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["storage"]["rows"][0]["bonuses"][0] = True
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "four positive bonus IDs"
        ):
            reference_data.load_reference_data(self.repo)

    def test_markdown_drift_is_rejected(self) -> None:
        self.prepare_repository(markdown=True)
        self._replace(
            "docs/reference/civilization-bonuses.md",
            "Factories provide triple Production",
            "Factories provide quadruple Production",
        )
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "rendered tables are stale"
        ):
            reference_data.check_repository(self.repo)

    def test_achievement_row_count_duplicate_and_renumbering_are_rejected(self) -> None:
        cases = (
            (
                "missing",
                lambda rows: rows.pop(),
                "achievements must contain 50 rows",
            ),
            (
                "duplicate",
                lambda rows: rows[1].__setitem__("id", 5),
                "achievement IDs must be unique and ordered",
            ),
            (
                "renumbered",
                lambda rows: rows[1].__setitem__("id", 55),
                "achievement IDs must be unique and ordered",
            ),
        )
        for label, mutate, diagnostic in cases:
            with self.subTest(case=label):
                self.prepare_repository()
                path = self.repo / "data" / "achievements.json"
                document = json.loads(path.read_text(encoding="utf-8"))
                mutate(document["achievements"])
                path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(
                    reference_data.ReferenceDataError, diagnostic
                ):
                    reference_data.load_reference_data(self.repo)

    def test_achievement_metadata_and_field_types_are_rejected(self) -> None:
        cases = (
            (
                "schema",
                lambda document: document.__setitem__("schemaVersion", 2),
                "schemaVersion must be 1",
            ),
            (
                "schema type",
                lambda document: document.__setitem__("schemaVersion", True),
                "schemaVersion must be 1",
            ),
            (
                "image",
                lambda document: document.__setitem__("image", "wrong.json"),
                "image must be",
            ),
            (
                "title",
                lambda document: document["source"].__setitem__("titleId", "wrong"),
                "unexpected source.titleId",
            ),
            (
                "extractor",
                lambda document: document["source"].__setitem__("extractor", ""),
                "source.extractor must be nonempty",
            ),
            (
                "digest",
                lambda document: document["source"].__setitem__(
                    "extractorSha256", "z" * 64
                ),
                "source.extractorSha256 must be SHA-256",
            ),
            (
                "language",
                lambda document: document["source"].__setitem__("languageId", True),
                "unexpected source.languageId",
            ),
            (
                "score",
                lambda document: document["achievements"][0].__setitem__(
                    "gamerscore", True
                ),
                "gamerscore must be",
            ),
            (
                "imageId",
                lambda document: document["achievements"][0].__setitem__(
                    "imageId", "21"
                ),
                "imageId must be",
            ),
            (
                "version",
                lambda document: document["source"].__setitem__(
                    "extractorVersion", "not a version"
                ),
                "source.extractorVersion must be a version",
            ),
            (
                "duplicate imageId",
                lambda document: document["achievements"][1].__setitem__("imageId", 21),
                "duplicate imageId",
            ),
            (
                "matching imageId",
                lambda document: document["achievements"][0].__setitem__("imageId", 5),
                "imageId must differ from id",
            ),
        )
        for label, mutate, diagnostic in cases:
            with self.subTest(case=label):
                self.prepare_repository()
                path = self.repo / "data" / "achievements.json"
                document = json.loads(path.read_text(encoding="utf-8"))
                mutate(document)
                path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(
                    reference_data.ReferenceDataError, diagnostic
                ):
                    reference_data.load_reference_data(self.repo)

    def test_achievement_trigger_status_and_mapped_evidence_are_validated(self) -> None:
        self.prepare_repository()
        path = self.repo / "data" / "achievements.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["achievements"][0]["unlockTrigger"]["status"] = "unknown"
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "invalid unlockTrigger.status"
        ):
            reference_data.load_reference_data(self.repo)

        document["achievements"][0]["unlockTrigger"]["status"] = "mapped"
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "requires resolving evidence"
        ):
            reference_data.load_reference_data(self.repo)

        evidence_path = self.repo / "manifests" / "achievement-fixture.json"
        evidence_path.write_text(
            '{"finding":{"status":"accepted","rows":[{"value":"first"},{"value":"second"}]}}',
            encoding="utf-8",
        )
        document["achievements"][0]["unlockTrigger"]["evidence"] = [
            "../manifests/achievement-fixture.json#/finding/status"
        ]
        path.write_text(json.dumps(document), encoding="utf-8")
        data = reference_data.load_reference_data(self.repo)
        self.assertEqual(data.achievements[0].trigger_status, "mapped")

        document["achievements"][0]["unlockTrigger"]["evidence"] = [
            {"locator": "../manifests/achievement-fixture.json#/finding/status"}
        ]
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "locator must be a string"
        ):
            reference_data.load_reference_data(self.repo)

        document["achievements"][0]["unlockTrigger"]["evidence"] = [
            "../manifests/achievement-fixture.json#/finding/missing"
        ]
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "does not resolve"
        ):
            reference_data.load_reference_data(self.repo)

        for pointer in ("/finding/rows/-1", "/finding/rows/01"):
            with self.subTest(pointer=pointer):
                document["achievements"][0]["unlockTrigger"]["evidence"][0] = (
                    f"../manifests/achievement-fixture.json#{pointer}"
                )
                path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(
                    reference_data.ReferenceDataError, "does not resolve"
                ):
                    reference_data.load_reference_data(self.repo)

    def test_achievement_markdown_is_stale_and_escapes_multiline_cells(self) -> None:
        self.prepare_repository(markdown=True)
        path = self.repo / "data" / "achievements.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["achievements"][43]["unachievedDescription"] = "line one|line two\r\n"
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError,
            "achievements.md: rendered tables are stale",
        ):
            reference_data.check_repository(self.repo)
        data = reference_data.load_reference_data(self.repo)
        rendered = reference_data._render_achievement_table(data)
        self.assertIn("line one\\|line two<br>", rendered)
        self.assertNotIn("line one|line two\r\n", rendered)

    def test_crossed_generated_markers_are_rejected(self) -> None:
        self.prepare_repository(markdown=True)
        path = self.repo / "docs" / "reference" / "civilization-bonuses.md"
        text = path.read_text(encoding="utf-8")
        begin = reference_data.BONUS_TABLE_BEGIN
        end = reference_data.BONUS_TABLE_END
        text = text.replace(begin, "MARKER_PLACEHOLDER", 1)
        text = text.replace(end, begin, 1)
        text = text.replace("MARKER_PLACEHOLDER", end, 1)
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(
            reference_data.ReferenceDataError, "crossed generated markers"
        ):
            reference_data.check_repository(self.repo)


if __name__ == "__main__":
    unittest.main()
