from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MANIFESTS = REPO / "manifests"
ID_RE = re.compile(r"^RVA-F-[0-9]{4}$")
TOPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FORBIDDEN_HISTORY_KEYS = {"commit", "migration", "relocation", "sourceEvidence"}
FORBIDDEN_CURRENT_EVIDENCE_KEYS = {
    "pairs",
    "source",
    "sourceAddress",
    "sourceInstructionCount",
    "sourceVtable",
    "target",
    "targetAddress",
    "targetInstructionCount",
    "targetVtable",
}


class TopicManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents = []
        for path in sorted(MANIFESTS.glob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            if "topic" in document:
                cls.documents.append((path, document))

    def test_common_contract_and_unique_identity(self) -> None:
        ids: set[str] = set()
        topics: set[str] = set()
        for path, document in self.documents:
            self.assertEqual(document.get("schemaVersion"), 1, path.name)
            self.assertRegex(document.get("id", ""), ID_RE, path.name)
            self.assertRegex(document.get("topic", ""), TOPIC_RE, path.name)
            self.assertEqual(path.stem, document["topic"], path.name)
            self.assertEqual(document.get("image"), "image.json", path.name)
            self.assertIn(document.get("status"), {"open", "closed"}, path.name)
            self.assertIn(
                document.get("confidence"),
                {"confirmed", "strong", "candidate", "rejected"},
                path.name,
            )
            self.assertNotIn(document["id"], ids, path.name)
            self.assertNotIn(document["topic"], topics, path.name)
            ids.add(document["id"])
            topics.add(document["topic"])

    def test_current_dependencies_resolve_in_checkout(self) -> None:
        for path, document in self.documents:
            for dependency in document.get("dependencies", []):
                topic = dependency.get("topic", "")
                self.assertRegex(topic, TOPIC_RE, path.name)
                dependency_path = MANIFESTS / f"{topic}.json"
                self.assertTrue(dependency_path.is_file(), dependency_path.name)
                dependency_document = json.loads(
                    dependency_path.read_text(encoding="utf-8")
                )
                self.assertEqual(dependency_document.get("topic"), topic, path.name)

    def test_current_evidence_has_no_history_dependency(self) -> None:
        def visit(value: object, path: Path) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key, FORBIDDEN_HISTORY_KEYS, path.name)
                    visit(child, path)
            elif isinstance(value, list):
                for child in value:
                    visit(child, path)

        for path, document in self.documents:
            visit(document, path)

            current_evidence = document.get("currentEvidence", {})
            for key in current_evidence:
                self.assertNotIn(key, FORBIDDEN_CURRENT_EVIDENCE_KEYS, path.name)

    def test_production_cost_ownership_preserves_boundaries(self) -> None:
        path = MANIFESTS / "production-cost-ownership.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["baseCostField"]["offset"], "0x44")
        self.assertEqual(document["effectiveScalar"]["function"], "0x82CF1148")
        self.assertIn(
            "BuildingWonderProductionCostLookup at 0x82CF1278",
            document["costWrappers"][0]["result"],
        )
        non_unit = document["nonUnitBaseCostFields"]["inputRanges"]
        self.assertEqual(
            (non_unit["first"]["table"], non_unit["first"]["recordSize"],
             non_unit["first"]["fieldOffset"], non_unit["first"]["width"]),
            ("0x82F71FD8", "0xCC", "0x41", "signed byte"),
        )
        self.assertEqual(
            (non_unit["second"]["table"], non_unit["second"]["recordSize"],
             non_unit["second"]["fieldOffset"], non_unit["second"]["width"]),
            ("0x82F73238", "0x14C", "0x40", "signed halfword"),
        )
        self.assertEqual(
            [entry["function"] for entry in document["consumers"]["ai"]],
            ["0x82CB44E0", "0x82CB6E48"],
        )
        self.assertTrue(
            any("runtime" in guard.lower() for guard in document["guards"])
        )

    def test_unique_unit_combat_predicate_contract(self) -> None:
        path = MANIFESTS / "unique-unit-combat-predicates.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["status"], "closed")
        self.assertEqual(
            document["coreRole"]["domain"], ["attack-side", "defense-side"]
        )
        self.assertEqual(document["coreRole"]["carrier"], "derived-callsite-state")
        self.assertEqual(
            document["coreRole"]["ordering"], ["0x82CDA214", "0x82CDA234"]
        )
        self.assertEqual(document["coreRole"]["attackSide"]["playerLocal"], "r1+1572")
        self.assertEqual(document["coreRole"]["defenseSide"]["playerLocal"], "r1+1596")
        self.assertEqual(
            document["aiEvaluationBoundary"]["roleParity"],
            "one-resolver-backed-consumer",
        )
        self.assertEqual(
            {entry["function"] for entry in document["aiEvaluationBoundary"]["entries"]},
            {"0x82CB44E0", "0x82CB6E48", "0x82CBF570"},
        )
        self.assertEqual(document["aiRoleConsumer"]["function"], "0x82CBF570")
        self.assertEqual(document["aiRoleConsumer"]["callsite"], "0x82CC03FC")
        self.assertEqual(document["aiRoleConsumer"]["mode"], 1)
        self.assertEqual(
            document["aiRoleConsumer"]["orderedEvaluation"],
            ["0x82CDA214", "0x82CDA234"],
        )
        self.assertIn(
            "r1+1596",
            document["aiRoleConsumer"]["resolverCarrier"]["defenderPlayer"],
        )
        self.assertIn(
            "r1+1604",
            document["aiRoleConsumer"]["resolverCarrier"]["defenderUnit"],
        )


if __name__ == "__main__":
    unittest.main()
