# AI settings and behavior

The AI is a set of separate decision paths, not one turn algorithm. This page
covers what a modder needs to know about it: how many AI civilizations a game
has, what difficulty they get, how a civilization is eliminated, what the AI
decides each turn, where economy outputs can be changed, and how Eternal Kombat
and Always at War diplomacy work. Each section opens in game terms. Addresses,
conditions and open questions follow.

Every path below needs the stated inputs, normal returns under the native ABI
and no memory writes that overwrite live state. The results come from static
reading of the image, not from observed games, unless a section says so. A hook
point is a place where a mod or the runtime could change native behavior (see
the [glossary](../glossary.md)); naming one does not mean it works. Evidence is
in [ai-options-boundaries.json](../../manifests/ai-options-boundaries.json) and
[ai-civilization-elimination.json](../../manifests/ai-civilization-elimination.json).

## A two-human network game

Take a network game with two humans. Network setup publishes six slots:
civilization ordinals 0 to 4 and the Barbarian at ordinal 5. Two humans leave
three AI civilizations (5 minus 2). Setup also writes difficulty 2, King, to the
shared word `0x82FFE7C8`. It reads no lobby value for that write. The word has
effects beyond the AI:

| Item | Result in this game | Why |
|---|---|---|
| AI civilizations | 3 | Five civilization slots minus 2 humans. |
| Barbarian | Ordinal 5 | The last of the six slots. |
| Difficulty word | 2, King | Written at `0x82D221EC`. |
| Research discount | Not applied | It needs the network game byte to be zero. |
| AI Wonder half cost | Not applied | It needs difficulty above 2. |
| Chieftain and Warlord combat help for the local player | Not applied | It needs difficulty 0 or 1. |
| Culture addend for the local player | 0 | The addend is `clamp(2 - D, 0, 2)` and D is 2. |
| Domination | Counts every capital that gets founded, AI included | The palace total includes all of them. |

The rest of this page explains each row, then the settings that change them.

## AI decision overview

The recovered AI is a set of paths with known edges and known gaps. The rows
below do not establish the order of the paths within a round.

| Area | What is known | Evidence |
|---|---|---|
| Research | The turn call `0x82D1D604` can reach the shared research prompt `0x82CECCD8` when research is unset or invalid and the state and resolver checks pass. The prompt builds ascending real technology IDs plus a sentinel and scores them. The order in which the scoring loop visits technologies is described in [Science and technology cost](science.md). | [technology-prompt-callers.json](../../manifests/technology-prompt-callers.json) |
| Production | `AIUnitChoiceEvaluate` (`0x82CB44E0`) reads the city owner and scores candidates. Candidate 103 reads UEA 4 and adds half a coefficient before scoring. The comparison at `0x82CB668C..0x82CB66A4` replaces the best candidate on a tie as well as on a higher score. Whether the winner becomes an executed production is not shown. | [RVA-F-0330](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0330), [production-cost-ownership.json](../../manifests/production-cost-ownership.json) |
| Unit filter | `AITurnUnitFilter` (`0x82CBF570`) takes a player and unit, computes a threshold from the unit stats and replaces the kept candidate only for a strictly greater score. A tie keeps the earlier candidate. Later checks can drop it. One path through `TurnSelectionUpdate` (`0x82D259E8`) carries the code to a command 17 Move and a five word staging area. | [ai-stat-choice.json](../../manifests/ai-stat-choice.json), [unit-movement-lifecycle.json](../../manifests/unit-movement-lifecycle.json) |
| Combat | `CombatResolve` (`0x82CD9970`) and three AI functions read the same effective attack and defense accessors. This shows that the AI consumes the stats. It does not show how the AI picks a war target, or how a result reaches live units. | [unit-definitions-ai-evaluation.json](../../manifests/unit-definitions-ai-evaluation.json), [Combat](combat.md), [Combat strength](combat-strength.md) |
| Diplomacy | The selected scan of nonhuman pairs checks the relation, an elapsed value above 20 and both human checks, then requests contact. A stored choice that stays nonzero reaches a warning, a history flag and a war request. See [Automatic AI contacts](#automatic-ai-contacts) and [Economic and strategic consumers](#economic-and-strategic-consumers). | [RVA-F-0330 `strategyDecisionBoundary`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0330/strategyDecisionBoundary) |
| Spy | Evidence covers all six harmful missions and the selected arrival paths. A freshly created Spy picks mission 0. Kidnapping and bribery have rejection loops with no attempt limit. Whether a natural AI Spy reaches these paths is not shown. | [spy-mission-selection.json](../../manifests/spy-mission-selection.json), [Spy missions](spy-missions.md) |

A leader name does not establish a personality table. Civilization bonuses
reach the AI only through shared consumers, as described under
[Economic and strategic consumers](#economic-and-strategic-consumers).

## Number of AI civilizations

A new game has five civilization slots and the Barbarian at slot 5. With one
human, the existing opponent control can keep up to four AI civilizations. The
serializer covers eight player pools, eight civilization and era entries and a
64 entry relation array. That storage does not show that more slots are
playable. Initialization, turn order, placement, the interface and networking
for players 6 and 7 are unverified.

### Eight civilizations

Eight civilizations means one human and seven AI. Keeping the Barbarians as a
separate participant suggests a count of 9 with the Barbarian at slot 8. The
placement loop has eight permutation entries and skips the Barbarian before it
writes coordinates, so eight civilization starts fit the coordinate rows. Their
capacity is enough, but no actual start has been observed.

Several consumers need structural change:

- The placement preference histogram scores every participant with eight player
  columns before it excludes Barbarians. At player 8 its counts alias the next
  terrain category for player 0.
- An unchanged ninth unit pool would overlap live map label and count planes and
  fall outside the fixed save transfer.
- Diplomacy indexing has stride 8. Barbarian consumers must be classified before
  that representation grows.
- Setup uses the count before the late count stores, so changing the two late
  constants alone does not add civilization initialization.

The [placement finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0331)
records these connections and limits. Four AI is the supported setting in the
shipped game, not a proved engine maximum.

### Six AI

One human and six AI civilizations, with Barbarians kept, make seven
civilizations and eight participants. The native storage for eight unit pools,
civilizations, coordinate pairs and relations fits this layout. Five AI use
seven participants. Both layouts keep every participant below index 8 and avoid
the ninth column and ninth pool collisions above.

The [setup assignment finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0332)
records the hook points: after the human mask is built, at the later count
stores, and at the native AI civilization writer with its duplicate retries.
The earlier human selection and the separate Barbarian ID are preserved, and the
human stays at slot 0, before every AI in the native comparison against earlier
civilization IDs. Valid starts, turns, contacts and saving and loading with this
layout have not been observed.

Restricted selection flags allow only five civilization IDs, so retries cannot
create enough distinct IDs in those modes. Game of the Week also changes the
duplicate comparison to omit player slot 0. Expansion excludes those modes,
multiplayer and the native special two-player override.

## Multiplayer AI count

Network setup publishes six participant slots, with the Barbarian at ordinal 5.
For a valid human mask, the configured AI count is 5 minus the number of humans
H. The eight slot limit caps what a larger count could use. It does not show
that a larger network layout, or a game with zero AI, works.

| Humans H | AI civilizations in the native layout (5 - H) | Largest request within the 0 to 5 range and eight slots |
|---|---|---|
| 1 | 4 | 5 |
| 2 | 3 | 5 |
| 3 | 2 | 4 |
| 4 | 1 | 3 |
| 5 | 0 | 2 |
| 6 | Outside the native layout | 1 |
| 7 | Outside the native layout | 0 |
| 8 | Outside the native layout | None: the Barbarian needs a slot |

The table is arithmetic over the layout. Eight slot storage alone holds `7 - H`
AI (six AI with one human, for example); the request range of 0 to 5 is what
caps the last column for 1 and 2 humans. It does not show that the lobby accepts
each H. For a valid mask, humans H and a request of 0 to 5 AI, three formulas
give the smallest layout that holds them:

```text
A = min(request, 7 - H)                         request capped by the 7 - H free slots
N = max(6, H + A + 1, highestHumanOrdinal + 2)   participant count
B = N - 1                                        Barbarian ordinal
```

A layout needs N at most 8 and every human ordinal below B. Take humans at
ordinals 0 and 1 asking for 5 AI: A is `min(5, 5)` = 5, N is `max(6, 8, 3)` = 8
and B is 7. Take humans at ordinals 0 and 6 asking for 0 AI: N is
`max(6, 3, 8)` = 8 and B is 7, so the five native AI at ordinals 1 to 5 would
all have to be removed, and the humans cannot be moved. A human at ordinal 7
cannot share eight slots with a separate Barbarian. These formulas set the
smallest extent, not a placement method. Humans at ordinals 0 and 4 asking for
0 AI cannot fit count 3 with the Barbarian at 2 without moving a human.

The formulas are in
[`multiplayerCountBoundary`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0332/multiplayerCountBoundary).
Rebuilding the human mask can read the count before the later setup hook point.
Setup also waits at `0x82D2206C..0x82D22078` for each human's civilization word
to differ from -1. A larger count creates no civilization IDs by itself.

### How the human mask is built

The mask `0x8312E608` is rebuilt by `0x82CD59A8`, called at `0x82D21FF4`. It
copies the source word `0x8314F1B0` when that word is nonzero. Otherwise it sets
bit p for each ordinal p below the count where `0x82D8AB00(0x8314EFE0, p)` is
nonzero. That predicate reaches `0x82CA9810` through the session object (`+0x10`,
virtual `+0x100`), which looks up the ordinal in a map at `+0x1C`. A valid mask
plus a distinct Barbarian identifies the AI civilizations by exclusion. A zero
mask falls back to this lookup, which is not evidence that everyone is an AI.
The same session lookup conditions the event routing described under
[Network events](#network-events).

In a network game the path at `0x82D22868..0x82D228E0` calls `0x82CD5A70` and
writes the human civilization word at `0x82D2288C`. The main network path can
branch from `0x82D22648` directly to `0x82D228E4`, so that write does not run
for every peer.

### Native roster publication and the early hook point

The default membership map has a connected native ordinal producer. The routine
at `0x82CAA598` publishes its payload in the ordinal keyed map, and payload
`+0x18` keeps the assigned ordinal. Reply 1200 carries that ordinal at `+0x44`,
and the receiving path uses it to publish membership. Request 1209 compares the
map size with the expected membership. Its receiving executor marks one member
ready and calls the lobby callback. That request does not freeze the map.

`0x82D217E4` is a hook point. It is the return address of the native reset call
at `0x82D217E0`, so it runs immediately after the reset. It comes before the
early membership read at `0x82CD59E4` inside `0x82D21FF4`, and before the count
read of the bypass at `0x82D22858`. The late count stores at `0x82D22918` and
`0x82D2291C` run again on the bypass and retry paths (`0x82D220CC` retries
`0x82D21FF4`), so a value published early must match them. The frontend getter
and one bit clear are recorded in
[`multiplayerRosterEarlyAdmissionBoundary`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0332/multiplayerRosterEarlyAdmissionBoundary).
Their order relative to setup is not established.
[`multiplayerPostResetFrozenRosterCandidateBoundary`](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0332/multiplayerPostResetFrozenRosterCandidateBoundary)
records the exact addresses, wire fields and conditions. Special modes, coherent
mappings, helper state, native civilization ID delivery and peer agreement
remain conditions. No game with more than the native AI count has been run.

### Zero AI and the turn loop

Command 48 loops over configured ordinals, not over a separate AI count. It
loads the count at `0x82CDE800`, classifies each ordinal at `0x82CDE81C`, calls
`0x82D1EAB0` and `0x82D1D1C0` for nonhumans at `0x82CDE830` and `0x82CDE838`,
and advances through the count at `0x82CDE8A8..0x82CDE8B4`. Barbarians still in
the roster are nonhuman, so a game with zero AI civilizations still gives this loop work.
Its waits and completion checks still need finite returns and peer agreement.

| Consumer | What the code does | What is not shown |
|---|---|---|
| Setup | `0x82D22908` and `0x82D22910` supply 6 and 5, and `0x82D22918` and `0x82D2291C` store the count and Barbarian. Special `0x8314F180` sets count 2 and Barbarian -1. | That setup creates added AI rows, starts or placement without further changes. |
| Players, contact and turns | Eight slot storage and the count loops can be reused. | Hardcoded network extents and every callback are not fully checked. |
| Domination and elimination | The Domination test reads no AI minimum. The elimination check at `0x82D0CB8C` reads the statistics at `0x830E5AD0` and `0x830E5650`. See [Eliminating AI civilizations](#eliminating-ai-civilizations). | That every victory, interface and turn reader works with zero AI. |
| Saving | The save transfers cover eight pools, eight civilizations and 64 relation words. | A new native format, or any saved multiplayer policy. |
| Peers | Matching local arithmetic follows from the same inputs. | That peers received or applied the same roster, layout, IDs and random state. |

## Multiplayer AI difficulty

Difficulty is one shared word at `0x82FFE7C8`, not an AI-only setting. The named
views map 0 to Chieftain, 1 to Warlord, 2 to King and 3 to Emperor. Every other
value, including 4, selects the Deity view. That is a display fallback, not a
range check. The same word feeds the local player's Culture and combat help and
several AI-only readers, so changing it changes more than the AI.

In a network game setup writes 2 (King) to the word at `0x82D221EC`. The store
comes first in the network arm: `0x82D221D4` reads the network game byte
`0x8314F10B`, a nonzero value reaches the literal 2 at `0x82D221E4`, and
`0x82D221EC` stores it through the base `0x83000000`. A zero byte branches to
`0x82D2264C` instead. The store runs before the call to `0x82D8AA60` at
`0x82D221FC`, so that later manager check does not choose the value. No lobby
or host value is read for it. In the other branch, `0x82D2264C..0x82D2267C`
stores the root getter result, or keeps the existing 0 when the halfword at
`0x8314F1C8` is nonzero. Setup reads the word again at `0x82D2293C`, before the statistics
recount at `0x82D2530C` (return address `0x82D25310`). The test at `0x82D22948`
treats 0 specially: when `0x8312B8D4` is -1 and the halfword at `0x8314F1CC` is
0, `0x82D22974` sets bit `0x800` in `0x830E4550`.

### Where the value comes from

| Storage | Address | Notes |
|---|---|---|
| Setup preference | `+0xF8` of the object at `0x8314EFC8` | `0x82E76FDC` copies the incoming value and `0x82E76FEC` stores the whole word with no range test. |
| Root getter | Cell `0x82138804` in table `0x82138768`, routine `0x82D7CED0` | Returns the setup value at `+0xF8` unchanged. `0x82D7E780` installs the table. |
| Shared word D | `0x82FFE7C8` | A full word, not a validated five value enum. Save transfers it at `0x82CC4104` and `0x82CC4138`. |
| Per-player production array L | `0x830E9050 + 2*p`, halfwords | A separate array. It is reset to `0xFFFF`, written by command 57 at `0x82CDE180`, saved as eight halfwords and read by production. It is not shown to be an AI difficulty array. |

The per-player array comes from a distinct chain. The root cell `0x82138808`
reaches `0x82D7DAA0`, which loads the setup object and continues at
`0x82DAD7A8`. That routine looks the player up in a map at setup `+0x58`. If the
lookup returns the sentinel at setup `+0x60`, it returns the word at `+0x114`
of the object at `0x8314EFCC`. Otherwise it returns the node's `+0xC` word.
`0x82D22464..0x82D224F0` gets a player candidate from the session, takes that
scalar and sends command 57. The readiness loop at `0x82D22518..0x82D225F8`
waits until each human's halfword is no longer `0xFFFF`. That loop shows
per-participant readiness, not an AI level.

### Who reads the word

| Reader | Where | Effect | Requires |
|---|---|---|---|
| Research cost | `0x82CF0F8C..0x82CF1014` (D at `0x82CF0FE4`) | The cost B becomes `trunc0(6*B / (D + 6))` before the scenario multiplier. | Network byte `0x8314F10B` zero, the human check false, a technology owned by the local player, and D above 1. |
| Unit, building and Wonder production | `0x82CF1148`, `0x82CF1278` read L; `0x82CF1500..0x82CF1548` read D | A positive L lowers the starting scalar 10. The final Wonder test at `0x82CF1520` (signed D against 2) halves the cost C to `C - trunc0(C/2)`. | Wonder half cost: the human check false and D above 2. D 0, 1 and 2 pass no reduction, 3 and 4 do. There is no network byte test in this arm. |
| Local Culture | `0x82D15094`, `0x82D15128`, `0x82D15134..0x82D15164` | Adds `clamp(2 - D, 0, 2)` to the Culture sum: 2, 1, 0, 0, 0 for D 0 to 4. This is Culture, not happiness. | The city owner equals the local player. |
| Local combat help | `0x82CDB120` and `0x82CDB268` pick the side | D 0 adds 100 (`0x82CDB15C`, `0x82CDB294`) and D 1 adds 50 (`0x82CDB1E4`, `0x82CDB31C`) to the attack or defense multiplier. `0x82CDB390` and `0x82CDB39C` then multiply the base strengths. | The side equals the local player and the mode is 0 or 2. See [Combat strength](combat-strength.md). |
| Higher difficulty combat paths | `0x82CDB8F4..0x82CDB944` | D above 2 or above 3 with the human check false can write a saved value to frame words `+0x9C` and `+0xA0`. | Flag meanings and effect are not established. |
| Garrison threshold | `0x82CB40C0..0x82CB40D8` | `low32(r10 + trunc0(s32(low32(low32(U32[0x830ECD08 + 4*r7] * (D + 1)) * r9)) / 60))`. | The index and inputs are selected, and the later use is open. It is not a general aggression multiplier. |
| City priority | `0x82CC0008..0x82CC013C` in `0x82CBF570` | D not 0 is one condition of a priority path for other owners' cities. D 0 excludes that path. | Many other classification, tile and state checks. It is not a universal attack ban. |
| Barbarian city credit | `0x82D15430..0x82D15448` | D 0 with weighted presence can zero a selected credit. | Not an AI wide factor. |
| Friendly village reward | `0x82D0EEB8..0x82D0EEE8` | A Settlers reward needs D below 2; otherwise the reward is 25 Gold. | Network byte zero, so it never applies in a network game. See [Friendly villages](friendly-villages.md). |
| Local win history | `0x82D052C8`, `0x82D05394` onward | King and Deity thresholds (D at least 2 and at least 4) and difficulty indexed history. | The single-player byte check. |
| Extra request when D is below 2 | `0x82D25330..0x82D25368` | D below 2 is one condition before a request to the root `+0x80` with 13 and -1. | Its effect is not tied to the village reward or an AI bonus. |
| Happiness | None found | No reader shows a difficulty specific happiness formula. | The Culture addend above is not happiness. |

Reuse of the reader formulas is in
[technology-research-cost.json](../../manifests/technology-research-cost.json),
[production-cost-ownership.json](../../manifests/production-cost-ownership.json),
[friendly-village-rewards.json](../../manifests/friendly-village-rewards.json)
and the [difficulty finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0381)
(`readerTable` and `nativeClosingBoundary`).

### What the evidence does not show

Not every reader is found. A masked scan found 70 `lwz`, 3 `stw` and 4 `addi`
candidates and a generated search found 66 comment hits in 25 functions, but cached,
indexed and passed pointer accesses are outside both. The scans include data
and wrong bases: `0x823DA5D0` and `0x823DA5DC` use `0x82F8E7C8`, not difficulty.
Research's discount also needs a zero network byte, so changing its difficulty
operand alone enables nothing in a network game. The Wonder test has two
outcomes, not five: operands 0 to 2 keep the reduction off and 3 and 4 turn it
on. Human values and the mode checks above must be kept. Legal input, every
alias, every active participant and execution on all peers are open, and no
setting or runtime behavior follows from this static finding.

## Eliminating AI civilizations

A civilization is destroyed when it has no cities and no Settlers at the end of a
round, or when it loses its last city in a capture. The native routine then
kills every live unit it owns and shows a leader message. Domination is a
separate rule: a civilization wins when it holds all palaces, or all but an
allowance, once at least 10 turns have passed since the start turn.

### The Domination palace count

The palace count `0x830ECB40[p]` and the total `0x830ECB60` (the ninth word) are
kept by event handler `0x82D1EAB0`, which adds one to the owner and the total
when a palace city is processed (`0x82D1F7D0`, `0x82D1F7DC`). A capture moves one
palace from the victim to the capturer (`0x82D1C948..0x82D1C964`). Victory
evaluation `0x82D10FD8` (`0x82D1121C..0x82D11284`) grants Domination through
`0x82D02AB8(p, 1)` when all of these hold:

```text
palaces[p] != 0
palaces[p] >= total - adj
turn - startTurn >= 10          (checked at 0x82D11264)
0x82CEEA50(1) is nonzero
```

Here `adj` is the definition halfword at `+0x16`, or 0 when bit `0x08000000` is
set in the word at `0x82FFE7C4`. `0x82CEFC98` (which returns `0x13`) and the
capture warning at `0x82D1CDC8` use the same comparison. The calendar year of
that turn is in [Game calendar state](game-calendar.md).

A civilization that never founds a capital never adds to the total, so the total
counts only capitals that exist. Take a two-human game where no AI founds a
capital: each human holds 1 of 2 palaces, so neither wins 10 turns after the start turn. Capturing
the other capital gives 2 of 2 and wins. A single human with no AI civilization
wins Domination 10 turns after the start turn once the capital exists. A human
who has not founded a capital by then lets the other human win. An eliminated civilization has 0
palaces and cannot win.

### The destroy routine

`0x82D0C1E0(p, killer, city)` does the following in order:

1. Returns when p is the Barbarian (`0x82D0C1FC`).
2. Returns when bit `0x100` of the pair word `0x830ED0D8[(local*8 + p)*4]` is
   set. The local player comes from `0x82D8A3A0`. The pair matrix also holds
   diplomacy bits.
3. Kills every live unit of p. Records sit at `0x830F2BF0 + p*0x5400 + u*0x54`
   for u below 256. A record is live when byte `+0` is not `0xFF` and bit 31 of
   word `+0xC` is clear. Each goes to `0x82D02390(p, u, 0)` at `0x82D0C27C`.
4. Returns when p is the local player.
5. Shows a leader message to the local player, then calls `0x82CFB620(0x32, 0)`
   and `0x82CC85D0(p, 0)` at `0x82D0C3A0`.
6. Sets the pair bit (`0x82D0C3C8`) and adds history code
   `(p << 8) | 0x3000 | p` through `0x82D00480` (`0x82D0C3DC`), which skips turn 0.

It writes no city, palace, alive or count word. A destroyed civilization is only
one with no cities and no live units. The unit kill `0x82D02390(p, u, mode)` with
mode 0 sets bit 31 of word `+0xC` and halfword `+0x26` to -1, kills units carried
by u and clears `+0x44` links to it. A nonzero mode calls virtual `+0x1A4` of
`0x8314F76C` instead, a presentation path. It uses no random number and posts no
event.

| Caller | Condition |
|---|---|
| `0x82D1D1B0` in city capture `0x82D1B400` | The victim has no cities after the capture. |
| `0x82CDF2D4` in the tail of dispatcher event `0x11` | For each p below the count with no cities. How the tail is reached is not traced. |
| `0x82D0CB8C` in the end of round routine `0x82D0C3E8` (event `0x36`) | For each non-Barbarian p below the count with no cities and a zero settlement presence, or, in a network game only, no cities and a turn count above 20 since `0x8312B8D8`. Session and pair checks follow. |

The statistics are arrays with stride `0x80`, rebuilt by `0x82D11AD8`, which
clears `0x830E5650` and `0x830E5AD0` for `0x480` bytes and counts again.
`0x830E5AD0[p*0x80]` is the city count (capture uses cities plus 1 as a divisor
at `0x82D1C61C`). `0x830E5650[p*0x80]` is settlement presence, indexed by the
Settlers class. It does not count every live unit; see
[friendly-village-rewards.json](../../manifests/friendly-village-rewards.json#/metricDefinitions/settlementPresence).
No general alive flag is shown.

### Setup and the first recount

The setup routine `0x82D217C8` is called only from the new game routine
`0x82D25170` at `0x82D25254`, which first clears the turn `0x8312B8DC` and the
start turn `0x8312B8D8`. It stores count 6 at `0x82F700AC` and Barbarian 5 at
`0x82F700B0` (`0x82D22918`, `0x82D2291C`). A two-human game therefore has three
AI. There is no separate AI constructor. The start loop skips only the Barbarian
(`0x82D231BC`) and gives each other player a start: a Settler (type 0) through
`0x82D11750` at `0x82D23258`, or a city through `0x82D18D88` at `0x82D23348` when
the definition field `+0x1E` is nonzero and the mode `0x8312B8D4` is not -1, plus
extra units at `0x82D23388`. A player is an AI when its bit is not in the human
mask.

`0x82D25170` returns at `0x82D25260` when setup yields -1. Otherwise it runs
virtual `+0x54` of `0x8314F76C` and then the statistics recount at `0x82D2530C`.
That call is a hook point: setup has returned, every peer runs this function
locally, and AI is simulated locally.

The count 2 branch replaces count 6 and Barbarian 5 with 2 and -1 (`0x82D22934`,
`0x82D22938`) when `0x8314F180` is nonzero. It also removes the Barbarians (their
word `0x82F700B0` has 201 readers) and needs humans at ordinals 0 and 1. No
writer of `0x8314F180` was found. Its other readers are `0x82D032B0` and
`0x82D0F19C`. The neighboring `0x8314F17C` is a start turn mark written at
`0x82D24F70`, `0x82D25898`, `0x82D0C8EC` and `0x82D0C958`.

### Network events

An event is five words `{id, a, b, c, d}`. `0x82CE16C8` queues one and drains the
queue through dispatcher `0x82CDDF08`, which has a 66 entry table at `0x82CDE014`.
The post routine `0x82CE1830` sends an event over the network and does not run
it locally when the network byte is set, the local player is valid and either the
event's player is human or its ID is at least `0x29`. The send goes through
`0x82D90988` and session virtual `+0x44`. Every other event runs locally
(`0x82CE1940`); `0x82CE1950` is the variant with an origin player. An AI event
with an ID below `0x29` therefore runs locally on every peer.

Setup sends events `0x3A`, `0x3B` and `0x39` (`0x82D223DC`, `0x82D22460`,
`0x82D224F0`) and, for each human and Barbarian pair, event `0x26` as a network
message (`0x82D24E88`). Otherwise `0x26` runs locally at `0x82D24EA4`. These can
still be in flight when setup returns. None touches AI units.

### Multiplayer behavior

`0x82D0C1E0` keeps its once only check on the local observer, so peers set
different pair matrix bits (`[A][p]` and `[B][p]`). This is native behavior for
any network elimination. The 20 turn rule exists only in network games. The
registry setting for multiplayer resynchronization is stored at `0x8314F1D4`
(`0x82E2D684`). The resync strings are at `0x82D8FCC8` and the start is
`0x82D8FF78`, called from `0x82D0E100`, `0x82D0E2BC`, `0x82CDE3C4` and
`0x82D25B0C`. The per turn comparison is a type 53 check over the scalar
`0x82CD4CF0` ([xbox-resync-target-selection.json](../../manifests/xbox-resync-target-selection.json)),
and a resync carries the host's full state. A peer that applies a different
elimination rule diverges from the first AI event.

### Saving and open questions

The serializer `0x82CC4040` (save `0x82D81654`, load `0x82D86674`) covers the
unit records, the pair matrix, the nine palace words and the count words. Load
routine `0x82D86400` and pre-load `0x82D84238` share one slot table
(`0x821387C4`, `0x821387CC`). A load either skips `0x82D25170` or overwrites what
that function changed, and setup cannot run after a load because it resets the
turn counter. Open questions: the writer and meaning of `0x8314F180`, whether
`0x82D25170` runs on the load path, how a scenario start that gives an AI a city
is eliminated (a kept city and palace stay in the total), and the first diverging
field behind a resync. The evidence is
[RVA-F-0252](../../manifests/ai-civilization-elimination.json).

## Economic and strategic consumers

Native research and production helpers expose three hook points after the cost
is composed. Research exposes the finished technology cost. Unit production
exposes a scalar that the native factor then multiplies and divides by 2.
Building and Wonder production expose a final cost after the existing
reductions. A change at these points needs its own rounding rules, a positive
minimum cost, an AI check and storage of the setting actually used. Percentages
are not retail difficulty fields.

Civilization bonuses already affect one production valuation. A cumulative UEA
lookup (`0x82CF0CB0`, over a 16 by 4 table) can add half a local coefficient
before later scoring. This does not show a leader personality, or any
aggression, diplomacy, army, target or research preference. Candidate 103 reads
UEA 4 at `0x82CB59E8..0x82CB5A08`, and the coefficient enters its score at
`0x82CB5A40..0x82CB5AFC`. Which civilization holds each effect is in
[Civilization bonuses](civilization-bonuses.md#effect-ownership-catalog).

The production score arm advances a local state, adds a scaled term to a
nonnegative coefficient and applies four flag dependent adjustments in order.
With B the incoming `r18`, C the coefficient (negative values set to 0),
`X = U32(B)`, `M = U32(B + 8)`, `A = u32(r15)`, `D = u32(r16)` and
`F = F64(B + 16)`:

```text
U32(B + 4) += 1
X1 = low32(X*A + D)                  stored at B
X2 = X1 mod M  (X2 = X1 when M = 0)  stored at B
S  = low32(C + low32(trunc64((double(trunc(C/2)) * double(X2)) * F)))
```

The adjustments then run in this order, each halving using the current signed
low32: add half of S when bit `0x8` of the halfword at `r19 + low32(r17 + 0x3C)`
is set; halve S when `r26` bit `0x20` is clear; halve S when `r26` bit `0x8` is
set; halve S when bit `0x4` of `U32(r24 + low32(4*r20))` is set. State, scale and
flag meanings are not named, so no random distribution or score range follows.
The comparison replaces the best candidate on a tie, while the unit filter needs
a strictly greater score. The update writes local stack state and continues the
candidate loop. The winner, the city assignment and execution stay open. Exact
arithmetic is in the
[score continuation finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0330/scoreContinuationBoundary).

The [AI findings](../../manifests/ai-options-boundaries.json) hold the exact
hook points, capacities and limits. Starting technology ownership and its
activation timing are in
[starting technology grants](../../manifests/starting-technology-grants.json).
A starting list of arbitrary technologies needs its setup time effects checked.

### Autonomous expansion in OCC games

In OCC (one city challenge) games the AI can still found cities without a Settler, through a tile scan arm
that starts at `0x82CBBE58`, calls the city creator at `0x82CBC03C` and has its continuation at `0x82CBC3D4`; see
[Settler production requirements](unit-definitions.md#settler-production-gates).

## Gold, Food and Culture output

The finished city contributions offer hook points for percentage changes before
the values reach caches and civilization state. Each hook must change both a
register and its saved temporary, because changing a cache or a return value
alone misses known copies. The
[city yield finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0343)
records the registers, widths, native overrides and consumer limits.

| Yield | Hook point | Also change |
| --- | --- | --- |
| Gold | Before `0x82D14ECC`, finished value in `r8` | Saved `stack+0x7C`, before city `+0x46`, the mode 0 aggregate and the later reserve credit. |
| Food | Before `0x82D14280`, finished contribution in `r10` | Saved `stack+0x90`, before city `+0x4C` and `+0x40`, the mode 0 aggregate and the growth input. |
| Culture | Before `0x82D152E8`, finished value in `r18` | Saved `stack+0x78`, before city `+0x48`, the mode 0 aggregate and the later owner accumulator. |

Gold and Culture keep the signed entry owner in `r17` and the mode in `r15`;
`r31` is the city ordinal times `0xBC`. Food keeps the city base in `r21` and the
same city offset in `r31`, but has no common owner register at its earliest
scalar hook point. A Food hook must read the saved entry owner at `stack+0x84`,
because `r4` can hold population on a native branch.

These points keep native composition, including technology, building, Wonder and
civilization effects, and the native clearing that follows must still run. The
path for an excluded owner can clear a credit without rewriting an earlier cache,
and the UEA 42 path clears Food and Gold but keeps Culture. A percentage must
respect these cases and the difference between the signed halfword cache and the
full word contribution.

Food's finished sum is added to the growth box at city `+0x34`. The growth path
subtracts its native threshold and carries the remainder when population grows.
Its negative progress path resets the box and lowers population. Scaling the
accumulated box would compound the change. Scaling the new contribution can
affect both growth and population loss. The evidence does not recover separate
gross harvest and maintenance values, so it supports a growth contribution
option with an explicit sign rule, not a proved gross harvest percentage.

Known downstream effects are limited to these. Gold reaches an owner aggregate,
the reserve credit and one refresh then cache reader. Food reaches its two
snapshots, an owner aggregate and growth state. Culture reaches an owner
aggregate, a separate owner accumulator and two signed `+0x48` inputs of the
border sweep. Complete displays, final yield AI valuation, trade, rush, Great
People and Cultural Victory are not connected. The UEA 25 rush rate and
valuation formulas are separate from city Gold. Scaling the border inputs does
not establish a fixed territorial increment.

The city Culture aggregate also feeds the
[Culture strength score](../../manifests/resource-definitions.json#/centerResourceBonusBoundary/class4ConsumerBoundary),
which takes part in Cultural Leader ranking and a derived border influence
level. The ranking reads the score; border influence also depends on the
quantized level. Both differ from the Cultural Victory count.

Reaching a hook point shows that a contribution was calculated, not that it
happens once per city per turn. Mode 1 skips this yield block, and mode -1
refreshes caches then exits before the state credits. The calendar can call mode
0 more than once for a city and can use cached Culture without recomposing it.
Scale each original temporary once, when its contribution is calculated. Do not
scale a reserve, growth box, accumulator or already scaled cache. A change of
setting needs demonstrated cache invalidation and a known recomputation order.
Saved cache transfer, load order, setting storage, and refresh after capture,
resource or technology changes are open. City founding resource rewards are
separate from these contributions.

## Eternal Kombat and Always at War

Eternal Kombat is a built-in scenario preset whose contacts start as war. Always
at War here means keeping a pair of civilizations at war (relation 0) for the
whole game. Take a human and an AI that meet for the first time. In a normal
game (`WARANDPEACE` 1) the contact handler goes on to offers, demands and
threats. With the Eternal Kombat value the same contact requests war,
`0x82D03388(p, q, 0, 0)`, and skips the offers. Peace stays possible only
through other code paths, listed below, that write the relation matrix.

The [scenario finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/nativeScenarioBoundary)
shows that Eternal Kombat is scenario ordinal 9, with `WARANDPEACE` slot 9 set to
2. The preset also changes upgrade rate, starting size, attack bonus and display
inputs, so copying the whole preset would change more than diplomacy.

The relation matrix is `0x830ED2D8`, stride 8, with `R(p, q) = U32[0x830ED2D8 + 4*(8*p + q)]`.
War is 0, peace is 1 and -1 is an unnamed reset or contact value. Any nonzero
write over a war pair breaks Always at War. Resetting, input replacement,
elimination and member publication also write it and need their own handling.
Diagonal, unused and dynamic Barbarian cells are not part of the active pair
projection. The
[relation generations finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/selectedAlwaysAtWarClosureBoundary)
records the full set of relation generations, refusal paths and setup and load
points.

### Who can change a relation

| Writer | Where | What else it does |
|---|---|---|
| Shared request | `0x82D03388` (`0x82D03484`, `0x82D03488`, `0x82D03494`) | Stores both directions. A positive clock or force 0 can emit message 38. The same nonzero value can return and the same 0 proceeds. |
| Shared application | `0x82D1A6C0` (`0x82D1A6D4..0x82D1A7B8`, groups `0x82D1AA4C..0x82D1AAF8`) | Updates history, flags, clocks and the recount. Group expansion can include diagonal and other pairs. Setup input is separate from gameplay peace. |
| Delivered command 39 | Table `0x82CDE0B0` to `0x82CE0068`; `0x82CE0088` and `0x82CE008C` use record word `+12` | Writes the supplied relation. |
| Reset | `0x82D0606C..0x82D06084`, from the reset at `0x82D217E0` | Fills all 256 bytes (64 words) with `0xFF`, diagonal and unused cells included. |
| Input | `0x82CC4C5C..0x82CC4CA4` (mode 1, null auxiliary) | Replaces all 64 words. A non-null auxiliary stream is a separate copy mode. |
| Contact handler | `0x82CCEFA8`: `0x82CCFB98`, `0x82CCFBA4` store 1; `0x82CCFCE8` peace request; `0x82CCFBC8` war 0 preset | Earlier contact effects happen first. The preset forces war only for reached pairs. |
| Saved contact home | `0x82CD11EC`, `0x82CD11F0` store 3; `0x82CD1654`, `0x82CD1658` and `0x82CD2044`, `0x82CD2048` store 1 | Two notifications are ignored; the Gold chooser branches before debit and credit. |
| Tower of Babel (selector 7) | `0x82D18514`, `0x82D1852C` | A tested -1 becomes 1. An asymmetric reverse war 0 can also be overwritten. |
| Tesla's Peace Ray (selector 11) | `0x82D18AC4`, `0x82D18ADC` | A tested war 0 becomes 1, with clocks and flags. |
| Cleanup | `0x82D1D1C0` (`0x82D1E460`, `0x82D1E468`) | Writes 1 across a row and column for a player with sampled zero cities and Settlers. A sweep of 256 unit records may call `0x82D02390(p, record, 0)` first, at `0x82D1E428`. |

The saved contact home at `stack+0xC8` holds three more symmetric non-war
pairs (the last three rows above that use it). Its full home version and six
register generations are native. Other named homes and readers, including the
United Nations Wonder path (UN19), are classified under stated frame, ABI and
current target conditions. UN19's terminal flag `0x10000` at `0x82FFE7C4` is
separate from relation peace. The recount's nearby stores target the derived
table `0x830E3AD8`, not the relation matrix. An initial search for constructions of the matrix base found 53 split pairs and
52 low sites. It is navigation, not a complete writer count.

Command 38 sets peace through nine call sites (`0x82CCA71C`, `0x82CCA864`,
`0x82CCA910`, `0x82CCAC88`, `0x82CCAD88`, `0x82CCAE28`, `0x82CCB124`,
`0x82CCCA54`, `0x82CC91B0`). Their earlier effects are technology command 43,
Gold request pairs through `0x82D24F98` (which stages command 41 debits and
credits), a unit byte write with `0x82D02390(p, unit, 0)`, presentation and
bookkeeping, and the notification chain through `0x82CC85D0`. No city transfer
was proved in the eight arms recorded for these calls.

### Contact rules in Eternal Kombat

The native scheduler `0x82D034A0` is centered on context K. With K = 0 and three
supplied ordinals it leaves pair 1 and 2 out in both orientations. The edge at
`0x82D1D1C0` keeps its original player in `stack+0x234` and passes K = P at
`0x82D1E90C`. Command 48 can request that sweep, subject to service, mask,
one-shot and delivered-command checks. These are contact paths. They do not
reconcile every pair before setup and load readers.

### Refusing peace

Normal refusal depends on the path:

- The three choosers in `0x82CC9FF8` send native result -1 to the native war
  continuation. When symmetric war 0 is still in place, this skips `0x82CC9078`, keeps
  pair flag 4 and completes normally.
- `0x82CC9078` has a place at `0x82CC90EC` that leads to its existing result 0
  and frame suffix. Cancelling its later notification is too late: the return is
  ignored. The two early `stack+0xC8` contact branches also need a check before
  the notification. The Gold chooser's nonzero result already branches before
  the transfer and keeps its war and completion path.
- Democracy forces the response to accept (response 0) even after the player
  cancels. The place to choose native response 1 is the actual response producer.
  Response 1 keeps war 0, command 34 acknowledgement 99, queue use and the
  `0x82CCD458` completion, and it skips the technology negotiation arm. It is a
  native protocol value, not a new interface row. The offered vector comes from
  LF separated strings, and unmatched 4 is not a supported refusal token.
- The dialog's native cancel target `0x82E053E8` needs ready `+11` and clear
  `+0x434`, marks the dialog closed before the close work and publishes result -1
  after callbacks. The cancel request branch keeps AnimateExit, the current `+4`
  update loop and the usual completion suffix, all of which depend on the same
  dialog, script and finite exit action staying in place. Animation state bytes are not
  written, and call depth does not stop a modal command from re-entering.
- Command 39 writes the supplied relation at `0x82CE0088` and `0x82CE008C`. A
  check after the dispatch depth increment and before its first effects can
  consume a forbidden delivered record with the native result 1 suffix; a return
  of 0 would roll the queue head back. This does not undo earlier producer
  effects. The builders keep the supplied tag. Wrapper `0x82CE1AD8` suppresses 61
  and 62 and passes 39 unchanged. Four apparent builder function pointers belong
  to the PE Exception directory, not application dispatch. Direct call and
  literal searches and those metadata facts do not rule out an indirect producer
  or earlier effects.
- Event 30's producer checks eligibility before it stages a timestamp and emits.
  The real event pick uses `0x821C6548`. Tower of Babel selector 7 changes a
  tested reset -1 to 1; Tesla's Peace Ray selector 11 changes a tested war 0 to 1.
  A check belongs before each forbidden pair body, so that discovery history,
  Wonder presentation, achievement 8 and native tile use and callback completion
  still run with honest refusal text. Returning from the whole event early can
  leave the tile retriggerable.

### Setup and load

A repair after setup is too late for the refresh in CityCreate (`0x82D1A310`):
its relation reader can commit unit displacement or deletion. The hook points for
new game setup are:

1. After the late count and Barbarian stores near `0x82D22940` and before the
   start callbacks. Before the first provisional write the inputs (a count from
   0 to 8, the dynamic Barbarian, and the intended and removal lists) must be
   coherent, and participants scheduled for AI removal are left out. Only
   distinct intended pairs go to war 0. Diagonal, unused, Barbarian and excluded
   native cells keep their values.
2. Setup command 38 with -1 keeps its native bookkeeping, and the matching
   projection comes after its group stores at `0x82D1AAE8`, before the recount.
   Its -1 arm skips the peace only displacement block (`0x82D1A810`).
3. Last, immediately before the original recount call `0x82D2530C` (return address
   `0x82D25310`), after any AI removal and start resource changes, with a fresh
   check of who is in the game.

A civilization counts as active when it has a configured identity and either a
populated owned city or any occupied live unit. Settlers alone are not enough
for a military only civilization. The dynamic Barbarian is excluded. After any
partial change, a failed start or a missing or extra member must discard the whole
candidate setup and enter native cancellation, reset or fresh initialization.
Turning the policy off cannot undo the changes. That abort and rebuild path is
not provided by the inspected APIs. Cities are published at `0x82D1B45C`, and
`0x82D1B460` is a later place to re-check if supported input needs it. Inactive
native cells keep their values, with no rollback ledger or stale restore.

On a successful load of the same generation, the repair comes right before the
single ranking call `0x82D2582C`. The `0x82D25848` recount and the later refresh
still follow. Loaded input has a selected limited copy and callback and count
steps, and a positive report or native 1 alone is not enough: matching completion,
count, buffers and raw state remain conditions. Failed, short or undelivered input
does not trigger repair. These hook points have not passed runtime acceptance.
The relation storage versions are classified apart from the paths that can refuse
a change. The selected producer graph has fixed tag and call blocks and checks of
other entry paths, and it excludes 39 from the selected compiler controlled source
family. Foreign calls, dynamic code changes and arbitrary computed entry into a
routine are outside that. The static work covers single player setup; peer
enforcement, other modes and Game of the Week are separate.

### Automatic AI contacts

`WARANDPEACE` is a signed 16 bit slot 9 at base `0x830E8FD0`, field `+0x12`
(`0x830E8FE2`). The default is 1 and Eternal Kombat is 2. A scan of literal base
loads found 8 loads in 7 functions; pointer and callback aliases are outside it.
Value 2 is broader than contact silence:

| Reader | Function | What value 2 changes |
|---|---|---|
| `0x82CB4000` | `0x82CB3F08` | Subtracts 1 from the selected non-Barbarian city threshold when city flag bit 0 is clear. Value 0 returns 1 instead. |
| `0x82CCA190` | `0x82CC9FF8` | Makes the selected unit candidate -1. Presentation can still happen. |
| `0x82CCFA3C` | `0x82CCEFA8` | Chooses war 0 for the reached pair at `0x82CCFBC8`, skipping the value 0 peace route. |
| `0x82CD0210` | `0x82CCEFA8` | Uses a dedicated war path before the offer, demand and threat suffix. |
| `0x82CD49DC` | `0x82CD4798` | Sets pair history bit 4 and skips the later Great Wall and Democracy response. |
| `0x82CF0E4C` | `0x82CF0E28` | Rejects Great Wall eligibility (normalized index 1). |
| `0x82D03664` | `0x82D034A0` | Adds 5 to the automatic contact age delay. A prior pair turn of -1 skips it. |
| `0x82D16FF8` | `0x82D16BA0` | Suppresses the Great Wall symmetric pair turn writes. |

Value 2 skips the usual negotiation, adds 5 to the delay and, on its automatic
c0 path, sets status `0x10000000` in the word at `0x82FFE7C4` (at `0x82CD0238`
and `0x82CD023C`). Normal negotiation can also set it at `0x82CD0B14` and
`0x82CD0B18`. `0x82D253B8` reads it at `0x82D25574..0x82D25580`, only after
network 0, normalized x equal to the current player, c0, a nonhuman y and
`R(x, y)` not -1; a set bit takes the native no-contact return. `0x82D1EAB0`
clears it at `0x82D1EC0C` and `0x82D1EC10`, and a new game (`0x82D2524C`) clears
the whole word. A one time bit write is not a lasting rule. Pair history bit 4
has warning, capture and nuclear history readers in
[ai-nuclear-weapon-requirements.json](../../manifests/ai-nuclear-weapon-requirements.json#/historyProducerBoundary/responseBoundary);
value 2 alone does not imply a nuclear outcome.

The special demand `0x82CC9FF8(p, q, 999999, -1, 0)` can still reach the leader
presentation at `0x82CCB254` with low Gold, or the chooser at `0x82CCAB98` with
enough Gold. 999999 is a demand value, not a no-dialog marker. Writing only
field 2 is coherent if it is kept after scenario publication and before setup
and gameplay readers, because gameplay rereads it. The scenario transfer carries
index 9 on the 64 halfword path and on the separate 32 halfword legacy path, and
file input and output must succeed for a reload. The field stores the value, not
why it was set. Copying every Eternal Kombat field also changes unrelated preset
settings.

The hook point at `0x82D25580` can extend a reached check to its existing return
at `0x82D255B0` for a pair of a validated local human x and an active non-Barbarian
AI y. The registers are `r31` = x and `r29` = y. The native path already needs
c0 and a known relation. Ten direct wrapper calls were classified: four
automatic c0 calls and six explicit c1 calls. The identified c1 routes and the
independent command 33 dispatch (`0x82CCBED0`) are outside this check, and
command 33 is not proved to be manual only. The native condition `R(x, y)` not -1 still applies, and
a pair set to 0 by projection may not yet be disclosed, so first contact needs
checking. Other message producers are not silenced. The
[contact finding](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362/aiContactSilenceBoundary)
records the full reader table, inputs and limits.

### Default transport path for command 48

The records below are facts about the default network transport that carries
command 48. None of them shows that command 48 is received, who may send it, or
continuous war between every pair. Each is a finding in
[ai-options-boundaries.json](../../manifests/ai-options-boundaries.json#/findings/RVA-F-0362).

- `constructorTransportInitializationBoundary`: the call at `0x82CB1348` (target
  `0x82CB12F0`) reaches the constructor `0x82CA5E80`. The store at `0x82CA5EC4`
  writes zero to `S+0x14` before the first allocator call, and the 82 word local
  object has no later explicit overlapping store relative to S. Helper aliases,
  normal return and the receiver staying the same remain conditions. With a zero
  `S+0x14`, the accepted sender takes its missing transport path.
- `sameSTransportPublicationBoundary`: child table `+0x18` is `0x82CA7720`. Under
  the stated call, allocator and helper conditions, `0x82CA77B0` installs table
  `0x8215FC0C` to P and `0x82CA77C4` publishes it to the same
  `S+0x14`. Its `+0x0C` cell selects `0x82CA0488`. An allocation of zero
  also publishes zero, and the next pointer read has no null check, so nothing
  follows about a failed completion. The actual `+0x18` call, the current
  `S+0x130` and the initialization of captured table or current P `+0x04` are
  still needed for the table to reach the sender and the receipt.
- `selectedTransportQueueCopyBoundary`: `0x82CA0488` and the payload initializer
  `0x82C9FA10`. A nonzero low 32 bit routing input requests `0x82A087A8`. Zero
  requests a separate payload E and node J, then publishes J to the local
  `P+116` and `P+120` head and tail and adds 1 to `P+64`. The node stores E, not
  the original serialized buffer pointer. With a supported block, count, storage,
  clear and copy, and alias and lifetime conditions, E holds the selected source
  bytes plus zero padding. Clear before copy can destroy aliased source bytes,
  and aliasing of the node and control words can change resampled tail state.
  Storage delivery, the queue and payload staying in place, and one connected consumer,
  parser, factory or message processing edge are open. A copy request or queue
  append does not show a receipt or authority, and it needs coherent earlier
  links and a fresh node.
- `selectedTransportMethodFrontierBoundary`: the installed table `+0x10` cell
  `0x8215FC1C` points to `0x82CA0080`, with the direct helper `0x82C9FF68`. Their
  comparisons against globals can reach the current Q = `U32[P+4]` virtual `+0x18`
  and other external requests. Those targets, their storage and lifetime and their
  meanings are open. Neither local body explicitly reads `P+64`, `P+116`,
  `P+120` or `J+0`. No selected call links this slot's second argument V to the
  queued E or J, or defines a returned payload. Indirect effects are possible,
  so the local absence shows no actual non-use or release rule. A connected queue
  consumer and received processing are open.
- `transportConstructorContextBoundary`: `0x82CA07DC` stores its second
  argument at `P+4` after two opaque helper requests. The accepted publication path
  supplies Q = `U32[S+0x18]`. This narrows the later current Q `+0x18` call target
  to a constructor argument; the word alone does not show Q's table,
  effects or lifetime. Whether the later initializer and call keep these values, and any identity of a
  queued E with a received command, are open.
- `selectedTransportContextChildBoundary`: the installed Q `+0x18` method
  `0x82CA08D8` looks up T from Q `+4`, gets R through the captured T table `+0x100`,
  then looks up `low32(V)` at R `+68`. The helper's word U (zero, or node `+12`)
  becomes the second argument to captured table `+0x64`. The full V is not that
  callback argument. The current registry, map, table and node must stay valid.
  For a default child and table that independently stay in place, the callback prefix tells
  a null U from a signed `U+24` before further requests. No actual T equal to S,
  the identity of the queued E, which function holds the payload, or receipt of
  command 48 follows. The
  constructor path keeps its thunk, current state and finite return conditions.
- `selectedTransportDefaultDispatchPrefixBoundary`: table `0x8215FA78` slot
  `+0xDC` (`0x8215FB54`) points to `0x82CA58A0`. The prefix keeps the full incoming
  T, U and F, reads the key `U32[U+0x8]`, requests the target at `+0x100` of the
  freshly read current table, then passes its return and the cached key to the
  accepted `0x82CA97A8` lookup. A zero or payload result controls a local low 32
  bit branch. The prefix identifies no command or delivered bytes. Using the
  default `+0x100` result also needs fresh equality of the current table, beyond
  equality at an earlier `+0xDC` dispatch. The current map, sentinel, node, frame
  and arguments must stay valid. The prefix ends at the result check.
- `selectedTransportDefaultProcessingRequestBoundary`: the nonzero fallthrough makes
  a fresh `+0x118` request at `0x82CA58F8` with T in `r3`, while `r4` and `r5` keep
  the lookup's exit values. It caches `U32[O+0x18]` first. Only after that
  target returns normally does `0x82CA5908` request `0x82E463D0` with the earlier
  return, U, the cached word and F. Earlier table equality gives no later
  provider identity. Both effects, the received U, the `+0x10` call, command 48, K,
  peer authority and war between all pairs are open.

## Limits and open questions

- Eight slot storage does not show that more than four AI civilizations, a game
  with zero AI or a larger network layout works. Initialization, turn order,
  placement, interface and networking for players 6 and 7 are unverified.
- Difficulty readers are not fully listed, the legal input range is open, and no
  difficulty specific happiness or general aggression effect is shown.
- The AI paths in the overview are not connected into a complete turn: research
  and production winners, unit command delivery, diplomacy completion and natural
  Spy selection are open.
- The Always at War hook points have not passed runtime acceptance.
- Evidence is in [ai-options-boundaries.json](../../manifests/ai-options-boundaries.json)
  and [ai-civilization-elimination.json](../../manifests/ai-civilization-elimination.json).
