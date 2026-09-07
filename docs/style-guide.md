# Research style guide

This guide covers tracked scripts, machine-readable records, and evidence-facing prose in
ReRevved Research. Content ownership and evidence requirements live in the [documentation
index](README.md), especially the [evidence model](evidence-model.md), [topic manifest](topic-manifests.md),
[catalog](catalogs.md), [workflow](workflow.md), and [comments and prose](ai_agents/comments-and-prose.md) contracts.

## General style

- Keep changes focused on the script, manifest, catalog, or reference page being maintained.
  Follow an established local pattern first.
- Tracked source is ASCII. Use ordinary ASCII punctuation and short declarative prose. Keep
  field names, command names, runtime strings, and test labels exact when they are interfaces.
- Use four spaces for Python, PowerShell, and Java indentation. Keep surrounding formatting;
  this repository has no configured source formatter.
- Keep stable object and array order. Preserve domain order, such as field or vtable-slot
  offsets. Do not reorder existing catalog records only to sort IDs.

## Script families

### Python tools

Python tools live under `tools/`. The established pattern is `from __future__ import annotations`,
standard-library imports before external imports, `pathlib.Path`, and typed public helpers.
Constants use `UPPER_SNAKE_CASE`; functions and locals use `snake_case`; classes use `PascalCase`;
private helpers begin with `_`. Use a descriptive `...Error` class for a distinct input failure.

Command-line tools use `argparse`, expose an integer-returning `main()`, and end with
`raise SystemExit(main())`. Report malformed input with a useful path or field and return
nonzero. Standalone tools commonly include `#!/usr/bin/env python3` and a short module
docstring; preserve the file family's convention. Keep record encoding, newline behavior,
and serialization explicit.

Existing tool filenames use both `snake_case.py` and hyphenated command names; match the
nearest tool family rather than renaming an existing command.

### PowerShell drivers

PowerShell drivers live under `tools/`. Follow the local `[CmdletBinding()]` and parameter-block
pattern. Use `Verb-Noun` function names and PascalCase parameters; keep local variable casing
consistent with the script. Resolve paths explicitly, fail early on missing inputs, and set
`$ErrorActionPreference = 'Stop'` when later steps depend on earlier commands.

The read-only analysis entry point is `tools\run-headless.ps1` with `-ReadOnly`. The mutating
repair chain is entered through `tools\bootstrap-ghidra.ps1` and targets a disposable project.
Headers state the interface, required environment or parameters, and output contract in the
style of `.SYNOPSIS` and `.DESCRIPTION`.

### Java Ghidra post-scripts

Java post-scripts live under `ghidra/`. Filenames and public classes use `PascalCase`; methods
and locals use `camelCase`; constants use `UPPER_SNAKE_CASE`. Use four spaces, same-line braces,
grouped standard and Ghidra imports, and `@Override` where applicable. Keep `//@category ReRevved`
and document `REREVVED_*` inputs in the entry comment.

A query script writes bounded output to `REREVVED_DUMP_PATH` or its declared output interface and
runs through the read-only driver. A repair script retains its bootstrap guard and ordered-chain
contract. Keep query limits and address ranges as named constants.

## Comments and entry headers

Use the [comments and prose policy](ai_agents/comments-and-prose.md) as the authority for
whether a comment belongs. A short entry comment is useful for a non-obvious guest locator,
ABI or layout constraint, safety boundary, tool interface, generated-output boundary, or
provenance requirement. Keep it to one to three lines at the use site.

Use ordinary inline comments on individual enum members, fields, or list entries only when
that entry's meaning or boundary is non-obvious. Put shared rationale above the group; keep
each per-entry comment adjacent and short.

Preserve language and tool metadata: Python shebangs and module docstrings, PowerShell help
blocks, Java `//@category` lines, and environment-variable names are interfaces. Runtime
strings, command help, catalog fields, and test labels are data or behavior. Generated output
belongs to its generator and canonical input and is never hand-edited for style.

## Names, addresses, and unknowns

Use names that describe the narrow observed role. Topic files use lowercase kebab-case and their
filename stem matches `topic`; catalog names follow their schema. Allocate IDs and choose a
canonical home under the [topic manifest contract](topic-manifests.md) or [catalog contract](catalogs.md).

Write guest virtual addresses as `0x` followed by eight uppercase hexadecimal digits. Write
offsets as `0x` followed by uppercase hexadecimal with no redundant leading zeroes. Keep
placeholders such as `sub_XXXXXXXX` and `DAT_XXXXXXXX` until evidence supports a semantic name.
For an unresolved field, use a neutral nearby pattern such as `byte_0C`, `word_08`, or
`value_10`, and state the remaining interpretation in the claim or qualification.

Unknown is a supported result when evidence bounds a question without resolving it. Record an
explicit unknown or unresolved bucket, alternative, or falsification condition when the record
shape provides one. Do not use an invented semantic name, empty placeholder value, or missing
record to hide uncertainty. Keep `candidate` and `rejected` meanings aligned with the
[evidence model](evidence-model.md).

## Schemas and deterministic records

Schemas under `schemas/` use JSON Schema draft 2020-12, a repository `$id`, and shared
definitions from `common.schema.json`. Catalog schemas use `additionalProperties: false`, so a
new field needs a schema and focused validator or test change. Use declared `schemaVersion`,
required fields, enums, and relative image references exactly; omit optional data only where
permitted.

Human-maintained JSON uses two-space indentation, one property per line, and a trailing newline.
Keep key order stable and arrays in domain order. Generated JSON and JSONL follow the emitting
tool's exact contract: existing exporters sort inputs or records where needed, serialize
explicitly, and emit one JSONL object per line with a final newline. Preserve the consumer's
record type, fingerprint algorithm, key ordering, and encoding; never hand-normalize output.

Topic manifests keep common identity fields at the top and finding details in descriptive
sections suited to the bounded question. Use existing section shapes when extending a topic.
Catalog records keep reusable entities and explicit relations in the four canonical files; a
topic manifest remains the investigation record. The [catalog contract](catalogs.md) and
[topic manifest contract](topic-manifests.md) own field and promotion rules.

## Evidence citations and public boundaries

Give each durable fact one canonical tracked home and link to it from other pages. A catalog
entry naming a topic manifest uses its relative JSON file and a resolving JSON Pointer. Script,
generated, runtime, and external locators use the forms accepted by the schema. Tie image
references to `manifests/image.json` and cite the exact address, offset, or producing tool.

Static queries, generated code, runtime probes, and external references have the limits in the
[evidence model](evidence-model.md); preserve source and provenance citations verbatim. Public
Markdown uses relative links to tracked pages or direct external references. Keep private
binaries, assets, Ghidra projects, raw output, logs, machine paths, prompts, and work-session
administration outside tracked files. Public reference prose states settled behavior; evidence
mechanics stay in manifests and private operations stay in the maintainer island.

## Verification

Run the repository gate after changing a script, schema, manifest, or linked Markdown page:

```powershell
powershell -NoProfile -File tools\verify.ps1
git diff --check
```

`tools\verify.ps1` parses JSON, validates catalogs and reference data, checks Python and
PowerShell syntax, runs Python tests, validates Markdown links and ASCII, checks the Ghidra
index, and checks repository hygiene. Run the focused test for a record family when its schema
or validator changes.
