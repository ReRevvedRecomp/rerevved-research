# Game calendar state

Turn and converted year are separate values. Names are recovered, not debug
symbols. Runtime observations are distinguished from static dataflow.

## Scalars and converter

| Item | Address | Recovered role |
| --- | ---: | --- |
| Current turn | `0x8312B8DC` | Numeric turn supplied to the native converter |
| Current year | `0x8312B8E0` | Current converted calendar value |
| `TurnToYear` | `0x82CEFA20` | Native piecewise conversion from turn to year |
| `CalendarTurnAdvance` | `0x82D1EAB0` | Routine that increments the turn, converts it to a year, and stores the year |

The initial pair of turn and year is 0 and -4000. Each positive `TurnToYear` step advances
the year by 100 while year < 0, 50 below 1000, 25 below 1700, 10 below 1900,
5 below 1950, and 2 thereafter.

## Transition flow

`CalendarTurnAdvance` increments `0x8312B8DC`, calls `TurnToYear`, then stores
year at `0x8312B8E0`. Initialization has converter-derived paths; selected
deserialization separately requests saved year and turn. Recomputing the pair
on every load is not established. The full ABI, triggering phase, side effects
and sole-writer status are not yet established.

Its exact direct `ActiveCivilizationBonusLookup` call establishes consumption,
not calendar arithmetic or bonus causation.

A continuation for initialization and load repeatedly increments the saved turn
until the converted year reaches a signed record-halfword threshold. A threshold
of zero, or of -4000 or less, is excluded. It can publish that turn to the
current and scheduling words before virtual dispatch. A frame-slot producer supplies the separate four-byte destination
`0x8314F17C`. Checking that value at the actual load discharges the intervening
pointer-store alias guard. That the source stays unchanged in every case is not
yet shown. The scheduling manifest holds the bypass-input and access guards. Callback
effects and credit cadence remain unknown.

## Presentation

Debug formatting consumes both scalars separately. Complete `0x82DF9FD0`
compares event-year `+0x444` with `0x8312B8E0`; inequality branches to
`0x82DFA038`, returns `1`, ending that match path. Event class, cadence and full
eligibility remain unknown.

Runtime observations: turn 61 is 1025 AD, and turn 62 is 1050 AD. No universal formatter
is identified. Complete `0x82CF3920..0x82CF39B0` selects negative, positive or
zero presentation by the signed year argument. Its positive arm requests
magnitude formatting without a local 2100 clamp or year-indexed table.
The chart-label function `0x82DF7648` passes a converter return to that formatter at
`0x82DF7690`; GotW also has a separately recorded consumer. Formatter
descendants, which code draws the HUD year and the final wording remain unknown.
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
Selected save and load requests carry four-byte current-year and current-turn
values. Successful delivery, a complete reload and whether the state stays
coherent in a continued game are not yet established.

At turn 1073740966 the year is 2147483646. The next turn stores low32
`0x80000000`, interpreted as -2147483648; later signed tests leave the simple
two-year curve. Signed nonpositive turn inputs return -4000. Conversion also
loops once per positive input turn. Removing a deadline therefore supplies
neither infinite integer storage nor arbitrary-turn consumer correctness.

A nearer limit is in generated code that stores history turns as signed 16-bit
values before conversion, at `0x82CE62A0`, `0x82CEB348` and `0x82CC75B8`. Turn
32768 would read as negative there. Turn 393 fits. Its writer and any
truncation are not linked to these readers, so this is a lead and not a
confirmed bug. See the
[calendar manifest](../../../manifests/game-calendar-state.json).

## Earliest Domination date

Domination cannot be won before a minimum number of elapsed turns. The game
counts the turns from the scenario start turn, then converts the winning turn to
a year. A standard game starts at turn 0 (4000 BC) and the native minimum is
10 turns, so Domination is first possible in 3000 BC. Each turn before the year
reaches 0 adds 100 years, so a smaller minimum gives these earliest dates:

| Minimum elapsed turns | Earliest date with start turn 0 |
|---:|---|
| 10, native | 3000 BC |
| 5 | 3500 BC |
| 1 | 3900 BC |

A scenario that starts at a nonzero turn does not share these dates. The minimum
is added to its own start turn, and the sum goes through the converter. For
example, a start at turn 20 (2000 BC) with the native minimum of 10 reaches turn
30, which is 1000 BC.

How the code does it. Victory evaluation `0x82D10FD8` tests signed
`currentTurn - startTurn >= 10` at `0x82D11264`, where the start turn is the word
at `0x8312B8D8`. The converter is `TurnToYear` (`0x82CEFA20`). The same
evaluation also needs a nonzero palace count for the player, a palace count at
least the total less the definition's allowance, and a nonzero `0x82CEEA50(1)`
(Domination enabled). It then requests `0x82D02AB8(player, 1)`. Lowering the
minimum changes only this date test. It does not raise a year limit, and the
palace and enabled checks still apply. The dates are arithmetic from the
converter and were not observed in play.

See [AI settings](../gameplay/ai-options.md) for civilization elimination and how it changes
the palace count, and the
[elimination manifest](../../../manifests/ai-civilization-elimination.json) for the
palace formula and addresses. The
[Domination dates](../../../manifests/game-calendar-state.json#/dominationDates)
hold the table and its limits.

## The 2100 deadline

The game ends with a type 1 result (the same one Domination uses) when the year
reaches 2100, with two extra conditions. The player must have a ranking value of
zero, and either the scenario word is -1 or at least 200 turns have passed since
the start turn. A five turn warning comes first.

Worked examples with the native settings:

- A standard game has scenario -1 and start turn 0. The warning fires at year
  2090 (turn 188). The deadline is reached at year 2100 (turn 193). Turn 192 is
  2098 and turn 194 is 2102.
- A scenario with an id other than -1 that starts at turn 20 needs 200 elapsed
  turns, so the deadline is turn 220, which is year 2154 (`2*220+1714`). The warning
  fires at elapsed 195, turn 215, year 2144, with no year check.
- Changing only the 2100 compare would leave both warnings unchanged. Skipping
  from `0x82D11304` to `0x82D1143C` removes the whole warning and deadline arm.

How the code does it. Victory evaluator `0x82D10FD8` has a separate arm at
`0x82D11378..0x82D11438`. It has earlier guards for entry, the player and
Barbarian loop, victory settings and callbacks. The rank formula needs fresh
loop and frame state. Current turn is `0x8312B8DC` and start turn is
`0x8312B8D8`.

| Site | What it does |
|---|---|
| `0x82D11308..0x82D11314` | A helper return must equal player r27 before the local player warning runs. |
| `0x82D11320`, `0x82D11328..0x82D1132C` | Signed year equal to 2090 and scenario exactly -1 starts the warning. |
| `0x82D11338..0x82D11348` | Otherwise low32 elapsed turns equal to 195 with scenario other than -1 starts it. |
| `0x82D11354`, `0x82D11370` | Separate formatting and presentation requests. Resource `0x8214D170` describes five turns and highest score Domination, with no replacement year. |
| `0x82D1137C..0x82D11384` | Read signed year at `0x8312B8E0`. Below 2100 jumps to `0x82D1143C`. |
| `0x82D11388..0x82D11394` | Require the unsigned ranking halfword at `0x830E9200+32*p` to be zero. |
| `0x82D11398..0x82D113B0` | Scenario `0x8312B8D4` equal to -1 skips the elapsed test. Any other value needs signed low32 current turn minus start turn of at least 200. |
| `0x82D113BC` | Requests shared result writer `0x82D02AB8(p,1)`. |
| `0x82D113F0` | Next request goes through current object `0x8314F76C` slot `+0x1C4`. Its target and effects are unresolved. |

The year test and the elapsed test are separate, so this is not a universal
turn 193 ending. The shared result writer's first stores publish rank and type
(`0x82D02AF4`, `0x82D02AFC`) and the turn and year (`0x82D02B08`,
`0x82D02B10`), then copy eight score words. They add no new limit field.
Game of the Week computes its own score and Year of Victory (see
[Game of the Week](game-of-the-week.md)), so changing the converter would alter
those dates without changing the deadline and warning policy coherently. Do not suppress every type 1 result,
because Domination uses the same writer.

The warning text is a five turn advance notice for highest score Domination.
Its request does not show that the message is delivered. The warning tests
compare 2090 and 195, so a late start or a changed year can separate the
warning from the deadline.

Changing displayed dates alone does not let a game run longer. A finite
extension needs a warning rule that fits the elapsed 200 test, other victories
left intact, and compatible peers and saves. These local tests and stores do not
prove a finished ending or continued play.

A search of aligned immediate forms found five signed compares with 2100 and
one with 2090 (the counts by form are in the
[turn limit manifest](../../../manifests/game-turn-limit.json)). Only the deadline
and warning compares are shown to read the current year as a limit. Other hits
test incoming arguments or build addresses. The search leaves out computed
constants, resource text, aliased or indirect readers, other opcode forms and
other ending paths. Replacing every 2100 is unsupported.

## Evidence boundaries

- Dataflow establishes no cadence, no sole writer, no save or load handling and
  no complete side effects.
- Reads require valid player state and pointers where they apply.
- No mutation, API, mod, SDK, presentation rewrite, movement field, duration
  producer or movement-specific timer follows.

## Evidence sources

- [Game calendar state](../../../manifests/game-calendar-state.json)
- [Game turn-limit boundary](../../../manifests/game-turn-limit.json)
- [AI civilization elimination](../../../manifests/ai-civilization-elimination.json)
- [Scenario preset and selected load widths](../../../manifests/scenario-speedmode-movement.json)
- [City yield scheduling
  producers](../../../manifests/city-yield-scheduling-producer.json)
- [Civilization Unique Ability storage](../../../manifests/civilization-bonus-storage.json)
- [Catalog contract](../../catalogs.md)
