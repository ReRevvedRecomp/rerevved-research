from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from verify_canonical_image_evidence import (  # noqa: E402
    build_attestation,
    load_contract,
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
                "5C7A8C3AD9B6A9D39CC9BBF3DA5AB230"
                "15A568C65C723D298F846086324C4680"
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
    def setUp(self):
        self.contract = load_contract(REPO)

    def test_matching_observations_pass(self):
        attestation = build_attestation(observations(), self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(attestation["result"], {"status": "pass", "passed": 5, "total": 5})

    def test_negative_field_mutation_fails(self):
        mutated = observations()
        mutated["fieldAccess"]["value"] = 6
        attestation = build_attestation(mutated, self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(attestation["result"]["status"], "fail")
        self.assertEqual(
            next(item for item in attestation["checks"] if item["name"] == "field-access")["status"],
            "fail",
        )

    def test_missing_observations_produce_schema_valid_failure(self):
        attestation = build_attestation(None, self.contract)
        validate_attestation(attestation, REPO)
        self.assertEqual(attestation["result"], {"status": "fail", "passed": 0, "total": 5})

if __name__ == "__main__":
    unittest.main()
