from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
CANONICAL_MANIFEST = REPO / "manifests" / "native-renderer-d3d-inventory.json"
FULL_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ROOT_ID_RE = re.compile(r"^NRD-ROOT-[0-9]{4}$")
OP_ID_RE = re.compile(r"^NRD-OP-[0-9]{4}$")
CONTRACT_ID_RE = re.compile(r"^NRD-CONTRACT-[0-9]{4}$")
ADDRESS_RE = re.compile(r"^0x[0-9A-F]{8}$")
JOIN_RE = re.compile(r"^d3d:0x[0-9A-F]{8}$")

TOP_LEVEL_KEYS = {
    "schemaVersion",
    "id",
    "topic",
    "status",
    "confidence",
    "image",
    "question",
    "scope",
    "dependencies",
    "completenessRoots",
    "surface",
    "contracts",
    "unresolvedCoverage",
    "partialExport",
    "guards",
    "conclusion",
}
UNRESOLVED_COVERAGE_CATEGORIES = [
    "device-publication",
    "dispatch-table",
    "remaining-lowering-sinks",
    "subsystem-anchors",
    "control-seeds",
]
RETIRED_WORKFLOW_KEYS = {
    "state",
    "frontier",
    "classificationState",
    "nextDiscriminator",
    "semanticStatus",
}
CATALOG_IDS = {
    "RVA-SYM-0172",
    "RVA-SYM-0255",
    "RVA-VTBL-0010",
    "RVA-SLOT-0032",
    "RVA-REL-0349",
    "RVA-REL-0350",
}
TOPIC_REFS = {
    "gfx-draw-producer.json#/scope",
    "gfx-draw-producer.json#/currentEvidence/entries/10",
    "gfx-draw-producer.json#/drawSubmission",
    "gfx-draw-producer.json#/drawSubmission/issue",
    "gfx-fetch-allocation.json#/scope",
    "gfx-fetch-allocation.json#/currentEvidence/entries/2",
    "gfx-fetch-allocation.json#/vertexFetchProducer/wrapper",
    "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex",
}

EXPECTED_SCOPE = {
    "surface": "partial-bootstrap",
    "includedEvidence": [
        "NRD-ROOT-0001",
        "NRD-OP-0001",
        "NRD-OP-0002",
        "NRD-CONTRACT-0001",
    ],
    "staticRuntimeBoundary": "Static reachability is distinct from runtime observation.",
    "referenceBoundary": (
        "Indirect or unrecovered references remain outside the maintained "
        "repaired reference index."
    ),
    "unclassified": [
        "device publication",
        "dispatch-table extent",
        "other lowering sinks",
        "subsystem anchors",
        "control seeds",
        "object lifetimes",
        "resources",
        "formats",
        "states",
        "shaders",
        "EDRAM",
        "resolve",
        "swap",
        "presentation",
    ],
    "boundary": (
        "This is a partial inventory, not a completeness claim. It includes "
        "one lowering root, two reachable operations, and one primitive "
        "contract."
    ),
}
EXPECTED_UNRESOLVED_COVERAGE = {
    "categories": UNRESOLVED_COVERAGE_CATEGORIES,
    "evidenceBasis": [
        "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex"
    ],
}
EXPECTED_DEPENDENCIES = [
    {
        "topic": "gfx-draw-producer",
        "use": (
            "accepted indexed-draw identity, gates, renderer slot, and two "
            "direct issue callsites"
        ),
    },
    {
        "topic": "gfx-fetch-allocation",
        "use": "accepted flush-and-issue wrapper identity and direct wrapper call",
    },
    {
        "topic": "native-renderer-d3d-draw-lowering-frontier",
        "use": (
            "accepted repaired reference replay for the two direct callsites "
            "and bounded partial root"
        ),
    },
]


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _require_exact(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValidationError(f"{label} differs from the accepted value")


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _json_pointer(document: Any, pointer: str) -> Any:
    _require(pointer.startswith("#/"), f"invalid JSON Pointer: {pointer}")
    current = document
    for raw_part in pointer[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            _require(part.isdigit(), f"non-integer list index in {pointer}")
            index = int(part)
            _require(index < len(current), f"list index outside {pointer}")
            current = current[index]
        else:
            _require(isinstance(current, dict), f"non-container in {pointer}")
            _require(part in current, f"missing JSON Pointer component in {pointer}")
            current = current[part]
    return current


def _json_deep_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            _json_deep_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_deep_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _validate_copy_pointers(
    document: dict[str, Any],
    container: dict[str, Any],
    prefix: str,
    fields: set[str],
    label: str,
) -> None:
    pointers = container.get("source_pointers")
    _require(isinstance(pointers, dict), f"{label} source_pointers must be an object")
    _require_exact(set(pointers), fields, f"{label} source-pointer field set")
    for field in sorted(fields):
        expected_pointer = f"{prefix}/{field}"
        pointer = pointers[field]
        _require_exact(pointer, expected_pointer, f"{label} {field} source pointer")
        resolved = _json_pointer(document, pointer)
        _require(
            _json_deep_equal(resolved, container[field]),
            f"{label} {field} source pointer is not type/value-equal",
        )


def _resolve_topic_ref(repo: Path, reference: str) -> Any:
    name, separator, pointer = reference.partition("#")
    _require(separator == "#", f"topic reference lacks JSON Pointer: {reference}")
    _require(Path(name).name == name, f"topic reference is not a manifest name: {reference}")
    path = repo / "manifests" / name
    _require(path.is_file(), f"topic manifest is missing: {name}")
    document = json.loads(path.read_text(encoding="utf-8"))
    return _json_pointer(document, f"#{pointer}")


def _catalog_id_counts(repo: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in sorted((repo / "manifests" / "catalogs").glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        for value in _walk(document):
            if isinstance(value, dict) and isinstance(value.get("id"), str):
                record_id = value["id"]
                counts[record_id] = counts.get(record_id, 0) + 1
    return counts


def _all_references(document: dict[str, Any]) -> set[str]:
    references: set[str] = set()
    for value in _walk(document):
        if not isinstance(value, dict):
            continue
        for key in ("claimRefs", "signatureRefs", "evidenceBasis"):
            entries = value.get(key, [])
            if isinstance(entries, list):
                references.update(entry for entry in entries if isinstance(entry, str))
    for operation in document.get("surface", []):
        for predecessor in operation.get("predecessors", []):
            if isinstance(predecessor, dict):
                for key in ("vtable", "slot", "relation"):
                    if isinstance(predecessor.get(key), str):
                        references.add(predecessor[key])
    for contract in document.get("contracts", []):
        if isinstance(contract.get("identity"), str):
            references.add(contract["identity"])
    return references


def _validate_authorities(document: dict[str, Any], repo: Path) -> None:
    references = _all_references(document)
    _require(TOPIC_REFS <= references, "one or more accepted topic references are missing")
    for reference in sorted(reference for reference in references if ".json#" in reference):
        _resolve_topic_ref(repo, reference)

    counts = _catalog_id_counts(repo)
    _require(CATALOG_IDS <= references, "one or more accepted catalog IDs are missing")
    for record_id in sorted(reference for reference in references if reference.startswith("RVA-")):
        _require(counts.get(record_id) == 1, f"catalog ID does not resolve once: {record_id}")


def _validate_ids_and_links(document: dict[str, Any]) -> None:
    roots = document["completenessRoots"]
    operations = document["surface"]
    contracts = document["contracts"]
    families = (
        (roots, ROOT_ID_RE, "root"),
        (operations, OP_ID_RE, "operation"),
        (contracts, CONTRACT_ID_RE, "contract"),
    )
    all_ids: set[str] = set()
    for rows, pattern, label in families:
        ids = [row.get("id", "") for row in rows]
        _require(all(pattern.fullmatch(row_id) for row_id in ids), f"malformed {label} ID")
        _require(len(ids) == len(set(ids)), f"duplicate {label} ID")
        _require(not (all_ids & set(ids)), "ID reused across aggregate row families")
        all_ids.update(ids)

    root_ids = {row["id"] for row in roots}
    operation_ids = {row["id"] for row in operations}
    contract_ids = {row["id"] for row in contracts}
    addresses: set[str] = set()
    for operation in operations:
        address = operation.get("address", "")
        join = operation.get("runtimeJoinKey", "")
        _require(ADDRESS_RE.fullmatch(address) is not None, "malformed operation address")
        _require(address not in addresses, "duplicate operation address")
        addresses.add(address)
        _require(JOIN_RE.fullmatch(join) is not None, "malformed runtime join")
        _require(join == f"d3d:{address}", "runtime join differs from operation address")
        _require(set(operation.get("rootIds", [])) <= root_ids, "operation root does not resolve")
        _require(
            set(operation.get("contractRefs", [])) <= contract_ids,
            "operation contract does not resolve",
        )
        _require("discriminator" not in operation, "operation retains discriminator")
    for contract in contracts:
        linked = set(contract.get("operationIds", []))
        _require(linked <= operation_ids, "contract operation does not resolve")
        for operation_id in linked:
            operation = next(row for row in operations if row["id"] == operation_id)
            _require(contract["id"] in operation["contractRefs"], "contract link is not bidirectional")


def _validate_no_retired_workflow_fields(document: dict[str, Any]) -> None:
    for value in _walk(document):
        if not isinstance(value, dict):
            continue
        retired = RETIRED_WORKFLOW_KEYS & set(value)
        if retired:
            raise ValidationError(f"retired workflow field remains: {sorted(retired)[0]}")


def _validate_unresolved_coverage(document: dict[str, Any]) -> None:
    coverage = document["unresolvedCoverage"]
    categories = coverage.get("categories", [])
    _require(categories, "unresolved coverage categories are empty")
    _require(
        len(categories) == len(set(categories)),
        "duplicate unresolved coverage category",
    )
    _require(
        categories == UNRESOLVED_COVERAGE_CATEGORIES,
        "unresolved coverage categories differ from the accepted value",
    )
    _require(
        coverage.get("evidenceBasis") == EXPECTED_UNRESOLVED_COVERAGE["evidenceBasis"],
        "unresolved coverage evidence basis differs from the accepted value",
    )
    _require(EXPECTED_SCOPE["boundary"] == document["scope"].get("boundary"), "partial scope changed")

    forbidden_keys = {
        "id",
        "locator",
        "claimRefs",
        "runtimeJoinKey",
    }
    for value in _walk(document):
        if not isinstance(value, dict):
            continue
        for key in forbidden_keys:
            child = value.get(key)
            values = child if isinstance(child, list) else [child]
            _require(
                not any(item in UNRESOLVED_COVERAGE_CATEGORIES for item in values),
                f"unresolved coverage category leaked into {key}",
            )


def _validate_partial_export(document: dict[str, Any], repo: Path) -> None:
    partial_export = document.get("partialExport")
    _require(isinstance(partial_export, dict), "partialExport must be an object")
    _require_exact(
        set(partial_export),
        {"schema_version", "image_sha256", "surface", "source_pointers", "operations"},
        "partialExport field set",
    )
    _require_exact(partial_export["schema_version"], 1, "partialExport schema version")
    image_sha256 = _resolve_topic_ref(
        repo, "image.json#/analysisProgram/flatImageSha256"
    )
    _require_exact(partial_export["image_sha256"], image_sha256, "partialExport image SHA-256")
    _require_exact(partial_export["surface"], "partial", "partialExport surface")
    _validate_copy_pointers(
        document,
        partial_export,
        "#/partialExport",
        {"schema_version", "image_sha256", "surface"},
        "partialExport",
    )

    operations = partial_export["operations"]
    _require(isinstance(operations, list), "partialExport operations must be a list")
    _require_exact(len(operations), 1, "partialExport operation count")
    operation = operations[0]
    _require(isinstance(operation, dict), "partialExport operation must be an object")
    semantic_fields = {
        "operation_id",
        "runtime_join_key",
        "roles",
        "contract_ids",
        "hook_sites",
        "registers",
        "value_domains",
        "resource_action",
        "claim_refs",
    }
    _require_exact(
        set(operation), semantic_fields | {"source_pointers"}, "partialExport operation field set"
    )
    accepted_operation = document["surface"][1]
    _require_exact(operation["operation_id"], accepted_operation["id"], "export operation ID")
    _require_exact(
        operation["runtime_join_key"],
        accepted_operation["runtimeJoinKey"],
        "export runtime join",
    )
    _require_exact(operation["roles"], accepted_operation["roles"], "export roles")
    _require_exact(
        operation["contract_ids"], accepted_operation["contractRefs"], "export contracts"
    )
    _require_exact(
        operation["hook_sites"],
        [
            {
                "address": "0x82303E3C",
                "phase": "value",
                "discriminator": "primitive-4",
            },
            {
                "address": "0x82303E8C",
                "phase": "value",
                "discriminator": "primitive-4",
            },
        ],
        "export hook sites",
    )
    _require_exact(operation["registers"], [], "export registers")
    _require_exact(
        operation["value_domains"],
        [
            {"id": "primitive-4", "value": 4, "selection": "site-fixed"},
            {"id": "unknown", "value": None, "selection": "unmapped-input"},
        ],
        "export value domains",
    )
    _require_exact(operation["resource_action"], "none", "export resource action")
    _require_exact(
        operation["claim_refs"],
        [
            "#/surface/1",
            "#/contracts/0",
            "#/completenessRoots/0",
            "RVA-SYM-0255",
            "RVA-REL-0349",
            "gfx-draw-producer.json#/drawSubmission/issue",
            "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex",
        ],
        "export claim references",
    )
    _validate_copy_pointers(
        document,
        operation,
        "#/partialExport/operations/0",
        semantic_fields,
        "partialExport operation",
    )
    for value in _walk(partial_export):
        _require(
            value not in UNRESOLVED_COVERAGE_CATEGORIES,
            "unresolved coverage category leaked into partialExport",
        )


def _validate_exact_packet(document: dict[str, Any]) -> None:
    _require_exact(set(document), TOP_LEVEL_KEYS, "top-level field set")
    expected_header = {
        "schemaVersion": 1,
        "id": "RVA-F-0081",
        "topic": "native-renderer-d3d-inventory",
        "status": "open",
        "confidence": "candidate",
        "image": "image.json",
        "question": "What is the complete reachable title-used Xbox D3D surface above PM4?",
    }
    for key, expected in expected_header.items():
        _require_exact(document.get(key), expected, key)
    _require_exact(document["scope"], EXPECTED_SCOPE, "scope")
    _require_exact(document["dependencies"], EXPECTED_DEPENDENCIES, "dependencies")
    _require_exact(len(document["completenessRoots"]), 1, "root count")
    _require_exact(len(document["surface"]), 2, "operation count")
    _require_exact(len(document["contracts"]), 1, "contract count")

    root = document["completenessRoots"][0]
    _require_exact(root["id"], "NRD-ROOT-0001", "root ID")
    _require_exact(root["kind"], "lowering-sink", "root kind")
    _require_exact(root["locator"], "0x826A3568", "root locator")
    _require_exact(root["closureDirection"], "reverse", "root closure direction")
    _require_exact(
        root["claimRefs"],
        [
            "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex",
            "RVA-SYM-0255",
            "RVA-REL-0349",
        ],
        "root claim references",
    )
    for field in ("claim", "extentRule", "reproduction", "qualification"):
        _require(isinstance(root.get(field), str) and bool(root[field]), f"root lacks {field}")

    expected_operations = {
        "NRD-OP-0001": {
            "address": "0x82303C38",
            "name": "GfxIndexedDraw",
            "roles": ["entry-point", "lowering-boundary"],
            "classes": ["draw", "gfx"],
            "runtimeJoinKey": "d3d:0x82303C38",
            "claimRefs": [
                "RVA-SYM-0172",
                "RVA-VTBL-0010",
                "RVA-SLOT-0032",
                "RVA-REL-0349",
                "gfx-draw-producer.json#/currentEvidence/entries/10",
                "gfx-draw-producer.json#/drawSubmission",
                "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex",
            ],
        },
        "NRD-OP-0002": {
            "address": "0x826A3568",
            "name": "GraphicsFlushAndIssue",
            "roles": ["wrapper", "lowering-boundary"],
            "classes": ["draw", "state"],
            "runtimeJoinKey": "d3d:0x826A3568",
            "claimRefs": [
                "RVA-SYM-0255",
                "RVA-REL-0349",
                "RVA-REL-0350",
                "gfx-fetch-allocation.json#/currentEvidence/entries/2",
                "gfx-fetch-allocation.json#/vertexFetchProducer/wrapper",
                "native-renderer-d3d-draw-lowering-frontier.json#/repairedReferenceIndex",
            ],
        },
    }
    for operation in document["surface"]:
        expected = expected_operations.get(operation["id"])
        _require(expected is not None, "unexpected operation ID")
        for key, value in expected.items():
            _require_exact(operation.get(key), value, f"{operation['id']} {key}")
        _require_exact(operation["rootIds"], ["NRD-ROOT-0001"], "operation roots")
        _require_exact(operation["callerFamilies"], ["gfx-renderer"], "caller family")
        _require_exact(operation["contractRefs"], ["NRD-CONTRACT-0001"], "contracts")
        _require_exact(operation["staticReachability"], "reachable", "reachability")
        _require_exact(operation["confidence"], "strong", "operation confidence")
        for field in (
            "predecessors",
            "signatureRefs",
            "hostRequirements",
            "qualification",
            "reproduction",
        ):
            _require(bool(operation.get(field)), f"operation lacks {field}")

    contract = document["contracts"][0]
    _require_exact(contract["id"], "NRD-CONTRACT-0001", "contract ID")
    _require_exact(contract["kind"], "primitive", "contract kind")
    _require_exact(contract["identity"], "RVA-REL-0349", "contract identity")
    _require_exact(
        contract["operationIds"],
        ["NRD-OP-0001", "NRD-OP-0002"],
        "contract operations",
    )
    _require_exact(
        contract["claimRefs"],
        [
            "RVA-REL-0349",
            "gfx-draw-producer.json#/drawSubmission/issue",
            "gfx-fetch-allocation.json#/vertexFetchProducer/wrapper",
        ],
        "contract claim references",
    )
    _require("site-fixed primitive discriminator 4" in contract["hostRequirement"], "primitive value changed")
    _require("unknown discriminator" in contract["hostRequirement"], "unknown bucket missing")
    _require("0x82303E3C" in contract["reproduction"], "first hook site missing")
    _require("0x82303E8C" in contract["reproduction"], "second hook site missing")
    _require("0x826A3568" in contract["reproduction"], "hook target missing")

    _require_exact(
        document["unresolvedCoverage"],
        EXPECTED_UNRESOLVED_COVERAGE,
        "unresolved coverage",
    )
    _require_exact(len(document["guards"]), 4, "guard count")
    _require("Five unresolved coverage categories" in document["conclusion"], "conclusion changed")


def validate_document(document: dict[str, Any], repo: Path = REPO) -> None:
    _require(isinstance(document, dict), "aggregate must be a JSON object")
    for key in ("completenessRoots", "surface", "contracts"):
        _require(isinstance(document.get(key), list), f"{key} must be a list")
    _require(
        isinstance(document.get("unresolvedCoverage"), dict),
        "unresolvedCoverage must be an object",
    )
    _validate_no_retired_workflow_fields(document)
    _validate_exact_packet(document)
    _validate_ids_and_links(document)
    _validate_unresolved_coverage(document)
    _validate_partial_export(document, repo)
    _validate_authorities(document, repo)


def load_and_validate(path: Path = CANONICAL_MANIFEST) -> dict[str, Any]:
    document = json.loads(path.read_text(encoding="utf-8"))
    validate_document(document, path.resolve().parents[1])
    return document


def validate_partial_snapshot(snapshot: dict[str, Any], document: dict[str, Any]) -> None:
    partial_export = document["partialExport"]
    _require_exact(
        set(snapshot),
        set(partial_export) | {"published_research_commit", "aggregate_sha256"},
        "snapshot field set",
    )
    _require(
        FULL_COMMIT_RE.fullmatch(snapshot["published_research_commit"]) is not None,
        "snapshot research commit must be full lowercase hex",
    )
    _require(
        SHA256_RE.fullmatch(snapshot["aggregate_sha256"]) is not None,
        "snapshot aggregate SHA-256 must be lowercase hex",
    )
    for field, value in partial_export.items():
        _require(
            _json_deep_equal(snapshot[field], value),
            f"snapshot {field} diverges from partialExport",
        )
    _validate_copy_pointers(
        document,
        snapshot,
        "#/partialExport",
        {"schema_version", "image_sha256", "surface"},
        "snapshot",
    )
    operation_fields = set(snapshot["operations"][0]) - {"source_pointers"}
    _validate_copy_pointers(
        document,
        snapshot["operations"][0],
        "#/partialExport/operations/0",
        operation_fields,
        "snapshot operation",
    )


def _copy_partial_export(document: dict[str, Any]) -> dict[str, Any]:
    partial_export = document["partialExport"]
    _validate_copy_pointers(
        document,
        partial_export,
        "#/partialExport",
        {"schema_version", "image_sha256", "surface"},
        "partialExport",
    )
    for index, operation in enumerate(partial_export["operations"]):
        operation_fields = set(operation) - {"source_pointers"}
        _validate_copy_pointers(
            document,
            operation,
            f"#/partialExport/operations/{index}",
            operation_fields,
            "partialExport operation",
        )
    return deepcopy(partial_export)


def build_partial_snapshot(
    document: dict[str, Any], research_commit: str, aggregate_sha256: str
) -> dict[str, Any]:
    validate_document(document)
    _require(FULL_COMMIT_RE.fullmatch(research_commit) is not None, "research commit must be full lowercase hex")
    _require(SHA256_RE.fullmatch(aggregate_sha256) is not None, "aggregate SHA-256 must be lowercase hex")
    copied = _copy_partial_export(document)
    schema_version = copied.pop("schema_version")
    snapshot = {
        "schema_version": schema_version,
        "published_research_commit": research_commit,
        "aggregate_sha256": aggregate_sha256,
        **copied,
    }
    validate_partial_snapshot(snapshot, document)
    return snapshot


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the focused native-renderer D3D inventory")
    parser.add_argument("manifest", nargs="?", type=Path, default=CANONICAL_MANIFEST)
    parser.add_argument("--emit-partial-snapshot", action="store_true")
    parser.add_argument("--research-commit")
    parser.add_argument("--aggregate-sha256")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        document = load_and_validate(args.manifest)
        if not args.emit_partial_snapshot:
            _require(args.research_commit is None, "research commit is only valid for snapshot emission")
            _require(args.aggregate_sha256 is None, "aggregate SHA-256 is only valid for snapshot emission")
            print("native-renderer-d3d-inventory: valid")
            return 0

        _require(args.research_commit is not None, "snapshot emission requires --research-commit")
        _require(args.aggregate_sha256 is not None, "snapshot emission requires --aggregate-sha256")
        actual_sha256 = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
        _require(actual_sha256 == args.aggregate_sha256, "aggregate SHA-256 does not match manifest bytes")
        snapshot = build_partial_snapshot(document, args.research_commit, args.aggregate_sha256)
        print(json.dumps(snapshot, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"native-renderer-d3d-inventory: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
