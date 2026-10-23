# Topic manifest contract

Topic manifests in `manifests/*.json` canonically record each bounded question,
current-image evidence, limits, and conclusion. Raw decompiler output, query
reports, and runtime logs remain scratch.

The four `manifests/catalogs/` files inventory reusable symbols, structures
and fields, vtables and slots, and explicit relations. Promote reusable facts
there while preserving the investigation record. Catalog evidence can cite a
manifest by JSON Pointer; keep catalog inventories and investigations distinct.

## Identity and common fields

A topic manifest is a JSON file directly under `manifests/`, with a `topic`
field, or one finding in a family file. The checkout enforces these common
fields except `question`:

| Field | Rule |
| --- | --- |
| `schemaVersion` | Exactly `1`. |
| `id` | Unique across topic manifests and matches `RVA-F-` plus four digits. |
| `topic` | Lowercase kebab-case and unique; a standalone file's stem equals it. |
| `status` | `open` or `closed`: whether the bounded investigation remains active. |
| `confidence` | `confirmed`, `strong`, `candidate`, or `rejected`. |
| `image` | Exactly `image.json`, the supported image contract. |
| `question` | Narrow question answered or bounded by the evidence; required by convention, not the focused manifest test. |

| Descriptive section | Role |
| --- | --- |
| `scope` | Bounded functions, fields, addresses, or other surface |
| `currentEvidence` | Current-image support, when present |
| `guards` | Claims that must not be inferred |
| `conclusion` | Supported result |

Descriptive sections are conventions, not a fixed schema; adapt their shape
to the finding.

## Family files

A family file groups related findings that share a subject. Its fields are
`schemaVersion` (`1`), `family` (equal to the filename stem) and `findings`: a
nonempty object keyed by each record's `id`. Each record is a complete topic
manifest with its own `topic`; the family name is not a topic. Cite a finding as
`family.json#/findings/<id>` plus a pointer into the record. Group findings
only when they share a subject; keep each question, conclusion, observation,
and guard as its own record.

Confidence labels describe the evidence, not completion status:

- `confirmed` requires authoritative static identity or runtime corroboration
  for a behavioral claim.
- `strong` has direct evidence with a remaining boundary.
- `candidate` is a bounded interpretation needing discrimination.
- `rejected` retains a falsified candidate to prevent repeated work.

## Dependencies and current evidence

New manifests may use `dependencies`: objects with `topic` and a concise `use`
explaining the dependency. The focused test requires lowercase kebab-case
topics naming a standalone manifest or a family finding; `use` is a
contribution rule.
Older manifests may use `dependsOn` or omit `use`; normalize them only when
editing that manifest. Dependencies name current evidence inputs, not old
paths, commits, migrations, or relocations. Dependents retain their own
current-image locators.

Optional `currentEvidence` describes checkout-current methods, entries,
locators, and qualifications. History is not evidence: prohibit `commit`,
`migration`, `relocation`, and `sourceEvidence` throughout topic manifests.

Do not use these comparison or source-target keys in `currentEvidence`:
`pairs`, `source`, `sourceAddress`, `sourceInstructionCount`, `sourceVtable`,
`target`, `targetAddress`, `targetInstructionCount`, and `targetVtable`.

Qualifications record remaining boundaries, unresolved alternatives, or
falsification conditions. Cite exact guest addresses and offsets with the
supporting static, generated, runtime, or external evidence. Address proximity,
matching shapes, and decompiler guesses do not establish identity or behavior.

Java locators under `ghidra/` must resolve to maintained scripts. For an
unrecoverable historical producer, preserve the exact citation in top-level
`historicalToolReferences`: `locator` plus a nonempty `qualification` explaining
provenance and replay limits. This neither creates a current dependency nor
attributes evidence to a similarly named script. All other script references
must resolve in the checkout.

## Recording findings

Query narrowly in read-only mode; keep output in ignored scratch. Verify
conclusions against the image pinned by `manifests/image.json`. Behavioral
claims need a narrow generated-code comparison and a default-off runtime probe.

Retain compact supported facts, evidence, uncertainty, guards, and conclusions.
Promote reusable entities or edges with their own catalog evidence and resolving
JSON Pointers for topic citations. Promotion neither replaces nor requires
rewriting the investigation record.

## Structural example

This illustrative finding needs an existing dependency topic in a real manifest.

```json
{
  "schemaVersion": 1,
  "id": "RVA-F-0099",
  "topic": "example-boundary",
  "status": "closed",
  "confidence": "strong",
  "image": "image.json",
  "question": "Where does the bounded producer write the record?",
  "scope": { "function": "0x82123456", "recordOffset": "0x10" },
  "dependencies": [
    { "topic": "scene-render-tree-publication", "use": "current owner boundary" }
  ],
  "currentEvidence": {
    "method": "foreground read-only query and narrow generated-code comparison",
    "entries": [
      { "role": "record producer", "address": "0x82123456", "confidence": "strong" }
    ],
    "qualification": "The record field is bounded. Its original semantic name remains unresolved."
  },
  "guards": ["Do not infer runtime success from this static boundary."],
  "conclusion": "The producer writes the bounded record field at offset 0x10."
}
```
