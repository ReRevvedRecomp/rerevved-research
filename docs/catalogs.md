# Catalog contract

Four `manifests/catalogs/` files canonically inventory symbols, structs/fields,
vtables/slots and explicit relations. Investigation manifests are neither
generated from catalogs nor rewritten by promotion. See
[topic contract](topic-manifests.md) for fields, evidence, dependencies and
promotion boundaries.

## Identity and formats

Allocate unique four-digit IDs by kind: `RVA-SYM-`, `RVA-STR-`, `RVA-FLD-`,
`RVA-VTBL-`, `RVA-SLOT-`, `RVA-REL-`. Gate rejects duplicates across all four
catalogs. Reserved maxima: symbol 0278, struct 0050, field 0158, vtable 0028,
slot 0043, relation 0387. Keep established IDs; allocate above maxima, never
repurpose gaps.

Addresses: `0x` plus eight uppercase hex digits. Offsets: `0x` plus uppercase
hex, no redundant zeroes. Prefer placeholders such as `sub_82267A28` until
semantic evidence exists. Every top-level record references `../image.json`;
verify native addresses/locators against that image before promotion.

## Evidence and confidence

Each claim needs evidence in schema-supported form:

| Kind | Locator |
| --- | --- |
| `topic-manifest` | Catalog-relative JSON/resolving Pointer, e.g. `../runtime-baseline.json#/configuredRoot` |
| `ghidra-static` | Maintained script/optional site, e.g. `ghidra/DumpFunctions.java:0x821F3F48`; validator checks `ghidra/` existence |
| `generated-code` | e.g. `generated:rerevved/sub_821B0AF0` |
| `runtime-probe` | Named probe, e.g. `runtime:save_slot_probe` |
| `external-reference` | HTTPS URL |

Confidence is exactly:

- `confirmed`: authoritative static identity, or runtime-corroborated behavior.
- `strong`: direct evidence with remaining boundary.
- `candidate`: bounded interpretation needing discrimination.
- `rejected`: falsified candidate retained to prevent repetition.

Each claim needs an unresolved alternative or explicit falsification condition.

## Relations

Assert relations only with evidence for the edge; names, proximity, shapes and
endpoint evidence are insufficient. Endpoints must be existing symbol, struct,
field, vtable or slot IDs. `tools\verify.ps1` loads four schemas, checks global
IDs/endpoints, resolves topic evidence and runs focused negative tests.
