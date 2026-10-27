# Ghidra scripts

Run read-only scripts through `tools\run-headless.ps1 -ReadOnly`.
Keep output and logs in ignored scratch. Output failures raise an error before
`WROTE`; partial files remain for diagnosis and are not accepted evidence.

## Script index

- `DumpDataValues.java` prints defined data values at selected guest VAs.
- `ExportFunctionFingerprints.java` exports deterministic function fingerprints
  as JSON Lines.
- `DumpFunctionNeighborhood.java` dumps exact function boundaries around one
  address, with configurable radius and instruction cap (maximum/default
  `0x40` bytes per side and 64 instructions).
- `DumpFunctionNeighborhoodBatch.java` accepts up to 32 targets, adds raw words
  within `+/-0x10` bytes, and uses fixed instruction windows of `-0x20..+0x40`
  with a 32-instruction cap per target.
- `DumpFunctions.java` batches decompilation with caller and callee lists.
- `DumpInstructions.java` prints bounded instruction windows from selected guest VAs.
- `DumpMemoryWords.java` prints bounded big-endian word windows around selected
  guest VAs.
- `DumpReferences.java` lists code and data references to selected guest VAs.
- `DumpStringBoundary.java` dumps exact string references and a bounded native closure.
- `DumpStringsInRange.java` prints defined strings inside one bounded guest
  address range.
- `SummarizeRecordBytes.java` counts nonzero bytes in bounded records sized by
  the stride.
- `FindCallConstantArgs.java` finds direct calls whose nearest selected argument
  write is a requested immediate constant.
- `FindDirectCallers.java` finds capped raw PowerPC direct branch-and-link
  callers for exact target VAs.
- `FindFieldAccesses.java` classifies reads and writes inside selected functions
  and optional caller/callee closures. `REREVVED_SCAN_START_VA` and
  `REREVVED_SCAN_END_VA` bound an interval of instruction addresses;
  `REREVVED_MAX_HITS` caps emitted matches and reports truncation.
- `FindFieldRefs.java` finds PowerPC operands that add a displacement to a
  register for selected offsets.
- `FindRawFieldStores.java` finds capped raw PowerPC displacement stores for
  selected offsets in one bounded executable band, including undefined
  instructions.
- `FindRawGlobalStoreCandidates.java` finds capped raw `lis` plus
  scalar D-form store candidates within the same block for exact addresses;
  register lifetime, ownership, aliases, and other store forms require separate
  confirmation.
- `FindRawGlobalStoreChains.java` follows bounded raw `lis`-seeded arithmetic
  candidates to overlapping scalar, indexed or wider stores and exact-pointer
  call arguments. It leaves other register writes and control flow unchecked;
  every candidate needs instruction, lifetime and ownership confirmation.
- `FindGlobalAddressAccesses.java` finds decoded instructions that construct
  exact global addresses from split constants, then identifies their first use
  within the search bounds.
- `FindPointerValues.java` finds aligned 32-bit values in initialized guest
  memory, with an optional word mask for raw instruction candidates.
- `FindRawVtableSlotCalls.java` subtracts decoded slot loads from aligned
  executable raw words and emits bounded instruction windows that
  syntactically connect `lwz`, CTR, and `bctrl` in that order.
- `FindScalarUses.java` finds capped uses in decoded instructions of exact
  scalar values with an optional mnemonic allowlist.
- `FindSplitConstantUses.java` finds capped functions that construct selected
  32-bit values with PowerPC split constants.
- `FindSplitConstantCandidates.java` searches raw words for split constant
  candidates, including undefined code, and caps the results; each match
  requires confirmation of the instructions and register lifetime.
- `FindAbsoluteHalfwordCandidates.java` finds capped raw `lis` plus `lhz`/`lha`
  candidates for exact addresses within eight words; intervening register
  writes, paths and ownership require separate confirmation.
- `FindStrings.java` finds capped, case-insensitive substrings in defined guest strings.
- `FindVtableSlotCalls.java` finds decoded indirect calls whose vtable slot load
  feeds `mtctr` and `bctrl` within an eight-instruction straight-line window.
- `FindVtableSlotCallsCfg.java` finds additional bounded decoded slot calls
  across at most two branch edges within a function or exact aliases created
  by register copies. It allows 16 instructions and 256 states, reporting
  straight-line controls separately from additional paths.
- `ObserveCanonicalImageEvidence.java` records the bounded manual replay of
  the canonical image as private scratch JSON for the
  [evidence verifier](../docs/workflow.md#local-canonical-image-evidence-format).
- `FixXenonThunks.java` repairs undecodable Xenon VMX128 thunk slots.
- `RebuildTruncatedFunctions.java` rebuilds functions whose last instruction is a call.
- `RecoverSplitConstRefs.java` reruns the PowerPC constant-reference analyzer.
- `SeedGeneratedFunctions.java` seeds code and functions from a ReXGlue generated map.

Run mutating repairs only through `tools\bootstrap-ghidra.ps1`, in this order.
An optional generated function map and explicit code-analysis starting sites
guide code and function seeding after structural repair:

1. `FixXenonThunks.java`
2. `RebuildTruncatedFunctions.java`
3. `SeedGeneratedFunctions.java` (optional)
4. `RecoverSplitConstRefs.java`

Constant-reference acceptance defaults to the supported program. Override
`-ConstRefAcceptTarget` and `-ConstRefAcceptSites` together.

The bootstrap requires an explicit disposable project and refuses the one
configured by `REREVVED_GHIDRA_PROJECTS` and `REREVVED_GHIDRA_PROJECT`.
