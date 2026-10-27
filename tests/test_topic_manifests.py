from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path
from typing import NamedTuple

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


FAMILY_FIELDS = {"schemaVersion", "family", "findings"}


class ManifestLayoutError(ValueError):
    """A manifest file violates the standalone-record or family-file layout."""


class TopicRecord(NamedTuple):
    path: Path
    finding_id: str | None
    document: dict

    @property
    def label(self) -> str:
        if self.finding_id is None:
            return self.path.name
        return f"{self.path.name}#/findings/{self.finding_id}"


def load_topic_records(manifests: Path) -> list[TopicRecord]:
    """Return every standalone record and family finding under manifests."""
    records: list[TopicRecord] = []
    for path in sorted(manifests.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if "findings" in document:
            records.extend(_family_records(path, document))
        elif "topic" in document:
            records.append(TopicRecord(path, None, document))

    seen: dict[str, dict[str, TopicRecord]] = {"id": {}, "topic": {}}
    for record in records:
        for field, owners in seen.items():
            value = record.document.get(field)
            if value is None:
                continue
            if value in owners:
                raise ManifestLayoutError(
                    f"duplicate {field} {value} in {record.label} "
                    f"and {owners[value].label}"
                )
            owners[value] = record
    return records


def _family_records(path: Path, document: dict) -> list[TopicRecord]:
    if set(document) != FAMILY_FIELDS:
        raise ManifestLayoutError(
            f"{path.name}: family fields must be exactly {sorted(FAMILY_FIELDS)}"
        )
    if document["schemaVersion"] != 1:
        raise ManifestLayoutError(f"{path.name}: schemaVersion must be 1")
    if document["family"] != path.stem:
        raise ManifestLayoutError(f"{path.name}: family must equal the filename stem")
    findings = document["findings"]
    if not isinstance(findings, dict) or not findings:
        raise ManifestLayoutError(f"{path.name}: findings must be a nonempty object")
    records = []
    for finding_id, record in findings.items():
        if not ID_RE.fullmatch(finding_id):
            raise ManifestLayoutError(f"{path.name}: invalid finding key {finding_id}")
        if (
            not isinstance(record, dict)
            or record.get("id") != finding_id
            or "topic" not in record
        ):
            raise ManifestLayoutError(
                f"{path.name}: finding {finding_id} must be a record "
                "with that id and a topic"
            )
        records.append(TopicRecord(path, finding_id, record))
    return records


class TopicManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = load_topic_records(MANIFESTS)
        cls.by_topic = {
            record.document["topic"]: record.document for record in cls.records
        }

    def test_common_contract(self) -> None:
        for record in self.records:
            document, label = record.document, record.label
            self.assertEqual(document.get("schemaVersion"), 1, label)
            self.assertRegex(document.get("id", ""), ID_RE, label)
            self.assertRegex(document.get("topic", ""), TOPIC_RE, label)
            if record.finding_id is None:
                self.assertEqual(record.path.stem, document["topic"], label)
            self.assertEqual(document.get("image"), "image.json", label)
            self.assertIn(document.get("status"), {"open", "closed"}, label)
            self.assertIn(
                document.get("confidence"),
                {"confirmed", "strong", "candidate", "rejected"},
                label,
            )

    def test_current_dependencies_resolve_in_checkout(self) -> None:
        for record in self.records:
            for dependency in record.document.get("dependencies", []):
                topic = dependency.get("topic", "")
                self.assertRegex(topic, TOPIC_RE, record.label)
                self.assertIn(topic, self.by_topic, record.label)

    def test_current_evidence_has_no_history_dependency(self) -> None:
        def visit(value: object, label: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key, FORBIDDEN_HISTORY_KEYS, label)
                    visit(child, label)
            elif isinstance(value, list):
                for child in value:
                    visit(child, label)

        for record in self.records:
            visit(record.document, record.label)

            current_evidence = record.document.get("currentEvidence", {})
            for key in current_evidence:
                self.assertNotIn(key, FORBIDDEN_CURRENT_EVIDENCE_KEYS, record.label)

    def test_script_locators_resolve_or_preserve_historical_provenance(self) -> None:
        def visit(value: object):
            if isinstance(value, str):
                if value.startswith("ghidra/"):
                    yield value
            elif isinstance(value, dict):
                for child in value.values():
                    yield from visit(child)
            elif isinstance(value, list):
                for child in value:
                    yield from visit(child)

        for record in self.records:
            document = record.document
            with self.subTest(manifest=record.label):
                historical = document.get("historicalToolReferences", [])
                self.assertIsInstance(historical, list)
                for reference in historical:
                    self.assertEqual(set(reference), {"locator", "qualification"})
                    self.assertRegex(
                        reference["locator"], r"^ghidra/[A-Za-z0-9_]+\.java$"
                    )
                    self.assertFalse(
                        (REPO / reference["locator"]).exists(),
                        "Historical tool references are for unavailable producers",
                    )
                    self.assertIsInstance(reference["qualification"], str)
                    self.assertTrue(reference["qualification"].strip())
                current = {
                    key: value
                    for key, value in document.items()
                    if key != "historicalToolReferences"
                }
                for locator in visit(current):
                    self.assertIsNotNone(
                        re.fullmatch(r"ghidra/[^:\s]+\.java(?::.+)?", locator), locator
                    )
                    script = (REPO / locator.split(":", 1)[0]).resolve()
                    self.assertTrue(
                        script.is_relative_to((REPO / "ghidra").resolve()), locator
                    )
                    self.assertTrue(
                        script.is_file(), f"{record.label}: missing {locator}"
                    )

    def test_production_cost_ownership_preserves_boundaries(self) -> None:
        document = self.by_topic["production-cost-ownership"]

        self.assertEqual(document["baseCostField"]["offset"], "0x44")
        self.assertEqual(document["effectiveScalar"]["function"], "0x82CF1148")
        self.assertIn(
            "BuildingWonderProductionCostLookup at 0x82CF1278",
            document["costWrappers"][0]["result"],
        )
        non_unit = document["nonUnitBaseCostFields"]["inputRanges"]
        self.assertEqual(
            (
                non_unit["first"]["table"],
                non_unit["first"]["recordSize"],
                non_unit["first"]["fieldOffset"],
                non_unit["first"]["width"],
            ),
            ("0x82F71FD8", "0xCC", "0x41", "signed byte"),
        )
        self.assertEqual(
            (
                non_unit["second"]["table"],
                non_unit["second"]["recordSize"],
                non_unit["second"]["fieldOffset"],
                non_unit["second"]["width"],
            ),
            ("0x82F73238", "0x14C", "0x40", "signed halfword"),
        )
        self.assertEqual(
            [entry["function"] for entry in document["consumers"]["ai"]],
            ["0x82CB44E0", "0x82CB6E48"],
        )

    def test_unique_era_ability_effect_ownership_counts(self) -> None:
        document = self.by_topic["unique-era-ability-effect-ownership"]

        shared = document["retailOwnerClasses"]["sharedCumulativeLookup"]
        self.assertIn(23, {entry["ueaId"] for entry in shared})
        self.assertIn(8, {entry["ueaId"] for entry in shared})
        self.assertIn(42, {entry["ueaId"] for entry in shared})
        self.assertIn(47, {entry["ueaId"] for entry in shared})
        self.assertIn(1, {entry["ueaId"] for entry in shared})
        self.assertIn(50, {entry["ueaId"] for entry in shared})
        self.assertTrue(
            {3, 12, 18, 19, 20, 24, 25, 55}.issubset(
                {entry["ueaId"] for entry in shared}
            )
        )
        terrain_ids = {16, 28, 30, 32, 41, 56}
        self.assertTrue(terrain_ids.issubset({entry["ueaId"] for entry in shared}))
        self.assertTrue(
            {16, 28}.issubset(
                document["lookupInventorySeed"]["retailIdsObservedAsLiteralRequests"]
            )
        )
        self.assertEqual(
            document["lookupInventorySeed"]["retailIdsAbsentAsLiteralRequests"],
            [40],
        )
        self.assertNotIn(23, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(8, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(42, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(47, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(1, document["retailOwnerClasses"]["unknown"])
        self.assertNotIn(50, document["retailOwnerClasses"]["unknown"])
        self.assertTrue(
            {3, 12, 18, 19, 20, 24, 25, 55}.isdisjoint(
                document["retailOwnerClasses"]["unknown"]
            )
        )
        self.assertTrue(
            terrain_ids.isdisjoint(document["retailOwnerClasses"]["unknown"])
        )
        self.assertEqual(
            document["retailCellProjection"]["counts"],
            {
                "total": 64,
                "sharedCumulativeLookup": 47,
                "directCivilizationEffectPath": 1,
                "mixedCompanionPath": 0,
                "unknown": 16,
            },
        )

        terrain = document["terrainYieldBoundary"]
        self.assertEqual(
            terrain["functions"],
            ["0x82CF17C8", "0x82CF1AF0", "0x82CF1CE8"],
        )
        self.assertEqual(terrain["query"]["script"], "ghidra/DumpFunctions.java")
        self.assertEqual(terrain["query"]["invocations"], 1)
        self.assertEqual(
            [
                (
                    entry["function"],
                    entry["component"],
                    entry["baseTable"],
                    entry["body"],
                    [
                        (
                            branch["terrain"],
                            branch["ueaId"],
                            branch["callsite"],
                            branch["increment"],
                        )
                        for branch in entry["branches"]
                    ],
                )
                for entry in terrain["ownerResults"]
            ],
            [
                (
                    "0x82CF17C8",
                    "trade",
                    "0x82F771E2",
                    "complete",
                    [("desert", 32, "0x82CF1A28", 1)],
                ),
                (
                    "0x82CF1AF0",
                    "production",
                    "0x82F771E1",
                    "complete",
                    [
                        ("forest", 30, "0x82CF1C18", 1),
                        ("hill", 41, "0x82CF1C40", 1),
                        ("mountain", 56, "0x82CF1C68", 2),
                    ],
                ),
                (
                    "0x82CF1CE8",
                    "food",
                    "0x82F771E0",
                    "complete",
                    [
                        ("plains", 16, "0x82CF1E28", 1),
                        ("sea", 28, "0x82CF1E28", 1),
                        ("desert", 32, "0x82CF1E28", 1),
                    ],
                ),
            ],
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
        document = self.by_topic["building-wonder-cost-identities"]

        self.assertEqual(
            [
                (
                    record["itemId"],
                    record["name"],
                    record["baseCostFactor"],
                    record["ueaId"],
                )
                for record in document["buildingRecords"]
            ],
            [
                (101, "Barracks", 4, 19),
                (105, "Library", 4, 20),
                (114, "Courthouse", 8, 18),
            ],
        )
        self.assertEqual(document["wonderRange"]["itemIds"], "200 through 299")
        self.assertEqual(document["wonderRange"]["ueaId"], 24)
        self.assertIn("common wonder half-scaling", document["guards"][1])

    def test_map_list_selection_owner_contract(self) -> None:
        document = self.by_topic["map-list-selection-owner"]

        update = document["stateUpdate"]
        self.assertEqual(update["function"], "0x82DADC88")
        self.assertEqual(update["inputStore"]["offset"], "0x134")
        self.assertEqual(update["zeroOverride"]["selector"], "0x82E2B8D0")
        self.assertEqual(update["resultOffset"], "0x138")
        self.assertEqual(document["mapNumberNegative"]["activeSlot"], "0x830E9010")
        self.assertIn("no direct MAPNUMBER-to-argument edge", document["conclusion"])

    def test_map_list_update_argument_producers(self) -> None:
        document = self.by_topic["map-list-update-argument-producers"]

        self.assertEqual(document["id"], "RVA-F-0103")
        self.assertEqual(document["referenceInventory"]["count"], 2)
        self.assertEqual(
            [entry["function"] for entry in document["producers"]],
            ["0x82D06380", "0x82D91A78"],
        )
        self.assertEqual(document["receiverSource"]["global"], "0x8314EFC8")
        self.assertIn("incoming object's +0x34", document["conclusion"])

        symbols = json.loads(
            (MANIFESTS / "catalogs" / "symbols.json").read_text(encoding="utf-8")
        )["records"]
        relations = json.loads(
            (MANIFESTS / "catalogs" / "relations.json").read_text(encoding="utf-8")
        )["records"]
        self.assertEqual(
            {
                record["id"]: record["address"]
                for record in symbols
                if record["id"] in document["catalogPromotion"]["symbols"]
            },
            {
                "RVA-SYM-0334": "0x82D06380",
                "RVA-SYM-0335": "0x82D91A78",
                "RVA-SYM-0336": "0x8314EFC8",
            },
        )
        self.assertEqual(
            {
                record["id"]
                for record in relations
                if record["id"] in document["catalogPromotion"]["relations"]
            },
            set(document["catalogPromotion"]["relations"]),
        )

    def test_scene_root_ref_consumer_boundary(self) -> None:
        document = self.by_topic["scene-root-ref-consumer-boundary"]

        self.assertEqual(document["acceptedSeed"]["field"], "RVA-FLD-0070")
        self.assertEqual(
            [entry["function"] for entry in document["candidateResults"]],
            ["0x82D55808", "0x82D55C68"],
        )
        self.assertIn("do not directly consume", document["boundedNegative"]["result"])
        self.assertIn(
            "decode-coverage observation", document["currentEvidence"]["qualification"]
        )

    def test_scene_root_ref_vtable_consumer_boundary(self) -> None:
        document = self.by_topic["scene-root-ref-vtable-consumer-boundary"]

        self.assertEqual(document["id"], "RVA-F-0104")
        self.assertEqual(
            document["currentEvidence"]["entries"][0]["address"], "0x82147EF8"
        )
        self.assertIn(
            "eight exact targets", document["currentEvidence"]["entries"][0]["result"]
        )
        self.assertEqual(
            [entry["slot"] for entry in document["slotReadSet"]],
            ["+0x04", "+0x08", "+0x0C", "+0x10", "+0x18", "+0x1C", "+0x20", "+0x24"],
        )
        self.assertEqual(len(document["scope"]["candidateTargets"]), 8)
        self.assertIn(
            "318 decoded instructions",
            document["currentEvidence"]["entries"][1]["result"],
        )
        self.assertIn(
            "every decompilation reported",
            document["currentEvidence"]["entries"][2]["result"],
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])
        self.assertIn(
            "decoded-listing observation only",
            document["currentEvidence"]["qualification"],
        )

    def test_gfx_child_slot_consumer_boundary(self) -> None:
        document = self.by_topic["gfx-child-slot-consumer-boundary"]

        self.assertEqual(document["id"], "RVA-F-0105")
        self.assertEqual(document["scope"]["dispatchTarget"], "0x821FBC38")
        self.assertEqual(document["scope"]["fieldOffsets"], ["+0x90", "+0x94"])
        self.assertEqual(document["receiverProvenance"]["preservedRegister"], "r29")
        self.assertIn("stack base r1", document["receiverProvenance"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])
        self.assertEqual(
            document["catalogPromotion"]["updatedEntities"],
            ["RVA-FLD-0002", "RVA-FLD-0003"],
        )
        self.assertIn(
            "corrected exact-function query",
            document["currentEvidence"]["qualification"],
        )

    def test_non_unit_production_threshold_boundary(self) -> None:
        document = self.by_topic["non-unit-production-threshold-boundary"]

        self.assertEqual(document["id"], "RVA-F-0106")
        self.assertEqual(document["scope"]["function"], "0x82D13978")
        self.assertEqual(document["scope"]["costHelper"], "0x82CF1278")
        self.assertIn(
            "independent item-less-than-300 guard",
            document["itemSelection"]["rangeQualification"],
        )
        self.assertEqual(
            document["buildingPath"]["firstWrite"]["address"], "0x82D16150"
        )
        self.assertEqual(
            [entry["address"] for entry in document["wonderPath"]["firstWrites"]],
            ["0x82D16310", "0x82D16318", "0x82D16320"],
        )
        self.assertEqual(document["catalogPromotion"]["newRelations"], ["RVA-REL-0472"])
        self.assertIn("Raw words", document["currentEvidence"]["qualification"])

    def test_playable_interface_gate_ownership_boundary(self) -> None:
        document = self.by_topic["playable-interface-gate-ownership-boundary"]

        self.assertEqual(document["id"], "RVA-F-0107")
        self.assertEqual(document["scope"]["global"], "0x8314F28C")
        self.assertEqual(len(document["scope"]["writers"]), 6)
        self.assertEqual(document["referenceInventory"]["count"], 29)
        self.assertEqual(len(document["bodyResults"]), 7)
        self.assertIn("no publisher", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_player_production_scalar_lifecycle(self) -> None:
        document = self.by_topic["player-production-scalar-lifecycle"]

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

    def test_player_production_scalar_virtual_source_boundary(self) -> None:
        document = self.by_topic["player-production-scalar-virtual-source"]

        self.assertEqual(document["id"], "RVA-F-0102")
        self.assertEqual(document["acceptedAnchors"]["commandType"], 57)
        self.assertEqual(document["ghidraCoverage"]["entry"]["bodyBytes"], "0x8")
        self.assertIsNone(
            document["ghidraCoverage"]["submitSite"]["containingFunction"]
        )
        self.assertEqual(
            document["ghidraCoverage"]["submitSite"]["decodedInstructions"], 0
        )
        self.assertEqual(
            document["generatedCorroboration"]["receiverCandidate"]["register"], "r14"
        )
        self.assertEqual(
            document["generatedCorroboration"]["wrapperFlow"]["submitCall"],
            "0x82D224F0 calls 0x82CE1830",
        )

    def test_wonder_record_identities(self) -> None:
        for topic, expected in (
            (
                "wonder-record-identities",
                [
                    (200, "Pyramids of Egypt", 30),
                    (201, "The Great Wall", 30),
                    (202, "Hanging Gardens of Babylon", 20),
                    (203, "Stonehenge", 10),
                    (204, "Colossus of Rhodes", 20),
                ],
            ),
            (
                "wonder-record-identities-205-209",
                [
                    (205, "Oracle of Delphi", 25),
                    (206, "Great Library of Alexandria", 30),
                    (207, "The East India Company", 40),
                    (208, "Oxford University", 30),
                    (209, "Shakespeare's Theatre", 30),
                ],
            ),
        ):
            with self.subTest(topic=topic):
                document = self.by_topic[topic]
                self.assertEqual(
                    [
                        (record["itemId"], record["name"], record["baseCostFactor"])
                        for record in document["records"]
                    ],
                    expected,
                )
        document = self.by_topic["wonder-record-identities"]
        self.assertEqual(
            [entry["offset"] for entry in document["textOffsets"]],
            ["0x00", "0x4A", "0x8A", "0xCA"],
        )
        document = self.by_topic["wonder-record-identities-205-209"]
        self.assertIn("0x21", document["records"][2]["shortTokenBoundary"])
        self.assertIn("0x27", document["records"][4]["shortTokenBoundary"])

    def test_pyramids_government_availability_boundary(self) -> None:
        document = self.by_topic["pyramids-government-availability"]

        self.assertEqual(document["id"], "RVA-F-0098")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 200)
        self.assertEqual(
            [entry["function"] for entry in document["candidateResults"]],
            ["0x82CF0268", "0x82CEF7A0", "0x82CF81C8"],
        )
        self.assertTrue(document["itemIdScan"]["truncated"])
        self.assertEqual(len(document["itemIdScan"]["emittedFunctions"]), 8)

    def test_great_library_technology_transfer_boundary(self) -> None:
        document = self.by_topic["great-library-technology-transfer"]

        self.assertEqual(document["id"], "RVA-F-0099")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 206)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(
            document["itemIdScan"]["emittedFunctions"],
            ["0x8286FD70", "0x82951B58", "0x829C1298"],
        )
        self.assertTrue(
            all(
                "bad instruction data" in entry["stop"]
                for entry in document["candidateResults"]
            )
        )
        self.assertEqual(
            document["laterAcceptedEligibilityEdge"]["recordCells"],
            {"+0x44": 8, "+0x46": -1, "+0x48": 21},
        )
        self.assertIn(
            "no technology-acquisition", document["boundedNegative"]["result"]
        )

    def test_east_india_sea_trade_boundary(self) -> None:
        document = self.by_topic["east-india-sea-trade"]

        self.assertEqual(document["id"], "RVA-F-0100")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 207)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(document["itemIdScan"]["emittedFunctions"], ["0x82500288"])
        self.assertEqual(document["candidateResults"][0]["body"], "complete")
        self.assertIn(
            "D3D format-name decoder", document["candidateResults"][0]["result"]
        )
        self.assertEqual(
            document["terrainYieldBoundary"]["functions"],
            ["0x82CF17C8", "0x82CF1AF0", "0x82CF1CE8"],
        )

    def test_shakespeare_city_culture_boundary(self) -> None:
        document = self.by_topic["shakespeare-city-culture"]

        self.assertEqual(document["id"], "RVA-F-0101")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 209)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(document["itemIdScan"]["emittedFunctions"], ["0x826CFDC8"])
        self.assertIn("bad instruction data", document["candidateResults"][0]["stop"])

    def test_gold_reserve_interest_contract(self) -> None:
        document = self.by_topic["gold-reserve-interest"]

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
        self.assertEqual(
            document["arithmetic"]["term"],
            "signed divide toward zero of (reserve + 25) by 50",
        )

    def test_gold_reserve_aggregate_lifecycle_boundary(self) -> None:
        document = self.by_topic["gold-reserve-aggregate-lifecycle-boundary"]

        self.assertEqual(document["id"], "RVA-F-0108")
        self.assertEqual(document["scope"]["aggregate"], "0x830ED544 + player*4")
        self.assertEqual(document["aggregateReferenceResult"]["references"], 0)
        self.assertEqual(len(document["ownerResults"]), 2)
        self.assertTrue(
            all(entry["modeledCallers"] == 0 for entry in document["ownerResults"])
        )
        self.assertIn(
            "No additional exact reserve source", document["boundedNegative"]["result"]
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_native_renderer_indexed_draw_caller_frontier(self) -> None:
        document = self.by_topic["native-renderer-indexed-draw-caller-frontier"]

        self.assertEqual(document["id"], "RVA-F-0109")
        self.assertEqual(document["scope"]["indexedDraw"], "0x82303C38")
        self.assertEqual(document["referenceResult"]["references"], 1)
        self.assertEqual(document["referenceResult"]["rows"][0]["source"], "0x82169E6C")
        self.assertEqual(document["referenceResult"]["directCodeCallers"], [])
        self.assertEqual(document["referenceResult"]["decompiledCallerFunctions"], [])
        self.assertIn(
            "No direct caller-family ownership", document["boundedNegative"]["result"]
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_save_profile_owner_lifetime_boundary(self) -> None:
        document = self.by_topic["save-profile-owner-lifetime-boundary"]

        self.assertEqual(document["id"], "RVA-F-0111")
        self.assertEqual(document["scope"]["ownerGlobal"], "0x8314EFE0")
        self.assertEqual(document["globalReferenceResult"]["references"], 107)
        self.assertEqual(
            document["globalReferenceResult"]["types"], {"READ": 107, "WRITE": 0}
        )
        self.assertEqual(document["globalReferenceResult"]["modeledFunctions"], 65)
        self.assertEqual(len(document["bodyResults"]), 3)
        self.assertIn(
            "No teardown, republication", document["boundedNegative"]["result"]
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_xbox_dds_map_authoring_consumer_boundary(self) -> None:
        document = self.by_topic["xbox-dds-map-authoring-consumer-boundary"]

        self.assertEqual(document["id"], "RVA-F-0112")
        self.assertEqual(document["scope"]["terrainLoader"], "0x82C6E188")
        self.assertEqual(
            [entry["references"] for entry in document["stringReferenceResults"]],
            [0, 0, 0],
        )
        self.assertEqual(len(document["bodyResults"]), 2)
        self.assertEqual(document["provedProperties"]["newRoleSpecificProperties"], [])
        self.assertEqual(len(document["remainingBlockers"]), 6)
        self.assertIn(
            "No new role-specific DDS consumer contract",
            document["boundedNegative"]["result"],
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_calendar_event_year_consumer(self) -> None:
        document = self.by_topic["calendar-event-year-consumer"]

        self.assertEqual(document["id"], "RVA-F-0113")
        self.assertEqual(document["discovery"]["unionFunctionCount"], 5)
        self.assertEqual(document["discovery"]["pointerPlacements"], 0)
        self.assertEqual(document["eventYearConsumer"]["function"], "0x82DF9FD0")
        self.assertEqual(document["eventYearConsumer"]["objectYearField"], "+0x444")
        self.assertIn(
            "return value 1", document["eventYearConsumer"]["immediateBranch"]
        )
        self.assertEqual(
            document["catalogPromotion"]["newEntities"],
            ["RVA-SYM-0337", "RVA-REL-0473"],
        )

    def test_key2_game_start_registration_boundary(self) -> None:
        document = self.by_topic["key2-game-start-registration-boundary"]

        self.assertEqual(document["id"], "RVA-F-0114")
        self.assertEqual(document["referenceResults"]["combinedFunctionCount"], 2)
        self.assertEqual(document["referenceResults"]["factory"]["references"], 0)
        self.assertEqual(document["referenceResults"]["vtablePointerPlacements"], 0)
        self.assertEqual(
            [entry["function"] for entry in document["bodyResults"]],
            ["0x821B0AF0", "0x82E60D50"],
        )
        self.assertIn(
            "No direct key-2 registration owner", document["boundedNegative"]["result"]
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_frame_timing_field10_reader_boundary(self) -> None:
        document = self.by_topic["frame-timing-field10-reader-boundary"]

        self.assertEqual(document["id"], "RVA-F-0115")
        self.assertEqual(len(document["writerReconfirmation"]["fieldAccesses"]), 2)
        self.assertEqual(
            document["ownerReferenceResult"]["primaryGlobal"][
                "distinctReaderFunctions"
            ],
            28,
        )
        self.assertEqual(
            document["ownerReferenceResult"]["candidateReadersInspected"], []
        )
        self.assertIn(
            "exceeding the six-candidate cap", document["boundedNegative"]["result"]
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_audio_stream_handle_lifecycle_boundary(self) -> None:
        document = self.by_topic["audio-stream-handle-lifecycle-boundary"]

        self.assertEqual(document["id"], "RVA-F-0117")
        self.assertEqual(document["scope"]["slotSize"], "0x38")
        self.assertEqual(document["referenceResults"]["writer"]["references"], 1)
        self.assertEqual(document["referenceResults"]["dispatcher"]["references"], 1)
        self.assertEqual(document["fieldReadResult"]["matches"], 0)
        self.assertIn("No exact first consumer", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_hall_of_achievements_vtable_slot0(self) -> None:
        document = self.by_topic["hall-of-achievements-vtable-slot0"]

        self.assertEqual(document["id"], "RVA-F-0119")
        self.assertEqual(document["slotResult"]["word"], "0x821C6AB8")
        self.assertEqual(document["slotResult"]["referenceCount"], 1)
        self.assertEqual(document["targetOperation"]["body"], "complete")
        self.assertEqual(document["targetOperation"]["returnedGlobal"], "0x8314F5D0")
        self.assertEqual(
            document["catalogPromotion"]["newEntities"],
            ["RVA-SYM-0338", "RVA-SYM-0339", "RVA-SLOT-0058", "RVA-REL-0474"],
        )

    def test_nif_scene_transform_contract(self) -> None:
        document = self.by_topic["nif-scene-transform-contract"]

        self.assertEqual(document["id"], "RVA-F-0125")
        self.assertEqual(document["idAssignment"]["status"], "canonical")
        self.assertEqual(document["serializedLayout"]["uniformity"].count("one f32"), 1)
        self.assertEqual(document["inheritanceAndDispatch"]["composer"], "0x82D7A8A8")
        self.assertEqual(
            {entry["type"] for entry in document["inheritanceAndDispatch"]["tables"]},
            {"NiAVObject", "NiNode", "NiGeometry", "NiTriBasedGeom", "NiTriShape"},
        )
        self.assertEqual(
            document["composition"]["parented"],
            {
                "scale": "s_world = s_parent * s_local",
                "rotation": "R_world = R_parent * R_local",
                "translation": "t_world = t_parent + s_parent * (R_parent * t_local)",
            },
        )
        self.assertIn(
            "for node in ancestors_from_shape_parent_to_selected_root:",
            document["composition"]["orderedPseudocode"],
        )
        self.assertEqual(
            document["implementationContract"]["status"],
            "transformed-static-assembly-supported",
        )
        unresolved = " ".join(document["boundedNegatives"]).lower()
        self.assertIn("handedness", unresolved)
        self.assertIn("winding", unresolved)
        self.assertIn("renderer", unresolved)

    def test_nif_texturing_property_field_contract(self) -> None:
        document = self.by_topic["nif-texturing-property-field-contract"]

        self.assertEqual(document["id"], "RVA-F-0130")
        self.assertEqual(document["idAssignment"]["status"], "canonical")
        self.assertEqual(document["streamContract"]["reader"]["method"], "0x82355CC0")
        self.assertEqual(document["streamContract"]["writer"]["method"], "0x823563B0")
        self.assertEqual(document["slotContract"]["observedTextureCount"], 9)
        slots = document["slotContract"]["orderedStandardSlots"]
        self.assertEqual([slot["index"] for slot in slots], list(range(9)))
        self.assertEqual(
            [slot["name"] for slot in slots],
            [
                "Base",
                "Dark",
                "Detail",
                "Gloss",
                "Glow",
                "Bump",
                "Normal",
                "Parallax",
                "Decal 0",
            ],
        )
        observed = document["slotContract"]["observedPresentDescriptors"]
        self.assertEqual(
            {name: observed[name] for name in ("Base", "Glow", "Shader")},
            {"Base": 275, "Glow": 24, "Shader": 84},
        )
        tex_desc = document["descriptorContracts"]["TexDesc"]
        self.assertEqual(tex_desc["reader"], "0x823568B0")
        self.assertEqual(tex_desc["writer"], "0x82356B00")
        self.assertEqual(
            [field["width"] for field in tex_desc["fields"]],
            [4, 2, 1, 32],
        )
        self.assertEqual(
            document["descriptorContracts"]["BumpTexDesc"]["extraWidth"], 24
        )
        self.assertEqual(
            document["descriptorContracts"]["ParallaxTexDesc"]["extraWidth"], 4
        )
        shader = document["descriptorContracts"]["ShaderTexDesc"]
        self.assertEqual(
            [field["field"] for field in shader["fields"]], ["Has Map", "Map", "Map ID"]
        )
        self.assertIn("does not store", shader["titleRetention"])
        self.assertIn("0xF00F", document["derivedProfileLayout"]["flagsReadPolicy"])
        self.assertEqual(
            document["implementationContract"]["status"], "retention-supported"
        )
        unresolved = " ".join(document["boundedNegatives"]).lower()
        self.assertIn("uv-set", unresolved)
        self.assertIn("filter", unresolved)
        self.assertIn("renderer", unresolved)

    def test_nif_source_texture_field_contract(self) -> None:
        document = self.by_topic["nif-source-texture-field-contract"]

        self.assertEqual(document["id"], "RVA-F-0131")
        self.assertEqual(document["idAssignment"]["status"], "canonical")
        self.assertEqual(document["typeIdentity"]["descriptor"], "0x82F8E570")
        self.assertEqual(document["typeIdentity"]["parentDescriptor"], "0x82F8E66C")
        self.assertEqual(document["typeIdentity"]["readerSlot"], "+0x10 -> 0x82391BA8")
        self.assertEqual(document["typeIdentity"]["writerSlot"], "+0x1C -> 0x82391FF0")
        self.assertEqual(document["derivedLayout"]["serializedWidth"], 24)
        fields = document["derivedLayout"]["fields"]
        self.assertEqual([field["order"] for field in fields], list(range(9)))
        self.assertEqual(
            [field["field"] for field in fields],
            [
                "Use External",
                "File Name",
                "Pixel Data",
                "Pixel Layout",
                "Use Mipmaps",
                "Alpha Format",
                "Is Static",
                "Direct Render",
                "Persist Render Data",
            ],
        )
        self.assertEqual(
            [field["serializedOffset"] for field in fields],
            [
                "+0x00",
                "+0x01",
                "+0x05",
                "+0x09",
                "+0x0D",
                "+0x11",
                "+0x15",
                "+0x16",
                "+0x17",
            ],
        )
        self.assertEqual(
            [field["width"] for field in fields], [1, 4, 4, 4, 4, 4, 1, 1, 1]
        )
        observed = document["sourceSelectionContract"]["observedCombination"]
        self.assertEqual(observed["Use External"], 1)
        self.assertEqual(observed["count"], 383)
        self.assertIn("null", observed["Pixel Data"])
        self.assertIn(
            "standard null reference",
            document["sourceSelectionContract"]["supportedExternalRequirement"],
        )
        self.assertIn("both Use External values", fields[1]["profileCondition"])
        self.assertIn("both Use External values", fields[2]["profileCondition"])
        self.assertIn(
            "not a lossless carrier",
            document["titleReadWriteBehavior"]["rawPreservation"],
        )
        self.assertEqual(
            document["implementationContract"]["status"], "retention-supported"
        )
        unresolved = " ".join(document["boundedNegatives"]).lower()
        self.assertIn("embedded", unresolved)
        self.assertIn("path", unresolved)
        self.assertIn("renderer", unresolved)

    def test_native_renderer_resolve_resource_contract(self) -> None:
        document = self.by_topic["native-renderer-resolve-resource-contract"]

        self.assertEqual(document["id"], "RVA-F-0126")
        self.assertEqual(document["status"], "closed")
        self.assertEqual(document["creationPath"]["headerBytes"], "0x34")
        self.assertEqual(len(document["descriptorWords"]), 6)
        words = {entry["index"]: entry for entry in document["descriptorWords"]}
        self.assertIn("does not consume producer bit", words[0]["consumer"])
        self.assertIn("primary page base", words[1]["provedRole"])
        self.assertIn("width and height", words[2]["provedRole"])
        self.assertIn("secondary page base", words[5]["provedRole"])
        self.assertIn("does not consume the page-base", words[5]["consumer"])
        self.assertIn("no direct read", words[4]["consumer"])
        self.assertEqual(
            {
                key: document["missingContracts"][key]
                for key in (
                    "typedExactResource",
                    "generationAndLifetime",
                    "completion",
                    "nativeImplementation",
                )
            },
            {
                "typedExactResource": "unresolved",
                "generationAndLifetime": "unresolved",
                "completion": "unresolved",
                "nativeImplementation": "unresolved",
            },
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_nif_material_property_field_contract(self) -> None:
        document = self.by_topic["nif-material-property-field-contract"]

        self.assertEqual(document["id"], "RVA-F-0129")
        self.assertEqual(document["idAssignment"]["status"], "canonical")
        self.assertEqual(document["streamContract"]["reader"]["method"], "0x8235D228")
        self.assertEqual(document["streamContract"]["writer"]["method"], "0x8235D2E8")
        self.assertEqual(
            document["streamContract"]["reader"]["baseCall"],
            "0x82354338 -> 0x82358928",
        )
        self.assertEqual(
            document["streamContract"]["writer"]["baseCall"],
            "0x82354350 -> 0x82358E00",
        )
        self.assertEqual(document["derivedLayout"]["serializedWidth"], 56)
        fields = document["derivedLayout"]["fields"]
        self.assertEqual([field["order"] for field in fields], list(range(6)))
        self.assertEqual(
            [field["inspectionLabel"] for field in fields],
            [
                "Ambient color",
                "Diffuse color",
                "Specular color",
                "Emissive color",
                "Glossiness",
                "Alpha",
            ],
        )
        self.assertEqual(
            [field["serializedOffset"] for field in fields],
            ["+0x00", "+0x0C", "+0x18", "+0x24", "+0x30", "+0x34"],
        )
        self.assertEqual(
            [field["runtimeOffset"] for field in fields],
            ["+0x1C", "+0x28", "+0x34", "+0x40", "+0x4C", "+0x50"],
        )
        self.assertEqual([field["width"] for field in fields], [12, 12, 12, 12, 4, 4])
        self.assertEqual(
            [field["serializedType"] for field in fields],
            ["Color3: three consecutive f32 values"] * 4 + ["f32", "f32"],
        )
        self.assertEqual(
            [field["titleLabel"] for field in fields],
            ["m_amb", "m_diff", "m_spec", "m_emit", "m_fShine", "m_fAlpha"],
        )
        self.assertIn("unconditionally", document["profileConditions"]["titleBehavior"])
        self.assertIn("no arithmetic", document["rawValueBehavior"]["readPath"])
        self.assertEqual(
            document["implementationContract"]["status"], "retention-supported"
        )
        unresolved = " ".join(document["boundedNegatives"]).lower()
        self.assertIn("finite", unresolved)
        self.assertIn("color-space", unresolved)
        self.assertIn("renderer", unresolved)

    def test_native_renderer_resource_lifetime_boundary(self) -> None:
        document = self.by_topic["native-renderer-resource-lifetime-boundary"]

        self.assertEqual(document["id"], "RVA-F-0127")
        self.assertEqual(document["status"], "closed")
        self.assertEqual(document["referenceResult"]["references"], 96)
        self.assertEqual(document["referenceResult"]["cap"], 6)
        self.assertEqual(document["referenceResult"]["inspectedCallerBodies"], [])
        self.assertIn(
            "No exact allocation generation", document["boundedNegative"]["result"]
        )
        self.assertEqual(
            document["missingContracts"]["generationAndLifetime"], "unresolved"
        )
        self.assertEqual(
            document["missingContracts"]["persistentResourceIdentity"], "unresolved"
        )
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_native_renderer_ring_span_boundary(self) -> None:
        document = self.by_topic["native-renderer-ring-span-boundary"]

        self.assertEqual(document["id"], "RVA-F-0128")
        self.assertEqual(document["status"], "closed")
        self.assertEqual(document["functionReadResult"]["requestedBodies"], 8)
        self.assertEqual(document["functionReadResult"]["completeBodies"], 0)
        self.assertEqual(document["ringContract"]["startIndex"], "unresolved")
        self.assertEqual(document["ringContract"]["endIndex"], "unresolved")
        self.assertEqual(document["ringContract"]["wrapBehavior"], "unresolved")
        self.assertIn("unresolved", document["ringContract"]["publicationOrDoorbell"])
        self.assertIn("unresolved", document["ringContract"]["completionFence"])
        self.assertEqual(
            document["ringContract"]["consumerAcknowledgement"], "unresolved"
        )
        self.assertEqual(document["ringContract"]["completedSpanAdvance"], "prohibited")
        self.assertIn("pre-swap", document["vdswapOrdering"]["provedTitleOrder"])
        contracts = document["missingContracts"]
        gate_names = {
            "typedExactResource",
            "generationAndLifetime",
            "exactOwnedSpanAndWrap",
            "vdswapSemanticOrdering",
            "realNativeSubmission",
            "realCompletionFence",
            "completedSpanAcknowledgement",
        }
        self.assertEqual(set(contracts), gate_names)
        self.assertTrue(all(contracts[name] == "unresolved" for name in gate_names))
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_nif_external_texture_lookup_policy(self) -> None:
        document = self.by_topic["nif-external-texture-lookup-policy"]

        self.assertEqual(document["id"], "RVA-F-0132")
        self.assertEqual(document["idAssignment"]["status"], "canonical")
        self.assertEqual(document["acceptedPopulation"]["externalReferences"], 383)
        chain = document["lookupChain"]
        self.assertEqual(chain["serializedCarrier"]["reader"], "0x82391BA8")
        self.assertEqual(
            chain["serializedCarrier"]["runtimeFilenameField"], "object +0x34"
        )
        self.assertEqual(chain["streamResolution"]["provider"], "stream +0x1C0")
        self.assertEqual(chain["lazyResourceRequest"]["resourceField"], "object +0x3C")
        self.assertEqual(
            chain["fileAndDecodeBoundary"]["chain"],
            [
                "0x82393D40",
                "0x82466738",
                "0x82466748",
                "0x82467538",
                "0x8280F578",
                "NtCreateFile",
            ],
        )
        policy = document["filenamePolicy"]
        self.assertIn("NUL-terminated", policy["byteInterpretation"]["proved"])
        self.assertIn(
            "not a proved text encoding", policy["byteInterpretation"]["encoding"]
        )
        self.assertIn("both backslash and forward slash", policy["separatorHandling"])
        self.assertIn("collapses repeated backslashes", policy["separatorHandling"])
        self.assertIn("after the leading bytes", policy["separatorHandling"])
        self.assertIn("preserving leading duplicates", policy["separatorHandling"])
        self.assertIn("0x40", policy["case"])
        self.assertIn("0x823914A0", chain["release"])
        self.assertTrue(
            any(
                "0x823914A0" in locator
                for locator in document["currentEvidence"]["locators"]
            )
        )
        readiness = document["implementationReadiness"]
        self.assertEqual(readiness["lookupVerdict"], "CLOSED NEGATIVE")
        self.assertEqual(readiness["standaloneNifLookup"], "REMAIN BLOCKED")
        self.assertEqual(readiness["archiveContainedNifLookup"], "REMAIN BLOCKED")
        self.assertEqual(readiness["targetAuditGate"], "NOT OPEN")
        self.assertEqual(
            readiness["authorized"],
            "No inspection-tool external texture lookup is authorized by this manifest. "
            "Existing lossless source metadata retention remains valid.",
        )
        self.assertIn(
            "Do not inspect the asset inventory",
            document["guards"][0],
        )
        unresolved = " ".join(document["searchPolicy"]["unresolved"]).lower()
        self.assertIn("candidate roots", unresolved)
        self.assertIn("owning nif", unresolved)
        self.assertIn("containing archive", unresolved)
        self.assertIn("duplicate", unresolved)
        privacy = document["currentEvidence"]["privacy"].lower()
        self.assertIn("no retail filename", privacy)
        self.assertIn("no asset checkout", privacy)

    def test_city_growth_threshold_contract(self) -> None:
        document = self.by_topic["city-growth-threshold"]

        self.assertEqual(document["activation"]["ueaId"], 8)
        owner = document["thresholdOwner"]
        self.assertEqual(owner["function"], "0x82CF1060")
        self.assertEqual(owner["lookupCallsite"], "0x82CF10F8")
        self.assertEqual(owner["adjustment"]["activeResult"], "max(20, baseline - 10)")
        consumer = document["cityUpdateConsumer"]
        self.assertEqual(consumer["thresholdCalls"], ["0x82D163BC", "0x82D163D4"])
        self.assertEqual(consumer["storedProgressField"]["offset"], "0x34")

    def test_unit_movement_stat_contract(self) -> None:
        document = self.by_topic["unit-movement-stat"]

        self.assertEqual(document["baseMovement"]["fieldOffset"], "0x42")
        self.assertEqual(document["accessor"]["function"], "0x82CF1F70")
        owners = {entry["ueaId"]: entry for entry in document["retailUeaOwners"]}
        self.assertEqual(set(owners), {3, 12, 55})
        self.assertEqual(owners[12]["predicate"]["unitType"], 10)
        self.assertEqual(owners[55]["predicate"]["unitType"], 6)
        self.assertEqual(owners[3]["predicate"]["mask"], "0x200")
        self.assertEqual(document["inventoryCorrection"]["ueaId"], 12)

    def test_road_build_cost_contract(self) -> None:
        document = self.by_topic["road-build-cost"]

        self.assertEqual(document["activation"]["ueaId"], 1)
        owner = document["costOwner"]
        self.assertEqual(owner["function"], "0x82CF83C0")
        self.assertEqual(owner["lookupCallsite"], "0x82CF8460")
        self.assertEqual(owner["activeDivide"], ["0x82CF846C", "0x82CF8470"])
        consumer = document["cityUpdateConsumer"]
        self.assertEqual(consumer["lookupCallsite"], "0x82D16848")
        self.assertEqual(consumer["commandSubmit"]["command"], 7)

    def test_new_warrior_veteran_contract(self) -> None:
        document = self.by_topic["new-warrior-veteran"]

        self.assertEqual(document["activation"]["ueaId"], 50)
        owner = document["owner"]
        self.assertEqual(owner["unitTypePredicate"]["value"], 6)
        self.assertEqual(owner["lookupCallsite"], "0x82D15B78")
        self.assertEqual(owner["rankField"]["offset"], "0x05")
        self.assertEqual(owner["saturation"]["maximum"], 2)

    def test_unique_unit_combat_predicate_contract(self) -> None:
        document = self.by_topic["unique-unit-combat-predicates"]

        self.assertEqual(document["status"], "closed")
        self.assertEqual(
            document["coreRole"]["domain"], ["attack-side", "defense-side"]
        )
        self.assertEqual(document["coreRole"]["carrier"], "derived-callsite-state")
        self.assertEqual(document["coreRole"]["ordering"], ["0x82CDA214", "0x82CDA234"])
        self.assertEqual(document["coreRole"]["attackSide"]["playerLocal"], "r1+1572")
        self.assertEqual(document["coreRole"]["defenseSide"]["playerLocal"], "r1+1596")
        self.assertEqual(
            document["aiEvaluationBoundary"]["roleParity"],
            "one-resolver-backed-consumer",
        )
        self.assertEqual(
            {
                entry["function"]
                for entry in document["aiEvaluationBoundary"]["entries"]
            },
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


def record(finding_id: str, topic: str) -> dict:
    return {
        "schemaVersion": 1,
        "id": finding_id,
        "topic": topic,
        "status": "closed",
        "confidence": "strong",
        "image": "image.json",
    }


def family(name: str, *records: dict) -> dict:
    return {
        "schemaVersion": 1,
        "family": name,
        "findings": {entry["id"]: entry for entry in records},
    }


class FamilyContainerTests(unittest.TestCase):
    def load(self, **files: dict) -> list[TopicRecord]:
        with tempfile.TemporaryDirectory() as temporary:
            manifests = Path(temporary)
            for name, document in files.items():
                (manifests / f"{name.replace('_', '-')}.json").write_text(
                    json.dumps(document), encoding="utf-8"
                )
            return load_topic_records(manifests)

    def test_loads_standalone_records_and_family_findings(self) -> None:
        records = self.load(
            alone=record("RVA-F-9001", "alone"),
            group=family(
                "group", record("RVA-F-9002", "first"), record("RVA-F-9003", "second")
            ),
            image={"schemaVersion": 1},
        )

        self.assertEqual(
            [(entry.label, entry.document["topic"]) for entry in records],
            [
                ("alone.json", "alone"),
                ("group.json#/findings/RVA-F-9002", "first"),
                ("group.json#/findings/RVA-F-9003", "second"),
            ],
        )

    def test_rejects_malformed_containers(self) -> None:
        good = record("RVA-F-9001", "first")
        cases = {
            "extra field": {**family("group", good), "topic": "group"},
            "wrong family": family("other", good),
            "wrong version": {**family("group", good), "schemaVersion": 2},
            "no findings": {**family("group"), "findings": {}},
            "key is not an id": {
                **family("group"),
                "findings": {"first": record("first", "first")},
            },
            "key differs from record id": {
                **family("group"),
                "findings": {"RVA-F-9002": good},
            },
            "record without topic": {
                **family("group"),
                "findings": {"RVA-F-9001": {"id": "RVA-F-9001"}},
            },
        }
        for name, document in cases.items():
            with self.subTest(name):
                with self.assertRaises(ManifestLayoutError):
                    self.load(group=document)

    def test_rejects_duplicate_ids_and_topics(self) -> None:
        cases = {
            "id": (
                record("RVA-F-9001", "alone"),
                family("group", record("RVA-F-9001", "other")),
            ),
            "topic": (
                record("RVA-F-9001", "alone"),
                family("group", record("RVA-F-9002", "alone")),
            ),
        }
        for field, (standalone, container) in cases.items():
            with self.subTest(field):
                with self.assertRaisesRegex(ManifestLayoutError, f"duplicate {field}"):
                    self.load(alone=standalone, group=container)


if __name__ == "__main__":
    unittest.main()
