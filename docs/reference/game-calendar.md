# Game calendar state

The game calendar keeps the numeric turn and converted calendar year as
separate guest scalars. The semantic names below are recovered labels, not
original debug symbols. Runtime corroboration is stated separately from the
static update contract.

## Owned scalars and converter

| Item | Address | Recovered role |
| --- | ---: | --- |
| Current turn | `0x8312B8DC` | Numeric turn supplied to the native converter |
| Current year | `0x8312B8E0` | Current converted calendar value |
| `TurnToYear` | `0x82CEFA20` | Native piecewise turn-to-year conversion |
| `CalendarTurnAdvance` | `0x82D1EAB0` | Bounded turn increment, conversion, and year-store owner |

The initial pair is turn 0 and year -4000. For each positive turn,
`TurnToYear` advances the calendar by 100 years while the year is negative, 50
while below 1000, 25 while below 1700, 10 while below 1900, 5 while below
1950, and 2 thereafter.

## Transition flow

The bounded update sequence inside `CalendarTurnAdvance` is:

1. Load `0x8312B8DC`, add one, and store the new turn.
2. Call `TurnToYear` with that incremented value.
3. Store the returned calendar value at `0x8312B8E0`.

Initialization and load code derive and store the same scalar pair before
gameplay resumes. The transition sequence does not establish that
`CalendarTurnAdvance` is the sole writer, define its complete ABI, or assign a
user-action or game-phase trigger.

One exact direct call from `CalendarTurnAdvance` reaches
`ActiveCivilizationBonusLookup`. That edge proves shared lookup consumption,
not that the lookup determines calendar arithmetic or that one particular
bonus caused the transition.

## Presentation

The retail debug formatter consumes both scalars as separate integer
arguments. Separately, complete function `0x82DF9FD0` compares scheduled
event-year field `+0x444` directly with `0x8312B8E0`. Inequality immediately
branches to `0x82DFA038`, returns `1`, and stops that match path. The concrete
event class, scheduling cadence, and complete eligibility meaning remain
unresolved. Bounded runtime observation maps turn 61 to 1025 AD and turn 62 to
1050 AD.

These values do not identify one native UI formatter for every calendar
value. The image contains separate BC, AD, and year-zero strings, but final
year-zero wording remains unresolved. Era and year are separate guest values;
neither should be derived from the other.

## Evidence boundaries

- The static sequence proves scalar dataflow, not cadence, sole ownership,
  save/load ownership, or every side effect of the enclosing function.
- Calendar reads remain subject to the applicable player-state and pointer
  validity gates.
- The calendar model does not define a runtime mutation, API, mod, SDK, or
  presentation rewrite.
- No movement field, duration producer, or movement-specific timer follows
  from the calendar sequence.

## Evidence sources

- [Game calendar state](../../manifests/game-calendar-state.json)
- [Civilization Unique Ability storage](../../manifests/civilization-bonus-storage.json)
- [Catalog contract](../catalogs.md)
