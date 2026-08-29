from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import validate_native_renderer_d3d_inventory as validator  # noqa: E402


MANIFEST = REPO / "manifests" / "native-renderer-d3d-inventory.json"
TEST_COMMIT = "a" * 40


class NativeRendererD3DInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.sha256 = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()

    def assert_invalid(self, document: dict) -> None:
        with self.assertRaises(validator.ValidationError):
            validator.validate_document(document, REPO)

    def test_committed_aggregate_and_deterministic_partial_export_pass(self) -> None:
        validator.validate_document(self.document, REPO)
        first = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        second = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        self.assertEqual(first, second)
        self.assertEqual(first["surface"], "partial")
        self.assertEqual(
            first["image_sha256"],
            "5C7A8C3AD9B6A9D39CC9BBF3DA5AB23015A568C65C723D298F846086324C4680",
        )
        self.assertEqual(first["operations"][0]["registers"], [])
        for field, value in self.document["partialExport"].items():
            self.assertTrue(validator._json_deep_equal(first[field], value))
        self.assertEqual(
            self.document["unresolvedCoverage"]["categories"],
            validator.UNRESOLVED_COVERAGE_CATEGORIES,
        )
        self.assertEqual(
            self.document["unresolvedCoverage"]["evidenceBasis"],
            validator.EXPECTED_UNRESOLVED_COVERAGE["evidenceBasis"],
        )

    def test_top_level_copy_pointers_are_exact_and_value_equal(self) -> None:
        partial_export = self.document["partialExport"]
        for field in ("schema_version", "image_sha256", "surface"):
            pointer = partial_export["source_pointers"][field]
            self.assertEqual(pointer, f"#/partialExport/{field}")
            self.assertTrue(
                validator._json_deep_equal(
                    validator._json_pointer(self.document, pointer),
                    partial_export[field],
                )
            )

    def test_top_level_resolvable_wrong_and_noncanonical_pointers_fail(self) -> None:
        replacements = {
            "schema_version": "#/schemaVersion",
            "image_sha256": "#/image",
            "surface": "#/scope/surface",
        }
        for field, pointer in replacements.items():
            document = copy.deepcopy(self.document)
            document["partialExport"]["source_pointers"][field] = pointer
            with self.subTest(field=field, pointer=pointer):
                self.assert_invalid(document)

        mutations = []
        missing = copy.deepcopy(self.document)
        del missing["partialExport"]["source_pointers"]["surface"]
        mutations.append(missing)
        extra = copy.deepcopy(self.document)
        extra["partialExport"]["source_pointers"]["extra"] = "#/partialExport/surface"
        mutations.append(extra)
        relative = copy.deepcopy(self.document)
        relative["partialExport"]["source_pointers"]["surface"] = "surface"
        mutations.append(relative)
        container = copy.deepcopy(self.document)
        container["partialExport"]["source_pointers"]["surface"] = "#/partialExport"
        mutations.append(container)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

    def test_image_sha256_must_match_canonical_image_manifest(self) -> None:
        for value in (
            "5c7a8c3ad9b6a9d39cc9bbf3da5ab23015a568c65c723d298f846086324c4680",
            "0" * 64,
            True,
        ):
            document = copy.deepcopy(self.document)
            document["partialExport"]["image_sha256"] = value
            with self.subTest(value=value):
                self.assert_invalid(document)

    def test_operation_resolvable_wrong_prose_and_container_pointers_fail(self) -> None:
        replacements = {
            "runtime_join_key": "#/partialExport/operations/0/operation_id",
            "hook_sites": "#/contracts/0/reproduction",
            "value_domains": "#/contracts/0/hostRequirement",
            "registers": "#/contracts/0",
            "resource_action": "#/contracts/0",
            "roles": "#/surface/1/roles",
            "claim_refs": "#/partialExport/operations/0",
        }
        for field, pointer in replacements.items():
            document = copy.deepcopy(self.document)
            document["partialExport"]["operations"][0]["source_pointers"][field] = pointer
            with self.subTest(field=field, pointer=pointer):
                self.assert_invalid(document)

    def test_operation_pointer_map_rejects_missing_extra_and_relative(self) -> None:
        mutations = []
        missing = copy.deepcopy(self.document)
        del missing["partialExport"]["operations"][0]["source_pointers"]["hook_sites"]
        mutations.append(missing)
        extra = copy.deepcopy(self.document)
        extra["partialExport"]["operations"][0]["source_pointers"]["extra"] = (
            "#/partialExport/operations/0/roles"
        )
        mutations.append(extra)
        relative = copy.deepcopy(self.document)
        relative["partialExport"]["operations"][0]["source_pointers"]["roles"] = "roles"
        mutations.append(relative)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

    def test_recursive_json_equality_is_type_order_and_key_sensitive(self) -> None:
        self.assertFalse(validator._json_deep_equal(True, 1))
        self.assertFalse(validator._json_deep_equal([1, 2], [2, 1]))
        self.assertFalse(validator._json_deep_equal({"a": 1}, {"b": 1}))
        self.assertTrue(
            validator._json_deep_equal(
                {"a": [1, {"b": None}]},
                {"a": [1, {"b": None}]},
            )
        )

    def test_copy_helper_uses_sentinel_values_without_semantic_defaults(self) -> None:
        document = copy.deepcopy(self.document)
        partial_export = document["partialExport"]
        partial_export["schema_version"] = True
        partial_export["image_sha256"] = "sentinel-image"
        partial_export["surface"] = "sentinel-surface"
        operation = partial_export["operations"][0]
        sentinels = {
            "operation_id": "sentinel-operation",
            "runtime_join_key": "sentinel-join",
            "roles": ["sentinel-role"],
            "contract_ids": ["sentinel-contract"],
            "hook_sites": [{"sentinel": True}],
            "registers": ["sentinel-register"],
            "value_domains": [{"sentinel": 9}],
            "resource_action": "sentinel-action",
            "claim_refs": ["sentinel-claim"],
        }
        operation.update(sentinels)
        copied = validator._copy_partial_export(document)
        self.assertEqual(copied, partial_export)
        self.assertIsNot(copied, partial_export)
        self.assertIsNot(copied["operations"][0], operation)
        self.assert_invalid(document)

    def test_emitter_path_contains_no_accepted_semantic_literals(self) -> None:
        source = inspect.getsource(validator._copy_partial_export) + inspect.getsource(
            validator.build_partial_snapshot
        )
        constants = {
            node.value
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        forbidden = {
            "5C7A8C3AD9B6A9D39CC9BBF3DA5AB23015A568C65C723D298F846086324C4680",
            "NRD-OP-0002",
            "d3d:0x826A3568",
            "NRD-CONTRACT-0001",
            "0x82303E3C",
            "0x82303E8C",
            "primitive-4",
            "none",
        }
        self.assertFalse(constants & forbidden)

    def test_malformed_or_duplicate_ids_addresses_and_joins_fail(self) -> None:
        mutations = []
        malformed_id = copy.deepcopy(self.document)
        malformed_id["surface"][0]["id"] = "NRD-OP-1"
        mutations.append(malformed_id)
        duplicate_id = copy.deepcopy(self.document)
        duplicate_id["surface"][1]["id"] = "NRD-OP-0001"
        mutations.append(duplicate_id)
        duplicate_address = copy.deepcopy(self.document)
        duplicate_address["surface"][1]["address"] = "0x82303C38"
        mutations.append(duplicate_address)
        malformed_join = copy.deepcopy(self.document)
        malformed_join["surface"][1]["runtimeJoinKey"] = "d3d:826A3568"
        mutations.append(malformed_join)
        mismatched_join = copy.deepcopy(self.document)
        mismatched_join["surface"][1]["runtimeJoinKey"] = "d3d:0x82303C38"
        mutations.append(mismatched_join)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

    def test_missing_packet_catalog_root_contract_and_reverse_link_fail(self) -> None:
        mutations = []
        missing_pointer = copy.deepcopy(self.document)
        missing_pointer["surface"][0]["claimRefs"][4] = (
            "gfx-draw-producer.json#/currentEvidence/entries/999"
        )
        mutations.append(missing_pointer)
        missing_catalog = copy.deepcopy(self.document)
        missing_catalog["surface"][1]["claimRefs"][0] = "RVA-SYM-9999"
        mutations.append(missing_catalog)
        missing_root = copy.deepcopy(self.document)
        missing_root["surface"][0]["rootIds"] = ["NRD-ROOT-9999"]
        mutations.append(missing_root)
        missing_contract = copy.deepcopy(self.document)
        missing_contract["surface"][0]["contractRefs"] = ["NRD-CONTRACT-9999"]
        mutations.append(missing_contract)
        missing_reverse_link = copy.deepcopy(self.document)
        missing_reverse_link["contracts"][0]["operationIds"] = ["NRD-OP-0002"]
        mutations.append(missing_reverse_link)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

    def test_changed_snapshot_register_site_phase_value_unknown_or_action_fails(self) -> None:
        snapshot = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        mutations = []
        registers = copy.deepcopy(snapshot)
        registers["operations"][0]["registers"] = ["r3"]
        mutations.append(registers)
        site = copy.deepcopy(snapshot)
        site["operations"][0]["hook_sites"][0]["address"] = "0x82303E40"
        mutations.append(site)
        phase = copy.deepcopy(snapshot)
        phase["operations"][0]["hook_sites"][0]["phase"] = "entry"
        mutations.append(phase)
        value = copy.deepcopy(snapshot)
        value["operations"][0]["value_domains"][0]["value"] = 5
        mutations.append(value)
        missing_unknown = copy.deepcopy(snapshot)
        missing_unknown["operations"][0]["value_domains"].pop()
        mutations.append(missing_unknown)
        action = copy.deepcopy(snapshot)
        action["operations"][0]["resource_action"] = "use"
        mutations.append(action)
        for candidate in mutations:
            with self.subTest(candidate=candidate):
                with self.assertRaises(validator.ValidationError):
                    validator.validate_partial_snapshot(candidate, self.document)

    def test_partial_aggregate_or_export_presented_as_complete_fails(self) -> None:
        aggregate = copy.deepcopy(self.document)
        aggregate["scope"]["surface"] = "complete"
        self.assert_invalid(aggregate)
        snapshot = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        snapshot["surface"] = "complete"
        with self.assertRaises(validator.ValidationError):
            validator.validate_partial_snapshot(snapshot, self.document)

    def test_unresolved_coverage_contract_rejects_invalid_categories_or_basis(self) -> None:
        mutations = []
        empty = copy.deepcopy(self.document)
        empty["unresolvedCoverage"]["categories"] = []
        mutations.append(empty)
        duplicate = copy.deepcopy(self.document)
        duplicate["unresolvedCoverage"]["categories"].append("control-seeds")
        mutations.append(duplicate)
        unknown = copy.deepcopy(self.document)
        unknown["unresolvedCoverage"]["categories"][0] = "unknown-family"
        mutations.append(unknown)
        missing_basis = copy.deepcopy(self.document)
        del missing_basis["unresolvedCoverage"]["evidenceBasis"]
        mutations.append(missing_basis)
        wrong_basis = copy.deepcopy(self.document)
        wrong_basis["unresolvedCoverage"]["evidenceBasis"] = [
            "native-renderer-d3d-draw-lowering-frontier.json#/missing"
        ]
        mutations.append(wrong_basis)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

    def test_unresolved_coverage_categories_cannot_leak_into_evidence_fields(self) -> None:
        mutations = []
        for field_path in ("id", "locator"):
            document = copy.deepcopy(self.document)
            document["completenessRoots"][0][field_path] = "device-publication"
            mutations.append(document)
        claim_ref = copy.deepcopy(self.document)
        claim_ref["contracts"][0]["claimRefs"][0] = "dispatch-table"
        mutations.append(claim_ref)
        join = copy.deepcopy(self.document)
        join["surface"][1]["runtimeJoinKey"] = "remaining-lowering-sinks"
        mutations.append(join)
        for document in mutations:
            with self.subTest(document=document):
                self.assert_invalid(document)

        snapshot = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        snapshot["operations"][0]["claim_refs"][0] = "subsystem-anchors"
        with self.assertRaises(validator.ValidationError):
            validator.validate_partial_snapshot(snapshot, self.document)

    def test_retired_workflow_fields_fail(self) -> None:
        placements = {
            "state": "completenessRoots",
            "frontier": "completenessRoots",
            "classificationState": "surface",
            "discriminator": "surface",
            "nextDiscriminator": "surface",
            "semanticStatus": "contracts",
        }
        for key, family in placements.items():
            document = copy.deepcopy(self.document)
            document[family][0][key] = "retired"
            with self.subTest(key=key):
                self.assert_invalid(document)

    def test_unsupported_runtime_backend_and_provenance_fields_fail(self) -> None:
        for key in (
            "runtimeObservation",
            "implementationOwner",
            "rawQueryOutput",
            "machinePath",
            "privateRecord",
            "generatedRuntimeDependency",
        ):
            document = copy.deepcopy(self.document)
            document[key] = "forbidden"
            with self.subTest(key=key):
                self.assert_invalid(document)

    def test_cli_emits_exact_snapshot_to_stdout_without_export_file(self) -> None:
        command = [
            sys.executable,
            "-B",
            str(TOOLS / "validate_native_renderer_d3d_inventory.py"),
            "--emit-partial-snapshot",
            "--research-commit",
            TEST_COMMIT,
            "--aggregate-sha256",
            self.sha256,
        ]
        before = set(REPO.rglob("*partial*snapshot*"))
        completed = subprocess.run(
            command,
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        expected = validator.build_partial_snapshot(self.document, TEST_COMMIT, self.sha256)
        self.assertEqual(completed.stdout, json.dumps(expected, indent=2) + "\n")
        self.assertEqual(set(REPO.rglob("*partial*snapshot*")), before)


if __name__ == "__main__":
    unittest.main()
