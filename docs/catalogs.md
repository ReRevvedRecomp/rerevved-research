# Catalog contract

Four `manifests/catalogs/` files are the canonical inventory of symbols, structs and fields,
vtables and slots, and explicit relations. Investigation manifests are neither
generated from catalogs nor rewritten by promotion. See
[topic contract](topic-manifests.md) for fields, evidence, dependencies and
promotion boundaries.

## Identity and formats

Allocate unique four-digit IDs by kind: `RVA-SYM-`, `RVA-STR-`, `RVA-FLD-`,
`RVA-VTBL-`, `RVA-SLOT-`, `RVA-REL-`. The verification check rejects duplicates across all four
catalogs. Reserved maxima: symbol 0278, struct 0050, field 0158, vtable 0028,
slot 0043, relation 0387. Keep established IDs. Allocate above the maxima and never
repurpose gaps.

Addresses use `0x` plus eight uppercase hex digits. Offsets use `0x` plus uppercase
hex with no redundant zeroes. Prefer placeholders such as `sub_82267A28` until
semantic evidence exists. Every top-level record references `../image.json`.
Verify native addresses and locators against that image before promotion.

## Evidence and confidence

Each claim needs evidence in schema-supported form:

| Kind | Locator |
| --- | --- |
| `topic-manifest` | Catalog-relative JSON with a resolving pointer, e.g. `../runtime-baseline.json#/configuredRoot` |
| `ghidra-static` | Maintained script with an optional site, e.g. `ghidra/DumpFunctions.java:0x821F3F48`; validator checks `ghidra/` existence |
| `generated-code` | e.g. `generated:rerevved/sub_821B0AF0` |
| `runtime-probe` | Named probe, e.g. `runtime:save_slot_probe` |
| `external-reference` | HTTPS URL |

Confidence is exactly one of:

- `confirmed`: authoritative static identity, or runtime-corroborated behavior.
- `strong`: direct evidence with a remaining limit.
- `candidate`: a limited interpretation that needs discrimination.
- `rejected`: a falsified candidate, kept to prevent repetition.

Each claim needs an unresolved alternative or explicit falsification condition.

## Relations

Assert relations only with evidence for the edge; names, proximity, shapes and
endpoint evidence are insufficient. Endpoints must be existing symbol, struct,
field, vtable or slot IDs. `tools\verify.ps1` loads four schemas, checks global
IDs and endpoints, resolves topic evidence and runs focused negative tests.
