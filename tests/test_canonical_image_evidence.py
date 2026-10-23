from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from verify_canonical_image_evidence import (  # noqa: E402
    CanonicalImageContractError,
    attestation_validator,
    build_attestation,
    load_contract,
    matching_registers,
    validate_attestation,
)


def observations() -> dict:
    return {
        "schemaVersion": 1,
        "program": {
            "name": "rerevved_image.bin",
            "imageBase": "0x82000000",
            "imageSize": 18939904,
            "processor": "PowerPC:BE:32:default",
            "sourceSize": 18939904,
            "sourceSha256": (
                "5C7A8C3AD9B6A9D39CC9BBF3DA5AB23015A568C65C723D298F846086324C4680"
            ),
        },
        "function": {
            "id": "RVA-SYM-0223",
            "address": "0x821B3BB8",
            "present": True,
            "entryMnemonic": "mfspr",
        },
        "fieldAccess": {
            "fieldId": "RVA-FLD-0121",
            "relationId": "RVA-REL-0290",
            "constantAddress": "0x821B3BE8",
            "constantMnemonic": "li",
            "constantRegister": "r9",
            "value": 5,
            "storeAddress": "0x821B3BF4",
            "storeMnemonic": "stw",
            "sourceRegister": "r9",
            "baseRegister": "r3",
            "offset": 4,
        },
        "relation": {
            "id": "RVA-REL-0293",
            "from": "RVA-SYM-0223",
            "to": "RVA-VTBL-0025",
            "highAddress": "0x821B3BE0",
            "highMnemonic": "lis",
            "highRegister": "r10",
            "lowAddress": "0x821B3BEC",
            "lowMnemonic": "addi",
            "lowTargetRegister": "r8",
            "lowBaseRegister": "r10",
            "storeAddress": "0x821B3BF8",
            "storeMnemonic": "stw",
            "sourceRegister": "r8",
            "baseRegister": "r3",
            "offset": 0,
            "valueAddress": "0x82121320",
        },
    }


class CanonicalImageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded_contract = load_contract(REPO)

    def setUp(self):
        # build_attestation aliases the contract image into its output and
        # tests mutate that output, so each test gets its own copy.
        self.contract = deepcopy(self.loaded_contract)

    def test_matching_observations_pass(self):
        attestation = build_attestation(observations(), self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(
            attestation["result"], {"status": "pass", "passed": 5, "total": 5}
        )

    def test_negative_field_mutation_fails(self):
        mutated = observations()
        mutated["fieldAccess"]["value"] = 6
        attestation = build_attestation(mutated, self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(attestation["result"]["status"], "fail")
        self.assertEqual(
            next(
                item for item in attestation["checks"] if item["name"] == "field-access"
            )["status"],
            "fail",
        )

    def test_register_pairs_require_two_nonempty_strings(self):
        for label, left, right, expected in (
            ("remove-left", None, "r9", False),
            ("remove-right", "r9", None, False),
            ("remove-both", None, None, False),
            ("null-left", None, "r9", False),
            ("null-right", "r9", None, False),
            ("empty-left", "", "r9", False),
            ("empty-right", "r9", "", False),
            ("non-string-equal", 7, 7, False),
            ("differing-valid", "r9", "r99", False),
            ("matching", "r9", "r9", True),
        ):
            with self.subTest(case=label):
                self.assertIs(matching_registers(left, right), expected)

    def test_register_pair_call_sites_reject_missing_registers(self):
        pairs = (
            ("fieldAccess", "field-access", "constantRegister", "sourceRegister"),
            ("relation", "vtable-ownership", "highRegister", "lowBaseRegister"),
            ("relation", "vtable-ownership", "lowTargetRegister", "sourceRegister"),
        )
        for path, check_name, left_key, right_key in pairs:
            with self.subTest(pair=(path, left_key, right_key)):
                mutated = observations()
                mutated[path].pop(left_key)
                mutated[path].pop(right_key)
                attestation = build_attestation(mutated, self.contract)
                validate_attestation(attestation, REPO)
                self.assertEqual(attestation["result"]["status"], "fail")
                self.assertEqual(
                    next(
                        item
                        for item in attestation["checks"]
                        if item["name"] == check_name
                    )["status"],
                    "fail",
                )

    def test_inconsistent_summary_is_rejected(self):
        for field, value, diagnostic in (
            ("passed", 4, "summary counts"),
            ("total", 4, "summary counts"),
            ("status", "fail", "summary status"),
        ):
            with self.subTest(field=field):
                document = build_attestation(observations(), self.contract)
                document["result"][field] = value
                self.assertEqual(
                    list(attestation_validator(REPO).iter_errors(document)), []
                )
                with self.assertRaisesRegex(CanonicalImageContractError, diagnostic):
                    validate_attestation(document, REPO)

    def test_isolated_observation_mismatches(self):
        for section, field, value, failed_check in (
            ("program", "sourceSize", 1, "image-identity"),
            ("program", "sourceSha256", "0" * 64, "image-identity"),
            ("program", "processor", "other", "program-contract"),
            ("function", "present", False, "function-entry"),
            ("relation", "valueAddress", "0x00000000", "vtable-ownership"),
        ):
            with self.subTest(section=section, field=field):
                mutated = observations()
                mutated[section][field] = value
                attestation = build_attestation(mutated, self.contract)
                validate_attestation(attestation, REPO)
                self.assertEqual(
                    attestation["result"], {"status": "fail", "passed": 4, "total": 5}
                )
                self.assertEqual(
                    [
                        item["name"]
                        for item in attestation["checks"]
                        if item["status"] == "fail"
                    ],
                    [failed_check],
                )

    def test_missing_observations_produce_schema_valid_failure(self):
        attestation = build_attestation(None, self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(
            attestation["result"], {"status": "fail", "passed": 0, "total": 5}
        )

    def test_incomplete_or_duplicate_checks_fail_even_with_consistent_summary(self):
        original = build_attestation(observations(), self.contract)
        mutations = []
        for index in range(5):
            missing = deepcopy(original)
            missing["checks"].pop(index)
            mutations.append(missing)
        duplicate = deepcopy(original)
        duplicate["checks"][-1] = deepcopy(duplicate["checks"][0])
        duplicate["checks"][-1]["status"] = "fail"
        mutations.append(duplicate)
        arbitrary = deepcopy(original)
        arbitrary["checks"] = [
            {"name": "anything", "entities": [], "addresses": [], "status": "pass"}
        ]
        mutations.append(arbitrary)
        extra = deepcopy(original)
        extra["checks"].append(deepcopy(arbitrary["checks"][0]))
        mutations.append(extra)

        for index, document in enumerate(mutations):
            with self.subTest(mutation=index):
                checks = document["checks"]
                passed = sum(item["status"] == "pass" for item in checks)
                document["result"] = {
                    "status": "pass" if passed == len(checks) else "fail",
                    "passed": passed,
                    "total": len(checks),
                }
                self.assertTrue(list(attestation_validator(REPO).iter_errors(document)))
                with self.assertRaises(CanonicalImageContractError):
                    validate_attestation(document, REPO)

    def test_checks_may_be_reordered(self):
        document = build_attestation(observations(), self.contract)
        document["checks"].reverse()
        validate_attestation(document, REPO)

    def test_image_identity_must_match_the_selected_contract(self):
        for field, value in (
            ("size", 1),
            ("sha256", "0" * 64),
            ("imageBase", "0x00000000"),
        ):
            with self.subTest(field=field):
                document = build_attestation(observations(), self.contract)
                document["image"][field] = value
                with self.assertRaisesRegex(CanonicalImageContractError, "image"):
                    validate_attestation(document, REPO)

    def test_check_identity_must_match_the_selected_contract(self):
        for index in range(5):
            for field, value in (
                ("entities", ["RVA-SYM-9999"]),
                ("addresses", ["0x00000000"]),
            ):
                with self.subTest(check=index, field=field):
                    document = build_attestation(observations(), self.contract)
                    document["checks"][index][field] = value
                    with self.assertRaisesRegex(CanonicalImageContractError, field):
                        validate_attestation(document, REPO)


if __name__ == "__main__":
    unittest.main()
