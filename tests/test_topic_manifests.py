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

    def test_unique_era_ability_effect_ownership_counts(self) -> None:
        path = MANIFESTS / "unique-era-ability-effect-ownership.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        shared = document["retailOwnerClasses"]["sharedCumulativeLookup"]
        self.assertIn(23, {entry["ueaId"] for entry in shared})
        self.assertIn(8, {entry["ueaId"] for entry in shared})
        self.assertIn(42, {entry["ueaId"] for entry in shared})
        self.assertIn(47, {entry["ueaId"] for entry in shared})
        self.assertIn(1, {entry["ueaId"] for entry in shared})
        self.assertIn(50, {entry["ueaId"] for entry in shared})
        self.assertTrue({3, 12, 18, 19, 20, 24, 55}.issubset(
            {entry["ueaId"] for entry in shared}
        ))
        self.assertNotIn(23, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(8, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(42, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(47, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(1, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(50, document["retailOwnerClasses"]["unknown"])
        self.assertTrue({3, 12, 18, 19, 20, 24, 55}.isdisjoint(
            document["retailOwnerClasses"]["unknown"]
        ))
        self.assertEqual(
            document["retailCellProjection"]["counts"],
            {
                "total": 64,
                "sharedCumulativeLookup": 35,
                "directCivilizationEffectPath": 1,
                "mixedCompanionPath": 0,
                "unknown": 28,
            },
        )

        owner = document["greatPersonGenerationOwner"]
        self.assertEqual(owner["lookup"]["callsite"], "0x82D15618")
        self.assertEqual(owner["lookup"]["target"], "0x82CF0CB0")
        self.assertEqual(owner["effectDataflow"]["tableBase"], "0x830ED484")
        self.assertEqual(
            owner["effectDataflow"]["halfDivide"],
            ["0x82D15624", "0x82D1562C"],
        )
        anarchy = document["anarchyImmunityOwner"]
        self.assertEqual(anarchy["lookup"]["callsite"], "0x82D15344")
        self.assertEqual(anarchy["lookup"]["activeBypass"], "0x82D15374")
        self.assertEqual(
            anarchy["effectDataflow"]["halfwordStores"],
            ["0x82D15350", "0x82D15358", "0x82D15360", "0x82D15368"],
        )

    def test_building_wonder_cost_identity_contract(self) -> None:
        path = MANIFESTS / "building-wonder-cost-identities.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            [(record["itemId"], record["name"], record["baseCostFactor"], record["ueaId"])
             for record in document["buildingRecords"]],
            [(101, "Barracks", 4, 19), (105, "Library", 4, 20),
             (114, "Courthouse", 8, 18)],
        )
        self.assertEqual(document["wonderRange"]["itemIds"], "200 through 299")
        self.assertEqual(document["wonderRange"]["ueaId"], 24)
        self.assertIn("common wonder half-scaling", document["guards"][1])

    def test_map_list_selection_owner_contract(self) -> None:
        path = MANIFESTS / "map-list-selection-owner.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        update = document["stateUpdate"]
        self.assertEqual(update["function"], "0x82DADC88")
        self.assertEqual(update["inputStore"]["offset"], "0x134")
        self.assertEqual(update["zeroOverride"]["selector"], "0x82E2B8D0")
        self.assertEqual(update["resultOffset"], "0x138")
        self.assertEqual(document["mapNumberNegative"]["activeSlot"], "0x830E9010")
        self.assertIn("no direct MAPNUMBER-to-argument edge", document["conclusion"])

    def test_scene_root_ref_consumer_boundary(self) -> None:
        path = MANIFESTS / "scene-root-ref-consumer-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["acceptedSeed"]["field"], "RVA-FLD-0070")
        self.assertEqual(
            [entry["function"] for entry in document["candidateResults"]],
            ["0x82D55808", "0x82D55C68"],
        )
        self.assertIn("do not directly consume", document["boundedNegative"]["result"])
        self.assertIn("decode-coverage observation", document["currentEvidence"]["qualification"])

    def test_player_production_scalar_lifecycle(self) -> None:
        path = MANIFESTS / "player-production-scalar-lifecycle.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["storage"]["base"], "0x830E9050")
        self.assertEqual(
            document["storage"]["reset"]["stores"],
            ["0x82D069F8", "0x82D06A10", "0x82D06A20", "0x82D06A2C"],
        )
        self.assertEqual(document["persistence"]["count"], 8)
        self.assertEqual(document["persistence"]["elementWidth"], "16 bits")
        self.assertEqual(document["setupProducer"]["commandType"], 57)
        self.assertEqual(document["commandWriter"]["branch"], "0x82CDE174")
        self.assertIn("policy name", document["conclusion"])
        self.assertIn("remain unresolved", document["conclusion"])

    def test_wonder_record_identities(self) -> None:
        path = MANIFESTS / "wonder-record-identities.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            [(record["itemId"], record["name"], record["baseCostFactor"])
             for record in document["records"]],
            [(200, "Pyramids of Egypt", 30), (201, "The Great Wall", 30),
             (202, "Hanging Gardens of Babylon", 20), (203, "Stonehenge", 10),
             (204, "Colossus of Rhodes", 20)],
        )
        self.assertEqual(
            [entry["offset"] for entry in document["textOffsets"]],
            ["0x00", "0x4A", "0x8A", "0xCA"],
        )
        self.assertIn("no display consumer", document["conclusion"])

    def test_wonder_record_identities_205_209(self) -> None:
        path = MANIFESTS / "wonder-record-identities-205-209.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            [(record["itemId"], record["name"], record["baseCostFactor"])
             for record in document["records"]],
            [(205, "Oracle of Delphi", 25),
             (206, "Great Library of Alexandria", 30),
             (207, "The East India Company", 40),
             (208, "Oxford University", 30),
             (209, "Shakespeare's Theatre", 30)],
        )
        self.assertIn("0x21", document["records"][2]["shortTokenBoundary"])
        self.assertIn("0x27", document["records"][4]["shortTokenBoundary"])
        self.assertIn("No display consumer", document["conclusion"])

    def test_gold_reserve_interest_contract(self) -> None:
        path = MANIFESTS / "gold-reserve-interest.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["activation"]["ueaId"], 47)
        self.assertEqual(document["reserveStorage"]["base"], "0x830ED544")
        mutation = document["mutationOwner"]
        self.assertEqual(mutation["function"], "0x82D1EAB0")
        self.assertEqual(mutation["lookupCallsite"], "0x82D1F484")
        self.assertEqual(mutation["store"], "0x82D1F4A4")
        consumer = document["readSideConsumer"]
        self.assertEqual(consumer["function"], "0x82CF9F38")
        self.assertEqual(consumer["lookupCallsite"], "0x82CF9FE8")
        self.assertEqual(consumer["reserveBase"]["value"], "0x830ED544")
        self.assertEqual(document["arithmetic"]["term"],
                         "signed divide toward zero of (reserve + 25) by 50")

    def test_city_growth_threshold_contract(self) -> None:
        path = MANIFESTS / "city-growth-threshold.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["activation"]["ueaId"], 8)
        owner = document["thresholdOwner"]
        self.assertEqual(owner["function"], "0x82CF1060")
        self.assertEqual(owner["lookupCallsite"], "0x82CF10F8")
        self.assertEqual(owner["adjustment"]["activeResult"],
                         "max(20, baseline - 10)")
        consumer = document["cityUpdateConsumer"]
        self.assertEqual(consumer["thresholdCalls"],
                         ["0x82D163BC", "0x82D163D4"])
        self.assertEqual(consumer["storedProgressField"]["offset"], "0x34")

    def test_unit_movement_stat_contract(self) -> None:
        path = MANIFESTS / "unit-movement-stat.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["baseMovement"]["fieldOffset"], "0x42")
        self.assertEqual(document["accessor"]["function"], "0x82CF1F70")
        owners = {entry["ueaId"]: entry for entry in document["retailUeaOwners"]}
        self.assertEqual(set(owners), {3, 12, 55})
        self.assertEqual(owners[12]["predicate"]["unitType"], 10)
        self.assertEqual(owners[55]["predicate"]["unitType"], 6)
        self.assertEqual(owners[3]["predicate"]["mask"], "0x200")
        self.assertEqual(document["inventoryCorrection"]["ueaId"], 12)

    def test_road_build_cost_contract(self) -> None:
        path = MANIFESTS / "road-build-cost.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["activation"]["ueaId"], 1)
        owner = document["costOwner"]
        self.assertEqual(owner["function"], "0x82CF83C0")
        self.assertEqual(owner["lookupCallsite"], "0x82CF8460")
        self.assertEqual(owner["activeDivide"], ["0x82CF846C", "0x82CF8470"])
        consumer = document["cityUpdateConsumer"]
        self.assertEqual(consumer["lookupCallsite"], "0x82D16848")
        self.assertEqual(consumer["commandSubmit"]["command"], 7)

    def test_new_warrior_veteran_contract(self) -> None:
        path = MANIFESTS / "new-warrior-veteran.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["activation"]["ueaId"], 50)
        owner = document["owner"]
        self.assertEqual(owner["unitTypePredicate"]["value"], 6)
        self.assertEqual(owner["lookupCallsite"], "0x82D15B78")
        self.assertEqual(owner["rankField"]["offset"], "0x05")
        self.assertEqual(owner["saturation"]["maximum"], 2)

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
