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

`ProductionItemCostLookup` at `0x82CE2B98` applies this unit formula to item
IDs 0 through 99. `CurrentProductionItemCostLookup` at `0x82CF8308` selects the
current city item at `+0x38` and returns the same unit result. Both route item
IDs 100 through 299 through separate `BuildingWonderProductionCostLookup` at
`0x82CF1278`. IDs 100 through 199 use a signed byte at `+0x41` of `0xCC`-byte
building records rooted at `0x82F71FD8`. Exact records now identify item 101
Barracks with factor 4, item 105 Library with factor 4, and item 114 Courthouse
with factor 8. The helper selects those item IDs with masks `0x2`, `0x20`, and
`0x4000`; cumulative UEA 19, 20, and 18 respectively reduce the composed
signed cost by half with truncation toward zero.

IDs 200 through 299 use a signed halfword at `+0x40` of `0x14C`-byte wonder
records rooted at `0x82F73238`. The helper applies a common signed half-scale
to every item in that range, then applies another signed half reduction when
cumulative UEA 24, Wonders cost half as much, is active. The common scale is
part of the native wonder formula, not UEA 24 itself. Exact records identify
items 200 through 204 as Pyramids of Egypt factor 30, The Great Wall factor 30,
Hanging Gardens of Babylon factor 20, Stonehenge factor 10, and Colossus of
Rhodes factor 20. Items 205 through 209 are Oracle of Delphi factor 25, Great
Library of Alexandria factor 30, The East India Company factor 40, Oxford
University factor 30, and Shakespeare's Theatre factor 30. Each carries
initialized name, short-token, art-token, and
effect-description strings at repeated offsets, but no display consumer or
effect implementation is proved. The remaining building and wonder identities,
complete layouts, adjacent fields, and other modifiers remain unresolved. Cost
locators are in
[`building-wonder-cost-identities.json`](../../manifests/building-wonder-cost-identities.json).
The five wonder records are in
[`wonder-record-identities.json`](../../manifests/wonder-record-identities.json).
The next five and their +0x49 token-boundary guard are in
[`wonder-record-identities-205-209.json`](../../manifests/wonder-record-identities-205-209.json).

A bounded Pyramids consumer packet did not establish an exact item-200 edge to
government availability or state, completion, display, or AI. Exact references
and split-address recovery found one Pyramids record-base materializer, one
technology-table materializer, and one shared technology-helper candidate; all
three exact candidate bodies truncated on bad instruction data. A filtered
item-200 literal/comparison scan then reached its eight-function cap, so those
functions remain unclassified. This is a bounded negative, not a claim that no
Pyramids consumer exists. Exact limits are in
[`pyramids-government-availability.json`](../../manifests/pyramids-government-availability.json).

A separate bounded Great Library packet did not establish an exact item-206
edge to technology ownership or acquisition, completion, display, or AI. Exact
references and split-address recovery exposed only generic technology helpers
and the accepted technology-table materializer. A complete filtered literal
scan emitted three functions; their recovered prefixes were unrelated or had
no Great Library carrier, and all three exact bodies truncated on bad
instruction data. This is a bounded negative, not a claim that no Great
Library consumer exists. Exact limits are in
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
- [Combat resolution lifecycle](../../manifests/combat-resolution-lifecycle.json)
- [Unique Unit combat predicates](../../manifests/unique-unit-combat-predicates.json)
