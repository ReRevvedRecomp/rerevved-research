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
The word `0x82FFE7C8` used by the final wonder reduction also follows two
conditional transfer paths in `BroadGameStateSerializer`: mode one with a null
auxiliary pointer passes it as the destination to `BufferReadU32`, and mode zero
with a null auxiliary pointer passes it as the source to `BufferWriteU32`. The
exact raw words match the generated-code paths, while Ghidra still has no decoded
body for these addresses. The concrete buffer virtual targets, external format,
policy meaning, runtime value, and visible effect remain unresolved. A separate
reader at `0x82D25330` uses signed less-than-two as one guard before a
slot `+0x80` call on receiver address `0x8314F76C` with arguments 13 and -1;
an exact-address materializer scan for the receiver hit its 32-result cap, and
the flat-image word at that address is zero, so the target and runtime value
remain unresolved. See the
[global cost-word transfer frontier](../../manifests/building-wonder-cost-global-transfer.json)
and [secondary-reader boundary](../../manifests/building-wonder-cost-global-secondary-reader-frontier.json),
plus the earlier [bounded candidate search](../../manifests/building-wonder-cost-global-writer-frontier.json).
The final building-cost half reduction tests city halfword `+0x3C` bit `0x8`.
A bounded direct-write scan found no non-stack `+0x3C` WRITE or READ_WRITE
operand in 272 function-owned decoded instructions. A raw D-form store scan
found one candidate, but its resolved base targets a different global address;
exact-address searches for `0x8314FE64` found no split-constant candidates.
Indexed, computed, functionless, and out-of-interval writers remain unresolved. See the
[city cost-flag writer frontier](../../manifests/building-cost-city-flag-writer-frontier.json).
An exact city-table-base follow-up reproduced 31 materializers and checked the
next eight unexamined functions. It found no direct non-stack `+0x3C` write in
231 function-owned instructions. See the
[city cost-flag materializer frontier](../../manifests/building-cost-city-flag-materializer-frontier.json).
The continuation checked the other 23 exact-base materializer functions in
four batches and also found no direct `+0x3C` stores. Together, those packets
cover all 31 exact city-table-base materializer functions, with zero direct
stores in 1817 decoded instructions. A generated-body review of all 31 owners
found no locally resolved store to `+0x3C` or an overlapping word; the pointer
destination at `0x82E57980` remains unresolved and could alias city state. See
the [remaining materializer results](../../manifests/building-cost-city-flag-materializer-continuation.json)
and [computed-writer boundary](../../manifests/building-cost-city-flag-computed-writer-frontier.json).
A separate 128-position loop at `0x82E8AEC8` stores `0x8314F0A8` at city-row
`+0xB8` and zero at `+0xB0` and `+0xB4`. Their field meanings and consumers
remain unknown; see the [city-row field initializer symbol](../../manifests/catalogs/symbols.json).
The shared Library/University three-quarter gate at `0x830E8FFE` has no
identified writer or policy meaning; bounded address searches found no match,
and its consumer lies in a Ghidra function gap. See the
[gate source frontier](../../manifests/building-wonder-cost-gate-source-frontier.json).

The Building option bridge in `0x82CED700` passes a fixed temporary-array tail
to its copy helper. After skipping `k` leading negative words, the byte-count
argument derives from `4 * (100 - k)` while its returned visible count is the
generator count minus `k`. Parent setup supplies the Building destination at
`+0x5DC` and records that return at `+0x43C`. Neither the complete selected
wrapper nor the child input loop has a local 100-entry maximum check; this
does not show that the native generator returns an excessive count. See the
[option-copy capacity boundary](../../manifests/building-option-copy-capacity-boundary.json).
These static copy arguments do not establish a safe new definition or ownership
slot.

The child's append helper `0x822D10C0` derives size and capacity from its
descriptor's begin, end, and capacity-end pointers. With a nonzero begin and
computed size below capacity, it writes one four-byte input at end and advances
end by four. A zero begin or computed size at least capacity delegates to
`0x822D1150`; growth, allocation, and failure handling remain unresolved there.
The local predicate does not validate the descriptor's allocation or pointer
invariants. See the [append capacity gate](../../manifests/building-option-append-capacity-gate.json).

After a sufficient-production building test, `0x82D02090` stores building-index
bits in city state, including a bank selected by clamped player era, for
ordinary indices. Spaceship-part items 119-122
take a separate conditional city-flag path. Both paths store the item ID
at city `+0x3A` and check a bounded city byte list. These static writes do not
establish each building's described effect or runtime execution. See
[`building-completion-state-writer.json`](../../manifests/building-completion-state-writer.json).
The spaceship-part path sets city `+0x24` bit `0x100` under its separate
player-indexed gate. A bounded direct-read scan found no non-stack `+0x24`
READ or READ_WRITE operand in 272 function-owned decoded instructions; a decoded
split-constant scan found no materializer for exact address `0x8314FE4C`.
Indexed, computed, aliased, functionless, and out-of-interval readers remain
unresolved. See the
[spaceship-part flag frontier](../../manifests/spaceship-part-city-flag-consumer-frontier.json).
An additional exact-base sample checked the next eight unique city-table
materializer functions after the previously followed path and the first eight
other functions. It found no direct non-stack `+0x24` READ or READ_WRITE operand
across 428 function-owned instructions. Remaining materializers and indexed,
computed, aliased, indirect, and functionless readers remain unresolved. See the
[materializer frontier](../../manifests/spaceship-part-city-flag-materializer-frontier.json).
The writer also stores era-indexed building bits at city `+0x14`, `+0x18`,
`+0x1C`, or `+0x20`. A bounded direct-read census found no decoded reads at
those offsets in 272 function-owned instructions across `[0x82D00000,0x82D20000)`;
indexed, computed, functionless, and out-of-interval readers remain unresolved.
See the [era-bit reader frontier](../../manifests/city-era-building-bit-reader-frontier.json).
A follow-up reproduced 31 exact city-table-base materializers and checked the
first eight unique functions after the previously followed `0x82CEDF90` path.
It found no direct reads at those offsets across 664 function-owned
instructions; other materializers and indexed or computed reads remain open.
One sufficient-production wonder path also copies the current item ID from
city `+0x38` to `+0x3A` after additional gates; later behavior remains outside
that packet. A bounded direct-read census found zero decoded `+0x3A` READ
operands across 272 function-owned instructions in `[0x82D00000,0x82D20000)`.
Indexed, computed, functionless, and out-of-interval readers remain unresolved.
See the [wonder threshold](../../manifests/non-unit-production-threshold-boundary.json)
and [stored item ID reader frontier](../../manifests/city-stored-item-id-reader-frontier.json).
An exact-base follow-up scanned 654329 decoded instructions for city-table
base `0x8314FE28` and emitted 31 split-constant materializers below its cap of
64. In one inspected path, `0x82CEDF90` reads a byte from the indexed city
record at offset `+0`, then calls `0x82D038E8`, whose 17-instruction body does
not read the incoming city-table base. This does not prove a `+0x3A` reader;
the other materializers and computed or indexed item-ID paths remain open.
An additional direct-read check found no `+0x3A` operands in the first eight
other exact-base materializer functions across 664 function-owned instructions;
indexed, computed, and remaining materializer paths are still unresolved.
The directly called city helper reads the Courthouse index-14 bit in city
`+0x10` and selects a scan of eight adjacent coordinate candidates or twenty
including a second ring. This establishes a static consumer of the Courthouse
bit, not which candidate tiles are worked or a runtime effect. See
[`courthouse-city-coordinate-scan.json`](../../manifests/courthouse-city-coordinate-scan.json).
The same helper also tests city `+0x10` bits for Barracks 101, Granary 102,
Temple 103, Workshop 106, either Market 104 or Library 105, and either Bank
110 or University 112. Passing each test adds half of an intermediate register
back into that register. The two paired masks each cause only one update when
either bit is present. On one later branch, the adjusted registers weight
food, production, and trade component returns in a local candidate score;
another branch replaces the weights. After further validation, the helper stores a
selected or replacement byte, including `-1`, at city `+0x58` plus a local
index. A separate function, `sub_82CE1C10`, reads the same indexed byte array
for indices below the positive signed city `+0x03` bound, counts entries not
equal to `0xFF`, and returns the bound minus that count, which equals the number
of `0xFF` entries. This proves a static external reader but does not establish
tile assignment, gameplay meaning, visible effect, or runtime invocation. See
the [bounded bit
arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json),
[weighted score](../../manifests/building-bit-weighted-yield-score.json),
[city byte store](../../manifests/building-bit-selected-city-index.json), and
[consumer frontier](../../manifests/building-bit-selected-city-index-consumer-frontier.json).
The nearby `sub_82D019F0` census still has 18 `lbzx` candidates, none joined to
that city pointer. The earlier 21/8/13 candidate filter is not recoverable from
tracked evidence, and the bounded census does not exclude readers outside that
function.

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
The exact body at `0x82CF0268` also contains no decoded register-relative
operand at wonder-record offsets `+0x42`, `+0x4A`, `+0x8A`, or `+0xCA`; that
one-function scan does not cover scaled/indexed address calculations or other
readers. The production-choice tail at `0x82E41538` calls `0x827F7C8C`, whose
Ghidra function body is one byte with no decoded instruction; its reference
listing was truncated at 64. This path adds no text or token reader evidence.
A separate [factor consumer](../../manifests/wonder-factor-array-accumulation.json)
reads wonder `+0x40` and adds a derived value to two indexed accumulators.
The wonder claim-slot owner indexes one global and one stack-local accumulator.
A later switch arm reads the stack-local accumulator at `0x82CB379C` after its
collection loop. A bounded continuation finds that one arm converts the signed
word to a float, divides by signed stack value `r25`, and writes a
single-precision result at `0x830E8DD0` plus 64 bytes per loop iteration. Two
other indexed paths read floats at that base plus 64-byte-scaled indices and
four bytes; they do not prove a read of the writer's `+0` cell. The global's
role, a same-cell consumer, and any effect on final cost remain unknown. See the
[bounded output and reader frontier](../../manifests/wonder-factor-global-output-reader-frontier.json).
A bounded [reader census](../../manifests/wonder-factor-accumulator-reader-frontier.json)
found an eight-word copy from the global at `0x830ECCC8` to `0x831228E4`.
Three indexed reads of the enclosing object could reach those words with
specific low-30-bit indices, but their selectors are data-dependent; no
copied-word read is proved. The global accumulator's later use and any effect
on final production cost remain unknown. The [index-source boundary](../../manifests/wonder-copy-index-sources.json)
traces one selector to an incoming object's `+0x434` pointee word and another
to an unresolved virtual result; neither has a proved value range.
The [bounded writer check](../../manifests/wonder-copy-index-writer-boundary.json)
joins the index reader's function-pointer table to an initializer that clears
its object's `+0x434`. A separate initializer stores a pointer at the same
offset under a different table value; no shared object or later live pointer
writer is established. Zero image words at that pointer establish no index or
copied-word read.
Two direct callers of the reader initializer occur in the same function as a
separate indexed read; their next method call has no direct `+0x434` store in
its checked body. Neither path establishes a live factor read or cost effect.
The enclosing caller is slot `+0xC8` of the initialized singleton vtable at
`0x82138768`. One indirect `+0xC8` call at `0x828AA8FC` uses a receiver loaded
from another object's `+0x18`; that receiver is not joined to the singleton,
so this is not a proved live caller or gameplay trigger.
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

## Building and wonder record contract

The table below lists assigned definition fields. Exact values for each ID live
in the [building identities](../../manifests/building-record-identities-100-122.json),
[building menu gates](../../manifests/building-menu-record-gates.json),
[wonder identities](../../manifests/wonder-record-identities.json) and their
linked continuation packets, and [wonder outer-gate fields](../../manifests/wonder-outer-gate-record-fields.json).
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

Generic `TechnologyAcquire` calls one other static consumer, `0x82CEA5A0`,
with its technology ID. That function compares the ID with
building `+0x42` and wonder `+0x44` while forming a local list. Its wonder
loop spans 33 positions; the list's downstream meaning remains
unresolved. See the [technology-field match](../../manifests/definition-technology-match-list.json).
A separate [conditional list](../../manifests/definition-technology-conditional-list.json)
reads building `+0x42` and wonder `+0x44` and `+0x46`. Its wonder path compares
the two technology IDs with a selected value and can query ownership of the
other field. Its two direct callers pass an item-minus-600 selector from the
preview helper or an indexed byte from another function. Its list output and
runtime use remain unresolved.

These are partial layouts, with no supported meaning for unlisted bytes.
Editing a known signed factor can change the accepted static cost calculation
for an initialized ID, subject to its later modifiers; it does not establish a
final in-game price. Building menu masks and wonder technology cells are known
inputs to local gates, not a complete buildability policy. Repeated or mismatched
tokens do not identify assets. The initialized record blocks cover IDs 100-122
and 200-236;
the helper's broader 100-199 and 200-299 routing cannot be used as an
arbitrary-ID extension contract.

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
The completion writer also checks or fills a 28-byte ordinal list at city
`+0x87..+0xA2`. In the exact building-loop window, generated code shows city
reads at `+0` and `+0x10`, with no list-byte read in that slice. Ghidra owns no
decoded instructions for the window, so its direct-field query covered zero
instructions; this does not rule out callees or other readers. No runtime list
filter was observed. See the
[`building completion-list reader frontier`](../../manifests/building-completion-list-menu-reader-frontier.json).
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
A bounded follow-up found no exact Ghidra references or decoded split-constant
materializers for table base `0x830ED1D8`; derived, indexed, computed, aliased,
and indirect readers remain unresolved. See the [pair-table consumer
frontier](../../manifests/great-wall-player-pair-consumer-frontier.json).
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
An exact-base split-constant scan found no decoded materializers for that
address; it does not cover direct-displacement accesses or derived addresses.
Three whole-word snapshot functions copy the status word to output parameter
offset `+0x200`, but their exact function-entry reference counts and the bounded
raw direct-call scan across initialized executable memory were zero; the latter
checked aligned direct branch-and-link instructions only. The output-buffer
provenance is unresolved. No bit-specific consumer or victory meaning has been
established. One player-matched path also updates a halfword
at `0x830EF348 + 2*index`; an exact-base materializer scan found no decoded
split-constant materializer, and the field meaning remains unknown. See
[`wonder-mode-two-terminal-state.json`](../../manifests/wonder-mode-two-terminal-state.json).
The immediate slot `+0xD0` target on that path does not directly read this
counter. It loads a pointer from `0x82FFD688` and branches to one direct tail
target when nonzero; that pointer's identity and provenance remain unresolved.
See the bounded [counter consumer frontier](../../manifests/wonder-mode-two-counter-consumer-frontier.json).
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
| Building 114 | The Courthouse bit selects a scan of eight or twenty coordinate candidates; one later path stores a selected or replacement ordinal byte at city `+0x58` plus a local index. The visible effect is unknown. See [coordinate scan](../../manifests/courthouse-city-coordinate-scan.json) and [city byte store](../../manifests/building-bit-selected-city-index.json). | Not observed |
| Buildings 101-106, 110, 112 | A direct post-completion city helper tests their presence bits and can change local weights on food, production, and trade component returns; a later path can store a selected or replacement ordinal byte at city `+0x58` plus a local index. The final city effect is unknown. See [bit arithmetic](../../manifests/building-postwrite-city-bit-arithmetic.json), [weighted score](../../manifests/building-bit-weighted-yield-score.json), and [city byte store](../../manifests/building-bit-selected-city-index.json). | Not observed |
| Wonders 200, 206, 207, 209 | Bounded searches found no exact edge for the described effect within each packet's stated scope: [Pyramids](../../manifests/pyramids-government-availability.json), [Great Library](../../manifests/great-library-technology-transfer.json), [East India Company](../../manifests/east-india-sea-trade.json), and [Shakespeare](../../manifests/shakespeare-city-culture.json). These are bounded negatives, not proof that no effect exists. | Not observed |
| Wonders 203-205, 210, 212-218, 221-226, 228-232 | These IDs normalize into the helper's accepted 0-32 range on the direct city-update callsite but do not match one of its five explicit mode-one branches. This bounds only that helper path; other consumers remain possible. See the [branch census](../../manifests/wonder-post-threshold-helper-boundary.json). | Not observed |
| Wonders 233-236 | Normalized indices 33-36 branch away before the direct post-threshold helper body. The known vtable's earlier gate also rejects them on this path; other receiver states and paths remain unresolved. See the [branch census](../../manifests/wonder-post-threshold-helper-boundary.json) and [eligibility target](../../manifests/wonder-eligibility-virtual-target.json). | Not observed |
| Buildings 100, 107-109, 111, 113, 115-122 | Stored descriptions are present, but no item-specific effect branch or bounded per-item negative packet is recorded here. The [consumer frontier](../../manifests/building-wonder-consumer-frontier.json) does not exclude indexed or indirect readers. | Not observed |

Barracks 101 remains an unresolved link to native veteran creation. The native
veteran grant branch is gated by a creation-record bit, while the accepted
building writer and veteran branch do not establish that Barracks completion or
ownership supplies it. A bounded raw PowerPC displacement-store scan found no
+0x3C stores in [0x82D13978,0x82D16BA0). This scan does not exclude computed or
indexed stores, other writers, or a link elsewhere; it does not establish that
Barracks has a veteran effect. See the [bounded link scan](../../manifests/barracks-veteran-creation-record-link.json).
Ghidra defines only an 8-byte body at city-update entry 0x82D13978 and no
containing function or instructions at veteran gate 0x82D15B84, so its current
function listing cannot join those paths. The modded veteran runtime acceptance
recorded in the latter packet does not test the Barracks link.

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
All 60 functions with direct Ghidra references to the frontend-root pointer
were checked for a `+0x08` store; none yielded a proved write to that root
field. This [bounded writer census](../../manifests/wonder-eligibility-mask-writer-frontier.json)
does not cover indirect or constructor paths. The application-owner base
constructor initializes this field to zero before its pointer is published
through `0x82FFD624`; see the [publication and initialization record](../../manifests/frontend-root-publication-mask-init.json).
The owner's vtable slot `+0x80` conditionally passes a nonzero `+0x08` word
to the Xbox `NtClose` wrapper and clears the field if that call returns. The
[bounded vtable review](../../manifests/frontend-root-vtable-offset8-clear.json)
does not identify the handle's producer or kind.
Bit meanings, other virtual targets, special-branch state owners, runtime
eligibility, and effects remain unresolved. See
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

The [ordinary combat boundary](ordinary-combat.md) records separate local
weighting and checkpoint-selection blocks with conditional generator-word stores.
The guarded frame-value calculations and local stack-store pointer are closed.
A guarded core-to-first-store trace depends on its stated ABI, nonalias and
finite ordinal conditions. Checked post-store subcases reset the array or bypass
presentation. A separate conditional presenter input chain reaches transfer-call
input. The frame `+148` Boolean producer is recovered separately. Participant
normalization rewrites the later defender input, invalidating the original-r6
sentinel derivation for a valid participant path. The null local-player return
also blocks the countdown alternative. The [local-player input boundary](frontend-frame-and-input.md)
binds a guarded owner `+0x10` writer, the child's dispatch, and initial result
allocation and word production. Two bounded displacement scans, selected store
owners, a class-owned reader and a child-field initializer did not bind a later
result `+0xC` writer. The child `+0x88` method now conditionally carries the result
to a writer that exchanges its current word between two searched ordinals.
Initial -1 remains unchanged under nonnegative/no-overflow ordinal and
ownership/ABI/nonalias guards. Registry lookup/getter paths conditionally reach
a prior-word producer, but current-owner key equality, scalar values and its
internal lookup/dispatch gate remain unproved. The tested setup/cleanup bodies
contain no child `+0x88` invocation. Invocation and ordered compatible word
retention remain required.
A compatible nonzero producer and resolver entry, full transfer and participant
persistence remain unclosed; no naturally reachable ordinary outcome path is proved.

## Evidence sources

- [Unique Unit identity selection](../../manifests/unique-unit-identity-selection.json)
- [Unit-definition AI evaluation](../../manifests/unit-definitions-ai-evaluation.json)
- [Production cost ownership](../../manifests/production-cost-ownership.json)
- [Non-unit production threshold boundary](../../manifests/non-unit-production-threshold-boundary.json)
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Unique Unit combat predicates](../../manifests/unique-unit-combat-predicates.json)
