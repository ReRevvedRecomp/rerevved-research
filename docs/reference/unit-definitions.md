# Unit definitions

The game stores 29 unit definitions at `0x82F700D8`. Each record is `0x94`
bytes. The unit type byte at offset `0x1` of the `0x54`-byte runtime unit
record indexes this table.

The names below are recovered semantic labels, not original debug symbols.

## Recovered layout and readers

| Item | Address or offset | Accepted meaning |
|---|---:|---|
| Unit-definition table | `0x82F700D8` | 29 records with stride `0x94` |
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
cumulative lookup adds one to retained movement. One special return path uses
an unresolved constant instead of the composed value, so the packet does not
claim every movement return, consumer, or AI path. The exact branches are in
[`unit-movement-stat.json`](../../manifests/unit-movement-stat.json).

## Normal unit production cost

`EffectiveUnitProductionCostScalar` at `0x82CF1148` starts from scalar 10 and
applies bounded player, condition, definition-flag, and civilization-bonus
reductions. The normal unit production cost is the signed factor at `+0x44`
multiplied by that scalar and divided by two with signed round-toward-zero
arithmetic.

The scalar's player-indexed input is one of eight signed halfwords at
`0x830E9050`. Initialization sets all eight to `-1`; broad game-state
serialization transfers all eight in both directions. Setup function
`0x82D217C8` submits numeric command type 57 with a player index and an
unresolved virtual result, and dispatcher case 57 stores that result into the
selected halfword. The array's policy meaning and the original command name
remain unresolved. Condition `0x82CEF4E8(14)` and bonus ID 33 also retain
neutral meanings. Accepted bonus IDs 5,
17, and 34 provide half-cost routes for Settlers, Riflemen, and Spies. The
eight bounded factor samples were Warrior 2, Archer 2, Riflemen 4, Horsemen 4,
Knights 5, Tank 10, Artillery 10, and Spy 5. These are factors, not direct
final-cost bytes.

The bounded lifecycle and persistence locators are in
[`player-production-scalar-lifecycle.json`](../../manifests/player-production-scalar-lifecycle.json).

A follow-up bounded source packet could not promote the virtual target behind
command-type-57 arg2. Ghidra models only eight bytes at setup entry
`0x82D217C8` and has no containing function or decoded instructions at submit
site `0x82D224F0`. Narrow generated corroboration shows the intended `r14`
receiver, vtable byte slot `+0xA0`, return flow through `r3`, `r31`, and wrapper
arg2 register `r5`, and a separately loaded receiver for the nearby `+0x100`
route. Because the exact receiver path is undecoded in Ghidra, no concrete
object, vtable, slot target, thunk, scalar source, or policy identity is
promoted. Exact limits are in
[`player-production-scalar-virtual-source.json`](../../manifests/player-production-scalar-virtual-source.json).

`ProductionItemCostLookup` at `0x82CE2B98` applies this unit formula to item
IDs 0 through 99. `CurrentProductionItemCostLookup` at `0x82CF8308` selects the
current city item at `+0x38` and returns the same unit result. Both route item
IDs 100 through 299 through separate `BuildingWonderProductionCostLookup` at
`0x82CF1278`. IDs 100 through 199 use a signed byte at `+0x41` of `0xCC`-byte
building records rooted at `0x82F71FD8`. The initialized block has 23 exact
records, IDs 100 through 122. Each has a name at `+0x00`, token text at
`+0x20`, signed production factor at `+0x41`, and stored description at
`+0x4C`. The next stride position overlaps adjacent non-record data. The
cost helper's broader ID range does not validate IDs 123 through 199. Exact
identities and factors are in
[`building-record-identities-100-122.json`](../../manifests/building-record-identities-100-122.json).
The production menu also reads signed technology ID `+0x42`, a required city
building-bit mask at `+0x44`, and a forbidden mask at `+0x48`. Exact values
for all 23 records are in
[`building-menu-record-gates.json`](../../manifests/building-menu-record-gates.json).
These checks alone do not establish menu availability or gameplay effects.
The nonzero masks join to the ordinary completion-bit writer: Bank requires
Market, Cathedral requires Temple, and University requires Library; the menu
hides each earlier-tier item when its later-tier bit is set. These are static
menu checks, with no runtime building-completion observation.
Barracks 101, Library 105, and Courthouse 114 have cumulative UEA 19, 20,
and 18 half-cost branches. Cathedral 111 has a UEA 21 branch, with no accepted
retail activation. University 112 and Factory 116 have separate neutral-gated
reductions. The exact branch sequence and other common modifiers are in
[`building-wonder-cost-modifier-branches.json`](../../manifests/building-wonder-cost-modifier-branches.json).
After a sufficient-production building test, `0x82D02090` stores building-index
bits in city state, including a bank selected by clamped player era, for
ordinary indices. Spaceship-part items 119-122
take a separate conditional city-flag path. Both paths store the item ID
at city `+0x3A` and check a bounded city byte list. These static writes do not
establish each building's described effect or runtime execution. See
[`building-completion-state-writer.json`](../../manifests/building-completion-state-writer.json).
The directly called city helper reads the Courthouse index-14 bit in city
`+0x10` and selects a scan of eight adjacent coordinate candidates or twenty
including a second ring. This establishes a static consumer of the Courthouse
bit, not which candidate tiles are worked or a runtime effect. See
[`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json).

IDs 200 through 299 use a signed halfword at `+0x40` of `0x14C`-byte wonder
records rooted at `0x82F73238`. The helper applies a common signed half-scale
to every item in that range, then applies another signed half reduction when
cumulative UEA 24, Wonders cost half as much, is active. The common scale is
part of the native wonder formula, not UEA 24 itself. The initialized block
has 37 exact records, IDs 200 through 236. Each has a name at `+0x00`, signed
production factor at `+0x40`, short token at `+0x4A`, art token at `+0x8A`,
and stored effect description at `+0xCA`; record-specific byte boundaries
remain in the identity manifests. The adjacent halfword at `+0x42` is
preserved in those packets but remains semantically unnamed. Ghidra's reference
manager returned no entries for the exact starts of the 217 accepted building
and wonder text fields; this does not resolve indexed, indirect, computed-address,
interior-string, or undecoded readers. See the [bounded text-field reference
census](../../manifests/building-wonder-text-field-reference-boundary.json) and
[consumer frontier](../../manifests/building-wonder-consumer-frontier.json).
The next twelve complete stride positions
are zero and the following position contains non-wonder data. Neither this
boundary nor the cost helper proves a program-wide valid-ID rule. Identity
packets cover the full initialized range: [items 200-204](../../manifests/wonder-record-identities.json),
[205-209](../../manifests/wonder-record-identities-205-209.json),
[210-214](../../manifests/wonder-record-identities-210-214.json), and
[215-219](../../manifests/wonder-record-identities-215-219.json), followed by
individual records for
[220](../../manifests/wonder-record-identity-220.json),
[221](../../manifests/wonder-record-identity-221.json),
[222](../../manifests/wonder-record-identity-222.json),
[223](../../manifests/wonder-record-identity-223.json),
[224](../../manifests/wonder-record-identity-224.json),
[225](../../manifests/wonder-record-identity-225.json),
[226](../../manifests/wonder-record-identity-226.json),
[227](../../manifests/wonder-record-identity-227.json),
[228](../../manifests/wonder-record-identity-228.json),
[229](../../manifests/wonder-record-identity-229.json),
[230](../../manifests/wonder-record-identity-230.json),
[231](../../manifests/wonder-record-identity-231.json),
[232](../../manifests/wonder-record-identity-232.json),
[233](../../manifests/wonder-record-identity-233.json),
[234](../../manifests/wonder-record-identity-234.json),
[235](../../manifests/wonder-record-identity-235.json), and
[236](../../manifests/wonder-record-identity-236.json). Also see the bounded
[`wonder-record-byte-boundary-237-249.json`](../../manifests/wonder-record-byte-boundary-237-249.json).
The bounded decoded city-item writer scan did not locate an item-selection or
validity rule; its coverage limits are recorded in
[`production-item-writer-decoded-frontier.json`](../../manifests/production-item-writer-decoded-frontier.json).
An approved runtime write observer subsequently found command type five storing
its record's item value to an owner-matched city `+0x38` at `0x82CE0020`.
That local case does not check the item ID. A separate cost-preview path
temporarily writes candidate IDs and restores the previous item. See
[`city-production-command-five-writer.json`](../../manifests/city-production-command-five-writer.json).
The city choice handler at `0x82E02CE0` calls a distinct command-five producer
at `0x82CEE650` for unit, building, and wonder categories. It forwards the
selected item into the command record without a local ID bound; the producer
can pass that record to the local drain at `0x82CEE76C`. A Barracks-selection
session logged no type-five calls at the separate submit entry `0x82CE1950`.
A bounded census found 27 direct local-drain calls; a 0x100-byte literal-five
check around each found no second proved type-five producer. A separate census
found all 100 direct calls to the submit entry. Helper `0x82CB42B8`, called
twice by the city-list generator, submits type five at `0x82CB44D0`; one
branch takes an ordinal from a 33-slot wonder scan and adds 200. If its
indirect chooser returns a valid row, that branch yields IDs 200 through 232.
The initialized chooser vtable leads to a dialog whose callback parses a decimal
row and stores it at `+0x470`. The dialog's content-update path checks that row
against a 16-byte-entry count after the store, but its return writer at
`0x82E0551C` copies `+0x470` to `+0x42C` without a row-count check. The source
of the callback string and live row values are unknown, so an unconditional
submission bound is not established. Runtime execution, indirect routes, and
earlier record construction also remain unresolved. See
[`city-production-command-five-source-frontier.json`](../../manifests/city-production-command-five-source-frontier.json).
The seven direct callers of this city-list generator pass mode 2 from the
building-choice wrapper, mode 1 from the unit-choice wrapper, or mode -1 from
AI, city-update, and turn paths. The `-12` wonder marker scan requires mode bit
`0x2`, so mode 1 skips it; mode and eligible slots alone do not select the
marker. In one interactive session, the owner reported selecting a wonder and
the default-off observer enabled at `0x82CECC98` logged zero calls before a
normal exit. That run does not establish whether another state reaches this
separate submit path. The array end register `r30`, relative to `r15-3808`,
provides its populated count; `r31` counts all 33 scanned slots.

The actual choice child copies nonnegative IDs from separate parent arrays and
checks the selected vector index before forwarding an item. Its wonder-array
generator tests exactly normalized indices 0 through 32, so this UI path can
offer wonder IDs 200 through 232; the mutable runtime slot and wonder gate
decide which appear. Initialized wonder IDs 233 through 236 are outside this
choice loop. A static reset fills its 33 mutable claim slots with -1; the
accepted mode-one completion helper writes owner and city index into a slot.
With known vtable `0x82138768` installed at receiver `0x8314F76C`, the inner
city-update gate also returns zero for normalized indices 33 through 36 (IDs
233 through 236): its virtual target rejects them, and its fallback accepts
only indices below 21. This is a static path result, not a runtime observation
of those IDs or a program-wide invalid-ID rule. See
[`wonder-eligibility-virtual-target.json`](../../manifests/wonder-eligibility-virtual-target.json).
One live city-menu pass found both words at -1 in all 33 slots; its eligibility
call returned nonzero for indices 2, 8, 11, 12, and 14 through 18. This
observes one city state, not a global validity rule. See
[`wonder-claim-slot-state.json`](../../manifests/wonder-claim-slot-state.json).
The building array uses a live count initialized to 23 and an
index-plus-100 append loop, yielding IDs 100 through 122 under that count.
Its availability predicates and any later count mutation remain unresolved.
The branch taken in the Barracks session
was not observed. See
[`city-production-choice-submit.json`](../../manifests/city-production-choice-submit.json)
and [`city-production-option-source.json`](../../manifests/city-production-option-source.json).
Stored descriptions do not prove implemented effects. One bounded
post-threshold branch for Hanging Gardens item 202 changes city population
byte `+0x03` to `clamp(trunc((3*x+1)/2),0,31)` and calls two city helpers; no
runtime execution or persistent doubled-growth rule is proved. See
[`hanging-gardens-population-branch.json`](../../manifests/hanging-gardens-population-branch.json).
The Oxford University item-208 branch scans 48 technology records, filters
owned and other candidates, ranks survivors with an unresolved score helper,
and can call the ordinary technology acquisition owner with the selected ID.
No selected runtime ID or successful acquisition has been observed. See
[`oxford-technology-acquisition-branch.json`](../../manifests/oxford-technology-acquisition-branch.json).
The Statue of Liberty item-227 branch scans 128 city slots and adds two to
population byte `+0x03`, clamped to 31, for populated cities owned by the
source city's player. Its execution and persistence have not been observed.
See [`statue-of-liberty-population-branch.json`](../../manifests/statue-of-liberty-population-branch.json).
The Great Wall item-201 branch writes equal values into two symmetric entries
of a player-pair table after local filters. The table's consumer and any
peace-offer behavior are unresolved. See
[`great-wall-player-pair-branch.json`](../../manifests/great-wall-player-pair-branch.json).
The Leonardo's Workshop item-211 branch compares two unit-definition
halfwords, checks technology ownership, and can replace live unit type byte
`+0x01` in qualifying records. Its virtual calls and runtime coverage do not
establish that every unit upgrades. See
[`leonardo-unit-type-branch.json`](../../manifests/leonardo-unit-type-branch.json).
Those are the five explicit indices in the direct mode-one branch group of
`0x82D16BA0`. The direct call skips the helper's later mode-two tail. A
separate mode-two call for items 219 and 220 can enter that tail;
the branch census is in
[`wonder-post-threshold-helper-boundary.json`](../../manifests/wonder-post-threshold-helper-boundary.json).
At its terminal join, that conditional mode-two path clears two state bits
and sets bit `0x10000` in shared status word `0x82FFE7C4` for index 19 or 20.
No bit-specific consumer or victory meaning has been established. One player-matched path also
updates a halfword at `0x830EF348 + 2*index`, whose meaning is unknown. See
[`wonder-mode-two-terminal-state.json`](../../manifests/wonder-mode-two-terminal-state.json).
Text and art-token consumers, complete layouts, final runtime costs, and most
gameplay effects remain unresolved. The exact cost inputs are in
[`building-wonder-cost-identities.json`](../../manifests/building-wonder-cost-identities.json).

## Effect coverage by ID

The records store descriptions, but description text does not prove that the
game implements the described behavior. The table classifies the effect-specific
evidence currently in scope. No gameplay-effect execution has been observed at
runtime in the mapped building and wonder effect packets; the runtime
observations above cover choice, eligibility, and production-item state only.

| IDs | Static evidence | Runtime effect execution |
|---|---|---|
| Wonders 201, 202, 208, 211, 227 | Item-specific branches exist in the direct mode-one helper. Their local writes and calls are mapped in the [branch census](../../manifests/wonder-post-threshold-helper-boundary.json) and [individual packets](../../manifests/great-wall-player-pair-branch.json), [Hanging Gardens](../../manifests/hanging-gardens-population-branch.json), [Oxford](../../manifests/oxford-technology-acquisition-branch.json), [Leonardo](../../manifests/leonardo-unit-type-branch.json), and [Statue of Liberty](../../manifests/statue-of-liberty-population-branch.json). | Not observed |
| Wonders 219-220 | A conditional mode-two path writes shared status bits and a halfword; their meanings and downstream consumers remain unknown. See [terminal state](../../manifests/wonder-mode-two-terminal-state.json). | Not observed |
| Building 114 | The Courthouse bit selects a scan of eight or twenty coordinate candidates; downstream scoring and visible effect remain unknown. See [coordinate scan](../../manifests/courthouse-city-coordinate-scan.json). | Not observed |
| Wonders 200, 206, 207, 209 | Bounded searches found no exact edge for the described effect within each packet's stated scope: [Pyramids](../../manifests/pyramids-government-availability.json), [Great Library](../../manifests/great-library-technology-transfer.json), [East India Company](../../manifests/east-india-sea-trade.json), and [Shakespeare](../../manifests/shakespeare-city-culture.json). These are bounded negatives, not proof that no effect exists. | Not observed |
| Wonders 203-205, 210, 212-218, 221-226, 228-232 | These IDs normalize into the helper's accepted 0-32 range on the direct city-update callsite but do not match one of its five explicit mode-one branches. This bounds only that helper path; other consumers remain possible. See the [branch census](../../manifests/wonder-post-threshold-helper-boundary.json). | Not observed |
| Wonders 233-236 | Normalized indices 33-36 branch away before the direct post-threshold helper body on the accepted city-update callsite. Earlier city writes occur, and other paths remain unresolved. See the [branch census](../../manifests/wonder-post-threshold-helper-boundary.json). | Not observed |
| Buildings 100-113, 115-122 | Stored descriptions are present, but no item-specific effect branch or bounded per-item negative packet is recorded here. The [consumer frontier](../../manifests/building-wonder-consumer-frontier.json) does not exclude indexed or indirect readers. | Not observed |

Barracks 101 remains a specific unresolved link: its stored description says
veteran units are produced, while the native veteran grant branch is gated by a
creation-record bit. The accepted [building writer](../../manifests/building-completion-state-writer.json)
and [veteran branch](../../manifests/new-warrior-veteran.json) do not establish
that Barracks completion or ownership supplies that bit. Ghidra defines only an
8-byte body at city-update entry `0x82D13978` and no containing function or
instructions at veteran gate `0x82D15B84`, so its current function listing cannot
join those paths. The modded veteran
runtime acceptance recorded in the latter packet does not test the Barracks
description.

One bounded wonder production gate uses normalized wonder index. In one fresh
game, its receiver dispatched virtual slot `+0x1E4` to `0x82D80C30` for
indices 0 through 32; every logged result was zero. This implementation can
return one for indices 21 through 32 only when the corresponding one of three
bits from slot `+0x1DC` is set. The observed slot's getter at `0x82D7D2A8`
returns frontend-root `+0x08`, except that context state codes 4 through 6
force zero. The later generic outer gate reads signed wonder-record halfwords
at `+0x44`, `+0x46`, and `+0x48`. The first two pass technology IDs or `-1`
sentinels to the ordinary technology ownership query. The third selects a
technology whose ownership bits are checked for other players. Exact stored
values for IDs 200 through 236 are in
[`wonder-outer-gate-record-fields.json`](../../manifests/wonder-outer-gate-record-fields.json).
Indices 19 and 20 use separate state checks mapped in
[`wonder-outer-gate-special-19-20.json`](../../manifests/wonder-outer-gate-special-19-20.json).
The mask-field writer, its bit meanings, other virtual targets, special-branch
state owners, runtime eligibility, and effects remain unresolved. See
[`wonder-eligibility-virtual-target.json`](../../manifests/wonder-eligibility-virtual-target.json)
and
[`wonder-eligibility-mask-source.json`](../../manifests/wonder-eligibility-mask-source.json).

A bounded Pyramids consumer packet did not establish an exact item-200 edge to
government availability or state, completion, display, or AI. Exact references
and split-address recovery found one Pyramids record-base materializer, one
technology-table materializer, and one shared technology-helper candidate; all
three exact candidate bodies truncated on bad instruction data. A filtered
item-200 literal/comparison scan then reached its eight-function cap, so those
functions remain unclassified. This is a bounded negative, not a claim that no
Pyramids consumer exists. Exact limits are in
[`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json).

A separate bounded Great Library packet found no item-206 effect edge through
direct references, split-address recovery, or filtered literal uses. The
later record-indexed outer gate does read technology ownership for its
eligibility check, using stored technology IDs 8 and 21. That read does not
prove the description's technology-transfer effect, acquisition, completion,
display, or AI behavior. Exact limits and the later edge are in
[`great-library-technology-transfer.json`](../../manifests/great-library-technology-transfer.json).

An effect-specific East India Company packet also found no exact item-207 edge
to sea-tile trade, city economy, completion, display, or AI. The record,
description, and cost cell had no direct or split-address matches. The complete
filtered item scan emitted only `0x82500288`, whose complete body proves the
`0xCF` comparison is part of packed D3D format decoding rather than wonder
identity. The generic terrain-yield evidence remains unresolved. Exact limits
are in
[`east-india-sea-trade.json`](../../manifests/east-india-sea-trade.json).

A bounded Shakespeare packet found no exact item-209 edge to city culture,
completion, display, or AI. The record, description, and cost cell had no
direct or split-address matches. The complete filtered item scan emitted only
`0x826CFDC8`; its recovered prefix has no Shakespeare or culture carrier and
the exact body truncates on bad instruction data. Exact limits are in
[`shakespeare-city-culture.json`](../../manifests/shakespeare-city-culture.json).

Bounded static consumers are:

- `RushCostCompute` at `0x82CE27F0`, which subtracts invested production at
  city `+0x36` before its separate rush-gold arithmetic.
- The accepted rush-area display owner at `0x82DFFE38`, which calls the current
  cost lookup and uses city `+0x36` and `+0x42` in percentage calculations.
- The unit branch in `0x82D13978`, which branches away while signed invested
  production at city `+0x36` is less than the composed cost.
- `AIUnitChoiceEvaluate` and `AITurnUnitEvaluation`, which both read `+0x44`
  and call the same scalar helper.

The display evidence is rush-area-specific, and the completion evidence closes
only one threshold. The two AI paths prove shared inputs, not scoring, decision,
or corrected-rush parity. No runtime production behavior was tested.

The same `0x82D13978` function has a separately bounded non-unit threshold.
Within the accepted current-item domain, signed city `+0x38` values at least
100 route to `BuildingWonderProductionCostLookup`. Item IDs 100 through 199
compare signed invested production at `+0x36` with the returned cost and branch
away when invested is less; the sufficient path first stores invested minus
cost back to `+0x36`. IDs 200 through 299 repeat the cost call, preserve its
result, and perform the same signed comparison. After two additional neutral
gates, their first promoted stores write invested minus cost to `+0x36`, copy
current item to `+0x3A`, and replace the word at `+0x24` with that word masked
by `0xFFFFFBFF`.

The function does not expose an independent item-less-than-300 guard in the
bounded evidence, so the range wording depends on the accepted current-item
domain and does not validate arbitrary IDs. The stores are neutral first-write
facts, not building or wonder completion, effect execution, queue advancement,
overflow handling, creation, notification, runtime behavior, or implementation
safety. Exact addresses and stops are in
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

These UUs do not create new unit-definition records. Roman Cataphracts
retain Knights type 13, and Mongolian Keshiks retain Horsemen type 12. The
mapping establishes display identity only. It does not establish
identity-specific movement, cost, effects, AI strategy, models, or animations.

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

## Combat stat-role boundary

The accepted ordinary unit-versus-unit path contains one exact ordered stat
pair inside `CombatResolve`:

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

Bounded windows in the three mapped AI evaluators confirm scalar consumption
but not role parity. `AIUnitChoiceEvaluate` adds attack and defense for the same
player and type; `AITurnUnitEvaluation` conditionally multiplies candidate stat
results; and `AITurnUnitFilter` compares defense and attack under one player
with separately sourced types. None of those scalar windows exposes the
accepted two-player combat participant carrier.

A separate later call in `AITurnUnitFilter` closes one bounded AI context. At
`0x82CC03FC` it passes its incoming player and unit to `CombatResolve` in mode
1 with provisional defender inputs of -1. The resolver retains that attacker
identity and, on the continuing opponent-present path, derives the accepted
defender player and unit before reaching the ordered attack-side then
defense-side core pair. The AI caller tests the returned value against
evaluation thresholds. This is one resolver-backed prediction path, not
general role parity for the other AI evaluators, early returns, or every
resolver outcome.

## Evidence sources

- [Unique Unit identity selection](../../manifests/unique-unit-identity-selection.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Production cost ownership](../../manifests/production-cost-ownership.json)
- [Non-unit production threshold boundary](../../manifests/non-unit-production-threshold-boundary.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Unique Unit combat predicates](../../manifests/unique-unit-combat-predicates.json)
