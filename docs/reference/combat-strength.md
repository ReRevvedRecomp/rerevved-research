# Combat strength

Every fight compares an attack strength with a defense strength. Each starts
from the unit's attack or defense stat, which already includes civilization,
Wonder and scenario bonuses. An Army triples that stat. The result is then
multiplied by a percentage built from points that add together: terrain, city
buildings, Veteran rank, Fortify, Fortress, Great General, special upgrades and
a few penalties. Points add. They never multiply each other, so Veteran and
full Fortify on an Archer give `2 * (100 + 50 + 100) / 100 = 5`, not 6.

This page covers how the two strengths are built. Loss protection, the early
2:1 rule and ratio rules are on the
[Combat loss protection](combat-loss-protection.md) page, and the random draws
that follow are on the [Combat](combat.md) page. All values here are static calculations from the
game code under the stated inputs. They are not observed battles, victory
chances or screen text.

## What changes a strength

| Source | Side | Effect | Details |
|---|---|---|---|
| Base stat | Both | Unit definition value plus civilization, Wonder and scenario terms | [Core stats](#core-stats) |
| Army | Both | Core stat times 3 | [Armies and injuries](#armies-and-injuries) |
| Starting defense | Defender | 100, or 150 in a Palace city, or 200 with Walls or the Great Wall | [Starting points](#starting-points) |
| Terrain | Defender | 100, 150 or 200 points outside a city | [Terrain](#terrain) |
| Attacking from Hills | Attacker | Starts at 150 instead of 100 | [Terrain](#terrain) |
| Veteran rank | Both | +50 points (rank 0 or lower: -50) | [Veteran](#veteran) |
| Fortify | Defender | +50, then +100 points | [Fortify](#fortify) |
| Fortress | Defender | +100 points outside a city | [Fortress](#fortress) |
| Great General | Both | +50 points on its own tile | [Great General](#great-general) |
| River | Attacker | -50 points | [River](#river) |
| Special upgrades | Both | +50 or +100 points for five upgrades | [Special upgrades](#special-upgrades) |
| Barbarian | Both | Attacker halved, defender -50 points | [Other adjustments](#other-adjustments) |
| Support from Sea | Both | Flat strength added after the percentage | [Other adjustments](#other-adjustments) |

## Worked example

A Veteran Archer is fortified in a city on Hills. The city has no Walls and no
Palace, and is not the Great Wall city. A Veteran Warrior attacks from a Hills
tile. Neither side has a civilization, Wonder or scenario bonus.

| Step | Defender (Archer, stat 2) | Attacker (Warrior, stat 1) |
|---|---:|---:|
| Starting points | 150 (city, Hills) | 150 (attacking from Hills) |
| Veteran | +50 | +50 |
| Fortify, second step | +100 | none |
| Total points | 300 | 200 |
| Strength | `2 * 300 / 100` = 6.00 | `1 * 200 / 100` = 2.00 |

The city starting value does not stack with terrain. A city that is not a
Palace city and has no Walls starts at 100, and Hills lifts that to 150. Inside
a city the Fortress bonus is skipped. Other versions of the same defender:

| Change to the defender | Points | Strength |
|---|---:|---:|
| Not Veteran | 250 | 5.00 |
| Fortify order just issued (state 0x06) | 200 | 4.00 |
| First Fortify step done (state 0x0E) | 250 | 5.00 |
| City with Walls, any terrain | 350 | 7.00 |
| Outside the city on Hills with a Fortress | 150 + 100 + 100 + 50 = 400 | 8.00 |
| An Army of such Archers in the Hills city | 300, core `2 * 3` | 18.00 |
| One of three casualty slots lost (single Archer) | 300, weighted 600 less 200 | 4.00 |

Without Hills the Veteran Warrior attacks at `1 * (100 + 50) / 100` = 1.50. A
River penalty would take 50 points off the attacker.

## Core stats

The core stat is the unit's base attack or defense plus modifiers. Two
accessors compute it. `EffectiveUnitAttackLookup` is at `0x82CF2230` and
`EffectiveUnitDefenseLookup` at `0x82CF21A0`. Both take only the player and the
unit type. The attacker or defender role comes from the caller.

Terms are listed below. `Ui` is a civilization bonus (UEA) with ID `i`, from
the [civilization bonus lookup](civilization-bonuses.md). `W10` is the Wonder
index 10 query. `s` is the signed scenario attack term at `0x830E8FFA`.

| Term | Applies to | Value |
|---|---|---|
| `P6` | Attack | 1 when the player word at `0x830ED3D8 + 4*player` is 6 and definition flags & `0x8087` are clear |
| `W10` | Attack | Wonder index 10 query |
| `F6` | Both | `U6`, only for definition flag `0x2` |
| Horsemen and Knights | Attack | `2*U15`, or `U14` when `U15` is not set |
| Phalanx | Attack | `U37` |
| Cannon | Attack | `2*U13` |
| Knights | Attack | `U27` |
| Legion | Attack | `L`, 0 or 1 |
| Scenario term `s` | Attack | Added to every nonzero base attack |
| Archer | Defense | `U61` |

Attack is `0` when the base attack is `0`, with no modifier added. Otherwise
it is base + `P6` + `W10` + `F6` + the type terms + `s`. Defense is base +
`F6` + the Archer term. Nothing clamps a negative result to zero. The Knight
terms are explained in the
[Knight attack finding](../../manifests/unique-unit-combat-predicates.json#/knightAttackModifierBoundary).
The player word that `P6` tests and the Legion term `L` are kept as formulas.
Their game meanings are not named here (see the
[manifest](../../manifests/combat-strength.json#/coreAccessors)).

## Starting points

The defender's percentage starts from one of three values:

| Defender location | Starting points |
|---|---:|
| Barbarian city | 100, and the building and terrain options are skipped |
| City with Walls, or the recorded Great Wall city | 200 |
| Palace city (without those) | 150 |
| Other city | 100, or 150 on Hills |
| Outside a city | Terrain value below, plus 100 for a Fortress |

A Palace does not add 50 on top of Walls. The attacker starts at 100, or 150
when attacking from Hills. If the attacker's definition flag `0x4` is set, only
the Hills start of 150 inside a city and the terrain and Fortress options
outside a city are skipped, and the defender keeps 100 there. Walls, Palace and
Great Wall values are not affected. That flag has no recovered name.

## Terrain

Outside a city, the defender gets `50 * (terrain byte + 1)` points. The byte
is at offset 28 of the terrain record in the table at `0x82F771C8` (stride 29).

| Terrain | ID | Starting points | Archer defense |
|---|---:|---:|---:|
| Sea | 0 | 100 | 2.00 |
| Grassland | 1 | 100 | 2.00 |
| Plains | 2 | 100 | 2.00 |
| Forest | 3 | 150 | 3.00 |
| Hills | 4 | 150 | 3.00 |
| Desert | 5 | 100 | 2.00 |
| Mountain | 6 | 200 | 4.00 |

The Sea row is an arithmetic input only. It does not show that an Archer can
legally defend at Sea. The table also holds Ice Cap 7 and City 8, both with
byte 1. A city uses its own starting value instead of its tile terrain.

Attacking from Hills sets the attack start to 150. This uses the attacker's own
tile, not the target tile. A Warrior then attacks at 1.50, or 2.00 as a
Veteran, before other adjustments.

## Veteran

Rank is a signed byte at unit offset `+0x05`. Both attack and defense add
`50 * clamp(rank - 1, -1, 1)` points. Rank 1 adds nothing, Veteran (rank 2)
adds 50, and higher ranks add the same 50. Ranks of 0 or lower subtract 50.

Buying a special upgrade (command type 22) lowers rank by 1, so an Elite
unit (rank 3) falls to Veteran and keeps the 50 points. The combat result
consumer at `0x82CD7A60` raises rank at `0x82CD85CC` or `0x82CD8BB8`, only
below rank 3. The [special upgrade finding](../../manifests/unit-special-upgrades.json#/veteranGrantPath)
records the path from that rise to the Veteran animation.

## Fortify

Native command 13 is Fortify. It ORs 6 into the unit state word (offset `+0x0C`)
for a unit that is allowed to fortify, or 2 otherwise, and clears bits
`0x88000`. Existing progress is kept, so reissuing the order at state `0x1E`
does not restart it. From a clear state the result is state 6. A unit is allowed when its
definition flags & `0x47` are clear and its attack is less than twice its
defense, which holds for an Archer. The order gives no bonus by itself.

Each later turn start for that player advances the state. The defense reader
gives 50 points at state `0x0E` and 100 points at state `0x1E`:

| Stage | State | Fortify points | Archer on neutral Grassland |
|---|---|---:|---:|
| Before the order | 0x00 | 0 | 2.00 |
| Order issued (from state 0x00) | 0x06 | 0 | 2.00 |
| First advance | 0x0E | 50 | 3.00 |
| Second advance | 0x1E | 100 | 4.00 |

The bonus applies to non-Barbarian defenders only. The selected Move and Combat
preparation paths clear bits `0x1E`, so a unit that moves or attacks starts
over. That is not a check of every wake, attack or save path. Other state
patterns can reach the same reader, so Fortify is not the only way to get the
bonus.

### When the steps happen

The advance counts a player's own turn start processing. It does not count the
turn number. In a game where every player's update completes once per round,
an Archer that fortifies on turn 20 reaches full Fortify at turn 22, and a
Fortress appears at turn 23:

| Event | Turn | State | Fortress | Archer defense |
|---|---:|---|---|---:|
| Fortify order | 20 | 0x06 | Clear | 2.00 |
| First next turn start | 21 | 0x0E | Clear | 3.00 |
| Second next turn start | 22 | 0x1E | Clear | 4.00 |
| Third next turn start | 23 | 0x1E | Set, if its conditions hold | 6.00 |

Against a Warrior with attack 1, the early 2:1 rule covers turn 20 (2 against
1). At turn 21 the defense of 3.00 is not above 3 times 1, so the later strict
test does not protect the Archer. At turns 22 and 23 it does (see
[Combat loss protection](combat-loss-protection.md)).

The timeline holds only under one completed update per player per round. With
two human players, the second player's Archer can advance while the game turn
stays the same. Command routing, the human mask and reload paths are in the
[manifest](../../manifests/combat-fortification-terrain.json#/beginTurnTiming).

## Fortress

A Fortress is tile flag `0x40`. It adds 100 defense points for a defender
outside a city. It is separate from the unit's own Fortify points. The turn
start code sets the flag on the unit's tile when all of these hold:

- The unit already has state bit `0x10` (second Fortify step done) when the
  update starts.
- The tile is not a city.
- The definition's base defense is at least its base attack, and is not 0.
  Warriors (1/1) and Archers (1/2) pass. Catapults (4/1) do not.
- The unit's owner is not the Barbarian owner.

The flag is set before the Fortify advance in the same update. A new second
step cannot set it in that update, so the Fortress appears on the update after
full Fortify. The Archer in the table above reaches
`2 * (100 + 100 + 100) / 100 = 6.00` at turn 23.

## Great General

When a Great General (unit type 30) stands on a land tile, a recount sets tile
flag `0x200` on that tile. In a fight each participant gains 50 points when its
own tile has the flag and its definition flags & `0x6` are clear. The flag on
one tile does not affect the other side.

The code that sets the flag checks for the Great General's definition flag
`0x8000` and for non-Sea terrain. It has no test for attachment to a carrier or
for a second unit on the tile. An Archer sharing the tile can therefore receive
the 50 points. The active map reset masks tile flags with `0xF4FB`, which clears `0x200` and
keeps `0x40`. A flag shows a current General only when the reset and then the
recount ran for that tile and nothing changed it before the fight. See the
[attachment finding](../../manifests/great-general-attachment-lifecycle.json).

## River

The River modifier takes 50 points off the attacker. It does not halve the
finished strength: a Veteran Warrior attacking from Hills has
`1 * (150 - 50 + 50) / 100` = 1.50.

| Warrior | Without River | With River |
|---|---:|---:|
| Rank 1, neutral land | 1.00 | 0.50 |
| Veteran, neutral land | 1.50 | 1.00 |
| Rank 1, Hills origin | 1.50 | 1.00 |
| Veteran, Hills origin | 2.00 | 1.50 |

The penalty is skipped when any bit of attacker definition flags & `0x00200006`
is set. A Catapult has flags `0x00200028`, so it never gets the penalty.

The code checks eight directions using paired edge bits on the tile plane
`0x8311F690`. A cardinal attack needs its one matching edge. A diagonal attack
needs both of its two edges, and either edge can come from a river edge or a
Sea tile beside the path. Two Sea flank tiles alone can trigger it, with no
river drawn. A single Sea flank does not. The label text calls the modifier
River, but the check also fires for some Sea adjacency cases, so it does not
identify visible rivers. The full predicate and case table are in the
[manifest](../../manifests/combat-fortification-terrain.json#/river).

## Armies and injuries

An Army triples the core stat for each side. Strength is then
`core * points`, in hundredths. Injury removes a share of that value:

```text
n = figure slots in the definition mask (3 for Warrior and Archer)
h = injured slots in the casualty halfword
remaining = W - trunc(h * W / n)
```

One of three slots lost leaves two thirds, rounded up in hundredths:
a Warrior 1.00 becomes 0.67, an Archer 2.00 becomes 1.34 and an Archer Army at
6.00 becomes 4.00. These are internal slots. They are not the displayed health
bar segments or single Army members.

The random figure selection later uses a different weight, built from the
uninjured value and the definition mask. See the
[manifest](../../manifests/combat-strength.json#/casualties) and
[Combat](combat.md).

## Special upgrades

Five of the nine special upgrades add points in two helper loops
(`0x82CFC0A8` for attack and `0x82CFBED0` for defense). They read the upgrade
word at unit offset `+0x10`.

| Upgrade | Side | Points | When |
|---|---|---:|---|
| Infiltration | Attack | +50 | The target tile is a city whose tile owner is not the Barbarian owner |
| Guerilla | Attack | +50 | The territory byte at the defender's tile equals the attacker's owner |
| Loyalty | Defense | +50 | The territory byte at the defender's own tile equals the defender's owner |
| Engineer | Defense | +100 | The defender's tile is a city |
| Leadership | Defense | +100 | The weighted presence on the defender's tile is above 1 |

Several apply together. Weighted presence counts a unit as 1 and an Army as 3,
so Leadership can apply to a lone Army. Territory equality is the proved test.
No separate home or enemy territory rule has been added. Blitz, March, Medic
and Scout add no points. The
[upgrade finding](../../manifests/unit-special-upgrades.json) lists storage,
grant and each upgrade's status.

## Other adjustments

- Barbarians: a Barbarian attacker halves its current percentage. A Barbarian
  defender loses 50 points. A Barbarian city starts at 100 and skips Walls,
  Palace and terrain.
- Sea attackers: an attacker on Sea terrain whose definition flags & `0x6` are
  clear has its percentage halved. On non-Sea defender terrain, definition
  flag `0x2` halves that unit's core stat.
- Support from Sea: units with definition flag `0x2` on a Sea tile next to the
  defender, except types 19 and 20, add flat strength (not percentage points).
  The scan runs only when the defender is not on Sea and its definition flag
  `0x4` is clear. Each candidate counts its effective attack times its Army
  factor times (rank + 1), divided by 2 with UEA 51 and by 4 without it.
- Local player assist: in a real battle and in the numbers prepared for the
  battle panel (modes 0 and 2, not the AI prediction call), the local player
  gains 100 points when the word at `0x82FFE7C8` is 0 and 50 when it is 1. The
  [AI options page](ai-options.md#multiplayer-ai-difficulty) records the word
  as the difficulty word, where 0 and 1 are Chieftain and Warlord.
- Technology query: in a real battle, a side that is not Barbarian can have
  its strength halved after support. The code reads the definition's
  technology field and checks technology availability for the opponent.

The flag meanings (`0x2`, `0x4`, `0x6`, `0x8000`) are not named in the
[unit definitions page](unit-definitions.md).

## How the code does it

`CombatResolve` (`0x82CD9970`) runs the stages in order. Later stages work on
the result of earlier ones, so they cannot be reordered. `pA` and `pD` are the
attack and defense percentages. The first column gives each stage's start. The
[manifest](../../manifests/combat-strength.json#/resolverStages) has the full
conditions.

| Stage | Start | What it does |
|---:|---|---|
| 1 | `0x82CD9EC4` | Sets `pA` and `pD` to 100 |
| 2 | `0x82CD9EF8` | Scans the eight neighbor tiles for Sea support |
| 3 | `0x82CDA1D4` | Scales support by the word at `0x830E8FDC` |
| 4 | `0x82CDA200` | Reads both core stats |
| 5 | `0x82CDA27C` | Triples cores for Armies |
| 6 | `0x82CDA2EC` | Sets the defender's starting points |
| 7 | `0x82CDA5F0` | Hills attack start, Barbarian halving and -50 |
| 8 | `0x82CDA748` | River -50 |
| 9 | `0x82CDAA4C` | Great General +50 for each side |
| 10 | `0x82CDAB9C` | Special upgrade points |
| 11 | `0x82CDAC50` | Rank points |
| 12 | `0x82CDAE2C` | Fortify points (100 or 50) |
| 13 | `0x82CDAF04` | Sea attacker halving, flag `0x2` core halving |
| 14 | `0x82CDB0F8` | Local player assist |
| 15 | `0x82CDB390` | Core times percentage, plus 100 times support |
| 16 | `0x82CDB460` | Technology query halving in a real battle |

Casualty reductions follow at `0x82CDB548`. The final value for each side is:

```text
W0 = B * p + 100 * F
W  = W0 / 2 (toward zero) when a real battle and the technology query applies
R  = W - trunc(h * W / n)
```

The native code uses 32 bit wrapping arithmetic and rereads inputs between
calls. The formulas assume the inputs stay unchanged between those reads.

## Addresses

| Item | Address or offset |
|---|---|
| Unit table | `0x830F2BF0`, stride `0x54` |
| Owner, type, army, rank | `+0x00`, `+0x01`, `+0x04`, `+0x05` |
| State word, special upgrades | `+0x0C`, `+0x10` |
| Coordinates, casualties | `+0x1C` and `+0x1E`, `+0x52` |
| Unit definition table | `0x82F700D8`, stride `0x94` |
| Base attack, defense | `+0x40`, `+0x41` |
| Definition mask, technology query, flags | `+0x48`, `+0x4E`, `+0x50` |
| Terrain plane, terrain table | `0x8312B288`, `0x82F771C8` |
| Fortify command, calendar advance | `0x82CE04E8`, `0x82D1EAB0` |
| Fortify reader, Fortress reader | `0x82CDAE2C`, `0x82CDA5AC` |
| Great General publisher, reader | `0x82D11AD8`, `0x82CDAA4C` |
| River plane, flag | `0x8311F690`, `0x8312E60C` |

## Limits and open questions

- Nothing here was observed in a running game. The values come from decoded
  game code and formula replays.
- Percentage points add. The page does not claim a final multiplier for any
  single bonus.
- The meanings of the player word behind `P6`, the Legion term `L` and the
  definition flags are not recovered.
- The tile plane addresses behind Infiltration, Engineer and Leadership are
  not recorded.
- Fortify progress counts player updates. Whether the game delivers exactly
  one update per round in real play is not shown.
- The River check is exact, but how every visible river reaches it is open.
- Natural battles on the example tiles, display of these values and save or
  multiplayer behavior are not covered.

## Evidence

- [Combat strength](../../manifests/combat-strength.json): stages, core stats,
  special upgrade points, injuries.
- [Fortify, terrain and tile modifiers](../../manifests/combat-fortification-terrain.json):
  terrain, Fortify timing, Fortress, Great General, River.
- [Special upgrades](../../manifests/unit-special-upgrades.json)
- [Knight and AI combat roles](../../manifests/unique-unit-combat-predicates.json)
- [Combat outcome](../../manifests/combat-outcome.json)
