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

    def test_map_list_update_argument_producers(self) -> None:
        path = MANIFESTS / "map-list-update-argument-producers.json"
        document = json.loads(path.read_text(encoding="utf-8"))

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
            {record["id"]: record["address"] for record in symbols
             if record["id"] in document["catalogPromotion"]["symbols"]},
            {
                "RVA-SYM-0334": "0x82D06380",
                "RVA-SYM-0335": "0x82D91A78",
                "RVA-SYM-0336": "0x8314EFC8",
            },
        )
        self.assertEqual(
            {record["id"] for record in relations
             if record["id"] in document["catalogPromotion"]["relations"]},
            set(document["catalogPromotion"]["relations"]),
        )

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

    def test_scene_root_ref_vtable_consumer_boundary(self) -> None:
        path = MANIFESTS / "scene-root-ref-vtable-consumer-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0104")
        self.assertEqual(document["currentEvidence"]["entries"][0]["address"], "0x82147EF8")
        self.assertIn("eight exact targets", document["currentEvidence"]["entries"][0]["result"])
        self.assertEqual(
            [entry["slot"] for entry in document["slotReadSet"]],
            ["+0x04", "+0x08", "+0x0C", "+0x10", "+0x18", "+0x1C", "+0x20", "+0x24"],
        )
        self.assertEqual(len(document["scope"]["candidateTargets"]), 8)
        self.assertIn("318 decoded instructions", document["currentEvidence"]["entries"][1]["result"])
        self.assertIn("every decompilation reported", document["currentEvidence"]["entries"][2]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])
        self.assertIn("decoded-listing observation only", document["currentEvidence"]["qualification"])

    def test_gfx_child_slot_consumer_boundary(self) -> None:
        path = MANIFESTS / "gfx-child-slot-consumer-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

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
        self.assertIn("corrected exact-function query", document["currentEvidence"]["qualification"])

    def test_non_unit_production_threshold_boundary(self) -> None:
        path = MANIFESTS / "non-unit-production-threshold-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0106")
        self.assertEqual(document["scope"]["function"], "0x82D13978")
        self.assertEqual(document["scope"]["costHelper"], "0x82CF1278")
        self.assertIn("independent item-less-than-300 guard", document["itemSelection"]["rangeQualification"])
        self.assertEqual(document["buildingPath"]["firstWrite"]["address"], "0x82D16150")
        self.assertEqual(
            [entry["address"] for entry in document["wonderPath"]["firstWrites"]],
            ["0x82D16310", "0x82D16318", "0x82D16320"],
        )
        self.assertEqual(
            1 + len(document["wonderPath"]["firstWrites"]),
            4,
        )
        self.assertEqual(document["catalogPromotion"]["newRelations"], ["RVA-REL-0472"])
        self.assertIn("Raw words", document["currentEvidence"]["qualification"])

    def test_playable_interface_gate_ownership_boundary(self) -> None:
        path = MANIFESTS / "playable-interface-gate-ownership-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0107")
        self.assertEqual(document["scope"]["global"], "0x8314F28C")
        self.assertEqual(len(document["scope"]["writers"]), 6)
        self.assertEqual(document["referenceInventory"]["count"], 29)
        self.assertEqual(len(document["bodyResults"]), 7)
        self.assertIn("no publisher", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

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

    def test_player_production_scalar_virtual_source_boundary(self) -> None:
        path = MANIFESTS / "player-production-scalar-virtual-source.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0102")
        self.assertEqual(document["acceptedAnchors"]["commandType"], 57)
        self.assertEqual(document["ghidraCoverage"]["entry"]["bodyBytes"], "0x8")
        self.assertIsNone(document["ghidraCoverage"]["submitSite"]["containingFunction"])
        self.assertEqual(document["ghidraCoverage"]["submitSite"]["decodedInstructions"], 0)
        self.assertEqual(document["generatedCorroboration"]["receiverCandidate"]["register"], "r14")
        self.assertEqual(document["generatedCorroboration"]["wrapperFlow"]["submitCall"],
                         "0x82D224F0 calls 0x82CE1830")
        self.assertIn("does not prove", document["boundedNegative"]["result"])
        self.assertIn("not a claim", document["conclusion"])

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

    def test_pyramids_government_availability_boundary(self) -> None:
        path = MANIFESTS / "pyramids-government-availability.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0098")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 200)
        self.assertEqual(
            [entry["function"] for entry in document["candidateResults"]],
            ["0x82CF0268", "0x82CEF7A0", "0x82CF81C8"],
        )
        self.assertTrue(document["itemIdScan"]["truncated"])
        self.assertEqual(len(document["itemIdScan"]["emittedFunctions"]), 8)
        self.assertIn("does not establish", document["boundedNegative"]["result"])
        self.assertIn("not an executable-wide absence", document["conclusion"])

    def test_great_library_technology_transfer_boundary(self) -> None:
        path = MANIFESTS / "great-library-technology-transfer.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0099")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 206)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(
            document["itemIdScan"]["emittedFunctions"],
            ["0x8286FD70", "0x82951B58", "0x829C1298"],
        )
        self.assertTrue(all(
            "bad instruction data" in entry["stop"]
            for entry in document["candidateResults"]
        ))
        self.assertIn("does not establish", document["boundedNegative"]["result"])
        self.assertIn("not an executable-wide absence", document["conclusion"])

    def test_east_india_sea_trade_boundary(self) -> None:
        path = MANIFESTS / "east-india-sea-trade.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0100")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 207)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(document["itemIdScan"]["emittedFunctions"], ["0x82500288"])
        self.assertEqual(document["candidateResults"][0]["body"], "complete")
        self.assertIn("D3D format-name decoder", document["candidateResults"][0]["result"])
        self.assertEqual(
            document["terrainYieldBoundary"]["functions"],
            ["0x82CF17C8", "0x82CF1AF0", "0x82CF1CE8"],
        )
        self.assertIn("does not establish", document["boundedNegative"]["result"])
        self.assertIn("not an executable-wide absence", document["conclusion"])

    def test_shakespeare_city_culture_boundary(self) -> None:
        path = MANIFESTS / "shakespeare-city-culture.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0101")
        self.assertEqual(document["acceptedAnchors"]["wonder"]["itemId"], 209)
        self.assertFalse(document["itemIdScan"]["truncated"])
        self.assertEqual(document["itemIdScan"]["emittedFunctions"], ["0x826CFDC8"])
        self.assertIn("bad instruction data", document["candidateResults"][0]["stop"])
        self.assertIn("does not establish", document["boundedNegative"]["result"])
        self.assertIn("not an executable-wide absence", document["conclusion"])

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

    def test_gold_reserve_aggregate_lifecycle_boundary(self) -> None:
        path = MANIFESTS / "gold-reserve-aggregate-lifecycle-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0108")
        self.assertEqual(document["scope"]["aggregate"], "0x830ED544 + player*4")
        self.assertEqual(document["aggregateReferenceResult"]["references"], 0)
        self.assertEqual(len(document["ownerResults"]), 2)
        self.assertTrue(all(entry["modeledCallers"] == 0 for entry in document["ownerResults"]))
        self.assertIn("No additional exact reserve source", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_native_renderer_indexed_draw_caller_frontier(self) -> None:
        path = MANIFESTS / "native-renderer-indexed-draw-caller-frontier.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0109")
        self.assertEqual(document["scope"]["indexedDraw"], "0x82303C38")
        self.assertEqual(document["referenceResult"]["references"], 1)
        self.assertEqual(document["referenceResult"]["rows"][0]["source"], "0x82169E6C")
        self.assertEqual(document["referenceResult"]["directCodeCallers"], [])
        self.assertEqual(document["referenceResult"]["decompiledCallerFunctions"], [])
        self.assertIn("No direct caller-family ownership", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_save_profile_owner_lifetime_boundary(self) -> None:
        path = MANIFESTS / "save-profile-owner-lifetime-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0111")
        self.assertEqual(document["scope"]["ownerGlobal"], "0x8314EFE0")
        self.assertEqual(document["globalReferenceResult"]["references"], 107)
        self.assertEqual(document["globalReferenceResult"]["types"], {"READ": 107, "WRITE": 0})
        self.assertEqual(document["globalReferenceResult"]["modeledFunctions"], 65)
        self.assertEqual(len(document["bodyResults"]), 3)
        self.assertIn("No teardown, republication", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_xbox_dds_map_authoring_consumer_boundary(self) -> None:
        path = MANIFESTS / "xbox-dds-map-authoring-consumer-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0112")
        self.assertEqual(document["scope"]["terrainLoader"], "0x82C6E188")
        self.assertEqual(
            [entry["references"] for entry in document["stringReferenceResults"]],
            [0, 0, 0],
        )
        self.assertEqual(len(document["bodyResults"]), 2)
        self.assertEqual(document["provedProperties"]["newRoleSpecificProperties"], [])
        self.assertEqual(len(document["remainingBlockers"]), 6)
        self.assertIn("No new role-specific DDS consumer contract", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_calendar_event_year_consumer(self) -> None:
        path = MANIFESTS / "calendar-event-year-consumer.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0113")
        self.assertEqual(document["discovery"]["unionFunctionCount"], 5)
        self.assertEqual(document["discovery"]["pointerPlacements"], 0)
        self.assertEqual(document["eventYearConsumer"]["function"], "0x82DF9FD0")
        self.assertEqual(document["eventYearConsumer"]["objectYearField"], "+0x444")
        self.assertIn("return value 1", document["eventYearConsumer"]["immediateBranch"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], ["RVA-SYM-0337", "RVA-REL-0473"])

    def test_key2_game_start_registration_boundary(self) -> None:
        path = MANIFESTS / "key2-game-start-registration-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0114")
        self.assertEqual(document["referenceResults"]["combinedFunctionCount"], 2)
        self.assertEqual(document["referenceResults"]["factory"]["references"], 0)
        self.assertEqual(document["referenceResults"]["vtablePointerPlacements"], 0)
        self.assertEqual([entry["function"] for entry in document["bodyResults"]], ["0x821B0AF0", "0x82E60D50"])
        self.assertIn("No direct key-2 registration owner", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_frame_timing_field10_reader_boundary(self) -> None:
        path = MANIFESTS / "frame-timing-field10-reader-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0115")
        self.assertEqual(len(document["writerReconfirmation"]["fieldAccesses"]), 2)
        self.assertEqual(document["ownerReferenceResult"]["primaryGlobal"]["distinctReaderFunctions"], 28)
        self.assertEqual(document["ownerReferenceResult"]["candidateReadersInspected"], [])
        self.assertIn("exceeding the six-candidate cap", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_audio_stream_handle_lifecycle_boundary(self) -> None:
        path = MANIFESTS / "audio-stream-handle-lifecycle-boundary.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0117")
        self.assertEqual(document["scope"]["slotSize"], "0x38")
        self.assertEqual(document["referenceResults"]["writer"]["references"], 1)
        self.assertEqual(document["referenceResults"]["dispatcher"]["references"], 1)
        self.assertEqual(document["fieldReadResult"]["matches"], 0)
        self.assertIn("No exact first consumer", document["boundedNegative"]["result"])
        self.assertEqual(document["catalogPromotion"]["newEntities"], [])

    def test_hall_of_achievements_vtable_slot0(self) -> None:
        path = MANIFESTS / "hall-of-achievements-vtable-slot0.json"
        document = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(document["id"], "RVA-F-0119")
        self.assertEqual(document["slotResult"]["word"], "0x821C6AB8")
        self.assertEqual(document["slotResult"]["referenceCount"], 1)
        self.assertEqual(document["targetOperation"]["body"], "complete")
        self.assertEqual(document["targetOperation"]["returnedGlobal"], "0x8314F5D0")
        self.assertEqual(document["catalogPromotion"]["newEntities"], ["RVA-SYM-0338", "RVA-SYM-0339", "RVA-SLOT-0058", "RVA-REL-0474"])

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
