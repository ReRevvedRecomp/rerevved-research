# Game calendar state

Turn and converted year are separate scalars. Names are recovered, not debug
symbols; runtime observations are distinguished from static dataflow.

## Owned scalars and converter

| Item | Address | Recovered role |
| --- | ---: | --- |
| Current turn | `0x8312B8DC` | Numeric turn supplied to the native converter |
| Current year | `0x8312B8E0` | Current converted calendar value |
| `TurnToYear` | `0x82CEFA20` | Native piecewise conversion from turn to year |
| `CalendarTurnAdvance` | `0x82D1EAB0` | Bounded routine that increments the turn, converts it to a year, and stores the year |

The initial turn/year pair is 0/-4000. Each positive `TurnToYear` step adds
100 while year<0, 50 below 1000, 25 below 1700, 10 below 1900, 5 below 1950,
then 2.

## Transition flow

`CalendarTurnAdvance` increments `0x8312B8DC`, calls `TurnToYear`, then stores
year at `0x8312B8E0`. Initialization/load derive the same pair before
resumption. The full ABI, triggering action or phase, and side effects remain
unproved. Whether this is the sole writer is also unproved.

Its exact direct `ActiveCivilizationBonusLookup` call establishes consumption,
not calendar arithmetic or bonus causation.

An initialization/load continuation repeatedly increments retained turn until
converted year reaches a signed record-halfword threshold, except zero or values
<=-4000. It can publish that turn to current/scheduling words before virtual
dispatch. A frame-slot producer supplies the separate four-byte destination
`0x8314F17C`. Checking that value at the actual load discharges the intervening
pointer-store alias guard; unconditional source retention remains unproved.
The scheduling manifest owns the bypass-input and access guards. Callback
effects and credit cadence remain unknown.

## Presentation

Debug formatting consumes both scalars separately. Complete `0x82DF9FD0`
compares event-year `+0x444` with `0x8312B8E0`; inequality branches to
`0x82DFA038`, returns `1`, ending that match path. Event class, cadence and full
eligibility remain unknown.

Runtime observations: turn 61 -> 1025 AD; 62 -> 1050 AD. No universal formatter
is identified. Separate BC/AD/year-zero strings exist, but final year-zero
wording remains unknown. Do not derive era and year from each other.

## Deadline admission

Victory evaluator `0x82D10FD8` has a separate deadline arm at
`0x82D11378..0x82D11438`. Its local admission requires:

- Signed current year >=2100.
- The selected player's unsigned ranking halfword at
  `0x830E9200+32*p` equals zero, under retained loop/frame state.
- Scenario word `0x8312B8D4` equals exactly -1, or signed low32
  `currentTurn-startTurn` >=200.

Admission requests `0x82D02AB8(p,1)`, the shared result writer also used by
ordinary Domination. Its initial stores publish player rank/type and sampled
turn/year in the result block. The deadline has its own admission; the ordinary
palace-based Domination condition retains its elapsed-ten-turn and
enabled-victory gates. Earlier victories and evaluator/iteration guards still
apply. A preceding warning tests year2090 or scenario elapsed195 separately.

The converter yields turn192=2098, turn193=2100 and turn194=2102. These are
static arithmetic witnesses, not observed endgame dates. The deadline consumes
calendar state; changing displayed dates alone does not establish more play.

The smallest candidate policy changes only this deadline admission and retains
its bypass to `0x82D1143C`. A higher cap and unlimited turns remain unselected.
Other victories, shared result handling and ordinary calendar/turn flow must
remain intact. Warning policy, current rank/calendar/scenario retention,
callback effects, peer compatibility and save/load of a continued game remain
requirements. The first selected post-result virtual request at `0x82D113F0`
uses current object `0x8314F76C` slot `+0x1C4`; its actual target and effects
remain unresolved. These local predicates and stores do not prove a completed
game ending or continued play.

## Evidence boundaries

- Dataflow establishes no cadence, sole/save/load ownership or complete side effects.
- Reads require applicable player-state/pointer validity.
- No mutation, API, mod, SDK, presentation rewrite, movement field, duration
  producer or movement-specific timer follows.

## Evidence sources

- [Game calendar state](../../manifests/game-calendar-state.json)
- [Game turn-limit boundary](../../manifests/game-turn-limit-boundary.json)
- [City yield scheduling
  producers](../../manifests/city-yield-scheduling-producer-boundary.json)
- [Civilization Unique Ability storage](../../manifests/civilization-bonus-storage.json)
- [Catalog contract](../catalogs.md)
