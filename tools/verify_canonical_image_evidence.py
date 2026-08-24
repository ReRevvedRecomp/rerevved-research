#!/usr/bin/env python3
"""Verify private canonical-image observations and emit a sanitized attestation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "schemas" / "canonical-image-evidence-attestation.schema.json"
BOUNDARY = "Canonical-image evidence validation, not retail derivation validation."
FUNCTION_ID = "RVA-SYM-0223"
FIELD_ID = "RVA-FLD-0121"
FIELD_RELATION_ID = "RVA-REL-0290"
VTABLE_ID = "RVA-VTBL-0025"
VTABLE_RELATION_ID = "RVA-REL-0293"
FIELD_VALUE_SITE = "0x821B3BE8"
VTABLE_HIGH_SITE = "0x821B3BE0"
VTABLE_LOW_SITE = "0x821B3BEC"


class CanonicalImageContractError(ValueError):
    """Raised when the selected public replay contract is inconsistent."""


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def find_entity(document: dict[str, Any], entity_id: str) -> dict[str, Any]:
    for record in document.get("records", []):
        if record.get("id") == entity_id:
            return record
        for child_name in ("fields", "slots"):
            for child in record.get(child_name, []):
                if child.get("id") == entity_id:
                    return child
    raise CanonicalImageContractError(f"missing selected entity {entity_id}")


def evidence_site(record: dict[str, Any]) -> str:
    sites = []
    for evidence in record.get("evidence", []):
        if evidence.get("kind") != "ghidra-static":
            continue
        match = re.search(r":(0x[0-9A-F]{8})$", evidence.get("locator", ""))
        if match:
            sites.append(match.group(1))
    if len(sites) != 1:
        raise CanonicalImageContractError("selected relation needs one Ghidra site")
    return sites[0]


def load_contract(repo: Path = REPO) -> dict[str, Any]:
    image = load_json(repo / "manifests" / "image.json")["analysisProgram"]
    catalogs = {
        name: load_json(repo / "manifests" / "catalogs" / f"{name}.json")
        for name in ("symbols", "structs", "vtables", "relations")
    }
    function = find_entity(catalogs["symbols"], FUNCTION_ID)
    field = find_entity(catalogs["structs"], FIELD_ID)
    field_relation = find_entity(catalogs["relations"], FIELD_RELATION_ID)
    vtable = find_entity(catalogs["vtables"], VTABLE_ID)
    vtable_relation = find_entity(catalogs["relations"], VTABLE_RELATION_ID)

    if function.get("kind") != "function":
        raise CanonicalImageContractError("selected symbol is not a function")
    if (
        field_relation.get("kind") != "writes-field"
        or field_relation.get("from") != FUNCTION_ID
        or field_relation.get("to") != FIELD_ID
    ):
        raise CanonicalImageContractError("selected field relation changed")
    if (
        vtable_relation.get("kind") != "installs-vtable"
        or vtable_relation.get("from") != FUNCTION_ID
        or vtable_relation.get("to") != VTABLE_ID
    ):
        raise CanonicalImageContractError("selected vtable relation changed")

    return {
        "image": {
            "name": image["name"],
            "size": image["imageSize"],
            "sha256": image["flatImageSha256"],
            "imageBase": image["imageBase"],
            "processor": image["processor"],
        },
        "function_address": function["address"],
        "field_offset": int(field["offset"], 16),
        "field_store_site": evidence_site(field_relation),
        "vtable_address": vtable["address"],
        "vtable_store_site": evidence_site(vtable_relation),
    }


def check(name: str, entities: list[str], addresses: list[str], passed: bool):
    return {
        "name": name,
        "entities": entities,
        "addresses": addresses,
        "status": "pass" if passed else "fail",
    }


def nested(document: Any, *keys: str) -> Any:
    current = document
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def build_attestation(
    observations: Any, contract: dict[str, Any]
) -> dict[str, Any]:
    image = contract["image"]
    program = nested(observations, "program")
    function = nested(observations, "function")
    field = nested(observations, "fieldAccess")
    relation = nested(observations, "relation")

    checks = [
        check(
            "image-identity",
            [],
            [],
            isinstance(observations, dict)
            and observations.get("schemaVersion") == 1
            and isinstance(program, dict)
            and program.get("name") == image["name"]
            and program.get("sourceSize") == image["size"]
            and program.get("sourceSha256") == image["sha256"],
        ),
        check(
            "program-contract",
            [],
            [image["imageBase"]],
            isinstance(program, dict)
            and program.get("imageBase") == image["imageBase"]
            and program.get("imageSize") == image["size"]
            and program.get("processor") == image["processor"],
        ),
        check(
            "function-entry",
            [FUNCTION_ID],
            [contract["function_address"]],
            isinstance(function, dict)
            and function.get("id") == FUNCTION_ID
            and function.get("address") == contract["function_address"]
            and function.get("present") is True
            and function.get("entryMnemonic") == "mfspr",
        ),
        check(
            "field-access",
            [FUNCTION_ID, FIELD_ID, FIELD_RELATION_ID],
            [contract["function_address"], contract["field_store_site"]],
            isinstance(field, dict)
            and field.get("fieldId") == FIELD_ID
            and field.get("relationId") == FIELD_RELATION_ID
            and field.get("constantAddress") == FIELD_VALUE_SITE
            and field.get("constantMnemonic") == "li"
            and field.get("constantRegister") == field.get("sourceRegister")
            and field.get("value") == 5
            and field.get("storeAddress") == contract["field_store_site"]
            and field.get("storeMnemonic") == "stw"
            and field.get("baseRegister") == "r3"
            and field.get("offset") == contract["field_offset"],
        ),
        check(
            "vtable-ownership",
            [FUNCTION_ID, VTABLE_ID, VTABLE_RELATION_ID],
            [
                contract["function_address"],
                contract["vtable_store_site"],
                contract["vtable_address"],
            ],
            isinstance(relation, dict)
            and relation.get("id") == VTABLE_RELATION_ID
            and relation.get("from") == FUNCTION_ID
            and relation.get("to") == VTABLE_ID
            and relation.get("highAddress") == VTABLE_HIGH_SITE
            and relation.get("highMnemonic") == "lis"
            and relation.get("highRegister") == relation.get("lowBaseRegister")
            and relation.get("lowAddress") == VTABLE_LOW_SITE
            and relation.get("lowMnemonic") == "addi"
            and relation.get("lowTargetRegister") == relation.get("sourceRegister")
            and relation.get("storeAddress") == contract["vtable_store_site"]
            and relation.get("storeMnemonic") == "stw"
            and relation.get("baseRegister") == "r3"
            and relation.get("offset") == 0
            and relation.get("valueAddress") == contract["vtable_address"],
        ),
    ]
    passed = sum(item["status"] == "pass" for item in checks)
    return {
        "schemaVersion": 1,
        "artifact": "canonical-image-evidence-attestation",
        "claimBoundary": BOUNDARY,
        "image": image,
        "checks": checks,
        "result": {
            "status": "pass" if passed == len(checks) else "fail",
            "passed": passed,
            "total": len(checks),
        },
    }


def attestation_validator(repo: Path = REPO) -> Draft202012Validator:
    common = load_json(repo / "schemas" / "common.schema.json")
    schema = load_json(repo / "schemas" / SCHEMA_PATH.name)
    Draft202012Validator.check_schema(schema)
    registry = Registry().with_resource(
        common["$id"], Resource.from_contents(common)
    )
    return Draft202012Validator(schema, registry=registry)


def validate_attestation(document: dict[str, Any], repo: Path = REPO) -> None:
    errors = list(attestation_validator(repo).iter_errors(document))
    if errors:
        raise CanonicalImageContractError("sanitized attestation failed its schema")
    result = document["result"]
    passed = sum(item["status"] == "pass" for item in document["checks"])
    if result["passed"] != passed or result["total"] != len(document["checks"]):
        raise CanonicalImageContractError("attestation summary counts are inconsistent")
    if (passed == len(document["checks"])) != (result["status"] == "pass"):
        raise CanonicalImageContractError("attestation summary status is inconsistent")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.preflight == (args.input is not None):
        parser.error("choose exactly one of --preflight or --input")
    return args


def main() -> int:
    args = parse_args()
    contract = load_contract()
    if args.preflight:
        validator = attestation_validator()
        failure = build_attestation(None, contract)
        if list(validator.iter_errors(failure)):
            raise CanonicalImageContractError("preflight attestation failed its schema")
        print("canonical-image evidence preflight: PASS")
        return 0

    try:
        observations = load_json(args.input)
    except (OSError, UnicodeError, json.JSONDecodeError):
        observations = None
    attestation = build_attestation(observations, contract)
    validate_attestation(attestation)
    json.dump(attestation, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if attestation["result"]["status"] != "pass":
        print("canonical-image evidence verification failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CanonicalImageContractError as exc:
        raise SystemExit(str(exc)) from exc
