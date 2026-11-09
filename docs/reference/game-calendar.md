# Game calendar state

Turn and converted year are separate values. Names are recovered, not debug
symbols. Runtime observations are distinguished from static dataflow.

## Owned scalars and converter

| Item | Address | Recovered role |
| --- | ---: | --- |
| Current turn | `0x8312B8DC` | Numeric turn supplied to the native converter |
| Current year | `0x8312B8E0` | Current converted calendar value |
| `TurnToYear` | `0x82CEFA20` | Native piecewise conversion from turn to year |
| `CalendarTurnAdvance` | `0x82D1EAB0` | Bounded routine that increments the turn, converts it to a year, and stores the year |

The initial turn/year pair is 0/-4000. Each positive `TurnToYear` step advances
the year by 100 while year < 0, 50 below 1000, 25 below 1700, 10 below 1900,
5 below 1950, and 2 thereafter.

## Transition flow

`CalendarTurnAdvance` increments `0x8312B8DC`, calls `TurnToYear`, then stores
year at `0x8312B8E0`. Initialization has converter-derived paths; selected
deserialization separately requests saved year and turn. Recomputing the pair
on every load is not established. The full ABI, triggering phase, side effects
and sole-writer status remain unproved.

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
is identified. Complete `0x82CF3920..0x82CF39B0` selects negative, positive or
zero presentation by the signed year argument. Its positive arm requests
magnitude formatting without a local 2100 clamp or year-indexed table.
Chart-label owner `0x82DF7648` passes a converter return to that formatter at
`0x82DF7690`; GotW also has a separately recorded consumer. Formatter
descendants, ordinary HUD ownership and final wording remain unknown.
Do not derive era and year from each other.

## Calendar beyond 2100

The complete 32-instruction converter has no memory read or call, so speed and
scenario state cannot directly change its mapping. The selected transition
passes current turn plus one unchanged. Scenarios can select a starting turn
through the initialization year-threshold search; cadence, other writers and
later overwrites are separate questions.

Turn 118 is 1950. Until the first signed year wrap, the late curve is
`year = 2*turn + 1714`. There is no 2100 or 2500 clamp in the converter.

| Year | Absolute turn | Five-turn lead year | Lead turn |
| ---: | ---: | ---: | ---: |
| 2100 | 193 | 2090 | 188 |
| 2200 | 243 | 2190 | 238 |
| 2300 | 293 | 2290 | 288 |
| 2500 | 393 | 2490 | 388 |

These dates follow from the arithmetic; they are not observed endgame dates
or a replacement deadline policy. Scenario elapsed turns are counted from a
separate start turn.
Selected save/load requests carry four-byte current-year and current-turn
values; successful delivery, complete reload and retained coherence remain
unproved for a continued game.

At turn 1073740966 the year is 2147483646. The next turn stores low32
`0x80000000`, interpreted as -2147483648; later signed tests leave the simple
two-year curve. Signed nonpositive turn inputs return -4000. Conversion also
loops once per positive input turn. Removing a deadline therefore supplies
neither infinite integer storage nor arbitrary-turn consumer correctness.

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
apply. The local-player warning separately tests year 2090 at `0x82D11320`
with scenario -1, or elapsed 195 at `0x82D1133C` with another scenario value.
The selected warning resource promises a five-turn lead. Its request does not
establish delivered presentation.

The converter yields turn 192 = 2098, turn 193 = 2100 and turn 194 = 2102.
These results come from static arithmetic, not observed endgame dates. The
deadline reads calendar state. Changing displayed dates alone does not
establish that the game can continue longer.

Changing only the 2100 compare leaves both old warning tests unchanged.
Bypassing from `0x82D11304` to `0x82D1143C` skips the complete warning/deadline
arm. A finite extension instead needs a coherent warning policy, including
the separate scenario elapsed-200 gate. Other victories, shared result
handling and ordinary calendar/turn flow must remain intact. Current inputs,
callback effects, peer compatibility and save/load of a continued game remain
requirements. The first selected post-result virtual request at `0x82D113F0`
uses current object `0x8314F76C` slot `+0x1C4`; its actual target and effects
remain unresolved. These local predicates and stores do not prove a completed
game ending or continued play.

A bounded aligned-immediate census found five signed comparisons with 2100
and one with 2090 in the tested forms. Only the selected deadline/warning
comparisons are established current-year limit readers. Other hits include
incoming-argument predicates and address/code construction. This does not
exclude computed constants, resource/advisor text, aliased or indirect readers,
other opcode forms or other ending paths. A global replacement is unsupported.

## Evidence boundaries

- Dataflow establishes no cadence, sole/save/load ownership or complete side effects.
- Reads require applicable player-state/pointer validity.
- No mutation, API, mod, SDK, presentation rewrite, movement field, duration
  producer or movement-specific timer follows.

## Evidence sources

- [Game calendar state](../../manifests/game-calendar-state.json)
- [Game turn-limit boundary](../../manifests/game-turn-limit.json)
- [Scenario preset and selected load widths](../../manifests/scenario-speedmode-movement.json)
- [City yield scheduling
  producers](../../manifests/city-yield-scheduling-producer.json)
- [Civilization Unique Ability storage](../../manifests/civilization-bonus-storage.json)
- [Catalog contract](../catalogs.md)
