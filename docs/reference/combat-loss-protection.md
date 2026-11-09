# Combat loss protection

Combat loss protection lets the battle resolver throw away a random result that
would wipe out one side, and draw again. It is a filter on the outcome. It does
not hand anyone the win, and it does not change the strengths shown on the
battle screen.

Which side is protected depends on the strength ratio, the turn, who controls
each side, whether the defender sits in a city or is a Barbarian, and a few
unit state checks. [Combat](combat.md) explains how a battle is decided.
[Combat strength](combat-strength.md) explains how each side's strength is
built. This page covers the protection rules, the retry that enforces them,
the proof that a protected Catapult cannot run out of retries, and what the
result does to the units afterward.

The examples below use exact internal strengths written in familiar attack and
defense points, with the base values from the unit definitions and no modifier.
They are illustrations of the rules, not observed battles. Real battles add
terrain, rank, city and other modifiers first, so use the strength page to get
the actual pair. Evidence is in
[combat-ratio-protection.json](../../manifests/combat-ratio-protection.json),
[combat-catapult-retry-bounds.json](../../manifests/combat-catapult-retry-bounds.json),
[combat-victory-survival.json](../../manifests/combat-victory-survival.json)
and [combat-outcome.json](../../manifests/combat-outcome.json).

## Which battles are protected

In this page, "human" means a human-controlled civilization and "computer"
means an AI civilization. "Ratio" means effective attack strength divided by
effective defense strength at the check, after the combat modifiers and the
casualty reduction. It is not a count of units and not a displayed chance to
win.

| Situation | Test | Protects |
|---|---|---|
| Any attacker, through turn 20 | Attack at least 2 times defense | Attacker |
| Any defender, through turn 20 | Defense at least 2 times attack | Defender |
| Attacker after turn 20, against a civilization | Attack more than 3 times defense | Attacker, with the extra requirement below |
| Attacker after turn 20, against Barbarians | Attack more than 2 times defense | Attacker, with the extra requirement below |
| Human defender after turn 20, outside a city, against a civilization | Defense more than 3 times attack | Defender |
| Human defender after turn 20, in a city or against Barbarians | Defense more than 2 times attack | Defender |

The extra requirement for the attacker is that the attacker is human, or the
turn is below 30, or the attacker override word is nonzero (see
[the override](#the-override-word)). Computer defenders get no protection from
the strict rules.

Two requirements apply to every strict row. The protected side must have no
recorded casualties in its low three casualty bits (the field is the unit's
`+0x52` halfword, and a zero record always passes). And the test is strict: at
exactly 3 times, the strict 3 times rule does not fire.

There is no 4:1 or 5:1 step. A battle at 4:1 or 5:1 uses the same strict 3
times rule, as long as its other requirements hold. Failing one row means only
that the row adds nothing; another row, or the human safeguard below, can still
add protection.

For whole numbers, the same tests read as a minimum strength for the protected
side against an opposing strength S:

| Rule | Minimum protected strength |
|---|---|
| Early inclusive 2:1 | 2*S |
| Strict 2:1 | 2*S + 1 |
| Strict 3:1 | 3*S + 1 |

One internal unit need not equal one displayed point. Battle screen numbers
drop low digits, so a visible ratio can hide a threshold (see
[displayed strengths](combat.md#displayed-strengths)).

### Which side is protected, by turn

Using no override, no safeguard word, battle participants that are not
Barbarian, a city flag that is clear and no casualties:

| Turns | Attacker protection | Defender protection |
|---|---|---|
| 0 through 20 | Attack at least 2 times defense, human or computer | Defense at least 2 times attack, human or computer |
| 21 through 29 | Attack more than 3 times defense, human or computer | Defense more than 3 times attack, human defender only |
| 30 onward | Attack more than 3 times defense, human attacker only | Defense more than 3 times attack, human defender only |

The game tests the turn number, not the displayed year. On the standard
calendar turn 20 is 2000 BC, turn 30 is 1000 BC, and turns 19, 20 and 21 are
2100 BC, 2000 BC and 1900 BC. A loaded game with another turn and year pairing
must be judged by the turn.

### Worked examples

These rows use base unit stats (Warrior 1 and 1, Archer 1 and 2, Horsemen 2
and 1, Catapult 4 and 1, Cannon 6 and 2, Riflemen 3 and 5, Tank 10 and 6, each
as attack and defense, and Barbarians 1 and 1). Defenders are outside cities
unless stated. Casualty fields are zero and the override is zero.

| Battle | Turn | Protected side | Why |
|---|---|---|---|
| Horsemen (attack 2) attack Warrior (defense 1), any controller | 15 | Attacker | 2 is at least 2*1 |
| Same battle | 25 | Nobody | 2 is not more than 3*1 |
| Warrior (attack 1) attacks Archer (defense 2), any controller | 15 | Defender | 2 is at least 2*1 |
| Same battle | 25 | Nobody | 2 is not more than 3*1 |
| Catapult (attack 4) attacks Archer (defense 2) | 15 | Attacker | 4 is at least 2*2 |
| Same battle | 25 | Nobody | 4 is not more than 3*2 |
| Cannon (attack 6) attacks Archer (defense 2) | 25 | Nobody | Exactly 3:1 fails the strict test |
| Catapult attacks Warrior (defense 1) | 25 | Attacker, human or computer | 4 is more than 3*1 and the turn is below 30 |
| Same battle | 35 | Attacker only if human | 4 is more than 3*1, but the date test for computer attackers ended at turn 29 |
| Human Catapult attacks Catapult (defense 1) | 35 | Attacker | 4 is more than 3*1; this pairing is also the proved case in [Catapult guarantee](#catapult-guarantee) |
| Human Riflemen (attack 3) attack Barbarian (defense 1) | 35 | Attacker | 3 is more than 2*1 against Barbarians |
| Same Riflemen attack a Warrior (defense 1) | 35 | Nobody | 3 is not more than 3*1 |
| Human Horsemen (attack 2) attack Barbarian (defense 1) | 35 | Nobody | 2 is not more than 2*1 |
| Warrior attacks human Riflemen (defense 5) | 35 | Defender | 5 is more than 3*1 |
| Horsemen attack human Riflemen outside a city | 35 | Nobody | 5 is not more than 3*2 |
| Horsemen attack human Riflemen in a city | 35 | Defender | 5 is more than 2*2 in a city |
| Horsemen attack human Tank (defense 6) | 35 | Nobody | 6 is not more than 3*2 |
| Warrior attacks computer Riflemen | 35 | Nobody | After turn 20 only human defenders get strict protection |
| Barbarian (attack 1) attacks human Archer (defense 2) | 35 | Nobody | 2 is not more than 2*1 |

Injured units fail the strict rows even at a large ratio. A human defender at
4.00 against attack 1.00 after turn 20 passes the ratio test, but gets no strict
protection if one of its three base casualty bits is set. The early rule has no
casualty requirement. The checked bits are the stored casualty record, so they
differ from the raw army selection masks: for a supplied raw army casualty
count of one, the result consumer stores zero base casualties.

### Worked examples with modified strengths

[Combat strength](combat-strength.md) shows how each pair below is built. The
rows give only the finished strengths and the protection result. Unless a row
says otherwise, the battle is after turn 20, the protected side is human, both
civilizations are not Barbarian, casualties are zero, both tiles are Grassland
and the defender is outside a city. The override and the safeguard word are
off. "None" means no protection from these rules, not a predicted defeat. A
row marked "slot" has one of the three base casualty bits set.

| Battle | Attack : defense | Result |
|---|---|---|
| Veteran Warrior attacks Warrior | 1.50 : 1.00 | None: 1.5 is not more than 3*1 |
| Warrior Army attacks Warrior | 3.00 : 1.00 | None: exactly 3:1 fails the strict test |
| Wounded Warrior (1 slot) attacks Warrior, turn 20 or earlier | 0.67 : 1.00 | None: neither side reaches 2:1 |
| Warrior attacks Archer in a Palace city | 1.00 : 3.00 | Defender: 3 is more than 2*1 in a city |
| Veteran Warrior attacks Archer in a Palace city | 1.50 : 3.00 | None: exactly 2:1 |
| Veteran Warrior attacks Veteran Archer in a Palace city | 1.50 : 4.00 | Defender: 4 is more than 2*1.5 |
| Warrior attacks Archer in a walled city | 1.00 : 4.00 | Defender |
| Warrior attacks Veteran Archer in a walled city | 1.00 : 5.00 | Defender |
| Warrior Army attacks Archer Army outside a city | 3.00 : 6.00 | None: 6 is not more than 3*3 |
| Warrior Army attacks Veteran Archer Army in a walled city | 3.00 : 15.00 | Defender: 15 is more than 2*3 |
| Warrior attacks wounded Archer (1 slot), turn 20 or earlier | 1.00 : 1.34 | None: neither side reaches 2:1 |
| Warrior attacks wounded Archer Army (1 slot), turn 20 or earlier | 1.00 : 4.00 | Defender: the early rule has no casualty requirement |
| Same battle after turn 20 | 1.00 : 4.00 | None: 4 is more than 3*1, but the casualty bits are not clear |
| Warrior attacks Archer in Forest | 1.00 : 3.00 | None: field defense needs more than 3*1 |
| Same, first Fortify advance | 1.00 : 4.00 | Defender |
| Warrior attacks Archer on Mountain | 1.00 : 4.00 | Defender |
| Warrior attacks Archer on Grassland, first Fortify advance | 1.00 : 3.00 | None |
| Same, full Fortify, no Fortress | 1.00 : 4.00 | Defender |
| Warrior attacks Archer on a Fortress, no Fortify | 1.00 : 4.00 | Defender |
| Warrior attacks fully fortified Archer on a Fortress | 1.00 : 6.00 | Defender |
| Warrior attacks fully fortified Veteran Archer in a walled city | 1.00 : 7.00 | Defender: 7 is more than 2*1 |
| Warrior Army attacks fully fortified Veteran Archer Army in a walled city | 3.00 : 21.00 | Defender: 21 is more than 2*3 |
| Warrior attacks Archer with a Great General marker on its tile | 1.00 : 3.00 | None |
| Same, first Fortify advance | 1.00 : 4.00 | Defender |
| Warrior attacks Warrior from Hills | 1.50 : 1.00 | None |
| Warrior crosses the River edge to attack Archer | 0.50 : 2.00 | Defender: 2 is more than 3*0.5 |
| Veteran Warrior crosses the River edge | 1.00 : 2.00 | None: field defense is only 2:1 |
| Veteran Warrior from Hills crosses the River edge | 1.50 : 2.00 | None |
| Catapult crosses the River edge to attack Archer | 4.00 : 2.00 | None: the Catapult definition skips the River penalty, and 4 is not more than 3*2 |

A Fortress or a Fortify bonus does not make a tile a city. Forest, Mountain and
a Fortress on their own are field defense and need more than 3 times the
attack. A Great General counts only when its marker is on the defender's own
tile. The 3:1 failures are strict comparisons, not predicted outcomes. The all
state guarantee for a single Catapult does not extend to these Army and
multi figure rows.

## The early rule

The resolver tests the current turn against 20 at `0x82CDC138..0x82CDC140`, so
the early rule includes turn 20. For positive internal operands A and D
without overflow, A at least 2*D sets attacker protection and D at least 2*A
sets defender protection. These operands include the weighting and mask
reductions, and their equality with displayed values is not proved. The tests
do not check human or computer control, difficulty or network mode. A failed
test leaves any protection already set.

| Turn | Standard year | Early rule |
|---|---|---|
| 19 | 2100 BC | Runs |
| 20 | 2000 BC | Runs |
| 21 | 1900 BC | Skipped |

Skipping the early rule does not remove protection after turn 20. The strict
rules and the human safeguard still apply.

## The human safeguard

A separate rule at `0x82CDC174..0x82CDC1EC` adds protection for each side that
is human. It needs that civilization's signed word in the array at
`0x830E45E4` to be at least 1, and the side's strength to be more than the
other side's strength divided by two, rounded toward zero. With a word of 1 or
more, a human side is protected whenever its strength is more than half of its
opponent's, which is far below a 2:1 ratio. The word's
meaning, its writers and its live values are all unknown. It is not a
difficulty, luck or experience value so far as the code shows. Confidence in
this rule is `candidate`.

## The override word

The word at `0x830E4554` is reached through frame word 268. Its name is
unknown. When it is nonzero, the strict attacker rule stays available to
computer attackers after turn 29, and the selection step forces value 1, which
removes a defender figure (see [Forced attacker selection](#forced-attacker-selection)).

## Cancellation and Militia

After all rules have run, `0x82CDC1F4..0x82CDC208` clears both flags if both
sides are protected. Then `0x82CDC20C..0x82CDC21C` clears defender protection
when the defender is a Militia (unit type 7). A Militia defender that gained
protection can therefore cancel the attacker's protection before losing its own.

## Complete formula

This is the formula for the protection block, for positive strengths without
signed overflow and stable participant and state values.

| Symbol | Meaning |
|---|---|
| A, D | Effective attack and defense at the protection check |
| T | Current game turn, not the displayed year |
| HA, HD | Attacker or defender is human |
| BA, BD | Attacker or defender is the Barbarian player (global `0x82F700B0`) |
| C | Defender's tile has the city flag (tile plane bit 0) |
| CA, CD | Attacker or defender has all three checked casualty bits clear |
| O | The override word |
| QA, QD | Each civilization's safeguard word |
| M | Defender is a Militia |

```text
attackMultiplier  = 2 if BD else 3
defenseMultiplier = 2 if BA or C else 3

earlyAttack  = (T <= 20) and (A != 0) and (A >= 2*D)
earlyDefense = (T <= 20) and (D != 0) and (D >= 2*A)

strictAttack  = (HA or T < 30 or O != 0) and CA and (A > attackMultiplier*D)
strictDefense = HD and CD and (D > defenseMultiplier*A)

humanAttack  = HA and (QA >= 1) and (A > trunc(D/2))
humanDefense = HD and (QD >= 1) and (D > trunc(A/2))

rawAttack  = earlyAttack  or strictAttack  or humanAttack
rawDefense = earlyDefense or strictDefense or humanDefense

protectAttack  = rawAttack  and not rawDefense
protectDefense = rawDefense and not rawAttack and not M
```

`trunc` rounds toward zero. The city flag is bit 0 of the tile plane at the
defender's coordinates, not a unit type or a city object query. The setters are
`0x82CDBFC4..0x82CDC068` (strict attacker), `0x82CDC06C..0x82CDC134` (strict
defender), `0x82CDC138..0x82CDC170` (early), `0x82CDC174..0x82CDC1EC` (human
safeguard), then cancellation and Militia as above. The early additions do not
need the strict rules' classifier, Barbarian, city or casualty conditions.

The code after `0x82CDC220` has no more protection flag changes and no other
turn test. Its history tests, weight transforms and army divisions are not a
protection ladder. An unexpanded arithmetic child at `0x827F20F8` (called at
`0x82CDC318`) is the one scalar the direct read did not cover.

No unconditional winner formula follows. A protected side is not proved to
survive every legal battle and random state.

## What a protected battle does

The resolver picks which side loses a figure, one figure per round, until a
side has none. After a completed selection, if the protected side lost every
figure (attacker protection with the attacker mask 0, or defender protection
with the defender mask 0), `0x82CDC7B0..0x82CDC7CC` sends the resolver back to
select again.

- The shared retry counter at `r29` starts at 0 (`0x82CDC444` is `li r29,0`).
  Each protected rejection adds one at `0x82CDC7D0`.
- Once the counter reaches 1000 (`0x82CDC7D4` and `0x82CDC7D8`), protection no
  longer rejects. Below 1000, `0x82CDC7DC..0x82CDC7F0` restores the two saved
  participant `+0x52` halfwords and clears selection history bit 0x2, and
  `0x82CDC7F4` jumps to `0x82CDC45C`, where 18 stores of 8 bytes reset the
  144 byte selection array.
- The retry skips `0x82CDC444` and the generator loads at
  `0x82CDC448..0x82CDC458`. It keeps the counter and the stepped generator
  state. It does not reseed and does not repeat the same draw. Every retry uses
  new draws.
- Because `0x82CDC444` sets the counter to 0 before selection, the first
  protected rejection goes from 0 to 1 whatever the attack strength. Raising
  attack strength cannot skip the first retry.
- `0x82CDC788..0x82CDC7AC` uses the same counter for a separate rejection
  before the protection test. The cardinality checks at `0x82CDC7F8..0x82CDC878`
  can also retry without the 1000 limit. So 1000 is not a count of draws and not
  a count of whole battle attempts.
- At a reached exit (`0x82CDC880..0x82CDC8AC`) the stepped generator state and
  counter are published. A temporary mask or the first selected pair is not a
  persistent winner.

### From final masks to a defeated unit

The suffix that follows writes definition bits XOR the final remaining masks to
the real participants' `+0x52` halfwords at `0x82CDD690..0x82CDD72C`. An Army's
definition repeats at bit offsets 0, 3 and 6. The restoration arm at
`0x82CDD574` is excluded. A zero helper return at `0x82CDD4B0`, when reached,
is a condition.

At `0x82CDD5B4..0x82CDD5D8` the result payload carries actor casualties in the
low 12 bits, defender casualties in the high 12 bits and `0x01000000`. The
local command 1 and 42 bridge delivers it to `0x82CD7A60`. That consumer turns
army casualty counts into base casualties (divisor 3 at `0x82CD7C8C`), tests
actor exhaustion at `0x82CD7E68..0x82CD7EE8` and can reach the original actor
retirement at `0x82CD83D8`. This needs the same record, the same participants
and unit generations, a kept frame and normal returns. A defender casualty
count of zero alone does not prove survival.

Cap example. Starting the loop at counter 0 with the file generator values
(state 7, modulus 4294954991, scale bits `0x3DF0000301109066`), supplied
comparison weights 0 and 1, protection 1 and 0, and masks `0x49` and 7, the
resolver rejects 1000 times (3000 comparison draws, 3000 accepted ordinal draws,
13679 ordinal misses and one publication draw, 19680 draws in all). The final
masks are 0 and 7, the payload is `0x01000049` and the army conversion gives
1 actor casualty, which reaches original actor defeat. This shows that the cap
can pass exhaustion to the result. It is an arithmetic loop test, not a battle
a player can reach: the supplied zero comparison weight does not follow from
the positive inputs described next.

A finite corpus of 50176 cases (64 seeds, 14 nonempty masks per side and 4
positive weight settings of 2:1, 1:2, 3:1 and 1:3) never reached the cap. Its
largest counter was 213 and its longest run was 2869 draws. A corpus is not an
all state guarantee.

### Positive inputs and the zero weight example

For a positive weighted strength W, definition figure count n and a wounded
count h below n, the early comparison uses `ceil(W*(n-h)/n)`, which is between
1 and W. That reduction changes the ratio register, not the weighted frame
word. The late transforms use W: definition 1 triples it, definition 6 adds
`trunc(W/2)`, and any other byte keeps W. A nonzero army byte then divides by 3.

For a definition 1 Army actor with no wounds and 1 <= WA <= 715827882, the
early operand equals WA and the late weight is `trunc(3*WA/3)`, which is
WA and positive. That excludes the supplied zero weight of the cap example.
The Knight (type 13, definition byte 6 at `0x82F708A4`) gives a second case:
with valid wounds and positive early 2:1, WA is at least 2, and for WA up to
1431655765 its late Army weight is at least 1. The rank adjustment contributes
only -50, 0 or 50. A further 1088 correlated cases (byte 1 and byte 6
definitions) never reached the cap, with a largest retry of 4 and 104 draws.
This does not prove all legal strength ranges or all random states.

## Catapult guarantee

For one fixed case the retry cap is proved never to stop a protected win:
a human Catapult attacking another civilization's Catapult after turn 20, with
single units, no casualties and neutral modifiers. Strength 4.00 against 1.00
is a 4:1 ratio, so strict attacker protection applies.

| Question | Answer |
|---|---|
| Can the protected attacker reach the 1000 rejection cap? | No. At most 15 selections are rejected before a winning one, in at most 16 attempts and 2801 draws. |
| Which starting states are covered? | All 4294967296 state words and any draw counter word, with the stated modulus and scale kept. |
| What is the exact 4:1 bound? | At most 12 rejections, 13 attempts and 2276 draws, for late weights 1200 and 300. |

The 15 rejection row holds for any late attack above 3 times the defense, so
it covers more than 4:1. The bounds are upper limits, not tight maxima. They
cover single units only: no Army, no wounded record, no other definition mask,
no other generator parameters, no other override and no changed participant
generation. They are not probabilities and not a proof about whole battles.

### How the bound is built

The kernel starts at `0x82CDC444` with counter 0, masks 1 and 1, protection 1
and 0, override 0, history 0 and 0, and army bytes 0 and 0. The generator keeps
modulus 4294954991 and scale bits `0x3DF0000301109066`. The source has both
units as Catapults (UnitType 16, attack 4, defense 1) on Grassland at rank 1,
with weighted and wound reduced strengths 400 and 100 and late weights 1200 and
300. The factor 7 route at `0x82CDB75C` stores the zero override through
`0x830E4554` at `0x82CDB7BC`. The manifest lists every source condition.

Each attempt draws one comparison and then searches for ordinal bit 0. A losing
comparison removes the attacker figure, adds one to the counter and retries
without reseeding. A winning comparison removes the defender figure. The
unfolded sequence `F0` (multiplier 214013, increment 2531011, 32 bit wrap) has
full period, so every 32 bit state appears once in its cycle. The game's
generator `F` is `F0` folded at the modulus 4294954991. Its outputs stay below
the modulus, so it cannot visit every 32 bit state. It follows the `F0` cycle
exactly until a value reaches the folded range, and the fold lands on a state
that wins the next comparison. A scan of the whole `F0` cycle finds the longest
run of adverse results, and that run gives the bounds above for any starting
state word. Two numbers matter: K, the longest run of
consecutive adverse states, and J, the longest run of ordinal misses. The
bounds are at most K + 1 rejections, K + 2 attempts and (K + 2)*(J + 2) + 1
draws.

### Verifier

The scan is published as `tools/audit-combat-rng-period.ps1`. Run
`pwsh -NoProfile -File tools\audit-combat-rng-period.ps1 -SelfTest` for the
small checks. Use `-Case above-three-to-one` or `-Case exact-four-to-one` for a
full scan of all 2^32 states.

| Case | Loss threshold | Adverse states | K | J | Rejections | Attempts | Draws |
|---|---:|---:|---:|---:|---:|---:|---:|
| `above-three-to-one` | 3221216243 | 119303191 | 14 | 173 | 15 | 16 | 2801 |
| `exact-four-to-one` | 3435963993 | 95442550 | 11 | 173 | 12 | 13 | 2276 |

Both scans visit 4294967296 states, of which 477217222 are eligible, and both
end at state 0. The loss threshold for any strict strength above 3 times is a
conservative bound: a state below it cannot lose, and the real loss states are
a subset above it. The manifest gives the exact arithmetic.

### Forced attacker selection

When the override word is nonzero, the selection step replaces the drawn
comparison value with 1, which removes a defender figure. On the default
route, `0x82CDB774` and `0x82CDB778` compare the source attack with 7 times the
source defense, and equality reaches the nonzero path. Two examples give a
first attempt win within 176 draws for every starting state:

| Attacker against a Catapult on Grassland | Source operands | Late weights | Initial masks |
|---|---|---|---|
| Veteran Catapult attacking from Hills | 800 and 100 (strength 8) | 2400 and 300 | 1 and 1 |
| Catapult Army attacking from Grassland | 1200 and 100 (strength 12) | 1200 and 300 | `0x49` and 1 |

The strength page explains how 8 and 12 arise. The 176 draw bound is 174
ordinal draws plus one comparison draw plus one publication draw. It is not a
new 7:1 protection step. It is a separate effect of the override.

## Victory and survival

A winning selection leaves the winner's figure mask nonempty and the loser's
empty. An applied victory means the result marks the original losing unit dead
while the original winner stays alive. Original unit survival means the same
occupied record, owner and type remain with the dead bit clear at the stated
consumer return. It does not mean unchanged rank, no wounds, or survival of
later battles.

In symbols: if K holds (the fixed source and kernel conditions of a proved
selection case) and L holds (the same final masks and unit generations through
human writeback, the matching result record reaching the consumer, valid
disjoint memory and finite normal helper returns), then a winning selection is
applied to the original units, and the original attacker is alive and the
original defender dead at consumer return. A rounded battle screen ratio is not
enough to pick a row. The internal values and the row's conditions must match.

### Returned winners keep a figure

For any definition mask B in bits 0 through 2, a returned winner keeps at least
one figure slot. A single unit has the full figure mask B. An Army has
`E = B | (B << 3) | (B << 6)`, nine raw figures for a mask of 7. At the end of
a fight the human writeback packs `rawCasualties = E XOR remainingMask`. For an
Army winner with r raw figures left and n base slots:

```text
rawLosses = 3*n - r
baseCasualties = floor((rawLosses + 1)/3)
r >= 2 implies baseCasualties <= n - 1
```

After the capped rejection checks, `0x82CDC7F8..0x82CDC87C` retries a sole
Army winner with at most one raw figure left. These retries have no counter
limit. So a returned Army winner has at least 2 raw figures, and the consumer
cannot rebuild the full definition mask for a winner. This does not prove that
every Army fight terminates.

For Warrior (type 6) and Archer (type 9), both with mask 7 (three base slots):

| Raw figures left | Raw losses of 9 | Base casualty slots | Resolver treatment |
|---:|---:|---:|---|
| 9 | 0 | 0 | Passes the cardinality check |
| 8 | 1 | 0 | Passes |
| 7 | 2 | 1 | Passes |
| 6 | 3 | 1 | Passes |
| 5 | 4 | 1 | Passes |
| 4 | 5 | 2 | Passes |
| 3 | 6 | 2 | Passes |
| 2 | 7 | 2 | Passes, one base slot remains |
| 1 | 8 | 3 if supplied | Retried, never returned as a result |

These are developer quantities. They are not counts of separate unit records or
displayed health pips. The same limit excludes the one slot Catapult Army
example, where full mask `0x49` with one figure left would give base casualty 1.

### What is proved for each battle

The rows use a human attacker after turn 20 against a civilization that is not
the Barbarian player, healthy units and no modifiers except those named.

| Matchup | Strength | Why the selection wins | Applied result |
|---|---|---|---|
| Catapult attacks Catapult | 4.00 to 1.00 | Ratio protection with override 0: all 4294967296 starting states win in 13 attempts or fewer | Attacker survives with 0 casualties, defender is marked dead |
| Veteran Catapult attacks from Hills | 8.00 to 1.00 | The override forces the attacker's selection: first attempt, 176 draws or fewer | Attacker survives with 0 casualties, defender is marked dead |
| Catapult Army attacks Catapult | 12.00 to 1.00 | Same override: first attempt, 176 draws or fewer | Army survives with 0 base casualties, defender marked dead |
| Horsemen attack Warrior, turn 20 or earlier | 2.00 to 1.00 | Early protection is proved. A winning selection for all states is not. | No survival proof |
| Warrior Army attacks a fully fortified Veteran Archer Army in a walled city, after turn 20 | 3.00 to 21.00 | Defender protection is proved. Termination for all states is not. | The returned winner casualty limit applies. The whole pairing is open. |

Survival for the three Catapult rows rests on the result consumer. Its
strict local profile covers the real native Catapult definition, a supplied
32 by 32 map at turn 21 with two live units, and the human writeback of payload
`0x01001000`. It proves that the helper writes, the synchronous delivery of
the same battle's result, and the consumer's return keep the attacker alive and
the defender dead, without needing any later queue pump or turn.

| Engine situation | What is proved | Condition that remains |
|---|---|---|
| The same battle result is applied locally | Command 42's result is consumed. The attacker is alive and the defender dead at local return. | The reached emitter (`0x82CDDE6C`), human writeback, current mappings and the strict source |
| Other cities and units exist | With two population 2 cities and one extra Catapult per side, the full result consumer keeps the same outcome in all three Catapult matchups | The supplied city and plane values, Barbarian ordinal 0xFFFFFFFF, no unit creation child |
| The session names the human player | The active session child result gives local player 0, and the consumer returns with the same outcome | Matching delivery, current object lifetimes, manager `+0x18` = 0 |
| The defender has a registered model notification | The actual callback returns after writing only its own stack bytes | Construction and registration, kept objects, E+0x14 = 0 and a finite vector |
| Combat command 0 and presentation | The command identifies the defender through fresh normalization. The presenter call uses the same 144 byte selection array | The inline receiver at `0x82D821D0`, the pump at `0x82E2A570` and the reader path |

A completed battle through every presentation call is not yet proved. Details,
including the exact addresses, stack intervals and instruction counts, are in
[combat-victory-survival.json](../../manifests/combat-victory-survival.json).

## Limits and open questions

- The meanings of the override word at `0x830E4554` and the safeguard array at
  `0x830E45E4` are unknown. Their values at battle time are not established.
- No natural battle that loses to protection is known. No proof covers every
  legal input, retained generator state or retry.
- Which unit configurations other than the single Catapult have an all state
  winning selection is open, as are zero override Army fights and wounded units.
- The remaining callback, city creation and presentation effects keep the
  survival result to the selected profiles. Other worlds keep the general
  conditions in the manifest.
- The battle screen number path and its precision are in
  [Combat](combat.md#displayed-strengths).
