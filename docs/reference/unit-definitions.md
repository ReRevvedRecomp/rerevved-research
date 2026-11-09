# Unit definitions

The native table at `0x82F700D8` has stride `0x94` and initialized count 38. The
public catalog covers records 0 through 28. Runtime unit byte `0x1` in each
`0x54`-byte record indexes the table. Names are recovered semantic labels, not
debug symbols.

These findings cover the stated static paths and memory reads. "Accepted"
means that the evidence supports the claim. It does not imply runtime execution
or coverage of every consumer. Limits on return values, on which function
writes a value, and on aliasing remain explicit. These findings establish no
safe API for adding unit definitions.

- [Native count and storage limits](#native-count-and-end-boundary).
- [Settler production requirements](#settler-production-gates).
- [Production cost](#normal-unit-production-cost).
- [Building and wonder fields](#building-and-wonder-record-contract).
- [Unit IDs and stats](#unittype-values).
- [Combat stat roles](#combat-stat-role-boundary).
- [Native army formation](#native-army-formation).

## Native army formation

Native command 10, `MakeArmy`, calls `0x82D13618`. Its eligibility helper
requires at least three matching units of the same kind on one tile. It also
applies additional type, definition and player checks. Formation consumes the
first two eligible slots other than the selected unit, combines their state into
the survivor, writes its army selector, invokes native callbacks and recounts.

This path forms an army; it does more than change the army name. An Archer
already on the tile can be consumed before newly created Archers. Granting an
army when the first capital is founded therefore still needs four things: a way
to preserve existing units, proof that founding completed, a save policy, and
allocation handling. It also needs evidence of actual callback lifetimes. No
such grant or runtime outcome is established here. The exact checks, writes and
qualifications are in the
[army formation record](../../manifests/army-formation-command.json).

## Recovered layout and readers

| Item | Address or offset | Accepted meaning |
|---|---:|---|
| Native unit-definition table | `0x82F700D8` | Initialized count 38, stride `0x94`; whether the live count is still 38 is not yet established |
| Public catalog subset | IDs 0 through 28 | 29 cataloged records; additional native records follow |
| Runtime unit type | unit record `+0x1` | Zero-based index into the definition table |
| Internal name | definition `+0x0` | NUL-terminated record name when present |
| Base attack | definition `+0x40` | Signed byte read by `EffectiveUnitAttackLookup` |
| Base defense | definition `+0x41` | Signed byte read by `EffectiveUnitDefenseLookup` |
| Base movement | definition `+0x42` | Signed byte read by `EffectiveUnitMovementLookup` |
| Production-cost factor | definition `+0x44` | Signed byte composed by `EffectiveUnitProductionCostScalar` |
| Effective attack reader | `0x82CF2230` | Applies unit and civilization modifiers to base attack |
| Effective defense reader | `0x82CF21A0` | Applies unit and civilization modifiers to base defense |
| Effective movement reader | `0x82CF1F70` | Applies local and civilization modifiers on its main composed return |
| Unique Unit identity selector | `0x82CEF160` | Maps a base `UnitType` and player civilization to a localized name index |
| Live unit-name reader | `0x82CF0550` | Reads the live unit type, applies the identity selector, and resolves the unit or army name |

Bytes `+0x43` and `+0x45` through `+0x47` remain intentionally unnamed. Their
adjacency to accepted fields does not show another gameplay meaning.

`EffectiveUnitMovementLookup` reads three retail movement UEAs on its main
composed return. Definition flag `+0x50 & 0x200` selects UEA 3, Riflemen
UnitType 10 selects UEA 12, and Warrior UnitType 6 selects UEA 55. Each active
cumulative lookup adds one to the movement value that is carried forward.

One special return path uses an unresolved constant instead of the composed
value. The finding therefore does not cover every movement return, consumer
or AI path. The exact branches are in
[`unit-movement-stat.json`](../../manifests/unit-movement-stat.json).

## Native count and end boundary

Initializer `0x82D25170` writes literal 38 to live count word `0x830E45D0` at
`0x82D25194`. The accepted game-start caller reaches that initializer through
an audio condition. Three points are not yet established: whether the
initializer is actually invoked, the timing for a new game versus a load, and
whether the current count stays at 38. The count is a literal, not a scan for
an empty record.

The logical 38-record span is `0x15F8` bytes at `[0x82F700D8,0x82F716D0)`. Its
final byte is `0x82F716CF`. The public catalog ends before `0x82F7119C`. The
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

These names do not show localized labels, buildability or model routing. The
first address beyond the count, `0x82F716D0`, immediately contains occupied
Blitz-related text. Appending a record there at the unchanged base would overlap
that data. This extent gives no safe spare unit ID, no universal maximum
capacity, no relocation contract and no API for additional definitions.

The
[count and extent evidence](../../manifests/unit-definition-count-extent.json)
records the native words, source identity, data queries and qualifications. The
[Militia and Scout feasibility page](city-militia-scout.md) records the separate
creation, cost, upgrade and all-player requirements.

## Definition-base consumers and relocation

Seven selected native functions construct `0x82F700D8` independently with
`lis` and `addi`. A count change, a data copy or one pointer-cell update alone
cannot redirect those instruction-defined bases. Each selected field address is
derived locally from the base. No separate absolute field-address producer was
established in these samples.

| Function | Selected use and state it keeps |
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
37. Neither scan reads the live count. Production enumeration does read it, and
refreshes it only after it accepts an entry.

These limits apply to different structures. Routing below 100 and a 100-word
scratch array do not show that the definition table can safely hold that many
records.

A compatible relocation of the existing 38 records needs five things from every
base producer and alias that reaches the table: a coherent storage identity,
valid guest addresses, the same stride and fields, signed pointer ordering, and
storage that lives across calls. Saved frame words and already-derived register
pointers both matter. No safe allocation or publication protocol was shown.

The maintained host catalog independently supports 29 public IDs and passes
scalar or runtime-unit contexts to the sampled hooks. Moving native data does
not extend that metadata or establish an API for registering definitions.

Letting production accept a new entry is a separate decision from growing fixed
scans. Keeping the defender range fixed could exclude a future Scout outside
that range from this selector. That does not show exclusion from every grant.
Omitting a custom Loyalty assignment also does not bypass the existing native
completion assignment, which applies only under its own condition.

Supported new IDs and other unit properties are not yet established.

The [base-consumer record](../../manifests/unit-definition-base.json#/findings/RVA-F-0277)
holds addresses, source digests and 66 fresh matching native words. Its raw
eight-word search found 114 syntactic pairs, with register lifetime and the
function that holds each code unchecked.

That search demonstrably missed the validated production base producer at
`0x82CEBF04` and `0x82CEBF84`, whose instructions are 32 instructions apart. It
is not a complete list of relocation sites.

### Census coverage and decode limits

The instruction-aware census missed the validated production control on the
unrepaired canonical listing. Lookaheads 8 and 32 both emitted 14 function
representatives. Neither endpoint was decoded or inside a function, and the
seeded function at `0x82CEBC38` covered eight bytes through `0x82CEBC3F`. A
longer lookahead cannot repair missing coverage.

| Evidence | Result and limit |
| --- | --- |
| [Census validation](../../manifests/unit-definition-base.json#/findings/RVA-F-0278) | Query model, limited failure and 33 fresh matching native words. The 14 deduplicated hits differ from the earlier 114 raw pairs; neither shows complete materializer coverage. The canonical project was queried without repair. |
| [Disposable coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0279) | Supported repairs decoded all 33 control instructions, but the function at `0x82CEBC38` still covered eight bytes. The post-call `stwu` at `0x82CEBC40` decoded and matched, which rules out an undecodable displayed opcode as the cause. The 34 unique matching words establish decode coverage, not a function body or a relocation inventory. The missing function coverage blocked census replay. |
| [Call flow](../../manifests/unit-definition-base.json#/findings/RVA-F-0280) | Normal call `0x82CEBC3C` has no flow or fallthrough override and has returning-callee metadata. Its continuation is `0x82CEBC40`, which the rebuild guard accepts. A read-only calculation produced 4,052 bytes in 12 ranges containing both controls, while the stored body stayed eight bytes. The current flags and calculation do not reproduce that cutoff. |
| [Creation reconciliation](../../manifests/unit-definition-base.json#/findings/RVA-F-0281) | The function body is eight bytes when an entry already exists, and the exact 4,052-byte, 12-range set when it is created fresh. With the exact entry removed, no functions overlap, and the result is not a thunk. Both controls belong to `0x82CEBC38` in the required basic block, and all 32 next-defined steps pass. The stored project bytes and the uncertainty about historical repair are unchanged. |
| [Same-session census](../../manifests/unit-definition-base.json#/findings/RVA-F-0282) | On the recreated state, the lookahead-32 census covers the control pair and 16 distinct representatives, with no truncation or cancellation. They include all 14 canonical representatives plus two more. The listings differ, so the counts cannot be compared causally. |
| [Omitted-site coverage](../../manifests/unit-definition-base.json#/findings/RVA-F-0283) | Five decoded pairs outside any function and one undefined pair. All six expected functions covered eight bytes, excluding endpoints. The census skipped them before low-part matching, register-write filtering and deduplication. No complete inventory or new count follows. |
| [Cost-lookup decode](../../manifests/unit-definition-base.json#/findings/RVA-F-0284) | The standard store at `0x82CE2B9C` falls through without overrides to inline `std` at `0x82CE2BA0`, whose constructor the selected 32-bit language excludes. Isolated decoding accepts the preceding store but not `std`. Native fields and the recompiled code corroborate the 64-bit store. The listing and the eight-byte body stayed unchanged. |
| [Detached strategy](../../manifests/unit-definition-base.json#/findings/RVA-F-0285) | Precompiled `PowerPC:BE:64:64-32addr` decodes both stores with the intended widths and fallthrough. Raw pcode keeps eight-byte STORE offsets into ram32 without explicit truncation. |
| [Consumer source trace](../../manifests/unit-definition-base.json#/findings/RVA-F-0286) | A later guarded `RulePtrFlow` extracts the low four address bytes and keeps the eight-byte value. Raw import and initial SSA and alias work come before it. |
| [Installed-native observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0287) | An isolated STORE fixture with a synthetic return produced a four-byte low32 address and the full eight-byte value. The diagnostic control kept an eight-byte address. Java's dead flag was unmaintained bookkeeping. The interpretation of the returned block remains qualified. |

The
[cost-lookup coverage record](../../manifests/unit-definition-base.json#/findings/RVA-F-0288)
holds the structural evidence. Three points are not yet established: a complete
base inventory, broader Xenon and ABI equivalence, and the causes of the
historical body writes and repairs.

### Shared coverage and remaining inventory limits

The
[shared-coverage record](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/ordinarySwitchRecoveredObservation)
covers seven selected functions in one unsaved native candidate. Adding 52
native inline-table bytes let the configured decompiler and its switch command
recover both CityUpdate switches. Standard body fixup reached the exact
12,788-byte input: all 3,197 instructions were inside functions, and the block
union matched at 654 blocks. Postanalysis followed stored references, and the
native target lists were comparison whitelists. Table one kept six labeled
records, duplicate destinations and no separate default. Table two kept seven
records plus default `0x82D13E14`.

The unchanged 32-step census recovered all seven selected producers without
truncation, including `0x82CEBF04 -> 0x82CEBF84`. The cost, long and creator
controls passed, and 53 raw snapshots and 43 read comparisons matched. The
canonical bytes stayed unchanged. This completes selected local coverage. It is
not an image-wide inventory of consumers or counts.

A
[broader raw-inventory attempt](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/rawInventoryMemoryIdentityObservation)
stopped before scanning, because canonical RAM failed the full supported-image
digest check. Zero counters do not show that no matches exist. The report omitted
the observed digest and the cause. A
[verified-file observation](../../manifests/unit-definition-base.json#/findings/RVA-F-0300/rawNativeFileInventoryObservation)
completed the declared address models against the full supported native-file
buffer. Independent reconstruction matched every candidate and control. The
saved RAM identity and its differences were recorded and kept. Their cause
remains unknown. Raw matches still need semantic classification.

The
[creator continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0301)
holds the reconciled 900-byte input. Four CityUpdate self-call tuples need
actual returns. The first two keep the original city and mode 1. The latter two
use the current r19 and mode -1. Four points are not yet established: the actual
r19 identity, recursive or computed returns, frame and pointee lifetime, and the
full semantic extent. Missing memory prevented following the restore target
`0x827F7CA0`. Broader coverage of bases, aliases, interior addresses and counts,
and a safe Scout registration, remain open.

## Settler production gates

The human production menu and three AI turn-evaluation call sites share a
candidate generator. When the Settlers definition is unchanged, the generator
requires population of at least three. The requirement drops to two when
cumulative UEA 45 is active or the player-indexed word equals five. Both inputs
have neutral meanings. The second Settlers record (ID 1) fails the generator's
first prerequisite, so it is not an interchangeable buildable entry.

Completion separately checks cost and the equivalent population threshold.
Command type five can assign Settlers to the current item `+0x38` of a city
whose owner matches the command, without repeating that check. Selection skips
resubmission when Settlers is already the current item, and existing production
still enters completion. A failing population check can exit mode one without
clearing or replacing the item. These paths depend on the calls made, on
delivery, and on the city, array and frame state staying as read.

A Settlers-only minimum R can preserve other units' native requirements:

| Native comparison | Settlers selector | Effective threshold in r11 |
|---|---|---|
| Candidate `0x82CEC7A8`, population >= T | candidate type r30 == 0 | max(native T, R) |
| Completion `0x82D15A7C`, population > K | current item r25 == 0 | max(native K, R - 1) |

These are comparison contracts that hold only under their stated conditions.
They are not an implemented setting or a per-unit field. The operands must be
supplied at full width after the native alternatives merge, and must keep the
supported type 0, flag 1 state. With the policy disabled, and for other types,
the native operands stay unchanged. R=32 rejects populations through 31. R=128
rejects every current signed-byte value, but supports no population above 31.
Widened readers need a new limit.

The AI evaluator adds wonder candidates. `0x82CB4828` and `0x82CB4834` form RNG
record `0x82F7AD00`, with divisor 4294954991 and rounded reciprocal binary64
scale. With the inputs unchanged and `0<=prefix<total<=100`, the result is a
random ordinal within the populated suffix. Excluding Settlers does not show
that another candidate exists, or that the ranges are valid for every scoring
choice.

With an empty suffix, the fallback computes `prefix`. Then `0x82CB5544` reads
outside it without a range check. Whether OCC can reach this path or crash is
not shown, but an unconditional safe fallback is ruled out. The caller accepts
`-1` at `0x82CECBBC` and `0x82CECBC0`, skipping the assignment. The native empty
flow does not use that exit. A safe change needs one of two things: a guard
before the first unsafe read together with a validated no-choice exit, or proof
that every relevant range is nonempty. A check after the return is too late.
Runtime evidence is needed to show that the turn continues without stalling.
Grants through the shared creator remain separate from construction.

The title's cost-scalar hook demonstrates typed register callbacks that run
before an instruction. Its Lua contract and hook corpus expose neither a
population policy nor callbacks at these comparisons. Locked SDK source
publishes module-launch Lua before it resumes guest main. This holds only when
the intervening callbacks return without starting guest work. It is a hook
point for publication, not an implemented OCC.

Publish one validated immutable `{enabled, R=32}` record before guest execution,
and keep it until execution stops. Both callbacks must read it and preserve all
guest state except the specified type 0 `r11` assignment. A restart without OCC
uses an explicit disabled default. This gives consistent thresholds without
tying a policy to each save. Three things still need implementation and
validation: actual registration, the identity and lifetime of the record, and
execution with the policy enabled and disabled for human and AI players. An
active-human snapshot cannot replace a shared policy.

Manual-load and finalized-save hook points can associate a fixed policy with the
namespaced identity in [Save storage](save-storage.md). Selection only at
creation remains unlinked to any save. Load function `0x82D86400` can skip
deserialization yet return locally true. Neither that result nor the serializer
hook shows that the OCC policy is restored. The exact checks and unresolved
command and dispatch edges are in
[occ-settler-production-requirements.json](../../manifests/occ-settler-production-requirements.json).

AI players can also found a city without a Settlers unit, so a Settlers rule
does not stop every AI city. In a selected AI routine, on turns where the turn
plus the player index divides by 8, a tile scan can accept an interior tile that
passes its distance, terrain and score checks. The routine then takes one
population from the nearest city the player owns and requests a new city at
`0x82CBC03C`. Its unit check searches the unit table for distance only. With no
live unit near the tile it passes, so no Settlers unit is needed. A refusal
point for OCC can sit at `0x82CBBE58`, continuing at `0x82CBC3D4`, before the
population is taken. A refusal at the city request alone would leave the
population loss and counters. This is static evidence: the route that produced
any reported AI city was not observed. See the
[AI founding finding](../../manifests/city-militia-scout-feasibility.json#/occAiFoundingBoundary).

## Normal unit production cost

`EffectiveUnitProductionCostScalar` at `0x82CF1148` starts at 10 and applies
reductions for the player, conditions, definition flags and civilization. Normal
cost is the signed factor `+0x44` times the final scalar, divided by two toward
zero.

The [scalar return boundary](../../manifests/production-cost-ownership.json#/effectiveScalar/returnBoundary)
limits its local return and stack effects. It holds only while the predicate and
lookup values stay as read. Optional bonus 5 uses the outgoing `r4` of the
index-14 predicate. Attributing bonus 5 to the player who originally owns the
city requires that `r4` to preserve that player's identity. The later
unit-specific lookup freshly reloads the city's owner. The
predicate's true arm, taken when the owner is equal and the state is outside
{0,1}, supplies that survival under its exact stack and protected-memory
conditions.

Eight signed halfwords at `0x830E9050` supply the player input. Initialization
sets all eight to `-1`, and broad serialization transfers them in both
directions. Setup `0x82D217C8` submits command 57 with the player index and an
unresolved virtual result, and case 57 stores that result in the selected
halfword. The array policy and the command name remain unknown, as do condition
`0x82CEF4E8(14)` and bonus 33.

Bonuses 5, 17 and 34 give half-cost Settlers, Riflemen and Spies. Eight sampled
factors are Warrior 2, Archer 2, Riflemen 4, Horsemen 4, Knights 5, Tank 10,
Artillery 10 and Spy 5. These are not final costs. See
[`player-production-scalar-lifecycle.json`](../../manifests/player-production-scalar-lifecycle.json).

The virtual source of command 57 `arg2` is not yet established. Ghidra covers
eight setup-entry bytes and neither instructions nor a function at `0x82D224F0`.
The recompiled code corroborates receiver `r14`, slot `+0xA0`, a return through
`r3` and `r31` to wrapper `arg2` in `r5`, and a separate receiver for nearby
`+0x100`. The native receiver is not decoded, so the object, vtable, target,
thunk, source and policy identity cannot be promoted. See
[`player-production-scalar-virtual-source.json`](../../manifests/player-production-scalar-virtual-source.json).

### Item routing and building costs

`ProductionItemCostLookup` (`0x82CE2B98`) uses the unit formula for IDs 0
through 99. `CurrentProductionItemCostLookup` (`0x82CF8308`) selects city
`+0x38` and returns the same result. Both route 100 through 299 to
`BuildingWonderProductionCostLookup` (`0x82CF1278`).

Building routing covers 100 through 199, but the `0xCC`-stride block at
`0x82F71FD8` has only 23 initialized records, IDs 100 through 122. The next
stride overlaps non-record data. The fields are name `+0x00`, token `+0x20`,
signed factor `+0x41` and description `+0x4C`. IDs 123 through 199 remain
unvalidated; see
[`building-record-identities-100-122.json`](../../manifests/building-record-identities-100-122.json).

The menu checks read signed technology `+0x42`, required building mask `+0x44`
and forbidden mask `+0x48`. All 23 records are in
[`building-menu-record-requirements.json`](../../manifests/building-menu-record-requirements.json).
The masks correspond to completion bits: Bank requires Market, Cathedral
requires Temple, and University requires Library. Bits for later buildings
hide earlier items. These local checks do not show complete availability or
effects, and do not show runtime completion.

Building half-cost branches pair Barracks 101 with UEA 19, Library 105 with
UEA 20 and Courthouse 114 with UEA 18. Cathedral 111 with UEA 21 has no
accepted retail activation. University 112 and Factory 116 have reductions that
apply under a neutral check. The early item-specific tests use a shared
word-shift mask. Initialized Wonder 229 also matches the Barracks mask, and 233
matches the Library mask and the later three-quarter subtraction. These static
aliases keep the order of arithmetic for the current cost and the limits on
retail cost composition in
[the modifier record](../../manifests/building-wonder-cost-modifier-branches.json).
Wonder 229 still requires dynamic bit two to accept it and also its full outer
check. 233 is excluded from the menu and from the city-update route with a known
vtable. See
[the eligibility record](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170).

The final wonder reduction uses `0x82FFE7C8`. In `BroadGameStateSerializer`, a
null auxiliary pointer plus mode one passes it to `BufferReadU32` as the
destination. Mode zero passes it to `BufferWriteU32` as the source. Raw words
match the recompiled paths, but Ghidra has no decoded body. The virtual targets,
external format, policy, runtime value and visible effect remain unknown.
`0x82D25330` separately tests signed less than 2 before slot `+0x80` on
receiver `0x8314F76C`, with arguments 13 and -1. Its materializer scan hit cap
32. An image word of zero establishes neither the target nor the live value.

- [Transfer open question](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0218)
- [Secondary reader](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0219)
- [Candidate search](../../manifests/building-wonder-cost-global.json#/findings/RVA-F-0215)

The building's final half reduction tests city halfword `+0x3C` bit `0x8`. The
following negative searches leave indexed, computed, out-of-function and
out-of-interval writers open:

| Search | Result | Evidence |
| --- | --- | --- |
| Direct writes | No non-stack WRITE or READ_WRITE in 272 decoded instructions inside functions; one raw D-form candidate targets another global. No split constant for `0x8314FE64` | [Writer search](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0209) |
| City-base materializers | Reproduced 31; the next eight unexamined functions had no direct non-stack write in 231 instructions | [Materializer search](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0213) |
| Remaining materializers | The other 23 functions, in four batches, had no direct stores. Total 31 functions and 1817 instructions | [Continuation](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0214) |
| Recompiled copies | All 31 have no locally resolved store to `+0x3C` or an overlapping word; the destination at `0x82E57980` could alias city state | [Computed writer](../../manifests/building-cost-city-flag.json#/findings/RVA-F-0216) |

A 128-position loop at `0x82E8AEC8` writes `0x8314F0A8` to city `+0xB8` and zero
to `+0xB0` and `+0xB4`. The meanings and consumers remain unknown. See the
[initializer symbol](../../manifests/catalogs/symbols.json).
The shared three-quarter subtraction check at `0x830E8FFE` can receive the
authored scenario three-quarter price setting (`QUARTERPRICELIB`) through the accepted
scenario-slot copy. Four points are not yet established: the actual selection,
whether the value stays unchanged, other writers, and the complete gameplay
policy. The source and the initialized mask matches are recorded in
[the modifier record](../../manifests/building-wonder-cost-modifier-branches.json#/additionalCommonBranches/0).
Limited address searches found no writer, and the consumer lies in a Ghidra
function gap; see [the source search](../../manifests/building-wonder-cost-check-sources.json).

### Building choices and completion fields

In `0x82CED700`, the Building bridge skips `k` leading negative words, then
copies a fixed temporary-array tail. The byte count is `4 * (100 - k)`, and the
returned visible count is the generator count minus `k`. The parent destination
is `+0x5DC`, and the return is stored at `+0x43C`. Neither the wrapper nor the
child loop checks a 100-entry maximum. Whether excessive native output can occur
is not shown. The
[copy boundary](../../manifests/building-option-copy-capacity.json)
establishes no safe slot for a new definition or for who holds it.

Append helper `0x822D10C0` derives size and capacity from begin, end and
capacity-end. A nonzero begin with size below capacity permits a four-byte write
and advances the end. Otherwise `0x822D1150` handles growth, allocation and
failure, and its behavior is unresolved. The
[capacity check](../../manifests/building-option-append-capacity.json) does
not validate allocation or pointer invariants.

After sufficient production, `0x82D02090` writes standard building bits,
including a bank indexed by the clamped player era. Spaceship items 119 through
122 instead set city `+0x24` bit `0x100` under a player-indexed check. Both
store the item ID at `+0x3A` and check a limited city byte list. The writes in
[`building-completion-state-writer.json`](../../manifests/building-completion-state-writer.json)
do not show the described effects or runtime execution.

The negative searches below cover decoded operands inside functions only.
Indexed, computed, aliased, indirect, out-of-function and out-of-interval
readers remain unresolved, along with uninspected materializers.

| Field or search | Coverage and result | Evidence |
| --- | --- | --- |
| `+0x24` | No non-stack READ or READ_WRITE in 272 instructions; no split-constant materializer for `0x8314FE4C` | [Flag search](../../manifests/spaceship-part-city-flag.json#/findings/RVA-F-0208) |
| `+0x24` continuation | The next eight unique city-base functions after the followed path, and the first eight others, have no direct non-stack READ or READ_WRITE in 428 instructions | [Materializers](../../manifests/spaceship-part-city-flag.json#/findings/RVA-F-0211) |
| Era bits `+0x14`, `+0x18`, `+0x1C`, `+0x20` | No reads in 272 instructions across `[0x82D00000,0x82D20000)`; 31 city-base materializers reproduced, and the first eight after `0x82CEDF90` had none in 664 instructions | [Era-bit search](../../manifests/city-era-building-bit-readers.json) |
| `+0x3A` | No READ operands in 272 instructions across `[0x82D00000,0x82D20000)` | [Stored-item search](../../manifests/city-stored-item-id-readers.json) |
| City base `0x8314FE28` | 654329 instructions produced 31 split-constant materializers below cap 64. `0x82CEDF90` reads indexed byte `+0`, then calls `0x82D038E8`, whose inspected prefix does not read that base. For the first eight other materializers, no direct `+0x3A` reads in 664 instructions | Same stored-item search |

One sufficient-production wonder path, taken only when its condition holds,
copies `+0x38` to `+0x3A`. Later behavior lies outside
[`non-unit-production-threshold.json`](../../manifests/non-unit-production-threshold.json).

The directly called city helper tests Courthouse index 14 in `+0x10`. It selects
eight adjacent candidates, or twenty with a second ring. This
[`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json)
does not identify worked tiles. Other building-bit tests add half of an
intermediate register back into itself. They cover Barracks 101, Granary 102,
Temple 103, Workshop 106, Market 104 or Library 105, and Bank 110 or University
112. Each paired mask updates only once. One branch uses adjusted food,
production and trade weights in candidate scoring, and another replaces them.
After validation, city `+0x58` plus the local index receives a selected or
replacement byte, including `-1`.

`sub_82CE1C10` counts the entries below positive signed city `+0x03` that are
not `0xFF`. It returns the limit minus that count, which is the `0xFF` count. It
also groups the interval from the non-`0xFF` count up to the limit into sixes in
the caller's output. A caller compares eight output words with a cache, which
decides whether a helper runs and the cache refreshes. The candidate values and
sentinel positions are discarded. Changing them without changing the count or
the limit cannot affect those words. Tile assignment, gameplay meaning, visible
effect and runtime invocation are not yet established.

- [Bit arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json)
- [Weighted score](../../manifests/building-bit-selection.json#/findings/RVA-F-0202)
- [City byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203)
- [Consumer search](../../manifests/building-bit-selection.json#/findings/RVA-F-0204)

The intervening helper derives four target counts from a stored row and
selector, counts pointer-vector tags under range guards, and calls helpers for
signed differences. One call can update receiver words. The required calls and
the dispatch with no known target prevent linking its return to the cache
refresh. The row and city identity, the resource policy and the yield effects
remain unknown. Handling of a matched entry selects one outer index or skips it,
and a fixed zero bypasses the optional append. The clears of the local array and
object are tied to this path.

Empty regions and guarded zero per-cell fields restore the caller's pointer and
stack. Nonzero fields can require another helper or a dispatch with no known
target. The restoration does not show that the fields stay unchanged or how long
they live. An earlier updater requires a nonzero flag, and its zero-pointer arm
sets flag one without creating a pointer. Earlier consumers and unresolved calls
prevent choosing the later branch.

The earlier candidate replaces `+0x704`, `+0x708` and `+0x70C`. The function
that calls it passes the table word as argument two and stores it at `+0x700`.
The predicate lookup has no calls or stores and preserves `r5`, the stack and
standard memory. Returning zero uses the original receiver for the fallback. A
clear bit supplies a third guarded path that keeps unknown old-slot values. The
actual slots and targets, and the effects of predicate-one initialization,
remain unresolved.

Size 864 reaches the generic fallback after its prefix returns. Guarded writes
for global initialization, errors and manager-prefix metadata are tied to this
path. Image zeros do not identify the live prefix or context. Limited searches
for references and direct stores leave the producer and order unresolved, so no
descendant is selected. Imports and the full return are not yet established, and
neither is survival of the input object and its fields, the frames and the old slots,
despite register restoration. See the
[helper boundary](../../manifests/building-bit-selection.json#/findings/RVA-F-0204/groupedOutputConsumer).
Nearby `sub_82D019F0` has 18 `lbzx` candidates, none linked to the city pointer.
The earlier 21, 8 and 13 filter cannot be recovered from tracked evidence. This
census excludes no readers outside that function.

### Wonder costs and consumer limits

IDs 200 through 299 route to signed factor `+0x40` in `0x14C`-stride wonder
records at `0x82F73238`. The common signed half-scale applies first. Then
cumulative UEA 24 applies another half, so Wonders cost half as much. The common
scale is not UEA 24.

The 37 initialized records cover 200 through 236. The fields are name `+0x00`,
factor `+0x40`, short token `+0x4A`, art token `+0x8A` and description `+0xCA`.
The identity manifests keep the byte boundaries and the unnamed halfword
`+0x42`. The next twelve stride positions are zero, followed by non-wonder data.
Neither this nor the cost routing shows that an ID is valid throughout the
program.

Ghidra returned no exact-start references for 217 building and wonder text
fields. Indexed, indirect, computed, interior-string and undecoded readers
remain open. `0x82CF0268` has no decoded register-relative `+0x42`, `+0x4A`,
`+0x8A` or `+0xCA` operand. Scaled, indexed and other readers remain open.
Choice tail `0x82E41538` calls `0x827F7C8C`, whose one-byte body has no
instruction and whose references truncate at 64. It adds no reader evidence. See
[text census](../../manifests/building-wonder-text-field-reference.json)
and [consumer search](../../manifests/building-wonder-consumers.json).

| Consumer evidence | Finding and remaining limit |
|---|---|
| [Factor accumulation](../../manifests/wonder-factor.json#/findings/RVA-F-0197) | Reads `+0x40` and adds derived values to global and stack accumulators, indexed by the claiming player. |
| [Output and reader search](../../manifests/wonder-factor.json#/findings/RVA-F-0217) | After collection, `0x82CB379C` reads the stack accumulator. One arm converts the signed word to float, divides by signed stack `r25`, and writes single precision at `0x830E8DD0` plus 64 per iteration. Two reads use indices scaled by 64 and by four, which does not show that anything consumes the writer's `+0`. The role of the global and its effect on cost remain unknown. |
| [Reader census](../../manifests/wonder-factor.json#/findings/RVA-F-0198) | Eight-word copy `0x830ECCC8` -> `0x831228E4`. Three object reads could reach copied words with particular low-30-bit indices, but the selectors depend on data. The actual read, later use and effect on cost remain unknown. |
| [Index sources](../../manifests/wonder-copy-index.json#/findings/RVA-F-0199) | Selectors include the pointee of incoming-object `+0x434` and an unresolved virtual result. The ranges are not yet established. |
| [Writer check](../../manifests/wonder-copy-index.json#/findings/RVA-F-0200) | The reader's function table links to an initializer that clears `+0x434`. An initializer for a different table stores a pointer there, with no shown shared object or live writer. Image zeros establish no index or read. Two direct initializer callers share a function with an indexed read, and their next method has no direct `+0x434` store. No live link from the factor to cost is shown. |

The enclosing caller is singleton vtable `0x82138768` slot `+0xC8`. Indirect call
`0x828AA8FC` loads its receiver from another object's `+0x18`, which is not
linked to the singleton. The live caller and the gameplay trigger are not yet
established.

The identity records cover the full initialized range:

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

Also see the limited search in
[`wonder-records.json#/findings/RVA-F-0165`](../../manifests/wonder-records.json#/findings/RVA-F-0165).

## Building and wonder record contract

The table below lists assigned definition fields.

Exact values for each ID live in:

- The [`building-record-identities-100-122.json`](../../manifests/building-record-identities-100-122.json)
- The [`building-menu-record-requirements.json`](../../manifests/building-menu-record-requirements.json)
- The [wonder identities](../../manifests/wonder-records.json#/findings/RVA-F-0096) and their linked continuation records
- The [`wonder-outer-check-record-fields.json`](../../manifests/wonder-outer-check-record-fields.json)

No runtime probe has recorded an individual definition-field value or observed
execution of a described effect. The recorded sessions establish some menu and
production-item behavior, not these field values or effects.

| Record field | Static meaning | Remaining unknown |
|---|---|---|
| Building `+0x00` | Stored name text in IDs 100-122 | Text reader, localization, and display |
| Building `+0x20` | Stored token text | Token consumer and asset link |
| Building `+0x41` | Signed byte factor read by the non-unit cost helper | Final cost for a live player and all caller paths |
| Building `+0x42` | Signed technology ID checked by the city-menu query about the technology's owner; `-1` skips that query | Complete rule for accepting the item and the live result |
| Building `+0x44` | Required city building-bit mask; a nonzero mask needs at least one matching bit | Other city-bit writers and complete policy |
| Building `+0x48` | Forbidden city building-bit mask; a matching bit rejects the menu candidate | Other city-bit writers and complete policy |
| Building `+0x4C` | Stored English description | Display reader and implemented gameplay effect |
| Wonder `+0x00` | Stored name text in IDs 200-236 | Text reader, localization, and display |
| Wonder `+0x40` | Signed halfword factor read by the non-unit cost helper | Final cost for a live player and all caller paths |
| Wonder `+0x42` | Stored halfword; exact exposed values are recorded for 220, 223, and 236 | Writer, reader, and meaning |
| Wonder `+0x44`, `+0x46` | Signed technology IDs or `-1` sentinels checked by the generic outer check | Full eligibility and special-index 19 and 20 use; those indices bypass these generic reads |
| Wonder `+0x48` | Signed technology ID or `-1`; the generic check tests other-player ownership | Full eligibility and special-index 19 and 20 use; those indices bypass this generic read |
| Wonder `+0x4A` | Stored short token | Token consumer and display role |
| Wonder `+0x8A` | Stored art token, often repeated across records | Asset consumer and art link |
| Wonder `+0xCA` | Stored English effect description | Display reader and implemented gameplay effect |

Generic `TechnologyAcquire` calls one other static consumer, `0x82CEA5A0`, with
its technology ID. That function compares the ID with building `+0x42` and
wonder `+0x44` while forming a local list. Its wonder loop spans 33 positions;
the list's downstream meaning remains unresolved. See the
[technology-field match](../../manifests/definition-technology-match-list.json).
A separate
[list with its own condition](../../manifests/definition-technology-conditional-list.json)
reads building `+0x42` and wonder `+0x44` and `+0x46`. Its wonder path compares
the two technology IDs with a selected value and can query ownership of the
other field.

Its two direct callers pass a selector computed as the item minus 600 from the
preview helper, or an indexed byte from another function. Its list output and
runtime use remain unresolved.

These are partial layouts, with no supported meaning for unlisted bytes.
Editing a known signed factor can change the supported static cost calculation
for an initialized ID, subject to later modifiers. It does not establish a final
in-game price. Building menu masks and wonder technology cells are known inputs
to local checks, not a complete buildability policy.

Repeated or mismatched tokens do not identify assets. The initialized record
blocks cover IDs 100-122 and 200-236. The helper's broader routing of 100-199
and 200-299 cannot be used as a contract for extending the table with arbitrary
IDs.

### Item selection and acceptance

The
[`production-item-writers.json`](../../manifests/production-item-writers.json)
found no selection or validity rule within its recorded limits. A runtime write
observer found command five storing its item into city `+0x38`, for a city whose
owner matches the command, at `0x82CE0020`, without an ID check. Cost preview
separately writes candidate IDs temporarily and restores the prior item; see the
[`city-production.json#/findings/RVA-F-0183`](../../manifests/city-production.json#/findings/RVA-F-0183).

City choice handler `0x82E02CE0` calls producer `0x82CEE650` for units,
buildings and wonders. It forwards the selected ID without a local limit and can
drain at `0x82CEE76C`. A Barracks session logged no type-five call at separate
submit `0x82CE1950`. A census of 27 direct drain calls, each checked within
0x100 bytes for literal five, found no second producer.

The separate census found all 100 submit calls. The city-list generator calls
`0x82CB42B8` twice and submits five at `0x82CB44D0`. One branch adds 200 to an
ordinal from 33 wonder slots, yielding 200 through 232 only if the indirect
chooser returns a valid row. Initialized chooser dispatch reaches a dialog. Its
callback parses a decimal row into `+0x470`, and the content update afterward
checks that value against a count of 16-byte entries. Return writer `0x82E0551C`
copies `+0x470` to `+0x42C` without that check. Five points remain unknown: the
source of the callback string, the live rows, runtime execution, indirect routes
and earlier construction. No unconditional limit on submission follows. See the
[`city-production.json#/findings/RVA-F-0188`](../../manifests/city-production.json#/findings/RVA-F-0188).

Seven direct generator callers use mode 2 (building), 1 (unit) or -1 (AI, city
update or turn). Wonder marker `-12` requires bit `0x2`, which excludes mode 1.
The mode and the eligible slots alone do not select it. No runtime call through
`0x82CECC98` has been observed in a wonder selection, so whether the game
invokes this path is unresolved
([city production](../../manifests/city-production.json#/findings/RVA-F-0188)). End register `r30` relative to `r15-3808` gives the
populated count, and `r31` counts all 33 slots.

The choice child copies nonnegative IDs from separate parent arrays and checks
the vector index before forwarding. Its wonder generator tests normalized 0
through 32 (IDs 200 through 232), and mutable claims and eligibility decide
membership. Initialized IDs 233 through 236 are excluded. Reset fills 33 claims
with -1, and mode-one completion writes the player and city index.

With vtable `0x82138768` at `0x8314F76C`, the inner city check returns zero for
indices 33 through 36 (IDs 233 through 236). The virtual target rejects them,
and the fallback accepts only below 21. This
[`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170)
is neither runtime evidence for those IDs nor a rule for validity throughout the
program. One live menu pass observed both words -1 in all 33 slots and nonzero
eligibility for 2, 8, 11, 12 and 14 through 18; see
[`wonder-claim-slot-state.json`](../../manifests/wonder-claim-slot-state.json).

Building enumeration uses a live count that is initialized to 23, appending the
index plus 100 (IDs 100 through 122). Availability, later changes to the count
and whether the Barracks session took the branch remain unknown. See
[`city-production.json#/findings/RVA-F-0184`](../../manifests/city-production.json#/findings/RVA-F-0184)
and
[`city-production.json#/findings/RVA-F-0185`](../../manifests/city-production.json#/findings/RVA-F-0185).

Completion also checks and fills a 28-byte ordinal list at `+0x87..+0xA2`. The
exact recompiled window of the building loop reads city `+0` and `+0x10`, not
list bytes. Ghidra's direct-field query covered zero decoded instructions. The
callees and other readers remain open, and no runtime list filter was observed.
See the
[`building completion-list reader search`](../../manifests/building-completion-list-menu-readers.json).

### Post-threshold effect branches

Descriptions do not show that their stated effects are implemented. The five
direct mode-one indices in `0x82D16BA0` have these static contracts. Runtime
effects remain unobserved:

| Item | Branch and limit | Evidence |
| --- | --- | --- |
| Hanging Gardens 202 | City `+0x03` = `clamp(trunc((3*x+1)/2),0,31)`, then two helpers; no proof of persistent doubled growth | [`hanging-gardens-population-branch.json`](../../manifests/hanging-gardens-population-branch.json) |
| Oxford University 208 | Filters 48 technologies, ranks them with an unresolved score helper, and can request acquisition of the chosen one; the selected ID and success are unknown | [`oxford-technology-acquisition-branch.json`](../../manifests/oxford-technology-acquisition-branch.json) |
| Statue of Liberty 227 | Scans 128 cities and adds two to `+0x03`, clamped to 31, for populated cities of the source player; persistence unknown | [`statue-of-liberty-population-branch.json`](../../manifests/statue-of-liberty-population-branch.json) |
| Great Wall 201 | Filtered symmetric writes for player pairs; the consumer and the peace-offer meaning are unknown | [`great-wall-player-pair.json#/findings/RVA-F-0177`](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0177) |
| Leonardo's Workshop 211 | Compares definition halfwords and technology ownership, and can replace live `+0x01`; the virtual calls and limited coverage rule out universal upgrades | [`leonardo-unit-type-branch.json`](../../manifests/leonardo-unit-type-branch.json) |

Great Wall base `0x830ED1D8` has no exact references and no decoded split
constants in the
[limited search](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0207).
Derived, indexed, computed, aliased and indirect readers remain open. Mode one
skips the later tail, and separate mode-two items 219 and 220 can enter it; see
[`wonder-post-threshold-helper.json`](../../manifests/wonder-post-threshold-helper.json).

Mode-two terminal indices 19 and 20 clear two bits and set `0x10000` in
`0x82FFE7C4`. An exact-base scan found no decoded materializers, which excludes
neither displacement nor derived accesses. Three snapshot functions copy the
whole word to output `+0x200`. Entry-reference counts and an aligned direct-BL
scan across initialized executable memory were zero. The provenance of the
output, the consumer of the bits and the victory meaning remain unknown. The
flow that matches the player also updates `0x830EF348 + 2*index`; no decoded
split constant or field meaning was found. See
[`wonder-mode-two.json#/findings/RVA-F-0179`](../../manifests/wonder-mode-two.json#/findings/RVA-F-0179).

Immediate `+0xD0` does not directly read that counter. A nonzero `0x82FFD688`
pointer selects a direct tail target, and its identity and provenance are
unknown. See
[counter search](../../manifests/wonder-mode-two.json#/findings/RVA-F-0210).
Text and art consumers, full layouts, final costs and most effects remain open.
The cost inputs are in
[`building-wonder-cost-identities.json`](../../manifests/building-wonder-cost-identities.json).

## Effect coverage by ID

Descriptions do not show effects. Runtime observations cover choice,
eligibility and item state, not gameplay-effect execution:

| IDs | Static evidence | Runtime effect execution |
|---|---|---|
| Wonders 201, 202, 208, 211, 227 | Item-specific branches exist in the direct mode-one helper. Their local writes and calls are mapped in the [`wonder-post-threshold-helper.json`](../../manifests/wonder-post-threshold-helper.json) and [`great-wall-player-pair.json#/findings/RVA-F-0177`](../../manifests/great-wall-player-pair.json#/findings/RVA-F-0177), [`hanging-gardens-population-branch.json`](../../manifests/hanging-gardens-population-branch.json), [`oxford-technology-acquisition-branch.json`](../../manifests/oxford-technology-acquisition-branch.json), [`leonardo-unit-type-branch.json`](../../manifests/leonardo-unit-type-branch.json), and [`statue-of-liberty-population-branch.json`](../../manifests/statue-of-liberty-population-branch.json). | Not observed |
| Wonders 219-220 | A mode-two path, taken only under its own condition, writes shared status bits and a halfword. Their meanings and downstream consumers remain unknown. See [`wonder-mode-two.json#/findings/RVA-F-0179`](../../manifests/wonder-mode-two.json#/findings/RVA-F-0179). | Not observed |
| Building 114 | The Courthouse bit selects a scan of eight or twenty coordinate candidates. One later path stores a selected or replacement ordinal byte at city `+0x58` plus a local index. The visible effect is unknown. See [`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json) and [city byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203). | Not observed |
| Buildings 101-106, 110, 112 | A direct post-completion city helper tests their presence bits and can change local weights on food, production, and trade component returns. A later path can store a selected or replacement ordinal byte at city `+0x58` plus a local index. The final city effect is unknown. See [bit arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json), [weighted score](../../manifests/building-bit-selection.json#/findings/RVA-F-0202), and [city byte store](../../manifests/building-bit-selection.json#/findings/RVA-F-0203). | Not observed |
| Wonders 200, 206, 207, 209 | Limited searches found no exact edge for the described effect within each record's stated scope: [`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json), [`great-library-technology-transfer.json`](../../manifests/great-library-technology-transfer.json), [`east-india-sea-trade.json`](../../manifests/east-india-sea-trade.json), and [`shakespeare-city-culture.json`](../../manifests/shakespeare-city-culture.json). These are negatives within those limits, not proof that no effect exists. | Not observed |
| Wonders 203-205, 210, 212-218, 221-226, 228-232 | These IDs normalize into the helper's accepted 0-32 range on the direct city-update callsite but do not match one of its five explicit mode-one branches. This limits only that helper path; other consumers remain possible. See the [`wonder-post-threshold-helper.json`](../../manifests/wonder-post-threshold-helper.json). | Not observed |
| Wonders 233-236 | Normalized indices 33-36 branch away before the direct post-threshold helper body. The known vtable's earlier check also rejects them on this path; other receiver states and paths remain unresolved. See the [`wonder-post-threshold-helper.json`](../../manifests/wonder-post-threshold-helper.json) and [`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170). | Not observed |
| Buildings 100, 107-109, 111, 113, 115-122 | Stored descriptions are present, but no item-specific effect branch and no per-item negative search is recorded here. The [consumer search](../../manifests/building-wonder-consumers.json) does not exclude indexed or indirect readers. | Not observed |

Barracks 101 has no demonstrated link to the creation-record veteran bit. A raw
displacement scan found no +0x3C store in
[0x82D13978,0x82D16BA0), which leaves computed, indexed and other writers open.
Ghidra covers only 8 bytes at 0x82D13978 and has no function or instructions at
0x82D15B84. The modded veteran acceptance test did not cover Barracks.
See [link scan](../../manifests/barracks-veteran-creation-record-link.json).

One fresh-game wonder check dispatched `+0x1E4` -> `0x82D80C30` for
0 through 32, and all logged returns were zero. Indices 21 through 32 can return
one only for corresponding bits among three from `+0x1DC`.
Getter `0x82D7D2A8` reads frontend `+0x08`, which is forced to zero for state 4
through 6. The generic check queries signed technology `+0x44` and `+0x46` (or
`-1`), and queries other-player ownership for `+0x48`. The record fields for IDs
200 through 236 are in
[`wonder-outer-check-record-fields.json`](../../manifests/wonder-outer-check-record-fields.json).
Indices 19 and 20 use [`wonder-outer-check-special-19-20.json`](../../manifests/wonder-outer-check-special-19-20.json).

All 60 direct frontend-pointer-reference functions yielded no demonstrated write
to root `+0x08`. The
[census](../../manifests/wonder-eligibility.json#/findings/RVA-F-0192) excludes
neither indirect nor constructor paths. The base constructor zeros it before
`0x82FFD624` publishes it
([initialization](../../manifests/frontend-root-publication-mask-init.json)).
The function at `+0x80` can pass a nonzero `+0x08` to `NtClose`, then clear it.
The [vtable review](../../manifests/frontend-root-vtable-offset8-clear.json)
leaves the producer and kind unknown. Bit meanings, other targets, the functions
for special states, and runtime eligibility and effects remain open:
[`wonder-eligibility.json#/findings/RVA-F-0170`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0170),
[`wonder-eligibility.json#/findings/RVA-F-0171`](../../manifests/wonder-eligibility.json#/findings/RVA-F-0171).

These effect searches show only their stated negatives:

| Item | Search result and remaining limit |
| --- | --- |
| Pyramids 200 | No edge for government, state, completion, display or AI. The record-base materializer, the technology-table materializer and the shared helper all truncated. A filtered scan for literals and comparisons hit the eight-function cap, which leaves them unclassified. [`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json) |
| Great Library 206 | Direct, split and literal searches found no effect edge. Later eligibility reads technology IDs 8 and 21, which shows no transfer, acquisition, completion, display or AI behavior. [`great-library-technology-transfer.json`](../../manifests/great-library-technology-transfer.json) |
| East India Company 207 | No edge for sea trade, economy, completion, display or AI, and no direct or split match for the record, description or cost. The complete filtered scan emitted only `0x82500288`, where `0xCF` is packed D3D decoding, not a wonder identity. Generic terrain yield remains open. [`east-india-sea-trade.json`](../../manifests/east-india-sea-trade.json) |
| Shakespeare 209 | No edge for culture, completion, display or AI, and no direct or split match for the record, description or cost. The complete filtered scan emitted `0x826CFDC8`; its prefix has no Shakespeare or culture carrier, and its body truncates. [`shakespeare-city-culture.json`](../../manifests/shakespeare-city-culture.json) |

Cost consumers are as follows. `RushCostCompute` (`0x82CE27F0`) subtracts city
`+0x36` before the rush arithmetic. Display `0x82DFFE38` uses the current cost
and the `+0x36` and `+0x42` percentages. `0x82D13978` branches away below cost.
`AIUnitChoiceEvaluate` and `AITurnUnitEvaluation` read `+0x44` and the shared
scalar. The selected `AITurnUnitEvaluation` unit arm uses the signed normal cost
as a Gold prerequisite before a command-type 6 call, and a reserve equal to the
cost passes. The cost register is overwritten before submission, and no local
debit or completed action follows. The
[cost manifest](../../manifests/production-cost-ownership.json) holds the
qualifications on the input, the byte check, whether values stay unchanged, and
the arithmetic. This covers rush display, one completion threshold and a local
AI prerequisite. General AI decisions and corrected-rush parity are not yet
established. No runtime production test occurred.

For a delivered command with amount zero whose state is preserved, the selected
native unit consumer writes back the loaded production and Gold values. It still
reaches update calls and a later city flag store, so it need not leave all state
unchanged. The [zero-amount boundary](../../manifests/rush-cost-producer.json#/commandPath/zeroAmountUnitBoundary)
holds the guards on the player and item, the rate, the helper return and whether
values stay unchanged. No natural AI transaction or completed production is
established.

See also [gameplay cost arithmetic](gameplay-cost-arithmetic.md) for worked
rush, AI valuation and rounding examples.

The same `0x82D13978` routes signed current item `+0x38` >=100 to
`BuildingWonderProductionCostLookup`. IDs 100 through 199 compare signed
invested production `+0x36` against cost, branch away below cost, and on the
sufficient path first store invested minus cost. IDs 200 through 299 repeat the
call, keep the cost and compare likewise. After two additional neutral checks,
their first promoted stores subtract cost at `+0x36`, copy the current item to
`+0x3A`, and mask word `+0x24` with `0xFFFFFBFF`.

No independent item<300 guard appears in the limited evidence. These ranges
depend on the accepted current-item domain, not on validation of arbitrary IDs.
The neutral first writes do not show any of these: building or wonder
completion, effects, queue advancement, overflow handling, creation,
notification, runtime behavior or implementation safety. The exact addresses
and stops are in
[`non-unit-production-threshold.json`](../../manifests/non-unit-production-threshold.json).

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
come from record-local text at `+0x20`, one for each of the hot, temperate and
cold barbarian types. The table above renders the underscores in that text as
spaces.

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
Army and Keshik Army. The unit-name text resource supplies all 128 entries.

These UUs do not create new unit-definition records. Roman Cataphracts keep
Knights type 13, and Mongolian Keshiks keep Horsemen type 12. The mapping
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

This does not show that every AI path handles a Unique Unit modification
the same way as combat. Costs, movement, abilities, flags, production weights,
and naval or air special behavior each need their own mapping of producers and
consumers before mutation.

## Local AI candidate choice

In the no-alternative path of `AITurnUnitFilter`, signed defense >= attack for
the same player and type (stable across loads) enables two +8 threshold
additions: unit `+0xC` bit `0x10` and indexed halfword bit `0x40`. The table's
terrain and coordinate meaning is unknown.

A later candidate replaces the ordinal and threshold only for a strictly greater
signed score. Equality keeps the ordinal. Another loop short circuit can select
without that comparison, though a normal exit bypasses it. A later predicate
with unnamed byte-table and flag meanings can discard the ordinal and clear the
queued destination. If a path bypasses that predicate and an opaque helper, the
ordinal reaches original unit `+0x20`. Ordinals 0 through 7 also encode a
numeric caller-output code without changing the ordinal. Another selection route
writes the same field.

Caller `TurnSelectionUpdate` supplies frame `+0x7C`. A guarded return carries
the code to `0x82D2A718`, which decodes the original ordinal into r20. The
publisher's clear and other overwrites by callers make this hold only under
conditions. Move command 17 at `0x82D2CE00` uses r20 as the step. A player
reload must preserve the identity. The zero-result route below keeps the
original unit, while other entries need their own provenance. Executed movement
is not yet established.

| Check or continuation | Contract |
| --- | --- |
| Candidate position | Positive signed movement budget; unit coordinates plus the decoded ordinal, and a signed horizontal remainder. `0x82CF0268` seeds a bounds Boolean, then may clear it through indexed cells and definition flags. Failed bounds do not skip reads; valid memory is still required and the meanings are unnamed. |
| Override | A zero result can be overridden by target bit `0x4` plus an indexed signed byte that matches an unidentified saved scalar. With the following bit `0x1` clear, zero clears the original queued destination and exits. Nonzero resets a fixed global, clears r22 and searches for units at the candidate position. |
| No eligible unit | A definition-flag branch carries the original unit and coordinates into `0x82CB2430`. Its Boolean uses definition flags, original and candidate position bytes, halfwords and a matrix entry. `0x80000` forces zero, and `0x80` adds byte equality. Meanings remain unknown. |
| Zero helper result | No memory or nonvolatile writes; it bypasses the selected-unit reload, keeping the original index and r22=0. A stable player reload and memory guards permit writes of a global flag and an original-unit flag, then `0x82D038E8` at `0x82D2CDE0`. |
| Before Move | The helper updates another fixed global, may use eight stack bytes, and preserves the index and ordinal. Normal completion and separate stack storage reach Move without another branch or call, supplying the original player, unit and step. |
| Submission | With global bit `0x400` clear, it stages a five-word stack record. When set, it invokes a helper first. A null child preserves the arguments, and a nonnull dispatch has no known receiver or target. The flag's meaning remains unknown. |

Publication, delivery, dispatch, movement and compass mapping are not yet
established. Effective stats and +8 adjustments are possible controls, but
predicting behavior needs two proofs: the complete score, and that the
stat-adjusted threshold stays unchanged. See the
[AI choice manifest](../../manifests/ai-stat-choice.json).

## Additional count and model consumers

The
[count and model continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/countAndModelContinuation)
ties eight definition-base producers to four live-count walks. In total, 4,560
instruction comments matched native operands, and 37 data words confirmed the
complete image record of Militia (type 7). The 19 raw rows resolve to eight base
pairs, four count pairs and seven spurious pairs with overwritten high
registers.

| Function | What a relocation must change |
| --- | --- |
| `0x82CE77D8` | Retarget B at `0x82CE7A98` and `0x82CE7AA0`. A signed +0x4A match and a positive input that stays unchanged control the live-count tagged type and name output. |
| `0x82CEA5A0` | Retarget B at `0x82CEAB64` and `0x82CEAB70`. A signed +0x4A match drives the live-count tagged list. Literal helper argument 39 is not definition capacity. |
| `0x82D09208` | Retarget B at `0x82D0959C` and `0x82D095AC`, before frame +0x88 caching. Candidate +0x4A and source +0x4C match the incoming technology, and the loaded player-state word equals 4. There is no local exclusion of a nonzero match. |
| `0x82D16BA0` | Retarget B at `0x82D16C70` and `0x82D16C88`, before frame +0x80 caching. Leonardo's source +0x4C and candidate +0x4A must match with a nonzero value, and the technology must be owned. |
| `0x82D99CE8` | Retarget B at `0x82D99D1C` and `0x82D99D24`. Cached +0x48 model bits feed six additional child positions. |
| `0x82D99EB8` | Retarget B at `0x82D99EC8` and `0x82D99ED0`. Three +0x48 model bits feed child allocation, current dispatch, and vector and manager work. The 192-byte allocation is an object. |
| `0x82D9A320` | Retarget B at `0x82D9A374` and `0x82D9A378`. The +0x50 flags combine with live rank and upgrade bits in one selector arm. |
| `0x82D9A9E8` | Retarget B at `0x82D9AB08` and `0x82D9AB0C`. The +0x50 mask 0x4 controls one appearance parameter of the current object. |

Militia (type 7) has attack 0, defense, movement and cost factor 1, byte
+0x48=7, signed halfwords +0x4A and +0x4C equal to zero, and word +0x50=0x20.
Unchanged copies preserve these model inputs and miss Leonardo's nonzero-match
path. Separate technology acquisition can reach a copied Scout with technology
zero, player-state word 4, live-unit filters and an action bit. Reachability,
and whether the callbacks stay unchanged, hold only under their conditions. This
is not Leonardo's exclusion.

The record's stored name text at +0, asset token at +0x20 and two further text
fields at +0x54 and +0x74 show no localized Scout names, icons or assets. Factor
1 shows no absolute five-hammer cost. Five requirements remain: the live
definition stays unchanged, base, count and alias coverage is complete, the
output has capacity, child registration and lifetime are sound, and saves,
network and new IDs accept the change. Shared manifest navigation leads to the
next limited census.

## Description, derived-stat and ranking consumers

The
[next consumer continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/descriptionAndStatContinuation)
adds five B producers: `0x821BB120`, `0x821BE8B0`, `0x821BEA28`, `0x82CB2430`
and `0x82CB2E48`. All 2,332 instructions matched native operands. Five other
pairings were spurious, and one crossed two selected functions.

The description helper passes the complete indexed record to `0x821B1500`. The
copy, alias and name semantics remain unresolved. Fixed 31 through 37 dispatch
requires flags mask 0x80, and copied Militia flags 0x20 take the generic arm.
Two derived-stat helpers combine model masks 1, 2, 4 with a live-unit halfword
before effective attack and defense calls. Whether the float stays unchanged
remains a requirement. An AI candidate leaf reads flags 0x80000 and 0x80.
Ranking caches B in r16 and aggregates raw cost factors over live records, which
is not shown to be effective production cost.

Copied Militia prerequisite +0x4A=zero fails normal trainability. The ownership
query must return nonzero, but its exact zero-input arm returns zero, assuming
the live fields and inputs stay unchanged. Scout needs an eligibility override
alongside the name, cost and effects. -1 at +0x4A bypasses that first check,
but copied +0x4E=24 and other conditions still apply. Changing +0x4A also
reopens the candidate-side Leonardo exclusion, and the proof for unchanged zero
no longer applies. The continuation records the exact retargets and checks.

## Additional-definition names, models and cost

The
[name, model and cost continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/nameIdentityModelCostContinuation)
verified 486 instructions in eight helpers, adding B readers `0x82CF1148` and
`0x82CF8308`. Names load pointer `0x8314F188` and then add 12*identity, so the
names are not an inline array. Type 38 maps to 38, and to army 102, in the
existing presentation space. Scout needs a separate route that preserves those
identities.

`0x82D9B6E0` stores the name pointer at +132 and the component at +136, so
relocated names must live as long as the model uses them. The allocation tag is
not a model token. Assets, icons, and the lifetime of the child objects remain
unresolved, as does who holds them. Two adapters pass lengths and pointers to
`0x82D3B798`, and its copy and alias behavior is not yet established.

The signed +0x44 factor times the final scalar, divided by 2, truncates toward
zero. Factor 1 and scalar 10 or 11 yield 5. A Scout scalar of 10 must reach
every cost consumer after the native and host modifiers. The composition for
the current item is tied to this path, and the cost topic covers display, AI,
rush and completion. Shared delivery, override order and trainability remain
separate. The raw census stays open. `0x82CB44E0` and `0x82CB6E48` lack
following physical headers, so fresh reads of the recompiled copies stay closed
and the qualified native cost evidence is reused.

## AI and city consumer continuation

The
[AI and city continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/aiAndCityConsumerContinuation)
classifies eight further B producers after 7,829 native and source instruction
matches. `0x82CBF570` saves B at frame +0x5C, then reloads it for later attack,
defense and flags reads after reusing the original register.

Relocation must reach that frame save and all derived pointers. Other selected
paths read attack and defense, flags, technology, an unnamed +0x43 byte and the
model mask.

Copied Militia attack 0 excludes the selected candidates in `0x82CB3DC0`,
`0x82CC6D10` and `0x82CC75B8`. Other paths accept copied flags 0x20 at their
particular masks. These are inherited local filters. Neither result shows that
the item enters the build list, that the AI prefers it globally, or that an
action is delivered.

The 256 unit records, 128 city records and the local selector and component
limits remain separate from definition count 39. The 29-entry public catalog is
another namespace and does not exclude native special rows 29 through 37.

The continuation records the exact producers, the field and cached-pointer
locators, and the remaining requirements on returns, aliases and lifetime. It
also keeps five EOF candidates for native-only linking or for reuse of accepted
evidence. The global census remains open.

## Movement, selection and rush consumers

The
[movement, selection and rush continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/movementSelectionAndRushContinuation)
verified 4,188 native and source instruction operands and classified eight more
inline B producers, plus two spurious raw pairings. `0x82CD7A60` saves B at
frame +0x80 and later reloads it for flags and defense.

Retarget before that save. `0x82CD77E8` reads definition movement +0x42 and
writes its tripled value into a unit record. The complete order of March and the
movement refresh remains open. `0x82CE27F0` consumes factor +0x44 before
separate rush and display arithmetic, so factor 1 alone does not establish an
absolute hammer or gold cost.

The remaining four functions tie in selection filters and later presentation
calls. Copied flags 0x20 clear their selected masks, while other conditions on
live units, coordinates and callbacks remain. Keep the 256 instance records and
the separate context-index scale 38 distinct from definition count 39. The
global census, coherent storage and acceptance of new IDs remain open.

## Production, inline names and upgrade requirements

The
[selected continuation](../../manifests/unit-definition-base.json#/findings/RVA-F-0277/productionNameAndUpgradeContinuation)
verified 2,557 native and source instruction operands across eight more B
producers.

It ties in further factor and stat reads, the +0x4A fields of fixed rows 10 and
13, an inline-name builder with persistent output at `0x82FFD7C0`, and an
upgrade eligibility check that counts all low 16 upgrade bits against six. The
exact flag branches and the host research-prompt hook keep their recorded
qualifications. These are local consumer findings, with no global extension and
no runtime claim.

Scout uses Militia appearance as a placeholder. The
[minimum title support contract](../../manifests/city-militia-scout-feasibility.json#/minimumScoutSupportBoundary)
keeps its logical identity, trainability, absolute cost and creation effects
separate from Militia.

The exhaustive native census is incomplete. Neither a relocated 39-record table
nor a logical variant backed by Militia is accepted as an existing safe
registration path.

## Combat stat-role boundary

The accepted path for one unit against another contains one exact ordered pair
of stat calls inside `CombatResolve`:

| Derived role | Callsite | Player and type input | Result |
|---|---:|---|---|
| Attack side | `0x82CDA214` | Accepted attacker player and unit-record type | Effective attack kept separately |
| Defense side | `0x82CDA234` | Accepted defender player and unit-record type | Effective defense kept separately |

Attack is obtained before defense. The two-value role is derived from these
callsites; it is not a stored guest enum. The shared accessors themselves take
only the player and base `UnitType` before establishing their base scalar, so
they do not carry an opposing unit or a combat-role argument.

`CombatResolve` contains six other effective-stat calls, including a separate
literal-25 special branch immediately after the core pair. Those calls do not
inherit the attack-side or defense-side meaning, and this result does not show
an opposing class predicate or city, naval, or air equivalence.

Limited windows in the three mapped AI evaluators confirm that they consume the
scalars but not that they use the same roles. `AIUnitChoiceEvaluate` adds attack
and defense for the same player and type. `AITurnUnitEvaluation` multiplies
candidate stat results under a condition. `AITurnUnitFilter` compares defense
and attack under one player with separately sourced types.

None of those scalar windows exposes the accepted carrier of the two combat
participants.

A separate later call in `AITurnUnitFilter` covers one limited AI context. At
`0x82CC03FC` it passes its incoming player and unit to `CombatResolve` in mode 1
with provisional defender inputs of -1.

The resolver keeps that attacker identity. On the continuing path where an
opponent is present, it derives the accepted defender player and unit before
reaching the ordered attack-side then defense-side core pair. The AI caller
tests the returned value against evaluation thresholds.

This is one prediction path through the combat resolver. It does not show
that other AI evaluators, early returns or every resolver outcome use the same
combat roles.

The [combat reference](combat.md) records separate local weighting and
checkpoint-selection blocks, with stores of generator words under conditions.
The guarded frame-value calculations and the local stack-store pointer are
fully accounted for. A guarded trace from the core stat pair to the first store
depends on its stated ABI, on nonaliasing and on finite ordinals.

Checked post-store subcases reset the array or bypass presentation. A separate
presenter input chain, which applies under its own condition, reaches input to
the transfer call. The frame `+148` Boolean producer is recovered separately.
Participant normalization rewrites the later defender input, which invalidates
the original-r6 sentinel derivation for a valid participant path.

The null local-player return also blocks the countdown alternative. The
[local-player input boundary](frontend-frame-and-input.md) covers a guarded
write to the `+0x10` field of the resolver input object, the child's dispatch, and the
initial result allocation and word production.

Two limited displacement scans, the selected store functions, a reader defined by
the class, and a child-field initializer did not reveal a later writer of result
`+0xC`. The child `+0x88` method carries the result, under conditions, to a
writer that exchanges its current word between two searched ordinals. An initial
-1 remains unchanged under a nonnegative ordinal without overflow, given the ABI
and nonaliasing requirements and the guards on object identity and lifetime.

Registry lookup and getter paths reach a prior-word producer under conditions.
The equality with the current resolver input object's key, the scalar values and its internal
lookup and dispatch check are not yet established. The tested setup and cleanup
bodies contain no invocation of the child `+0x88`. That invocation remains a
separate open question. The prior-word route needs a compatible value and
ordered preservation of the state.

Two field readers pass their own `+0x34` to a four-byte input helper. Three
points are not yet established: shared receiver identity, the actual input
source, and receiver `+0x8 == 0`. A compatible nonzero producer, the resolver
entry, the full transfer and persistence of the participants all remain
unfinished. No naturally reachable path to a normal outcome is shown.

## Knight attack and defense

Knights (type 13) have base attack 4 and defense 2. The native code adds nothing
to the Knight's defense: its flags and type skip both defense modifier branches,
so defense stays 2. Attack is 4 plus these terms:

- Two small terms shared with other units, one from an unnamed player word and
  one from the Wonder with index 10 (see
  [core stats](combat-strength.md#core-stats)).
- 1 for an Arabian player from the Industrial era (UEA 14) or for a Japanese
  player from the Medieval era (UEA 27). A player gets at most one of them.
- The scenario attack bonus value (`ATTACKBONUS`), slot 21 at `0x830E8FFA`, a signed halfword
  that is added to every nonzero base attack.

A third Knight term tests UEA 15, which no civilization holds in the retail
table, so it adds nothing there; it would add 2. These terms do not change with
army size, health, rank, terrain or the opponent. Those enter later, in combat
resolution. The values are static results, and no battle involving Knights was
observed. The
[Knight findings](../../manifests/unique-unit-combat-predicates.json#/knightAttackModifierBoundary)
hold the exact conditions and addresses.

## Loaded-fleet sale value

A fleet sale adds the passengers' values to the carrier's first and applies the
fleet multiplier of 3 once to the total, so each Spy adds 75 Gold and the
multiplier does not triple the refund a second time.

The selected native sale path adds the carrier's production factor and the
factors of the linked passengers it accepts, then applies the carrier's army or
fleet multiplier to the whole sum. It does not use each passenger's own army
marker in that sum. For the supported Galleon and Spy inputs and the human
classifier arm, an empty fleet contributes 90 Gold, one loaded Spy brings the
total to 165, and ten bring it to 840. The cargo contributions are therefore 75
and 750 Gold. These are derived native amounts; actual command delivery and
reserve changes were not observed. [Sale valuation](../../manifests/unit-sale-refund-value.json)
records membership, identity, arithmetic and the limits of the preview and the
correction. The native register representation permits a correction at the
value producers without changing the formatter. Such a correction still needs
the roster to stay unchanged across the classifier, and a guard for nested
carriers that removal excludes.

## Evidence sources

- [Fleet scrap command boundary](../../manifests/fleet-scrap-command.json):
  army disbanding and unit deletion use different selected commands. Their
  inspected paths do not establish loaded-fleet refunds or cargo valuation.
- [Unique Unit identity selection](../../manifests/unique-unit-identity-selection.json)
- [AI candidate choice](../../manifests/ai-stat-choice.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Production cost evidence](../../manifests/production-cost-ownership.json)
- [`non-unit-production-threshold.json`](../../manifests/non-unit-production-threshold.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Unique Unit combat predicates](../../manifests/unique-unit-combat-predicates.json)
