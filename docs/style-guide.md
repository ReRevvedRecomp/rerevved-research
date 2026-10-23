# Research style guide

This guide covers tracked scripts, records, and evidence prose. Content ownership
and evidence requirements follow the [documentation index](README.md), [evidence
model](evidence-model.md), [topic manifest](topic-manifests.md),
[catalog](catalogs.md), [workflow](workflow.md), and [comments and
prose](ai_agents/comments-and-prose.md) contracts.

## General style

- Focus changes on the maintained script, manifest, catalog, or reference page;
  follow local patterns.
- Use ASCII and short declarative prose. Preserve interface spelling in field
  names, commands, runtime strings, and test labels.
- Indent Python, PowerShell, and Java with four spaces. Ruff formats Python and
  sorts imports; see verification below.
- Preserve object, array, and domain order, including field and vtable-slot
  offsets. Do not reorder catalogs merely to sort IDs.
- Add each new page under `docs/` to its index: system references to
  [reference/README.md](reference/README.md), and workflows and guides to
  [README.md](README.md).

## Script families

### Python tools

Python tools in `tools/` use `from __future__ import annotations`,
standard-library imports before external imports, `pathlib.Path`, and typed
public helpers. Constants use `UPPER_SNAKE_CASE`;
functions and locals use `snake_case`; classes use `PascalCase`; private helpers
begin with `_`. Name distinct input failures with descriptive `...Error` classes.

CLIs use `argparse`, integer-returning `main()`, and `raise SystemExit(main())`.
For malformed input, report the path or field and return nonzero. Preserve
family conventions for `#!/usr/bin/env python3` and short module docstrings.

Keep record encoding, newline behavior, and serialization explicit.

Filenames use Python `snake_case`, PowerShell hyphenated names, and Java
`PascalCase`.

### PowerShell drivers

PowerShell drivers in `tools/` follow local `[CmdletBinding()]` and parameter
blocks. Use `Verb-Noun` functions, PascalCase parameters, and consistent local
variable casing. Resolve paths explicitly, reject missing inputs early, and set
`$ErrorActionPreference = 'Stop'` for dependent steps.

Use `tools\run-headless.ps1 -ReadOnly` for analysis and
`tools\bootstrap-ghidra.ps1` for mutating repairs in disposable projects.
`.SYNOPSIS` and `.DESCRIPTION` headers state the interface, required environment
or parameters, and output contract.

### Java Ghidra post-scripts

Java post-scripts in `ghidra/` use `PascalCase` public classes, `camelCase`
methods and locals, and `UPPER_SNAKE_CASE` constants. Use same-line braces,
grouped standard and Ghidra imports, and applicable `@Override` annotations.
Keep `//@category ReRevved` and document `REREVVED_*` inputs in entry comments.

Queries write bounded output through `REREVVED_DUMP_PATH` or their declared
interface and run through the read-only driver. Repairs retain bootstrap guards
and chain order. Name query limits and address ranges as constants.

## Comments and entry headers

The [comments and prose policy](ai_agents/comments-and-prose.md) governs comment
placement. Explain non-obvious guest locators, ABI/layout constraints, safety
boundaries, tool interfaces, generated-output limits, or provenance requirements
in one to three lines at the use site.

Comment individual enum members, fields, or list entries only for non-obvious
meaning or limits. Keep comments adjacent and short; put shared rationale above
the group.

Preserve interface metadata: Python shebangs/docstrings, PowerShell help, Java
`//@category`, and environment variable names. Runtime strings, command help,
catalog fields, and test labels are data or behavior. Edit generated output
through its generator and canonical input, never by hand for style.

## Names, addresses, and unknowns

Name narrow observed roles. A standalone topic filename uses lowercase
kebab-case matching `topic`; a family file matches its `family`; catalog names
follow their schemas. Allocate IDs and canonical homes
under the [topic manifest](topic-manifests.md) or [catalog](catalogs.md) contract.

Write guest VAs as `0x` plus eight uppercase hexadecimal digits; offsets use
`0x` plus uppercase hexadecimal without redundant leading zeroes. Retain
`sub_XXXXXXXX` and `DAT_XXXXXXXX` until evidence supports semantic names.

For unresolved fields, use neutral local patterns such as `byte_0C`, `word_08`,
or `value_10`; state remaining interpretation in the claim or qualification.

Unknown is a supported bounded result. Use explicit unknown/unresolved buckets,
alternatives, or falsification conditions where supported by the record shape.
Never hide uncertainty with invented semantic names, empty values, or omissions.

Keep `candidate` and `rejected` meanings aligned with the [evidence
model](evidence-model.md).

## Schemas and deterministic records

`schemas/` uses JSON Schema draft 2020-12, repository `$id` values, and shared
`common.schema.json` definitions. Catalog `additionalProperties: false` requires
schema and focused validator or test changes for new fields. Preserve declared
`schemaVersion`, required fields, enums, and relative image references; omit
optional data only where permitted.

Authored JSON uses two-space indentation, one property per line, a final newline,
stable keys, and domain-ordered arrays. Generated JSON/JSONL follows its emitter:
exporters sort inputs or records as needed, serialize explicitly, and emit one
JSONL object per line with a final newline.

Preserve the consumer's record type, fingerprint algorithm, key ordering, and
encoding; never hand-normalize output.

Topic manifests place identity fields first, then finding-specific sections;
reuse section shapes when extending a topic. A family file keys complete
records by `id` under `findings`. The four canonical catalogs hold
reusable entities and explicit relations; manifests hold investigations.

The [catalog contract](catalogs.md) and [topic manifest
contract](topic-manifests.md) own field and promotion rules.

## Evidence citations and public boundaries

Give each durable fact one tracked home; link elsewhere. Catalog topic citations
use relative JSON files and resolving JSON Pointers; cite a family finding
through `findings/<id>`. Script, generated, runtime,
and external locators follow their schemas. Tie images to `manifests/image.json`
and cite exact addresses, offsets, or producers.

Preserve the [evidence model](evidence-model.md) limits on static queries,
generated code, runtime probes, and external references, and all provenance
citations verbatim. Markdown links use relative tracked paths or direct
external references.

Keep private binaries, assets, Ghidra projects, raw output, logs, machine paths,
prompts, and session administration untracked. Reference prose separates findings
from proposals; manifests own evidence mechanics, and operational context stays
private.

## Verification

The gate needs Python with `tools/requirements-dev.txt` (runtime requirements
and pinned Ruff), plus JDK `java` and `javac` on `PATH`. Query-writer fixtures
need neither a Ghidra project nor retail assets.

Install dependencies and run checks:

```powershell
python -m pip install -r tools/requirements-dev.txt
$settings = Import-PowerShellDataFile ./tools/powershell-checks.psd1
Install-Module -Name $settings.Module.ModuleName `
    -RequiredVersion $settings.Module.RequiredVersion `
    -Repository PSGallery -Scope CurrentUser -Force -ErrorAction Stop
python -m ruff check .
python -m ruff format --check .
powershell -NoProfile -File tools\verify.ps1
```

Apply safe Ruff fixes and formatting:

```powershell
python -m ruff check --fix .
python -m ruff format .
```

After script, schema, manifest, or linked Markdown changes, run:

```powershell
powershell -NoProfile -File tools\verify.ps1
git diff --check
```

`tools\verify.ps1` parses JSON, validates catalogs and reference data, checks
Python with Ruff, checks PowerShell syntax, formatting and selected diagnostics
against [the pinned settings](../tools/powershell-checks.psd1), runs Python
tests, validates Markdown links and ASCII, and checks the Ghidra index,
production writer/rebuild wiring, and repository hygiene.

Run the focused test for a record family when its schema or validator changes.

## Commit subjects

Use `type: imperative summary`, at most 50 characters. Use `research:` for a
bounded finding that spans manifests, catalogs, or reference prose; `catalog:`
for catalog-only work; and `docs:`, `tools:`, `test:`, `fix:`, or `ci:` for
the matching change.
