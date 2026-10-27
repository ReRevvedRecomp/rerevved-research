# Unit definitions

The native table at `0x82F700D8` has stride `0x94` and initialized count 38; the
ordinary catalog covers records 0 through 28. Runtime unit byte `0x1` in each
`0x54`-byte record indexes it. Names are recovered semantic labels, not debug
symbols.

Evidence terms: findings cover the stated static paths and read sets. "Accepted"
identifies supported evidence; it implies neither runtime execution nor complete
consumer coverage. Return, ownership and alias limits remain explicit. These
findings establish no safe additional-definition API.

- [Native count and storage limits](#native-count-and-end-boundary).
- [Settler production gates](#settler-production-gates).
- [Production cost](#normal-unit-production-cost).
- [Building and wonder fields](#building-and-wonder-record-contract).
- [Ordinary unit IDs and stats](#unittype-values).
- [Combat stat roles](#combat-stat-role-boundary).
- [Native army formation](#native-army-formation).

## Native army formation

Native command 10, `MakeArmy`, calls `0x82D13618`. Its eligibility helper requires
at least three matching ordinary units on one tile, with additional type,
definition and player gates. Formation consumes the first two eligible slots
other than the selected unit, combines their state into the survivor, writes
its army selector, invokes native callbacks and recounts.

This is a formation path, not just the army-name field. An earlier existing
Archer on the tile can be consumed before newly created Archers. A first-capital
army grant therefore still needs an existing-unit preservation contract,
founding receipt/save policy, allocation handling and actual callback lifetime
evidence. No such grant or runtime outcome is established here. Exact gates,
writes and qualifications are in the
[army formation boundary](../../manifests/army-formation-command-boundary.json).

## Recovered layout and readers

| Item | Address or offset | Accepted meaning |
|---|---:|---|
| Native unit-definition table | `0x82F700D8` | Initialized count 38, stride `0x94`; current live count remains conditional |
| Ordinary catalog subset | IDs 0 through 28 | 29 cataloged records; additional native records follow |
| Runtime unit type | unit record `+0x1` | Zero-based index into the definition table |
| Internal name | definition `+0x0` | NUL-terminated record name when present |
| Base attack | definition `+0x40` | Signed byte read by `EffectiveUnitAttackLookup` |
| Base defense | definition `+0x41` | Signed byte read by `EffectiveUnitDefenseLookup` |
| Base movement | definition `+0x42` | Signed byte read by `EffectiveUnitMovementLookup` |
| Production-cost factor | definition `+0x44` | Signed byte composed by `EffectiveUnitProductionCostScalar` |
| Effective attack reader | `0x82CF2230` | Applies unit and civilization modifiers to base attack |
| Effective defense reader | `0x82CF21A0` | Applies unit and civilization modifiers to base defense |
| Effective movement reader | `0x82CF1F70` | Applies local and civilization modifiers on its ordinary composed return |
| Unique Unit identity selector | `0x82CEF160` | Maps a base `UnitType` and player civilization to a localized name index |
| Live unit-name reader | `0x82CF0550` | Reads the live unit type, applies the identity selector, and resolves the unit or army name |

Bytes `+0x43` and `+0x45` through `+0x47` remain intentionally unnamed. Their
adjacency to accepted fields does not prove another gameplay meaning.

`EffectiveUnitMovementLookup` owns three retail movement UEAs on its ordinary
composed return. Definition flag `+0x50 & 0x200` selects UEA 3, Riflemen
UnitType 10 selects UEA 12, and Warrior UnitType 6 selects UEA 55. Each active
cumulative lookup adds one to retained movement.

One special return path uses an unresolved constant instead of the composed
value, so the packet does not claim every movement return, consumer, or AI path.
The exact branches are in
[`unit-movement-stat.json`](../../manifests/unit-movement-stat.json).

## Native count and end boundary

Initializer `0x82D25170` writes literal 38 to live count word `0x830E45D0` at
`0x82D25194`. The accepted game-start caller reaches that initializer through a
conditional audio gate. Actual invocation, new-game versus load timing and
retained current count remain unproved. The count is a literal, not a scan for
an empty record.

The logical 38-record span is `0x15F8` bytes at `[0x82F700D8,0x82F716D0)`. Its
final byte is `0x82F716CF`. The ordinary catalog ends before `0x82F7119C`; the
remaining nine native records have these stored internal names:

| ID | Record and name address | Stored name |
| --- | --- | --- |
| 29 | `0x82F7119C` | Caravan |
| 30 | `0x82F71230` | Great General |
| 31 | `0x82F712C4` | Great Scientist |
| 32 | `0x82F71358` | Great Humanitarian |
| 33 | `0x82F713EC` | Great Explorer |
| 34 | `0x82F71480` | Great Builder |
| 35 | `0x82F71514` | Great Artist |
| 36 | `0x82F715A8` | Great Leader |
| 37 | `0x82F7163C` | Great Tycoon |

These names do not prove localized labels, buildability or model routing. The
first beyond-count address, `0x82F716D0`, immediately contains occupied
Blitz-related text. Appending a record there at the unchanged base would overlap
that data. No safe spare unit ID, universal maximum capacity, relocation
contract or additional-definition API follows from this extent.

The
[count and extent evidence](../../manifests/unit-definition-count-extent.json)
owns the native words, source identity, data queries and qualifications. The
[Militia and Scout feasibility page](city-militia-scout.md) records the separate
creation, cost, upgrade and all-player requirements.

## Definition-base consumers and relocation

Seven selected native owners construct `0x82F700D8` independently with
`lis`/`addi`. A count change, data copy or one pointer-cell update alone cannot
redirect those instruction-defined bases. Each selected field address is derived
locally from the base; no separate absolute field-address producer was
established in these samples.

| Owner | Selected use and retained state |
| --- | --- |
| `0x82CF21A0` | Defense `+0x41`, flags `+0x50` |
| `0x82CF1F70` | Movement `+0x42` |
| `0x82CE2B98` | Cost factor `+0x44` after the scalar call |
| `0x82CEBC38` | Production requirements, flags and cost; base in r20, live count |
| `0x82D13978` | Completion and Loyalty inputs; base at frame `+152`, derived registers and fixed paired scan over IDs 0 through 37 |
| `0x82CFE828` | Defender selector; cached base and fixed scan over IDs 6 through 37 |
| `0x82D11750` | Creation-route and later live-slot flags; base at frame `+80` across callbacks |

The defender scan compares against `B + 38*148 + 0x41`, which is a
field-position sentinel, not the allocation end. The CityUpdate paired scan
compares against `B + 39*148 + 0x4A` while reading pairs covering IDs 0 through
37. Neither scan reads the live count. Production enumeration does read it and
refreshes it only after admitting an entry.

These are distinct contracts; routing below 100 and a 100-word scratch array do
not prove safe definition capacity.

A compatible relocation of the existing 38 records requires all reaching base
producers and aliases to retain a coherent storage identity, valid guest
addresses, stride and fields, signed pointer ordering and storage lifetime
across calls. Saved frame words and already-derived register pointers both
matter. No safe allocation or publication protocol was proved.

The maintained host catalog independently supports 29 public IDs and passes
scalar or runtime-unit contexts to the sampled hooks; moving native data does
not extend that metadata or establish a API for registering definitions.

Extending production admission is a separate decision from growing fixed scans.
Keeping the defender range fixed could exclude a future Scout outside that range
from this selector; it does not prove exclusion from every grant. Omitting a
custom Loyalty assignment also does not bypass the existing conditional native
completion assignment.

Supported new IDs and other unit properties remain unproved.

The [base-consumer packet](../../manifests/unit-definition-base.json#/findings/RVA-F-0277)
owns addresses, source digests and 66 fresh matching native words. Its raw
eight-word search found 114 syntactic pairs, with register lifetime and code
ownership unchecked.

It demonstrably missed the validated production base producer at
`0x82CEBF04`/`0x82CEBF84`, whose instructions are 32 instructions apart. This is
not a complete relocation site list.

### Census coverage and decode limits

The instruction-aware census missed the validated production control on the
unrepaired canonical listing. Lookaheads 8 and 32 both emitted 14 function
representatives: neither endpoint was decoded or function-owned, and seeded
`0x82CEBC38` covered eight bytes through `0x82CEBC3F`. Longer lookahead cannot
repair missing coverage.

| Evidence | Result and limit |
| --- | --- |
| [Census validation](../../manifests/unit-definition-base.json#/findings/RVA-F-0278) | Query model, bounded failure and 33 fresh matching native words. The 14 deduplicated hits differ from the earlier 114 raw pairs; neither proves complete materializer coverage. Canonical project queried without repair. |
| [Disposable coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0279) | Supported repairs decoded all 33 control instructions, but `0x82CEBC38` still owned eight bytes. Another ordered pass left ownership unchanged. Post-call `stwu` at `0x82CEBC40` decoded and matched, excluding an undecodable displayed opcode as the cause. The 34 unique matching words establish decode coverage, not a body or relocation inventory; missing ownership blocked census replay. |
| [Call flow](../../manifests/unit-definition-base.json#/findings/RVA-F-0280) | Normal call `0x82CEBC3C`: no flow/fallthrough override, returning-callee metadata, continuation `0x82CEBC40`, admitted by the rebuild guard. Read-only calculation produced 4,052 bytes in 12 ranges containing both controls; stored body stayed eight bytes. Current flags/calculation do not reproduce that cutoff. |
| [Creation reconciliation](../../manifests/unit-definition-base.json#/findings/RVA-F-0281) | Existing-entry creation preserved eight bytes; fresh creation retained the exact 4,052-byte, 12-range set. Removing the exact entry left no overlapping functions; the result was not a thunk. Both controls belonged to `0x82CEBC38` in the required basic block; all 32 next-defined steps passed. This transient read-only result was unsaved; retained project bytes and historical repair uncertainty remained. |
| [Same-session census](../../manifests/unit-definition-base.json#/findings/RVA-F-0282) | Recreated state and unchanged lookahead-32 census emitted the control pair and 16 distinct representatives without truncation/cancellation. Body and owner/block checks passed. All 14 canonical representatives remained, plus two; differing listings prevent a causal count comparison. |
| [Omitted-site coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0283) | Five decoded unowned pairs and one undefined pair; all six expected functions owned eight bytes excluding endpoints. Census skipped them before low-part matching, register-write filtering or deduplication. No complete inventory or new count follows. |
| [Cost-lookup decode](../../manifests/unit-definition-base.json#/findings/RVA-F-0284) | Ordinary store `0x82CE2B9C` falls through without overrides to inline `std` at `0x82CE2BA0`, whose constructor the selected 32-bit language excludes. Isolated decoding accepts the preceding store but not `std`; native fields/generated code corroborate the 64-bit store. Listing and eight-byte body stayed unchanged. |
| [Detached strategy](../../manifests/unit-definition-base.json#/findings/RVA-F-0285) | Precompiled `PowerPC:BE:64:64-32addr` decodes both stores with intended widths/fallthrough; raw pcode retains eight-byte STORE offsets into ram32 without explicit truncation. |
| [Consumer source trace](../../manifests/unit-definition-base.json#/findings/RVA-F-0286) | Later guarded `RulePtrFlow` extracts low four address bytes, retaining the eight-byte value; raw import and initial SSA/alias work precede it. |
| [Installed-native observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0287) | Isolated STORE/synthetic-return fixture returned a four-byte low32 address and full eight-byte value; diagnostic control retained an eight-byte address. Java's dead flag was unmaintained bookkeeping; returned-block interpretation remains qualified. |

The
[cost-owner coverage packet](../../manifests/unit-definition-base.json#/findings/RVA-F-0288)
owns structural evidence. Complete base inventory, broader Xenon/ABI equivalence
and historical body-writer/repair causes remain unproved.

### Shared coverage and remaining inventory limits

The
[shared-coverage boundary](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/ordinarySwitchRecoveredObservation)
records seven ordinary owners in one unsaved native candidate. Adding 52 native
inline-table bytes let the configured decompiler and ordinary switch command
recover both CityUpdate switches. Standard body fixup reached the exact
12,788-byte input: all 3,197 instructions owned, matching 654-block union.
Postanalysis followed stored references; native target lists were comparison
whitelists. Table one retained six labeled records, duplicate destinations and
no separate default; table two retained seven plus default `0x82D13E14`.

The unchanged 32-step census recovered all seven selected producers without
truncation, including `0x82CEBF04 -> 0x82CEBF84`. Cost, long and creator
controls passed; 53 raw snapshots and 43 read comparisons matched. Canonical
bytes remained unchanged. This closes selected local coverage, not an image-wide
consumer/count inventory.

A
[broader raw-inventory attempt](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/rawInventoryMemoryIdentityObservation)
stopped before scanning: canonical RAM failed the full supported-image digest
guard. Zero counters prove no absence; the report omitted the observed digest
and cause. A
[verified-file observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/rawNativeFileInventoryObservation)
completed the declared address models against the full supported native-file
buffer. Independent reconstruction matched every candidate/control. Saved RAM
identity and differences were recorded and preserved; their cause remains
unknown. Raw matches still need semantic classification.

The
[creator continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0301)
owns the reconciled 900-byte input. Four CityUpdate self-call tuples require
actual returns: the first two retain the original city/mode 1; the latter two
use current r19/mode -1. Actual r19 identity, recursive/computed returns,
frame/pointee lifetime and full semantic extent remain unproved. Missing memory
prevented following restore target `0x827F7CA0`. Broader
base/alias/interior/count coverage and safe Scout registration remain open.

## Settler production gates

The human menu and three AI-turn-evaluator call sites share a candidate
generator. With the Settlers definition retained, it requires population at
least three, or two when cumulative UEA 45 is active or the owner-indexed word
equals five. Both inputs retain neutral meanings. FSettler fails its first
prerequisite and is not an interchangeable buildable entry.

Completion separately checks cost and the equivalent population threshold.
Command type five can assign retained Settlers to owner-matched current item
`+0x38` without repeating that check. Selection skips resubmission when Settlers
is current; existing production still enters completion. A failing population
check can exit mode one without clearing/replacing the item. Calls, delivery and
retained city/array/frame state qualify these paths.

A Settlers-only minimum R can preserve other units' native requirements:

| Native comparison | Settlers selector | Effective threshold in r11 |
|---|---|---|
| Candidate `0x82CEC7A8`, population >= T | candidate type r30 == 0 | max(native T, R) |
| Completion `0x82D15A7C`, population > K | current item r25 == 0 | max(native K, R - 1) |

These are conditional comparison contracts, not an implemented setting or
per-unit field. Supply full-width operands after native alternatives merge,
retaining supported type0 flag1/state; disabled policy and other types retain
native operands. R=32 rejects populations through 31. R=128 rejects every
current signed-byte value, but supports no population above 31; widened readers
need a new bound.

The AI evaluator adds wonder candidates. `0x82CB4828/0x82CB4834` forms RNG
record `0x82F7AD00`, with divisor 4294954991 and rounded reciprocal binary64
scale. Retained inputs and `0<=prefix<total<=100` give a random ordinal within
the populated suffix. Excluding Settlers does not prove another candidate or
valid ranges for every scoring choice.

With an empty suffix, fallback computes `prefix`; `0x82CB5544` then reads
outside it without a range check. OCC reachability/crashing is unproved, but
unconditional safe fallback is excluded. The caller accepts `-1` at
`0x82CECBBC/0x82CECBC0`, skipping assignment; native empty flow does not use
that exit. Guard before the first unsafe read and validate a no-choice exit, or
prove every relevant range nonempty. A post-return check is too late; stall-free
turn continuation needs runtime evidence. Grants through the shared creator
remain separate from construction.

The title's cost-scalar hook demonstrates pre-instruction typed register
callbacks; its Lua contract/hook corpus exposes neither population policy nor
callbacks at these comparisons. Locked SDK source publishes module-launch Lua
before resuming guest main, conditional on intervening callbacks returning
without starting guest work. This is a publication seam, not implemented OCC.

Publish one validated immutable `{enabled, R=32}` record before guest execution;
retain it until execution stops. Both callbacks must read it and preserve all
guest state except the specified type0 `r11` assignment. Restart without OCC
uses an explicit disabled default. This provides consistent thresholds without
per-save binding; actual registration, record identity/retention and
enabled/disabled human/AI execution need implementation/validation. An
active-human snapshot cannot replace shared policy.

Manual-load and finalized-save seams can associate a fixed policy with the
namespaced identity in [Save storage](save-storage.md); creation-only selection
remains unbound. Load owner `0x82D86400` can skip deserialization yet return
locally true: neither that result nor the serializer hook proves restored OCC
policy. Exact gates and unresolved command/dispatch edges are in
[occ-settler-production-gates.json](../../manifests/occ-settler-production-gates.json).

## Normal unit production cost

`EffectiveUnitProductionCostScalar` at `0x82CF1148` starts at 10, applying
player, condition, definition-flag and civilization reductions. Normal cost is
signed factor `+0x44` times final scalar, divided by two toward zero.

The [scalar return boundary](../../manifests/production-cost-ownership.json#/effectiveScalar/returnBoundary)
bounds its local return and stack effects under predicate/lookup retention
conditions. Optional bonus 5 uses the index-14 predicate's outgoing `r4`;
assigning it to the entry owner requires that value to survive. The later
unit-specific lookup freshly reloads the city owner.
The predicate's selected owner-equal, state-outside-{0,1} true arm supplies
that retention under its exact stack and protected-memory conditions.

Eight signed halfwords at `0x830E9050` supply the player input; initialization
sets all eight to `-1`, and broad serialization transfers them both ways. Setup
`0x82D217C8` submits command 57 with player index and unresolved virtual result;
case 57 stores that result in the selected halfword. Array policy and command
name remain unknown, as do condition `0x82CEF4E8(14)` and bonus 33.

Bonuses 5, 17 and 34 give half-cost Settlers, Riflemen and Spies. Eight sampled
factors: Warrior 2, Archer 2, Riflemen 4, Horsemen 4, Knights 5, Tank 10,
Artillery 10, Spy 5; these are not final costs. See
[`player-production-scalar-lifecycle.json`](../../manifests/player-production-scalar-lifecycle.json).

Command 57 arg2's virtual source remains unbound: Ghidra owns eight setup-entry
bytes and neither instructions nor a function at `0x82D224F0`. Generated
corroboration shows receiver `r14`, slot `+0xA0`, return via `r3`/`r31` to
wrapper arg2 `r5`, and a separate receiver for nearby `+0x100`. Missing native
receiver decoding prevents promoting object, vtable, target, thunk, source or
policy identity. See
[`player-production-scalar-virtual-source.json`](../../manifests/player-production-scalar-virtual-source.json).

### Item routing and building costs

`ProductionItemCostLookup` (`0x82CE2B98`) uses the unit formula for IDs 0
through 99. `CurrentProductionItemCostLookup` (`0x82CF8308`) selects city
`+0x38` and returns the same result. Both route 100 through 299 to
`BuildingWonderProductionCostLookup` (`0x82CF1278`).

Building routing covers 100 through 199, but the `0xCC`-stride block at
`0x82F71FD8` has only 23 initialized records, IDs 100 through 122; the next
stride overlaps non-record data. Fields: name `+0x00`, token `+0x20`, signed
factor `+0x41`, description `+0x4C`. IDs 123 through 199 remain unvalidated; see
[`building-record-identities-100-122.json`](../../manifests/building-record-identities-100-122.json).

Menu gates read signed technology `+0x42`, required building mask `+0x44` and
forbidden mask `+0x48`; all 23 records are in
[`building-menu-record-gates.json`](../../manifests/building-menu-record-gates.json).
Masks join completion bits: Bank requires Market, Cathedral Temple, University
Library; later-tier bits hide earlier items. These local checks prove neither
complete availability/effects nor runtime completion.

Building half-cost branches pair Barracks 101/UEA 19, Library 105/20 and Courthouse
114/18; Cathedral 111/21 has no accepted retail activation. University 112 and
Factory 116 have neutral-gated reductions. The early item-specific tests use a
shared word-shift mask: initialized Wonder 229 also matches the Barracks mask,
and 233 matches the Library mask and later three-quarter subtraction. These
static aliases retain the ordered current-cost arithmetic and retail-composition
limits in [the modifier record](../../manifests/building-wonder-cost-modifier-branches.json).
Wonder 229 still requires dynamic bit-two admission and its full outer gate; 233
is excluded from the ordinary menu and known-vtable city-update route. See
[the eligibility record](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170).

Final wonder reduction uses `0x82FFE7C8`. In `BroadGameStateSerializer`, null
auxiliary pointer plus mode one passes it to `BufferReadU32` as destination;
mode zero to `BufferWriteU32` as source. Raw words match generated paths, but
Ghidra has no decoded body. Virtual targets, external format, policy, runtime
value and visible effect remain unknown. `0x82D25330` separately tests signed <2
before slot `+0x80` on receiver `0x8314F76C`, arguments 13/-1. Its materializer
scan hit cap 32; image word zero establishes neither target nor live value.

- [Transfer frontier](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0218)
- [Secondary reader](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0219)
- [Candidate search](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0215)

Building's final half reduction tests city halfword `+0x3C` bit `0x8`. The
following negative searches leave indexed, computed, functionless and
out-of-interval writers open:

| Search | Result | Evidence |
| --- | --- | --- |
| Direct writes | No non-stack WRITE/READ_WRITE in 272 decoded function-owned instructions; one raw D-form candidate targets another global. No split constant for `0x8314FE64` | [Writer frontier](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0209) |
| City-base materializers | Reproduced 31; next eight unexamined functions had no direct non-stack write in 231 instructions | [Materializer frontier](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0213) |
| Remaining materializers | Other 23 functions in four batches: no direct stores. Total 31/1817 instructions | [Continuation](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0214) |
| Generated bodies | All 31: no locally resolved `+0x3C`/overlapping-word store; `0x82E57980` destination could alias city state | [Computed writer](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0216) |

A 128-position loop at `0x82E8AEC8` writes `0x8314F0A8` to city `+0xB8` and zero
to `+0xB0`/`+0xB4`; meanings/consumers remain unknown. See the
[initializer symbol](../../manifests/catalogs/symbols.json).
The shared three-quarter subtraction gate at `0x830E8FFE` can receive authored
QUARTERPRICELIB through the accepted scenario-slot copy. Actual selection,
retention, other writers and complete gameplay policy remain unproved. The
conditional source and initialized mask matches are recorded in
[the modifier record](../../manifests/building-wonder-cost-modifier-branches.json#/additionalCommonBranches/0).
Bounded address searches found no writer, and the consumer lies in a Ghidra
function gap; see [the source frontier](../../manifests/building-wonder-cost-gate-source-frontier.json).

### Building choices and completion fields

In `0x82CED700`, the Building bridge skips `k` leading negative words, then
copies a fixed temporary-array tail: byte count `4 * (100 - k)`, returned
visible count generator-count minus `k`. Parent destination is `+0x5DC`; return
is stored at `+0x43C`. Neither wrapper nor child loop checks a 100-entry
maximum; excessive native output is unproved. The
[copy boundary](../../manifests/building-option-copy-capacity-boundary.json)
establishes no safe new definition/ownership slot.

Append helper `0x822D10C0` derives size/capacity from begin/end/capacity-end.
Nonzero begin and size below capacity permit a four-byte write and end advance;
otherwise `0x822D1150` owns unresolved growth/allocation/failure. The
[capacity gate](../../manifests/building-option-append-capacity-gate.json) does
not validate allocation or pointer invariants.

After sufficient production, `0x82D02090` writes ordinary building bits,
including a bank indexed by clamped player era. Spaceship items 119-122 instead
conditionally set city `+0x24` bit `0x100` under a player-indexed gate. Both
store item ID at `+0x3A` and check a bounded city byte list. These
[`building-completion-state-writer.json`](../../manifests/building-completion-state-writer.json)
prove neither described effects nor runtime execution.

Negative searches below cover decoded function-owned operands only. Indexed,
computed, aliased, indirect, functionless and out-of-interval readers remain
unresolved, along with uninspected materializers.

| Field/search | Coverage and result | Evidence |
| --- | --- | --- |
| `+0x24` | No non-stack READ/READ_WRITE in 272 instructions; no split-constant materializer for `0x8314FE4C` | [Flag frontier](../../manifests/spaceship-part-city-flag.json#/findings/RVA-F-0208) |
| `+0x24` continuation | Next eight unique city-base functions after the followed path and first eight others: no direct non-stack READ/READ_WRITE in 428 instructions | [Materializers](../../manifests/spaceship-part-city-flag.json#/findings/RVA-F-0211) |
| Era bits `+0x14`, `+0x18`, `+0x1C`, `+0x20` | No reads in 272 instructions across `[0x82D00000,0x82D20000)`; reproduced 31 city-base materializers, first eight after `0x82CEDF90` had none in 664 instructions | [Era-bit frontier](../../manifests/city-era-building-bit-reader-frontier.json) |
| `+0x3A` | No READ operands in 272 instructions across `[0x82D00000,0x82D20000)` | [Stored-item frontier](../../manifests/city-stored-item-id-reader-frontier.json) |
| City base `0x8314FE28` | 654329 instructions produced 31 split-constant materializers below cap 64. `0x82CEDF90` reads indexed byte `+0`, then calls `0x82D038E8`, whose inspected prefix does not read that base. First eight other materializers: no direct `+0x3A` reads in 664 instructions | Same stored-item frontier |

One gated sufficient-production wonder path copies `+0x38` to `+0x3A`; later
behavior remains outside the
[`non-unit-production-threshold-boundary.json`](../../manifests/non-unit-production-threshold-boundary.json).

The directly called city helper tests Courthouse index-14 in `+0x10`, selecting
eight adjacent candidates or twenty with a second ring. This
[`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json)
does not identify worked tiles. Other building-bit tests add half an
intermediate register back into itself: Barracks 101, Granary 102, Temple 103,
Workshop 106, Market 104 or Library 105, Bank 110 or University 112. Each paired
mask updates only once. One branch uses adjusted food/production/trade weights
in candidate scoring; another replaces them. After validation, city `+0x58` plus
local index receives a selected/replacement byte, including `-1`.

`sub_82CE1C10` counts non-`0xFF` entries below positive signed city `+0x03`,
returning bound minus count (the `0xFF` count). It also groups the interval from
non-`0xFF` count to bound into sixes in caller output. A caller compares eight
output words with cache, gating a helper and refresh. Candidate values/sentinel
positions are discarded; changing them without changing count/bound cannot
affect those words. Tile assignment, gameplay meaning, visible effect and
runtime invocation remain unproved.

- [Bit arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json)
- [Weighted score](../../manifests/building-bit-selection.json#/findings/RVA-F-0202)
- [City byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203)
- [Consumer frontier](../../manifests/building-bit-selection.json#/findings/RVA-F-0204)

The intervening helper derives four target counts from a stored row/selector,
counts pointer-vector tags under range guards, and calls helpers for signed
differences. One can update receiver words; required calls/unbound dispatch
prevent joining return to cache refresh. Row/city identity, resource policy and
yield effects remain unknown. Matched-entry handling selects one outer index or
skips; fixed zero bypasses optional append. Local array/object clears are bound.

Empty regions and guarded zero per-cell fields restore caller pointer/stack;
nonzero fields can require another helper/unbound dispatch. Restoration proves
neither field retention nor lifetime. An earlier updater requires nonzero flag;
its zero-pointer arm sets flag one without pointer creation. Earlier consumers
and unresolved calls prevent selecting the later branch.

The earlier candidate replaces `+0x704/+0x708/+0x70C`. Its owner passes the
table word as argument two and stores it at `+0x700`. Predicate lookup has no
calls/stores and preserves `r5`, stack and ordinary memory. Returning zero uses
the original receiver for fallback; a clear bit supplies a third guarded path
retaining unknown old-slot values. Actual slots/targets and predicate-one
initialization effects remain unbound.

Size 864 reaches generic fallback after its prefix returns. Guarded global
initialization, error and manager-prefix metadata writes are bound; image zeros
do not identify live prefix/context. Bounded reference/direct-store searches
leave producer/order unresolved, selecting no descendant. Imports/full return
and survival of owner, frames and old slots remain unproved despite register
restoration. See the
[helper boundary](../../manifests/building-bit-selection.json#/findings/RVA-F-0204/groupedOutputConsumer).
Nearby `sub_82D019F0` has 18 `lbzx` candidates, none joined to the city pointer.
The earlier 21/8/13 filter is unrecoverable from tracked evidence; this census
excludes no readers outside that function.

### Wonder costs and consumer limits

IDs 200 through 299 route to signed factor `+0x40` in `0x14C`-stride wonder
records at `0x82F73238`: common signed half-scale, then another half for
cumulative UEA 24, Wonders cost half as much. The common scale is not UEA 24.

The 37 initialized records cover 200 through 236: name `+0x00`, factor `+0x40`,
short token `+0x4A`, art token `+0x8A`, description `+0xCA`. Identity manifests
retain byte boundaries and unnamed halfword `+0x42`. The next twelve stride
positions are zero, then non-wonder data; neither this nor cost routing proves
program-wide ID validity.

Ghidra returned no exact-start references for 217 building/wonder text fields;
indexed, indirect, computed, interior-string and undecoded readers remain open.
`0x82CF0268` has no decoded register-relative `+0x42`, `+0x4A`, `+0x8A` or
`+0xCA` operand; scaled/indexed/other readers remain open. Choice tail
`0x82E41538` calls `0x827F7C8C`, whose one-byte body has no instruction and
references truncate at 64. It adds no reader evidence. See
[text census](../../manifests/building-wonder-text-field-reference-boundary.json)
and [consumer frontier](../../manifests/building-wonder-consumer-frontier.json).

| Consumer evidence | Finding and remaining limit |
| --- | --- |
| [Factor accumulation](../../manifests/wonder-factor.json#/findings/RVA-F-0197) | Reads `+0x40`, adding derived values to global and stack accumulators indexed by claim owner. |
| [Output/reader frontier](../../manifests/wonder-factor.json#/findings/RVA-F-0217) | After collection, `0x82CB379C` reads stack accumulator; one arm converts signed word to float, divides by signed stack `r25`, writes single precision at `0x830E8DD0` plus 64 per iteration. Two reads use indices scaled 64/four, without proving writer `+0` consumption. Global role and cost effect remain unknown. |
| [Reader census](../../manifests/wonder-factor.json#/findings/RVA-F-0198) | Eight-word copy `0x830ECCC8` -> `0x831228E4`. Three object reads could reach copied words with particular low-30-bit indices, but selectors are data-dependent; actual read, later use and cost effect remain unknown. |
| [Index sources](../../manifests/wonder-copy-index.json#/findings/RVA-F-0199) | Selectors include incoming-object `+0x434` pointee and unresolved virtual result; ranges unproved. |
| [Writer check](../../manifests/wonder-copy-index.json#/findings/RVA-F-0200) | Reader's function table joins initializer clearing `+0x434`; different-table initializer stores a pointer there, without shared-object/live-writer proof. Image zeros establish no index/read. Two direct initializer callers share a function with an indexed read; their next method has no direct `+0x434` store. No live factor/cost join. |

Enclosing caller is singleton vtable `0x82138768` slot `+0xC8`. Indirect call
`0x828AA8FC` loads receiver from another object's `+0x18`, unjoined to the
singleton; live caller/gameplay trigger remains unproved.

Identity packets cover the full initialized range:

- [items 200-204](../../manifests/wonder-records.json#/findings/RVA-F-0096)
- [205-209](../../manifests/wonder-records.json#/findings/RVA-F-0097)
- [210-214](../../manifests/wonder-records.json#/findings/RVA-F-0136)
- [215-219](../../manifests/wonder-records.json#/findings/RVA-F-0137)

Individual records follow:

- [220](../../manifests/wonder-records.json#/findings/RVA-F-0138)
- [221](../../manifests/wonder-records.json#/findings/RVA-F-0139)
- [222](../../manifests/wonder-records.json#/findings/RVA-F-0144)
- [223](../../manifests/wonder-records.json#/findings/RVA-F-0145)
- [224](../../manifests/wonder-records.json#/findings/RVA-F-0146)
- [225](../../manifests/wonder-records.json#/findings/RVA-F-0147)
- [226](../../manifests/wonder-records.json#/findings/RVA-F-0148)
- [227](../../manifests/wonder-records.json#/findings/RVA-F-0149)
- [228](../../manifests/wonder-records.json#/findings/RVA-F-0150)
- [229](../../manifests/wonder-records.json#/findings/RVA-F-0151)
- [230](../../manifests/wonder-records.json#/findings/RVA-F-0152)
- [231](../../manifests/wonder-records.json#/findings/RVA-F-0153)
- [232](../../manifests/wonder-records.json#/findings/RVA-F-0154)
- [233](../../manifests/wonder-records.json#/findings/RVA-F-0155)
- [234](../../manifests/wonder-records.json#/findings/RVA-F-0156)
- [235](../../manifests/wonder-records.json#/findings/RVA-F-0157)
- [236](../../manifests/wonder-records.json#/findings/RVA-F-0158)

Also see the bounded
[`wonder-records.json#/findings/RVA-F-0165`](../../manifests/wonder-records.json#/findings/RVA-F-0165).

## Building and wonder record contract

The table below lists assigned definition fields.

Exact values for each ID live in:

- The [`building-record-identities-100-122.json`](../../manifests/building-record-identities-100-122.json)
- The [`building-menu-record-gates.json`](../../manifests/building-menu-record-gates.json)
- The [wonder identities](../../manifests/wonder-records.json#/findings/RVA-F-0096) and their linked continuation packets
- The [`wonder-outer-gate-record-fields.json`](../../manifests/wonder-outer-gate-record-fields.json)

No runtime probe has recorded an individual definition-field value or observed
execution of a described effect. The recorded sessions establish some menu and
production-item behavior, not these field values or effects.

| Record field | Static meaning | Remaining unknown |
|---|---|---|
| Building `+0x00` | Stored name text in IDs 100-122 | Text reader, localization, and display |
| Building `+0x20` | Stored token text | Token consumer and asset binding |
| Building `+0x41` | Signed byte factor read by the non-unit cost helper | Final cost for a live player and all caller paths |
| Building `+0x42` | Signed technology ID checked by the city-menu ownership query; `-1` skips that query | Complete admission rule and live result |
| Building `+0x44` | Required city building-bit mask; a nonzero mask needs at least one matching bit | Other city-bit writers and complete policy |
| Building `+0x48` | Forbidden city building-bit mask; a matching bit rejects the menu candidate | Other city-bit writers and complete policy |
| Building `+0x4C` | Stored English description | Display reader and implemented gameplay effect |
| Wonder `+0x00` | Stored name text in IDs 200-236 | Text reader, localization, and display |
| Wonder `+0x40` | Signed halfword factor read by the non-unit cost helper | Final cost for a live player and all caller paths |
| Wonder `+0x42` | Stored halfword; exact exposed values are recorded for 220, 223, and 236 | Writer, reader, and meaning |
| Wonder `+0x44`, `+0x46` | Signed technology IDs or `-1` sentinels checked by the generic outer gate | Full eligibility and special-index 19/20 use; those indices bypass these generic reads |
| Wonder `+0x48` | Signed technology ID or `-1`; the generic gate tests other-player ownership | Full eligibility and special-index 19/20 use; those indices bypass this generic read |
| Wonder `+0x4A` | Stored short token | Token consumer and display role |
| Wonder `+0x8A` | Stored art token, often repeated across records | Asset consumer and art binding |
| Wonder `+0xCA` | Stored English effect description | Display reader and implemented gameplay effect |

Generic `TechnologyAcquire` calls one other static consumer, `0x82CEA5A0`, with
its technology ID. That function compares the ID with building `+0x42` and
wonder `+0x44` while forming a local list. Its wonder loop spans 33 positions;
the list's downstream meaning remains unresolved. See the
[technology-field
match](../../manifests/definition-technology-match-list.json).

A separate
[conditional
list](../../manifests/definition-technology-conditional-list.json)
reads building `+0x42` and wonder `+0x44` and `+0x46`. Its wonder path compares
the two technology IDs with a selected value and can query ownership of the
other field.

Its two direct callers pass a selector computed as the item minus 600 from the
preview helper or an indexed byte from another function. Its list output and
runtime use remain unresolved.

These are partial layouts, with no supported meaning for unlisted bytes. Editing
a known signed factor can change the accepted static cost calculation for an
initialized ID, subject to its later modifiers; it does not establish a final
in-game price. Building menu masks and wonder technology cells are known inputs
to local gates, not a complete buildability policy.

Repeated or mismatched tokens do not identify assets. The initialized record
blocks cover IDs 100-122 and 200-236; the helper's broader 100-199 and 200-299
routing cannot be used as a contract for extending the table with arbitrary IDs.

### Item selection and admission

The
[`production-item-writer-decoded-frontier.json`](../../manifests/production-item-writer-decoded-frontier.json)
found no selection/validity rule within its recorded limits. A runtime write
observer found command five storing its item into owner-matched city `+0x38` at
`0x82CE0020`, without an ID check. Cost preview separately writes candidate IDs
temporarily, restoring the prior item; see the
[`city-production.json#/findings/RVA-F-0183`](../../manifests/city-production.json#/findings/RVA-F-0183).

City choice handler `0x82E02CE0` calls producer `0x82CEE650` for units,
buildings and wonders. It forwards the selected ID without a local bound and can
drain at `0x82CEE76C`. A Barracks session logged no type-five call at separate
submit `0x82CE1950`. A census of 27 direct drain calls, each checked within
0x100 bytes for literal five, proved no second producer.

The separate census found all 100 submit calls. City-list generator calls
`0x82CB42B8` twice; it submits five at `0x82CB44D0`. One branch adds 200 to an
ordinal from 33 wonder slots, yielding 200 through 232 only if the indirect
chooser returns a valid row. Initialized chooser dispatch reaches a dialog:
callback parses decimal row into `+0x470`; content update checks it against a
count of 16-byte entries afterward. Return writer `0x82E0551C` copies `+0x470`
to `+0x42C` without that check. Callback-string source, live rows, runtime
execution, indirect routes and earlier construction remain unknown; no
unconditional submission bound follows. See the
[`city-production.json#/findings/RVA-F-0188`](../../manifests/city-production.json#/findings/RVA-F-0188).

Seven direct generator callers use mode 2 (building), 1 (unit), or -1
(AI/city-update/turn). Wonder marker `-12` requires bit `0x2`, excluding mode 1;
mode/eligible slots alone do not select it. In an owner-reported wonder
selection session, the default-off observer enabled at `0x82CECC98` logged zero
calls before normal exit; other states remain open. End register `r30` relative
to `r15-3808` gives populated count; `r31` counts all 33 slots.

The choice child copies nonnegative IDs from separate parent arrays and checks
vector index before forwarding. Its wonder generator tests normalized 0 through
32 (IDs 200 through 232); mutable claims and eligibility decide membership.
Initialized IDs 233 through 236 are excluded. Reset fills 33 claims with -1;
mode-one completion writes owner/city index.

With vtable `0x82138768` at `0x8314F76C`, the inner city gate returns zero for
indices 33 through 36 (IDs 233 through 236): virtual target rejects, fallback
accepts only below 21. This
[`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170)
is neither runtime evidence for those IDs nor a program-wide validity rule. One
live menu pass observed both words -1 in all 33 slots and nonzero eligibility
for 2, 8, 11, 12 and 14 through 18; see
[`wonder-claim-slot-state.json`](../../manifests/wonder-claim-slot-state.json).

Building enumeration uses live count initialized 23, appending index plus 100
(IDs 100 through 122). Availability, later count mutation and the Barracks
session's taken branch remain unknown. See
[`city-production.json#/findings/RVA-F-0184`](../../manifests/city-production.json#/findings/RVA-F-0184)
and
[`city-production.json#/findings/RVA-F-0185`](../../manifests/city-production.json#/findings/RVA-F-0185).

Completion also checks/fills a 28-byte ordinal list at `+0x87..+0xA2`. The exact
building-loop generated window reads city `+0`/`+0x10`, not list bytes; Ghidra's
direct-field query covered zero decoded instructions. Callees/other readers
remain open, and no runtime list filter was observed. See the
[`building completion-list reader frontier`](../../manifests/building-completion-list-menu-reader-frontier.json).

### Post-threshold effect branches

Descriptions prove no implemented effects. The five direct mode-one indices in
`0x82D16BA0` have these static contracts; runtime effects remain unobserved:

| Item | Branch and limit | Evidence |
| --- | --- | --- |
| Hanging Gardens 202 | City `+0x03` = `clamp(trunc((3*x+1)/2),0,31)`, then two helpers; no persistent doubled-growth proof | [`hanging-gardens-population-branch.json`](../../manifests/hanging-gardens-population-branch.json) |
| Oxford University 208 | Filters 48 technologies, ranks with unresolved score helper, can request ordinary acquisition; selected ID/success unknown | [`oxford-technology-acquisition-branch.json`](../../manifests/oxford-technology-acquisition-branch.json) |
| Statue of Liberty 227 | Scans 128 cities, adds two to `+0x03`, clamped 31, for populated source-player cities; persistence unknown | [`statue-of-liberty-population-branch.json`](../../manifests/statue-of-liberty-population-branch.json) |
| Great Wall 201 | Filtered symmetric player-pair writes; consumer/peace-offer semantics unknown | [`great-wall-player-pair.json#/findings/RVA-F-0177`](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0177) |
| Leonardo's Workshop 211 | Compares definition halfwords/technology ownership, can replace live `+0x01`; virtual calls/coverage preclude universal upgrades | [`leonardo-unit-type-branch.json`](../../manifests/leonardo-unit-type-branch.json) |

Great Wall base `0x830ED1D8` has no exact references/decoded split constants in
the
[bounded search](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0207);
derived/indexed/computed/aliased/indirect readers remain open. Mode one skips
the later tail; separate mode-two items 219/220 can enter it:
[`wonder-post-threshold-helper-boundary.json`](../../manifests/wonder-post-threshold-helper-boundary.json).

Mode-two terminal indices 19/20 clear two bits and set `0x10000` in
`0x82FFE7C4`. Exact-base scan found no decoded materializers, excluding neither
displacement nor derived accesses. Three snapshot functions copy the whole word
to output `+0x200`; entry-reference counts and aligned direct-BL scan across
initialized executable memory were zero. Output provenance, bit consumer and
victory meaning remain unknown. Player-matched flow also updates
`0x830EF348 + 2*index`; no decoded split constant/field meaning was found. See
[`wonder-mode-two.json#/findings/RVA-F-0179`](../../manifests/wonder-mode-two.json#/findings/RVA-F-0179).

Immediate `+0xD0` does not directly read that counter: nonzero `0x82FFD688`
pointer selects a direct tail target; identity/provenance unknown. See
[counter frontier](../../manifests/wonder-mode-two.json#/findings/RVA-F-0210).
Text/art consumers, full layouts, final costs and most effects remain open; cost
inputs:
[`building-wonder-cost-identities.json`](../../manifests/building-wonder-cost-identities.json).

## Effect coverage by ID

Descriptions do not prove effects. Runtime observations cover choice,
eligibility and item state, not gameplay-effect execution:

| IDs | Static evidence | Runtime effect execution |
|---|---|---|
| Wonders 201, 202, 208, 211, 227 | Item-specific branches exist in the direct mode-one helper. Their local writes and calls are mapped in the [`wonder-post-threshold-helper-boundary.json`](../../manifests/wonder-post-threshold-helper-boundary.json) and [`great-wall-player-pair.json#/findings/RVA-F-0177`](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0177), [`hanging-gardens-population-branch.json`](../../manifests/hanging-gardens-population-branch.json), [`oxford-technology-acquisition-branch.json`](../../manifests/oxford-technology-acquisition-branch.json), [`leonardo-unit-type-branch.json`](../../manifests/leonardo-unit-type-branch.json), and [`statue-of-liberty-population-branch.json`](../../manifests/statue-of-liberty-population-branch.json). | Not observed |
| Wonders 219-220 | A conditional mode-two path writes shared status bits and a halfword; their meanings and downstream consumers remain unknown. See [`wonder-mode-two.json#/findings/RVA-F-0179`](../../manifests/wonder-mode-two.json#/findings/RVA-F-0179). | Not observed |
| Building 114 | The Courthouse bit selects a scan of eight or twenty coordinate candidates; one later path stores a selected or replacement ordinal byte at city `+0x58` plus a local index. The visible effect is unknown. See [`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json) and [city byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203). | Not observed |
| Buildings 101-106, 110, 112 | A direct post-completion city helper tests their presence bits and can change local weights on food, production, and trade component returns; a later path can store a selected or replacement ordinal byte at city `+0x58` plus a local index. The final city effect is unknown. See [bit arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json), [weighted score](../../manifests/building-bit-selection.json#/findings/RVA-F-0202), and [city byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203). | Not observed |
| Wonders 200, 206, 207, 209 | Bounded searches found no exact edge for the described effect within each packet's stated scope: [`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json), [`great-library-technology-transfer.json`](../../manifests/great-library-technology-transfer.json), [`east-india-sea-trade.json`](../../manifests/east-india-sea-trade.json), and [`shakespeare-city-culture.json`](../../manifests/shakespeare-city-culture.json). These are bounded negatives, not proof that no effect exists. | Not observed |
| Wonders 203-205, 210, 212-218, 221-226, 228-232 | These IDs normalize into the helper's accepted 0-32 range on the direct city-update callsite but do not match one of its five explicit mode-one branches. This bounds only that helper path; other consumers remain possible. See the [`wonder-post-threshold-helper-boundary.json`](../../manifests/wonder-post-threshold-helper-boundary.json). | Not observed |
| Wonders 233-236 | Normalized indices 33-36 branch away before the direct post-threshold helper body. The known vtable's earlier gate also rejects them on this path; other receiver states and paths remain unresolved. See the [`wonder-post-threshold-helper-boundary.json`](../../manifests/wonder-post-threshold-helper-boundary.json) and [`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170). | Not observed |
| Buildings 100, 107-109, 111, 113, 115-122 | Stored descriptions are present, but no item-specific effect branch or bounded per-item negative packet is recorded here. The [consumer frontier](../../manifests/building-wonder-consumer-frontier.json) does not exclude indexed or indirect readers. | Not observed |

Barracks 101 has no proved link to creation-record veteran bit. Raw displacement
scan found no +0x3C store in
[0x82D13978,0x82D16BA0), leaving computed/indexed/
other writers open. Ghidra owns only 8 bytes at 0x82D13978 and no function or
instructions at 0x82D15B84; modded veteran acceptance did not test Barracks.
See [link scan](../../manifests/barracks-veteran-creation-record-link.json).

One fresh-game wonder gate dispatched `+0x1E4` -> `0x82D80C30` for
0 through 32; all logged returns were zero. Indices 21 through 32 can return
one only for corresponding bits among three from `+0x1DC`.
Getter `0x82D7D2A8` reads frontend `+0x08`, forced zero for state 4 through
6. Generic gate queries signed technology `+0x44`/`+0x46` (or `-1`),
and other-player ownership for `+0x48`. IDs 200 through 236:
[`wonder-outer-gate-record-fields.json`](../../manifests/wonder-outer-gate-record-fields.json).
Indices 19/20 use [`wonder-outer-gate-special-19-20.json`](../../manifests/wonder-outer-gate-special-19-20.json).

All 60 direct frontend-pointer-reference functions yielded no proved root
`+0x08` write;
[census](../../manifests/wonder-eligibility.json#/findings/RVA-F-0192) excludes
neither indirect nor constructor paths. Base constructor zeros it before
`0x82FFD624` publication
([initialization](../../manifests/frontend-root-publication-mask-init.json)).
Owner `+0x80` can pass nonzero `+0x08` to `NtClose`, then clear it;
[vtable review](../../manifests/frontend-root-vtable-offset8-clear.json) leaves
producer/kind unknown. Bit meanings, other targets, special-state owners,
runtime eligibility/effects remain open:
[`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170),
[`wonder-eligibility.json#/findings/RVA-F-0171`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0171).

These effect searches prove only their stated negatives:

| Item | Search result and remaining boundary |
| --- | --- |
| Pyramids 200 | No government/state/completion/display/AI edge. Record-base materializer, technology-table materializer and shared helper all truncated; filtered literal/comparison scan hit eight-function cap, leaving them unclassified. [`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json) |
| Great Library 206 | Direct/split/literal searches found no effect edge. Later eligibility reads technology IDs 8/21, proving no transfer/acquisition/completion/display/AI behavior. [`great-library-technology-transfer.json`](../../manifests/great-library-technology-transfer.json) |
| East India Company 207 | No sea-trade/economy/completion/display/AI edge or record/description/cost direct/split match. Complete filtered scan emitted only `0x82500288`: `0xCF` is packed D3D decoding, not wonder identity. Generic terrain yield remains open. [`east-india-sea-trade.json`](../../manifests/east-india-sea-trade.json) |
| Shakespeare 209 | No culture/completion/display/AI edge or record/description/cost direct/split match. Complete filtered scan emitted `0x826CFDC8`; prefix lacks Shakespeare/culture carrier, body truncates. [`shakespeare-city-culture.json`](../../manifests/shakespeare-city-culture.json) |

Cost consumers: `RushCostCompute` (`0x82CE27F0`) subtracts city `+0x36` before
rush arithmetic; display `0x82DFFE38` uses current cost and `+0x36`/`+0x42`
percentages; `0x82D13978` branches away below cost;
`AIUnitChoiceEvaluate`/`AITurnUnitEvaluation` read `+0x44` and shared scalar.
The selected `AITurnUnitEvaluation` unit arm uses the signed normal cost as a
Gold prerequisite before a command-type 6 call: reserve equal to cost passes.
The cost register is overwritten before submission; no local debit or completed
action follows. The [cost manifest](../../manifests/production-cost-ownership.json)
owns the input, byte-gate, retention and arithmetic qualifications. This bounds
rush display, one completion threshold and a local AI prerequisite; general AI
decisions and corrected-rush parity remain unproved. No runtime production test
occurred.

For a preserved delivered command with amount zero, the selected native unit
consumer writes back the loaded production and Gold values. It still reaches
update calls and a later city flag store, so it need not leave all state
unchanged. The [zero-amount boundary](../../manifests/rush-cost-producer.json#/commandPath/zeroAmountUnitBoundary)
owns the owner/item, rate, helper-return and retention guards; no natural AI
transaction or completed production is established.

The same `0x82D13978` routes signed current item `+0x38` >=100 to
`BuildingWonderProductionCostLookup`. IDs 100 through 199 compare signed
invested production `+0x36` against cost, branch away below cost, and first
store invested minus cost on the sufficient path. IDs 200 through 299 repeat the
call, retain cost and compare likewise. After two additional neutral gates,
their first promoted stores subtract cost at `+0x36`, copy current item to
`+0x3A`, and mask word `+0x24` with `0xFFFFFBFF`.

No independent item<300 guard appears in the bounded evidence: these ranges
depend on the accepted current-item domain, not arbitrary-ID validation. Neutral
first writes prove no building/wonder completion, effects, queue advancement,
overflow handling, creation, notification, runtime behavior or implementation
safety. Exact addresses/stops:
[`non-unit-production-threshold-boundary.json`](../../manifests/non-unit-production-threshold-boundary.json).

## UnitType values

| ID | Internal name | Attack | Defense |
|---:|---|---:|---:|
| 0 | Settlers | 0 | 0 |
| 1 | FSettler | 0 | 0 |
| 2 | Naval Crew | 0 | 1 |
| 3 | Barbarian Hot | 1 | 1 |
| 4 | Barbarian Temperate | 1 | 1 |
| 5 | Barbarian Cold | 1 | 1 |
| 6 | Warrior | 1 | 1 |
| 7 | Militia | 0 | 1 |
| 8 | Legion | 2 | 1 |
| 9 | Archer | 1 | 2 |
| 10 | Riflemen | 3 | 5 |
| 11 | Modern Infantry | 4 | 8 |
| 12 | Horsemen | 2 | 1 |
| 13 | Knights | 4 | 2 |
| 14 | Tank | 10 | 6 |
| 15 | Phalanx | 1 | 3 |
| 16 | Catapult | 4 | 1 |
| 17 | Cannon | 6 | 2 |
| 18 | Artillery | 16 | 2 |
| 19 | Submarine | 12 | 2 |
| 20 | Galley | 1 | 1 |
| 21 | Galleon | 2 | 2 |
| 22 | Cruiser | 6 | 6 |
| 23 | Battleship | 12 | 18 |
| 24 | Space Station | 0 | 3 |
| 25 | Bomber | 18 | 3 |
| 26 | Fighter | 6 | 4 |
| 27 | ICBM | 0 | 0 |
| 28 | Spy | 0 | 0 |

Definitions 3 through 5 have an empty string at the record start. Their labels
come from the record-local strings `Barbarian_Hot`, `Barbarian_Temperate`, and
`Barbarian_Cold` at `+0x20`. The table above renders underscores as spaces.

## Unique Units

The identity selector at `0x82CEF160` uses the base `UnitType` and the unit
owner's civilization. It keeps the base type when no civilization-specific
identity exists. A mapped identity is a Unique Unit (UU). Two combinations
select unique English names:

| Civilization | Base `UnitType` | Name index | English identity |
|---|---|---:|---|
| Roman, index 0 | Knights, type 13 | 62 | Cataphract |
| Mongolian, index 14 | Horsemen, type 12 | 63 | Keshik |

The live name reader at `0x82CF0550` passes the `+0x1` type byte and the unit
owner to the selector. A nonzero record byte at `+0x4` selects the second
64-entry name section, where the corresponding English values are Cataphract
Army and Keshik Army. The `UnitNames_` resource family supplies all 128 entries.

These UUs do not create new unit-definition records. Roman Cataphracts retain
Knights type 13, and Mongolian Keshiks retain Horsemen type 12. The mapping
establishes display identity only. It does not establish identity-specific
movement, cost, effects, AI strategy, models, or animations.

## Simulation and AI consumers

`CombatResolve` at `0x82CD9970` calls both effective stat readers. Three
independent AI-side functions also call both readers:

- `AIUnitChoiceEvaluate` at `0x82CB44E0`
- `AITurnUnitEvaluation` at `0x82CB6E48`
- `AITurnUnitFilter` at `0x82CBF570`

For base attack and defense, a table change reaches both combat simulation and
the AI evaluation paths through the same effective accessors.

This is not general AI parity for a Unique Unit modification. Costs, movement,
abilities, flags, production weights, and naval or air special behavior require
independent producer-consumer mapping before mutation.

## Local AI candidate choice

In `AITurnUnitFilter`'s no-alternative path, signed defense >= attack for the
same player/type (stable across loads) enables two +8 threshold additions: unit
`+0xC` bit `0x10` and indexed halfword bit `0x40`. The table's
terrain/coordinate meaning is unknown.

A later candidate replaces ordinal/threshold only for a strictly greater signed
score; equality retains the ordinal. Another loop short circuit can select
without that comparison, though normal exit bypasses it. A later predicate with
unnamed byte-table/flag meanings can discard the ordinal and clear queued
destination. Bypassing that predicate and an opaque helper lets the ordinal
reach original unit `+0x20`; ordinals 0 through 7 also encode a numeric
caller-output code without changing ordinal. Another selection route writes the
same field.

Caller `TurnSelectionUpdate` supplies frame `+0x7C`. Guarded return carries the
code to `0x82D2A718`, decoding the original ordinal into r20; publisher clear
and other caller overwrites make retention conditional. Move command 17 at
`0x82D2CE00` uses r20 as step. Player reload must preserve identity; the
zero-result route below retains original unit, while other entries need their
own provenance. Executed movement remains unproved.

| Gate/continuation | Contract |
| --- | --- |
| Candidate position | Positive signed movement budget; unit coordinates plus decoded ordinal, signed horizontal remainder. `0x82CF0268` seeds bounds Boolean, then may clear it through indexed cells/definition flags. Failed bounds do not skip reads; valid memory remains required and meanings unnamed. |
| Override | Zero result can be overridden by target bit `0x4` plus indexed signed byte matching an unidentified saved scalar. With following bit `0x1` clear, zero clears original queued destination and exits. Nonzero resets a fixed global, clears r22 and searches candidate-position units. |
| No eligible unit | A definition-flag branch retains original unit/coordinates into `0x82CB2430`. Boolean uses definition flags, original/candidate position bytes, halfwords and matrix entry. `0x80000` forces zero; `0x80` adds byte equality. Meanings remain unknown. |
| Zero helper result | No memory/nonvolatile writes; bypasses selected-unit reload, retaining original index and r22=0. Stable player reload/memory guards permit global/original-unit flag writes, then `0x82D038E8` at `0x82D2CDE0`. |
| Before Move | Helper updates another fixed global, may use eight stack bytes, and preserves index/ordinal. Normal completion and separate stack storage reach Move without another branch/call, supplying original player/unit/step. |
| Submission | Global bit `0x400` clear stages a five-word stack record. Set invokes a helper first: null child preserves arguments; nonnull dispatch has unbound receiver/target. Flag meaning remains unknown. |

Publication, delivery, dispatch, movement and compass mapping remain unproved.
Effective stats/+8 adjustments are possible controls, but complete score and
retained stat-adjusted threshold need proof before predicting behavior. See the
[AI choice manifest](../../manifests/ai-stat-choice.json).

## Additional count and model consumers

The
[count/model continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/countAndModelContinuation)
binds eight definition-base producers/four live-count walks: 4,560 instruction
comments matched native operands; 37 data words pinned Militia7's complete image
record. The 19 raw rows resolve to eight base pairs, four count pairs and seven
spurious pairs with overwritten high registers.

| Owner | Adaptation contract |
| --- | --- |
| `0x82CE77D8` | Retarget B at `0x82CE7A98/0x82CE7AA0`; signed +0x4A match and positive retained input gate live-count tagged type/name output. |
| `0x82CEA5A0` | Retarget B at `0x82CEAB64/0x82CEAB70`; signed +0x4A match drives live-count tagged list. Literal helper argument 39 is not definition capacity. |
| `0x82D09208` | Retarget B at `0x82D0959C/0x82D095AC` before frame +0x88 caching. Candidate +0x4A/source +0x4C match incoming technology; loaded owner-state word equals 4. No local nonzero-match exclusion. |
| `0x82D16BA0` | Retarget B at `0x82D16C70/0x82D16C88` before frame +0x80 caching. Leonardo source +0x4C/candidate +0x4A require nonzero match and owned technology. |
| `0x82D99CE8` | Retarget B at `0x82D99D1C/0x82D99D24`; cached +0x48 model bits feed six additional child positions. |
| `0x82D99EB8` | Retarget B at `0x82D99EC8/0x82D99ED0`; three +0x48 model bits feed child allocation, current dispatch, vector/manager work. The 192-byte allocation is an object. |
| `0x82D9A320` | Retarget B at `0x82D9A374/0x82D9A378`; +0x50 flags combine with live rank/upgrade bits in one selector arm. |
| `0x82D9A9E8` | Retarget B at `0x82D9AB08/0x82D9AB0C`; +0x50 mask 0x4 gates one current-object appearance parameter. |

Militia7 has attack 0, defense/movement/cost factor 1, byte +0x48=7, signed
halfwords +0x4A/+0x4C=zero, word +0x50=0x20. Unchanged copies preserve these
model inputs and miss Leonardo's nonzero-match path. Separate technology
acquisition can reach copied Scout with technology zero, owner-state word 4,
live-unit filters and action bit; reachability/callback retention remain
conditional. This is not Leonardo's exclusion.

Strings `Militia` at +0, `worker_rom_m` at +0x20 and `Swordsman` at +0x54/+0x74
prove no localized Scout names/icons/assets; factor 1 proves no absolute
five-hammer cost. Gates remain: live definition retention, complete
base/count/alias coverage, output capacity, child registration/lifetime and
save/network/new-ID admission. Shared manifest navigation leads to the next
bounded census.

## Description, derived-stat and ranking consumers

The
[next consumer continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/descriptionAndStatContinuation)
adds five B producers: `0x821BB120`, `0x821BE8B0`, `0x821BEA28`, `0x82CB2430`,
`0x82CB2E48`. All 2,332 instructions matched native operands. Five other
pairings were spurious; one crossed two selected functions.

The description-shaped helper passes the complete indexed record to
`0x821B1500`; copy/alias/name semantics remain unbound. Fixed 31 through 37
dispatch requires flags mask 0x80; copied Militia flags 0x20 take the generic
arm. Two derived-stat helpers combine model masks 1, 2, 4 with a live-unit
halfword before effective attack/defense calls; float retention remains a gate.
AI candidate leaf reads flags 0x80000/0x80. Ranking caches B in r16 and
aggregates raw cost factors over live records, not proved effective production
cost.

Copied Militia prerequisite +0x4A=zero fails normal trainability: ownership
query must return nonzero, but its exact zero-input arm returns zero, assuming
retained live fields/inputs. Scout needs eligibility override alongside
name/cost/effects. -1 at +0x4A bypasses that first gate; copied +0x4E=24 and
other conditions still apply. Changing +0x4A also reopens candidate-side
Leonardo exclusion; unchanged-zero proof no longer applies. The continuation
records exact retargets/gates.

## Additional-definition names, models and cost

The
[name/model/cost continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/nameIdentityModelCostContinuation)
verified 486 instructions/eight helpers, adding B readers `0x82CF1148` and
`0x82CF8308`. Names load pointer `0x8314F188` then add 12*identity (not inline
array). Type 38 maps to 38/army 102 in existing presentation space; Scout needs
a separate route preserving those identities.

`0x82D9B6E0` stores name pointer at +132, component at +136: relocated names
need lifetime through model use. Allocation tag is no model token; assets/icons,
child ownership/lifetime remain open. Two adapters pass lengths/pointers to
`0x82D3B798`; its copy/alias behavior is unbound.

Signed +0x44 factor times final scalar /2 truncates toward zero: factor 1 and
scalar 10 or 11 yield 5. Scout scalar 10 must reach every cost consumer after
native/host modifiers. Current-item composition is bound; cost topic covers
display/AI/rush/completion. Shared delivery, override order and trainability
remain separate. Raw census stays open; `0x82CB44E0`/`0x82CB6E48` lack following
physical headers, so fresh generated-body reads remain closed and qualified
native cost evidence is reused.

## AI and city consumer continuation

The
[AI/city
continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/aiAndCityConsumerContinuation)
classifies eight further B producers after 7,829 native/source instruction
matches. `0x82CBF570` saves B at frame +0x5C, then reloads it for later attack,
defense and flags reads after reusing the original register.

Relocation must reach that frame save and all derived pointers. Other selected
paths read attack/defense, flags, technology, an unnamed +0x43 byte and model
mask.

Copied Militia attack 0 excludes the selected candidates in `0x82CB3DC0`,
`0x82CC6D10` and `0x82CC75B8`. Other paths accept copied flags 0x20 at their
particular masks. These are inherited local filters; neither result establishes
build-list admission, global AI preference or a delivered action.

The 256 unit records, 128 city records and local selector/component bounds
remain separate from definition count 39. The 29-entry public catalog is another
namespace and does not exclude native special rows 29 through 37.

The continuation records exact producers, field/cached-pointer locators and
remaining return/alias/lifetime gates. It also preserves five EOF candidates for
native-only binding or accepted-evidence reuse. The global census remains open.

## Movement, selection and rush consumers

The
[movement/selection/rush
continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/movementSelectionAndRushContinuation)
verified 4,188 native/source instruction operands and classified eight more
inline B producers, plus two spurious raw pairings. `0x82CD7A60` saves B at
frame +0x80 and later reloads it for flags and defense.

Retarget before that save. `0x82CD77E8` reads definition movement +0x42 and
writes its tripled value into a unit record; the complete March and movement
refresh order remains open. `0x82CE27F0` consumes factor +0x44 before separate
rush/display arithmetic, so factor 1 alone does not establish an absolute hammer
or gold cost.

The remaining four bodies bind selection filters and later presentation calls.
Copied flags 0x20 clear their selected masks, while other live-unit, coordinate
and callback gates remain. Keep 256 instance records and the separate
context-index scale 38 distinct from definition count 39. The global census,
coherent storage and new-ID admission remain open.

## Production, inline names and upgrade gates

The
[selected
continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/productionNameAndUpgradeContinuation)
verified 2,557 native/source instruction operands across eight more B producers.

It binds further factor/stat reads, fixed rows 10 and 13's +0x4A fields, an
inline-name builder with persistent output at `0x82FFD7C0`, and an upgrade
eligibility check counting all low 16 upgrade bits against six. The exact flag
branches and host research-prompt hook retain their recorded qualifications.
These are local consumer findings, with no global extension or runtime claim.

Scout uses Militia appearance as a placeholder. The
[minimum title support
contract](../../manifests/city-militia-scout-feasibility.json#/minimumScoutSupportBoundary)
keeps its logical identity, trainability, absolute cost and creation effects
separate from ordinary Militia.

The exhaustive native census is incomplete; neither a relocated 39-record table
nor a Militia-backed logical variant is admitted as an existing safe
registration path.

## Combat stat-role boundary

The accepted ordinary path for one unit against another contains one exact
ordered stat pair inside `CombatResolve`:

| Derived role | Callsite | Player and type input | Result |
|---|---:|---|---|
| Attack side | `0x82CDA214` | Accepted attacker player and unit-record type | Effective attack retained separately |
| Defense side | `0x82CDA234` | Accepted defender player and unit-record type | Effective defense retained separately |

Attack is obtained before defense. The two-value role is derived from these
callsites; it is not a stored guest enum. The shared accessors themselves take
only player and base `UnitType` before establishing their base scalar, so they
do not carry an opposing unit or combat-role argument.

`CombatResolve` contains six other effective-stat calls, including a separate
literal-25 special branch immediately after the core pair. Those calls do not
inherit the attack-side or defense-side meaning, and this result does not prove
an opposing class predicate or city, naval, or air equivalence.

Bounded windows in the three mapped AI evaluators confirm scalar consumption but
not role parity. `AIUnitChoiceEvaluate` adds attack and defense for the same
player and type; `AITurnUnitEvaluation` conditionally multiplies candidate stat
results; and `AITurnUnitFilter` compares defense and attack under one player
with separately sourced types.

None of those scalar windows exposes the accepted two-player combat participant
carrier.

A separate later call in `AITurnUnitFilter` closes one bounded AI context. At
`0x82CC03FC` it passes its incoming player and unit to `CombatResolve` in mode 1
with provisional defender inputs of -1.

The resolver retains that attacker identity and, on the continuing
opponent-present path, derives the accepted defender player and unit before
reaching the ordered attack-side then defense-side core pair. The AI caller
tests the returned value against evaluation thresholds.

This is one resolver-backed prediction path, not general role parity for the
other AI evaluators, early returns, or every resolver outcome.

The [ordinary combat boundary](ordinary-combat.md) records separate local
weighting and checkpoint-selection blocks with conditional generator-word
stores. The guarded frame-value calculations and local stack-store pointer are
closed. A guarded trace from the core stat pair to the first store depends on
its stated ABI, nonalias and finite ordinal conditions.

Checked post-store subcases reset the array or bypass presentation. A separate
conditional presenter input chain reaches input to the transfer call. The frame
`+148` Boolean producer is recovered separately. Participant normalization
rewrites the later defender input, invalidating the original-r6 sentinel
derivation for a valid participant path.

The null local-player return also blocks the countdown alternative. The
[local-player input boundary](frontend-frame-and-input.md) binds a guarded owner
`+0x10` writer, the child's dispatch, and initial result allocation and word
production.

Two bounded displacement scans, selected store owners, a class-owned reader and
a child-field initializer did not bind a later result `+0xC` writer. The child
`+0x88` method conditionally carries the result to a writer that exchanges its
current word between two searched ordinals. Initial -1 remains unchanged under
nonnegative ordinal without overflow and ownership/ABI/nonalias guards.

Registry lookup/getter paths conditionally reach a prior-word producer, but
current-owner key equality, scalar values and its internal lookup/dispatch gate
remain unproved. The tested setup/cleanup bodies contain no child `+0x88`
invocation. That invocation remains a separate open question; the prior-word
route needs a compatible value and ordered retention.

Two field readers pass their own `+0x34` to a four-byte input helper; shared
receiver identity, actual input source and receiver `+0x8 == 0` remain unproved.
A compatible nonzero producer and resolver entry, full transfer and participant
persistence remain unclosed; no naturally reachable ordinary outcome path is
proved.

## Loaded-fleet sale value

The selected native sale path adds the carrier's production factor and admitted
linked passengers' factors, then applies the carrier's army/fleet multiplier
to the whole sum. It does not use each passenger's own army marker in that sum.
For the supported Galleon/Spy inputs and the human classifier arm, an empty
fleet contributes 90 Gold, one loaded Spy brings the total to 165, and ten bring
it to 840. The cargo contributions are therefore 75 and 750 Gold. These are
derived native amounts; actual command delivery and reserve changes were not
observed. [Sale valuation](../../manifests/unit-sale-refund-value-boundary.json)
records membership, identity, arithmetic and preview/correction limits.
The native register representation permits a correction at the value producers
without changing the formatter. Such a correction still needs roster retention
across the classifier and a guard for nested carriers excluded by removal.

## Evidence sources

- [Fleet scrap command boundary](../../manifests/fleet-scrap-command-boundary.json):
  army disbanding and unit deletion use different selected commands. Their
  inspected paths do not establish loaded-fleet refunds or cargo valuation.
- [Unique Unit identity selection](../../manifests/unique-unit-identity-selection.json)
- [AI candidate choice](../../manifests/ai-stat-choice.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Production cost ownership](../../manifests/production-cost-ownership.json)
- [`non-unit-production-threshold-boundary.json`](../../manifests/non-unit-production-threshold-boundary.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Unique Unit combat predicates](../../manifests/unique-unit-combat-predicates.json)
