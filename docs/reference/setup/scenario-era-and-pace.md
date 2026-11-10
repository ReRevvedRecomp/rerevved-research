# Starting eras and game pace

A scenario carries a starting era setting (STARTERA), a start year (STARTYEAR),
a pace setting (SPEEDMODE) and a research rate (TECHNOLOGYRATE). Setup reads
STARTERA to hand each player some starting technologies. It does not give a
player every technology from earlier eras, and no one setting slows the whole
game. The [starting-era finding](../../../manifests/scenario-start-era-grant.json)
and the [SPEEDMODE finding](../../../manifests/scenario-speedmode-movement.json)
hold the addresses and the conditions behind this page.

## What setup does with STARTERA

STARTERA values 1, 2 and 3 replace the number of starting grants with 5, 14
and 24. Each grant is a random draw from the technology list. A draw counts
only when the technology passes the eligibility check and the player does not
own it yet, so the numbers are additional successful grants, not final totals.
Eligibility checks ownership, prerequisites and other fields, and opaque
helpers can add policy. Value 0 does not turn grants off, and value 4 selects a different path that
grants almost everything (see Beta Centauri below).

Worked examples:

- A player starts with no technologies and STARTERA is 2. Setup keeps drawing
  until 14 new technologies are written. Rejected draws do not count. The
  player's acquisition tally is then 14, and the tally chooser maps 14 to era 2.
- A player already has a tally of 13 and STARTERA is 1. Five more successes make
  the tally 18, which the chooser maps to era 2. The same value on a player
  with tally 0 ends at tally 5 and era 1.
- Two players with the same STARTERA can own different technologies, because
  the draws depend on what each already owns.

The tally chooser requests era 1 at a tally of 5, era 2 at 14 and era 3 at 24,
and era 0 below 5. It classifies a player. It does not say which technologies
belong to which era, and no code read here compares a technology with an era.

## How the code does it

Active scenario Q is `0x830E8FD0`. These signed 16-bit slots matter here:

| Input | Slot | Address | Role |
|---|---:|---|---|
| TECHNOLOGYRATE | 4 | Q+8 | Research cost factor |
| SPEEDMODE | 12 | Q+0x18 | Movement stat addend (see Game pace) |
| STARTERA | 14 | Q+0x1C, `0x830E8FEC` | Starting grant selector |
| Base grant count | | Q+0x1A | Used when STARTERA is not 1, 2 or 3 |
| STARTYEAR | | Q+0x3E | Start year search |

The names alone do not define a gameplay policy. Changing STARTERA does not
select a calendar year or a slower pace. The new game setup function is `0x82D217C8`.

| Site | What it does |
|---|---|
| `0x82D22980`, `0x82D22988` | Form active Q in r31 and save it at frame+0x68. |
| `0x82D22A60..0x82D22A74` | Take the base count from Q+0x1A when nonzero, otherwise from a reaching fallback. |
| `0x82D22A78` | First read of STARTERA: `lhz r8,Q+0x1C`, then sign extension at `0x82D22A7C`. |
| `0x82D22A88`, `0x82D22A94`, `0x82D22AA0` | STARTERA 1, 2 and 3 replace the count with 5, 14 and 24. |
| `0x82D22AA4` | Samples N, the player count, through the count pointer. |
| `0x82D22AF0..0x82D22AF8` | Skip the sampled Barbarian ordinal. N is `0x82F700AC` and E is `0x82F700B0`. |
| `0x82D22B08`, `0x82D22B14`, `0x82D22B1C` | A positive STARTERA is stored as the player's era at `0x830ECD08+4*p`, before that player's grants. A value of zero or less skips the store. |
| `0x82D22BAC` | Calls eligibility `0x82CE2C50`, which must return nonzero. |
| `0x82D22BC4..0x82D22BEC` | Require an absent ownership bit, then OR the bit into `0x830EDC48`, add one to the success counter and add one to the acquisition tally at `0x830EDD08`. The loop repeats until successes reach the count. |
| `0x82D22BFC` | Rereads Q+0x1C after each player. Later players and the value 4 test use the reloaded value. |
| `0x82D22CA4`, `0x82D2301C`, `0x82D23050` | Enter the later player setup loop, cross a current virtual+0x40 call, then request era 0 from `0x82D05A48`. That setter writes a changed era before a current virtual+0x16C call and effects on the local player that apply only under further checks, so it is not a plain assignment. Earlier paths also cross a current virtual+0x100 call at `0x82D22D5C` and `0x82D22D7C`. |
| `0x82D20EB0..0x82D20EE4` | The tally chooser (thresholds 5, 14 and 24). |

Whether the state from the grants is still intact at the era 0 request, and at
the first reader of the era, depends on the dispatches in between, so the
earlier ownership grant window does not show that setup finishes safely.

The grant loop has no cap on rejected draws. The candidate factor is the double
`48.0` at `0x8216AD68`. The actual random scale, the valid candidate set and
the eventual supply of 24 eligible technologies are not established for every
scenario.

Setup reaches the grants through direct writes. It does not call the usual
acquisition routine `0x82D09208`, so derived unlocks, civilization abilities,
governments, city bonuses, discovery rewards and notifications are not
confirmed to be coherent after a grant. A change that grants a different set of
technologies also needs an authoritative list of technologies by era, plus a
point in setup before the code that reads the granted state. The
[starting-grant](../../../manifests/starting-technology-grants.json) and
[first-discovery](../../../manifests/technology-first-discovery-rewards.json)
findings keep those requirements, with save and peer behavior.

STARTERA, STARTYEAR and SPEEDMODE are separate inputs. The zero store at
`0x82D23034` writes through `0x830EDD48`, not the acquisition tally
`0x830EDD08`, so it does not clear the tally. The request for era 0 at
`0x82D23050` is normal setup scheduling.

The scenario publisher `0x82DAEFD8` requests a 128 byte clear of Q at
`0x82DAF000`, and its custom copy at `0x82DAF584..0x82DAF598` copies all 64
halfwords into Q. A value written before a later publication can be replaced.
The recompiled code at `0x82D219D4` is an early failure and reset call. It is
not a shown overwrite after a successful setup.

## Beta Centauri and STARTERA 4

Built-in scenario ordinal 4 is Beta Centauri. Its dispatch cell is
`0x82DAF0B8`, which selects `0x82DAF240`. There `0x82DAF284` writes STARTERA 4
and `0x82DAF298` writes STARTYEAR 2025. The same branch also stores Beta
settings for Barbarians, victory, space race and the display card (see the
finding's `futureEraPresetBoundary`). Copying a whole preset is different from
reusing the technology input.

STARTERA 4 takes the bulk path at `0x82D22C18..0x82D22CA0`. It replaces the
ownership words 1 through 46 at `0x830EDC48` with one mask. It does not OR
with earlier bits, and words 0 and 47 are untouched.

- The mask is `low32(slw(1,E)-1)`. E is the configured Barbarian ordinal at
  `0x82F700B0`, read through a pointer saved at frame+0x50 (`0x82D2290C`).
- With 6 players (N is 6, E is 5) the mask is `0x1F`. With 7 players (N 7, E 6)
  it is `0x3F`, and with 8 players (N 8, E 7) it is `0x7F`. Each covers the
  non-Barbarian players and leaves the Barbarian bit clear. This holds when
  N is E plus 1, E is from 0 to 7 and the playing civilizations are the
  contiguous ordinals below E.
- `0x82D22C44..0x82D22C4C` writes the words. `0x82D22C50..0x82D22CA0` writes
  era 3 and the value prior tally[0] plus 46 for all N players.
- The special value E of -1 would give `0xFFFFFFFF`. That case is outside the
  normal player layout.

STARTERA 4 does not replace the base count. A nonzero Q+0x1A, or its fallback,
can still run random grants before the bulk step and use the random sequence.
A count of 0 matters only to keep the state before the bulk step identical
to a start with no random grants. It is not needed for the bulk result.

The bulk arm bypasses the usual acquisition routine and its first-discovery
rewards. Technology 47 is Future Technology (definition at `0x82F787D6`,
prerequisites 46, 45 and 41). The acquisition tail at `0x82D0AD68..0x82D0ADB0`
clears the player's ownership bit for 47 and, on an odd phase, adds one to a
per-player word at `0x830ED568+4*p`. When a player's research choice list is
empty, the fallback `0x82CECF04` to `0x82CED1D0` stores 47 at `0x830EDD48+4*p`.
The Apollo shortcut that treats technologies 1 through 46 as owned is redundant
with bulk ownership. See
[Apollo discovery bonuses](../gameplay/apollo-discovery-bonuses.md).

Start year example. Setup at `0x82D24F20..0x82D24F58` increments the turn until
the converted year reaches the requested year. Beta asks for 2025, but the
calendar moves two years per turn after 1950: turn 155 is 2024 and turn 156 is
2026. The result is turn 156, year 2026. A request of 1000 gives turn 60 and
year 1000, 1500 gives turn 80 and year 1500, and 1800 gives turn 98 and year
1800. A value of 0 or -4000 and below skips the search. The start turn is
stored at `0x82D24F74`. These results need a reaching turn below the target
and the loop state to stay valid. They are arithmetic, not an observed Beta
start. See the [game calendar](game-calendar.md).

## Saving and loading the scenario block

The save routine for discriminator 14 and above requests all 64 scenario
halfwords: `0x82CC6208` in mode 1 and `0x82CC6228` in mode 0. With no auxiliary
stream, the array helpers step two bytes per element, so element 14 is STARTERA
at `0x830E8FEC`. Scalar input requests two bytes through the current stream at
slot +4 (`0x822DECB8`) and output through slot +8 (`0x822E1400`). Byte order
conversion and the current stream still affect the transfer. The older
discriminator 8 to 13 path uses a different temporary copy.

These requests carry the effective STARTERA value. They do not show that bytes
arrive, that a reload is complete, or whether the value came from the scenario
or from an override. Ownership and discovery data are saved separately, so a load
should not repeat the startup grants.

## Game pace

SPEEDMODE (slot 12) is added to a movement stat by `0x82CF1F70`
(`EffectiveUnitMovementLookup`) on both return paths. It adds to r25
(initialized to 1) or to the composed movement r26. This does not show a
movement budget, a command cost or a time multiplier. The preset store for built-in
ordinal 5 writes SPEEDMODE 1 at `0x82DAF2DC`, after selected formatting calls.

Coordinated slower progression needs a separate choice for each surface:

| Surface | Input and code | Open question |
|---|---|---|
| Science | TECHNOLOGYRATE factor in `0x82CF0EE8`; see [science](../gameplay/science.md) | Selected value, rounding, progress and cadence |
| Unit production | Definition+0x44, scalar `0x82CF1148`, completion `0x82D159F8`; see [unit definitions](../gameplay/unit-definitions.md) | Modifier, display, rush, AI and completion order |
| Buildings and Wonders | Category costs `0x82CF1278`, comparisons and stores `0x82D13978`; see [gameplay cost arithmetic](../gameplay/gameplay-cost-arithmetic.md) | Separate thresholds and composed effects |
| Growth | Shared word `0x830E45C8` read in `0x82CF1060`; see [city growth](../gameplay/city-growth.md) | Initialization, progress and policy |
| Culture and borders | City influence arithmetic and separate victory credits | No single culture scalar; borders, Great People and victory differ |
| Movement | SPEEDMODE in `0x82CF1F70` | No safety clamp; negative custom values are not shown safe |
| Calendar and events | Piecewise turn to year converter; separate year and turn readers | A new date need not slow the economy and can move event timing |
| Presentation | Normal and Fast animation divisors | Separate from game rule progress |

Turn to year converter `0x82CEFA20` has 32 instructions of local arithmetic
with no memory access or call. It has no SPEEDMODE input, so a pace setting
cannot change dates through it directly. Callers that transform its input and
the other economy and event readers are outside that result. See the
[game calendar](game-calendar.md).

## Growth value and its writers

The shared growth value G at `0x830E45C8` is written from the calendar.

Worked example. For a turn T with year Y below 1000, G is 10 minus the whole
number T divided by 25 (rounded toward zero). Turns 0 through 24 give 10,
turns 25 through 49 give 9, and turns 50 through 59 give 8. Turn 60 is year
1000, and from year 1000 on G is 6. A literal 5 also exists, but it needs Y
below 1000 and at least 1500 on the same sample, so this entry cannot reach it.
The arithmetic does not overflow for a signed 32-bit turn.

- Producer `0x82D255B8` writes G with the formula above. It has no scenario or
  SPEEDMODE input, though an upstream scenario value can change the sampled
  calendar.
- Its direct caller is the load tail `0x82D86400`, which requests it at
  `0x82D86A3C` after `0x82D58080`. That does not show a once per turn or initial
  setup cadence. On the load transfer, four byte year input at `0x82CC424C`
  comes before turn input at `0x82CC42B8`. Both go through the current stream
  at virtual+4, so request order alone does not show a coherent saved pair. The
  producer also crosses a direct helper and a current virtual+0x54 call before
  it samples year and turn.
- A second writer is in `0x82D0C3E8`, which the numeric EndTurn handler 54
  requests. It uses the same formula for Y below 1000 and gives 6 from year
  1000. It publishes year before an optional loop, and that loop's writes could
  alias global memory, so the pair is not shown to be coherent.
- After the growth store, the helper `0x82D022F0` (called at `0x82D0C54C`) samples
  a signed count. A nonpositive count returns without scanning or calls. A
  positive count scans 256 records per row, resamples the row bound, and for a
  qualifying record requests a current virtual +0x1A4 call at `0x82D0235C`.
  Only after that returns does it store a halfword and a byte marker. Normal
  return does not prove G or the calendar stays unchanged, and the marker writes
  can alias protected storage.

Delivery of these inputs, how often each writer runs, later overrides and the
order before the growth reader at `0x82CF1090` are open.

## Technology inputs

- The technology neighborhood reader has 144 instructions. It reads three
  direct prerequisites and a seven byte cell display neighborhood. The producer
  `0x82DD76E8` on the same receiver tests whether each non-sentinel
  prerequisite is already in a published group, then appends a temporary
  group. With empty starting groups and successful publication this forms
  prerequisite layers, not an era relation. Cycles, termination and the
  displayed grid are not established. Cells and the 16 byte groups depend on
  allocation and on current flag provider effects.
- Research cost body `0x82CF0EE8` has 94 instructions and eight local load
  sites. Its scenario input is TECHNOLOGYRATE at Q+8, and it has no local
  Q+0x18 read. A raw search for the same halfword found no other candidates, but
  long-lived bases and computed aliases are not excluded.
- A definition+0x26 reader at `0x82CED418` and `0x82CED41C` sign extends a
  halfword. The value -1 skips the adjustment. A bit overlap with a stored
  mask, plus a separate nonnegative global, adds 50 to a local score. This is a
  mask and sentinel use, not an ordered era comparison. Its upstream meaning is
  unknown.
- `0x82CF1060` has 58 instructions with ten loads: six gameplay inputs and four
  epilogue restores. It reads the global `0x830E45C8` and city fields. It forms
  no SPEEDMODE alias under the supported city index, table, stack and alias
  conditions. The helper `0x82CF0CB0` is open.
- The prerequisite exclusion body `0x82CE2280..0x82CE23FC` has no containing
  function in the configured project. A six iteration loop clears 48 workspace
  bytes and seeds index 0. Repeated scans of 48 rows mark a row when a
  non-sentinel prerequisite is exceptional or already marked. With stable
  definitions and supported indices, marks only change from 0 to 1 and at most
  48 scans run. The result byte is 0 or 1. `0x82CE2C50` may reject a nonzero
  result before its other checks, so zero is not the whole eligibility answer.
  The body reads prerequisite halfwords, not a player era.

## Limits and open questions

- The recompiled copy of the setup function `0x82D217C8` is split across
  files and was not read in full. The claims on this page rest on the specific
  instructions cited, not on the whole function.
- No source establishes which technologies belong to which era.
- Complete first turn behavior, ability delivery, byte delivery on load, and
  peer behavior for starting eras have not been observed.
- Actual input delivery, a coherent calendar sample and the cadence of the
  growth writers are open, so no coordinated pace setting is described here.
- The effect of changed STARTERA or pace inputs at runtime has not been
  observed.
