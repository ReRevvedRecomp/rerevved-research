# Headless Ghidra workflow

Use repository drivers for all Ghidra access. `tools\run-headless.ps1` always
passes `-readOnly`; its optional compatibility switch rejects `-ReadOnly:$false`.
`tools\bootstrap-ghidra.ps1` repairs only disposable projects.

## Prerequisites

Queries require local Ghidra, a compatible JDK, and an imported program matching
`manifests/image.json`; the driver does not import retail files. Asset-free
checks have separate [requirements](style-guide.md#verification).

Run examples from the repository root, replacing angle-bracket placeholders
with local paths or names. Create dedicated ignored scratch outside shared OS
temp; the driver does not create output directories.

## Configure the project

Set the local environment once per shell:

```powershell
$env:REREVVED_GHIDRA_HOME = '<ghidra-root>'
$env:REREVVED_GHIDRA_PROJECTS = '<canonical-project-directory>'
$env:REREVVED_GHIDRA_PROJECT = '<canonical-project-name>'
$env:REREVVED_GHIDRA_PROGRAM = 'rerevved_image.bin'
$env:REREVVED_GHIDRA_JAVA_HOME = '<jdk-root>'
```

## Repair a disposable project

The canonical project is query-only. Repair a fresh image in an explicit
disposable copy with dedicated output and log paths:

```powershell
$disposable = '<disposable-project-directory>'
$bootstrapOut = '<ignored-bootstrap-scratch>\repair-result.json'
$bootstrapLog = '<ignored-bootstrap-scratch>\repair.headless.log'
tools\bootstrap-ghidra.ps1 `
  -DisposableProjectDir $disposable `
  -DisposableProjectName '<disposable-project-name>' `
  -Out $bootstrapOut `
  -LogPath $bootstrapLog
```

For ReXGlue images, supply the generated function map and exact code sites
needing decoding across Xenon-only interruptions of normal PowerPC flow:

```powershell
tools\bootstrap-ghidra.ps1 `
  -DisposableProjectDir $disposable `
  -DisposableProjectName '<disposable-project-name>' `
  -FunctionMap '<generated-init.cpp>' `
  -CodeSeedSites '0x8269CAE0,0x8269CAE4' `
  -ConstRefAcceptTarget '0x821B15C0' `
  -ConstRefAcceptSites '0x82DAB144,0x82DAB14C,0x82DAB154' `
  -Out $bootstrapOut `
  -LogPath $bootstrapLog
```

The generated-image chain runs `FixXenonThunks.java`,
`RebuildTruncatedFunctions.java`, `SeedGeneratedFunctions.java`, then
`RecoverSplitConstRefs.java`. Use `-Plan` with the same explicit paths to
check guards and print order without starting Ghidra or writing files.

Import the supported image pinned by `manifests/image.json` separately; keep
flat images and Ghidra projects outside this repository.

## Run read-only queries

Batch-decompile a narrow function set with callers and callees:

```powershell
$queryScratch = '<ignored-query-scratch>'
$null = New-Item -ItemType Directory -Force -Path $queryScratch
tools\run-headless.ps1 -Script DumpFunctions.java -ReadOnly `
  -Out (Join-Path $queryScratch 'rerevved-functions.txt') `
  -ScriptEnv @{ REREVVED_TARGET_VAS = '0x821F2CA0,0x821F6B30' }
```

Find uses of a structure offset inside a bounded function set:

```powershell
tools\run-headless.ps1 -Script FindFieldRefs.java -ReadOnly `
  -Out (Join-Path $queryScratch 'rerevved-field-refs.txt') `
  -ScriptEnv @{
    REREVVED_FIELD_OFFSETS = '0x28'
    REREVVED_FUNCTION_VAS = '0x821F2CA0,0x821F6B30,0x821F4948,0x822688C0'
  }
```

Classify accesses while expanding through direct callers:

```powershell
tools\run-headless.ps1 -Script FindFieldAccesses.java -ReadOnly `
  -Out (Join-Path $queryScratch 'rerevved-field-accesses.txt') `
  -ScriptEnv @{
    REREVVED_FIELD_OFFSETS = '0x28'
    REREVVED_SEED_VAS = '0x821F2CA0,0x822688C0'
    REREVVED_CALLER_DEPTH = '2'
  }
```

Trace an indirect entry point back to a dispatch table or address materializer:

```powershell
tools\run-headless.ps1 -Script DumpReferences.java -ReadOnly `
  -Out (Join-Path $queryScratch 'rerevved-references.txt') `
  -ScriptEnv @{ REREVVED_TARGET_VAS = '0x821FBC38' }
```

For split constructions missing decoded references, run
`FindSplitConstantCandidates.java` with `REREVVED_TARGET_VAS` and an output path.
It scans aligned raw words for `lis` followed within eight words by compatible
`addi` or `ori`, capped at eight results unless `REREVVED_MAX_MATCHES` overrides.

Candidates may be data or contain intervening register writes; confirm exact
instructions and functions. The query neither disassembles nor repairs.

For known opcodes/displacements with varying registers, `FindPointerValues.java`
applies `REREVVED_WORD_MASK` before comparing words with `REREVVED_POINTER_VAS`.
Patterns must zero ignored bits; omitting the mask gives exact matching.

Mask `0xFFE0FFFF` and pattern `0x386001C0` find raw `addi r3,rN,0x1C0`
candidates. Confirm code ownership and base registers before naming fields.
Results reaching the match cap are not exhaustive.

## Function fingerprint comparison

Export independently identified programs to JSON Lines, changing the configured
project and program between source and target runs:

```powershell
tools\run-headless.ps1 -Script ExportFunctionFingerprints.java -ReadOnly `
  -Out (Join-Path $queryScratch 'source-functions.jsonl')

tools\run-headless.ps1 -Script ExportFunctionFingerprints.java -ReadOnly `
  -Out (Join-Path $queryScratch 'target-functions.jsonl')
```

ReXGlue generated output can supply an independent corpus of instruction text:

```powershell
python tools\export_generated_fingerprints.py `
  --generated-dir '<generated-directory>' `
  --prefix '<generated-prefix>' `
  --out (Join-Path $queryScratch 'generated-functions.jsonl')
```

Match only exports from the same fingerprint algorithm:

```powershell
python tools\match_version_functions.py `
  --source (Join-Path $queryScratch 'source-functions.jsonl') `
  --target (Join-Path $queryScratch 'target-functions.jsonl') `
  --out (Join-Path $queryScratch 'function-matches.json')
```

The matcher rejects different algorithms and ties, caps heuristic pools at 256,
and demotes many-source/one-target collisions. Exact or strong matches remain
identity candidates, insufficient for semantic claims. Re-query targets and
compare bounded generated bodies when available before promoting facts.

Promote compact findings into `manifests/`, then delete scratch fingerprint
streams, reports, and headless logs. List prerequisite topics under
`dependencies` per the [topic manifest contract](topic-manifests.md); retain
each dependent's current-image locators. Behavioral claims need a narrow
generated C++ comparison and a default-off runtime probe.

## GFx AVM1 inspection

Find action blocks containing exact decoded strings in an uncompressed retail
GFX or FWS movie. Repeat required `--target` for multiple strings; `--out`
writes JSON, otherwise output goes to stdout:

```powershell
python tools\inspect_gfx_avm1.py '<movie.gfx>' `
  --target '<exact-string>' --target '<another-string>' `
  --out (Join-Path $queryScratch 'avm1-matches.json')
```

Keep private movies and action-block reports local.

## Native renderer D3D inventory

Validate the canonical inventory, or pass another manifest path as the optional
positional argument:

```powershell
python tools\validate_native_renderer_d3d_inventory.py
```

Emit the manifest's partial snapshot as JSON on stdout with a full lowercase
published research commit and the SHA-256 of the exact manifest bytes. Both
identity options require `--emit-partial-snapshot`; the tool checks the digest:

```powershell
$inventory = 'manifests/native-renderer-d3d-inventory.json'
$digest = (Get-FileHash -LiteralPath $inventory -Algorithm SHA256).Hash.ToLowerInvariant()
python tools\validate_native_renderer_d3d_inventory.py $inventory `
  --emit-partial-snapshot `
  --research-commit '<full-lowercase-published-research-commit>' `
  --aggregate-sha256 $digest
```

## FX object shader correlation

ReXGlue `dump_shaders` writes guest microcode files named by runtime hash.
Correlate them with candidate Xbox 360 FX objects, keeping both inputs outside
this repository:

```powershell
python tools\correlate_fxobj_shaders.py `
  --fxobj '<candidate-one.fxobj>' `
  --fxobj '<candidate-two.fxobj>' `
  --shader-directory '<ReXGlue-shader-dump-directory>' `
  --require-all
```

The tool searches complete dumped microcode in raw and per-dword byte-swapped
form. JSON reports filenames, sizes, hashes, shader stages, match offsets,
byte-order labels, schema version, and summary counts, without raw payloads.

Keep reports in ignored scratch; promote bounded identities only when dump and
asset are independently identified. Byte matches prove neither draw execution,
visible output, sampler ownership, render-target state, nor defect causation.

## Local canonical-image evidence format

`.github/workflows/checks.yml` is asset-free and does not replay the canonical
image. Local observation tools, schemas, and sanitized attestations support
separately controlled analysis of an already generated private image. They
neither construct it from `default.xex` and `default.xexp` nor validate retail
derivation.

Import at image base `0x82000000` with processor `PowerPC:BE:32:default`.
The bounded contract covers `RVA-SYM-0223`, field
relation `RVA-REL-0290`, and vtable ownership relation `RVA-REL-0293`.

Check the public contract and [attestation schema](../schemas/image-evidence.schema.json)
without private inputs, then collect observations from the configured imported
program and verify them:

```powershell
python tools\verify_canonical_image_evidence.py --preflight
$observations = Join-Path $queryScratch 'canonical-observations.json'
tools\run-headless.ps1 -Script ObserveCanonicalImageEvidence.java -ReadOnly `
  -LogPath (Join-Path $queryScratch 'canonical-observations.headless.log') `
  -ScriptEnv @{ REREVVED_CANONICAL_OBSERVATIONS_OUT = $observations }
python tools\verify_canonical_image_evidence.py --input $observations
```

Choose exactly one of `--preflight` or `--input`. The producer reads the
imported program and hashes its source file, which must remain accessible.
`--input` emits sanitized attestation JSON on stdout and returns nonzero for a
failed result. Keep images, projects, observations, and raw logs local.

Attestations contain public image identity, entity IDs/addresses, check names,
and pass/fail summaries. All five checks must occur exactly once and match the
public image/check identities. Complete failure attestations are valid; omitted
checks never pass. The format cannot guarantee a runner's private-log handling.
